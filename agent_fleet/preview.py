"""Preview dashboard and process lifecycle for worktree fleets."""

from __future__ import annotations

import html
import http.server
import json
import os
import signal
import socket
import subprocess
import threading
import time
from pathlib import Path

from .commands import run
from .models import AgentSlot, FleetConfig, PreviewSlot

STATE_FILE = "preview-processes.json"


def start_preview(cfg: FleetConfig, slots: list[AgentSlot], install_deps: bool = True) -> int:
    """Start configured API/UI previews and serve the dashboard until interrupted."""

    if not cfg.preview.configured:
        print("Preview is not configured. Run `agentfleet init` and fill [preview].")
        return 1

    preview_slots = build_preview_slots(cfg, slots)
    if not preview_slots:
        print("No previewable worktrees found for the configured preview dirs.")
        return 1

    validate_ports(cfg, preview_slots)
    state_root = cfg.resolved_state_root()
    state_root.mkdir(parents=True, exist_ok=True)

    processes: list[subprocess.Popen[str]] = []
    try:
        for preview in preview_slots:
            processes.extend(start_preview_processes(cfg, preview, install_deps))
        write_state(cfg, preview_slots, processes)
        dashboard_path = write_dashboard(cfg, preview_slots)
        server = start_dashboard_server(dashboard_path.parent, cfg.preview.dashboard_port)
        print_summary(cfg, preview_slots)
        wait_forever(processes, server)
    finally:
        for proc in processes:
            stop_process(proc.pid)
        clear_state(cfg)
    return 0


def build_preview_slots(cfg: FleetConfig, slots: list[AgentSlot]) -> list[PreviewSlot]:
    """Return preview metadata with unique ports across all agent families."""

    preview_slots: list[PreviewSlot] = []
    for preview_index, slot in enumerate(
        [slot for slot in slots if is_previewable(cfg, slot.path)], start=1
    ):
        preview_slots.append(build_preview_slot(cfg, slot, preview_index))
    return preview_slots


def build_preview_slot(cfg: FleetConfig, slot: AgentSlot, preview_index: int | None = None) -> PreviewSlot:
    """Return preview metadata for a slot."""

    port_offset = slot.index if preview_index is None else preview_index
    api_port = cfg.preview.api_base_port + port_offset
    ui_port = cfg.preview.ui_base_port + port_offset
    log_root = cfg.resolved_state_root() / "logs"
    return PreviewSlot(
        slot=slot,
        api_port=api_port,
        ui_port=ui_port,
        api_log=log_root / f"{slot.label}-api.log",
        ui_log=log_root / f"{slot.label}-ui.log",
    )


def is_previewable(cfg: FleetConfig, worktree: Path) -> bool:
    """Return whether a worktree contains the configured preview directories."""

    return (worktree / cfg.preview.api_dir).is_dir() and (worktree / cfg.preview.ui_dir).is_dir()


def validate_ports(cfg: FleetConfig, previews: list[PreviewSlot]) -> None:
    """Fail early if any configured preview port is occupied."""

    ports = [cfg.preview.dashboard_port]
    for preview in previews:
        ports.extend([preview.api_port, preview.ui_port])
    for port in ports:
        if not port_is_free(port):
            raise SystemExit(f"Port {port} is already in use. Stop it or use fewer slots.")


def port_is_free(port: int) -> bool:
    """Return whether localhost has an active listener on the port."""

    checks = [(socket.AF_INET, ("127.0.0.1", port)), (socket.AF_INET6, ("::1", port))]
    for family, address in checks:
        with socket.socket(family, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.2)
            try:
                if sock.connect_ex(address) == 0:
                    return False
            except OSError:
                continue
    return True


def start_preview_processes(
    cfg: FleetConfig, preview: PreviewSlot, install_deps: bool
) -> list[subprocess.Popen[str]]:
    """Start the configured API and UI commands for one preview slot."""

    api_dir = preview.slot.path / cfg.preview.api_dir
    ui_dir = preview.slot.path / cfg.preview.ui_dir
    data_dir = preview.slot.path / cfg.preview.data_dir if cfg.preview.data_dir else preview.slot.path
    preview.api_log.parent.mkdir(parents=True, exist_ok=True)

    if install_deps and cfg.preview.install_if_missing:
        missing = ui_dir / cfg.preview.install_if_missing
        if not missing.exists() and cfg.preview.install_command:
            print(f"[{preview.slot.label}] installing UI dependencies...")
            run(split_command(cfg.preview.install_command), cwd=ui_dir)

    api_log = preview.api_log.open("w", encoding="utf-8")
    ui_log = preview.ui_log.open("w", encoding="utf-8")

    api_env = os.environ.copy()
    api_env["PYTHONPATH"] = str(preview.slot.path)
    if cfg.preview.data_dir:
        api_env["THE_SIMILARITY_DATA_ROOT"] = str(data_dir)
    ui_env = os.environ.copy()
    ui_env["NEXT_PUBLIC_THE_SIMILARITY_API_URL"] = preview.api_url

    api_proc = subprocess.Popen(
        split_command(render_command(cfg.preview.api_command, preview)),
        cwd=api_dir,
        env=api_env,
        stdout=api_log,
        stderr=subprocess.STDOUT,
        text=True,
    )
    ui_proc = subprocess.Popen(
        split_command(render_command(cfg.preview.ui_command, preview)),
        cwd=ui_dir,
        env=ui_env,
        stdout=ui_log,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return [api_proc, ui_proc]


def render_command(template: str, preview: PreviewSlot) -> str:
    """Render preview command templates."""

    return template.format(
        api_port=preview.api_port,
        ui_port=preview.ui_port,
        api_url=preview.api_url,
        ui_url=preview.ui_url,
        worktree=preview.slot.path,
    )


def split_command(command: str) -> list[str]:
    """Split a shell-like command template into argv."""

    import shlex

    return shlex.split(command)


def write_dashboard(cfg: FleetConfig, previews: list[PreviewSlot]) -> Path:
    """Write a live preview wall with embedded UI frames."""

    dashboard_dir = cfg.resolved_state_root() / "dashboard"
    dashboard_dir.mkdir(parents=True, exist_ok=True)
    cards = "\n".join(render_card(preview) for preview in previews)
    path = dashboard_dir / "index.html"
    path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AgentFleet Preview Wall</title>
  <style>
    :root {{
      --bg:
        radial-gradient(circle at 18% 12%, rgba(232, 196, 176, .58), transparent 28%),
        radial-gradient(circle at 78% 6%, rgba(91, 138, 114, .50), transparent 32%),
        radial-gradient(circle at 62% 88%, rgba(194, 101, 92, .28), transparent 34%),
        linear-gradient(160deg, #4a7a5a 0%, #6b9a72 25%, #c4b896 55%, #8a6a4a 80%, #3d2f1f 100%);
      --surface: rgba(255,255,255,.78);
      --ink: #171714;
      --muted: #6f7168;
      --line: rgba(22,22,20,.12);
      --accent: #3d6650;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      background-attachment: fixed;
      color: var(--ink);
    }}
    .shell {{
      min-height: 100vh;
      display: grid;
      grid-template-columns: 260px 1fr;
      gap: 16px;
      padding: 16px;
    }}
    aside, .card {{
      border: 1px solid rgba(255,255,255,.52);
      background: var(--surface);
      backdrop-filter: blur(20px) saturate(120%);
      box-shadow: 0 24px 80px rgba(38,43,31,.18);
      border-radius: 16px;
    }}
    aside {{ padding: 18px; }}
    h1 {{
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      font-size: 34px;
      line-height: .96;
      font-weight: 400;
      letter-spacing: -.03em;
    }}
    .copy {{ color: var(--muted); line-height: 1.45; font-size: 13px; }}
    .stat-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin: 18px 0; }}
    .stat {{ border: 1px solid var(--line); border-radius: 12px; padding: 10px; background: rgba(255,255,255,.55); }}
    .label {{ color: var(--muted); font-size: 10px; text-transform: uppercase; letter-spacing: .12em; font-weight: 700; }}
    .value {{ margin-top: 2px; font-family: Georgia, serif; font-size: 28px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(520px, 1fr)); gap: 16px; }}
    .card {{ overflow: hidden; }}
    .card-head {{ padding: 14px 16px; border-bottom: 1px solid var(--line); display: flex; justify-content: space-between; gap: 12px; align-items: start; }}
    .card h2 {{ margin: 2px 0 0; font-size: 16px; }}
    .links {{ display: flex; gap: 8px; flex-wrap: wrap; }}
    .pill {{ display: inline-block; padding: 7px 10px; border-radius: 999px; background: #fff; border: 1px solid var(--line); color: var(--accent); font-weight: 700; text-decoration: none; font-size: 12px; }}
    iframe {{ width: 100%; height: 420px; display: block; border: 0; background: #fff; }}
    .meta {{ padding: 12px 16px; display: grid; gap: 8px; border-top: 1px solid var(--line); }}
    code {{ display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; background: rgba(255,255,255,.66); border: 1px solid var(--line); border-radius: 9px; padding: 8px; font-size: 12px; }}
    @media (max-width: 900px) {{ .shell {{ grid-template-columns: 1fr; }} .grid {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <div class="shell">
    <aside>
      <div class="label">AgentFleet</div>
      <h1>Preview Wall</h1>
      <p class="copy">Local review wall for agent worktrees. Each card embeds a live UI preview backed by its isolated API and worktree.</p>
      <div class="stat-grid">
        <div class="stat"><div class="label">Agents</div><div class="value">{len(previews)}</div></div>
        <div class="stat"><div class="label">Dashboard</div><div class="value">{cfg.preview.dashboard_port}</div></div>
      </div>
      <p class="copy">Generated at <code>{html.escape(str(path))}</code></p>
    </aside>
    <main class="grid">
      {cards}
    </main>
  </div>
</body>
</html>
""",
        encoding="utf-8",
    )
    return path


def render_card(preview: PreviewSlot) -> str:
    """Render one live preview card."""

    slot = preview.slot
    return f"""<article class="card">
  <div class="card-head">
    <div>
      <div class="label">{html.escape(slot.label)}</div>
      <h2>{html.escape(slot.branch)}</h2>
    </div>
    <div class="links">
      <a class="pill" href="{preview.ui_url}" target="_blank" rel="noreferrer">UI :{preview.ui_port}</a>
      <a class="pill" href="{preview.api_url}" target="_blank" rel="noreferrer">API :{preview.api_port}</a>
    </div>
  </div>
  <iframe src="{preview.ui_url}" loading="lazy" title="{html.escape(slot.label)} preview"></iframe>
  <div class="meta">
    <div class="label">Worktree</div>
    <code>{html.escape(str(slot.path))}</code>
    <div class="label">Logs</div>
    <code>{html.escape(str(preview.api_log))}</code>
    <code>{html.escape(str(preview.ui_log))}</code>
  </div>
</article>"""


def start_dashboard_server(root: Path, port: int) -> http.server.ThreadingHTTPServer:
    """Serve the generated dashboard in a background thread."""

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args: object, **kwargs: object) -> None:
            super().__init__(*args, directory=str(root), **kwargs)

        def log_message(self, format: str, *args: object) -> None:
            return

    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def print_summary(cfg: FleetConfig, previews: list[PreviewSlot]) -> None:
    """Print dashboard and slot URLs."""

    print(f"\nDashboard -> http://localhost:{cfg.preview.dashboard_port}")
    for preview in previews:
        print(f"  {preview.slot.label}: {preview.ui_url} | {preview.api_url}")
        print(f"    logs: {preview.api_log} | {preview.ui_log}")
    print("\nPress Ctrl+C to stop previews.")


def wait_forever(
    processes: list[subprocess.Popen[str]], server: http.server.ThreadingHTTPServer
) -> None:
    """Wait until interrupted or a child preview exits."""

    try:
        while True:
            for proc in processes:
                if proc.poll() is not None:
                    raise SystemExit(f"Preview process exited early with code {proc.returncode}.")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping preview fleet...")
    finally:
        server.shutdown()


def write_state(cfg: FleetConfig, previews: list[PreviewSlot], processes: list[subprocess.Popen[str]]) -> None:
    """Persist enough process state for ``status`` and ``stop``."""

    state = {
        "dashboard_port": cfg.preview.dashboard_port,
        "processes": [proc.pid for proc in processes],
        "previews": [
            {
                "label": preview.slot.label,
                "ui_url": preview.ui_url,
                "api_url": preview.api_url,
                "api_log": str(preview.api_log),
                "ui_log": str(preview.ui_log),
            }
            for preview in previews
        ],
    }
    state_path(cfg).write_text(json.dumps(state, indent=2), encoding="utf-8")


def state_path(cfg: FleetConfig) -> Path:
    """Return the preview state file path."""

    root = cfg.resolved_state_root()
    root.mkdir(parents=True, exist_ok=True)
    return root / STATE_FILE


def clear_state(cfg: FleetConfig) -> None:
    """Remove stale preview process state."""

    path = state_path(cfg)
    if path.exists():
        path.unlink()


def stop_previews(cfg: FleetConfig) -> int:
    """Stop preview processes from the saved state file."""

    path = state_path(cfg)
    if not path.exists():
        print("No saved preview processes found.")
        return 0
    data = json.loads(path.read_text(encoding="utf-8"))
    for pid in data.get("processes", []):
        stop_process(int(pid))
    clear_state(cfg)
    print("Stopped preview processes.")
    return 0


def print_saved_preview_state(cfg: FleetConfig) -> None:
    """Print saved preview URLs and logs if a dashboard is running."""

    path = state_path(cfg)
    if not path.exists():
        print("\npreview: no saved preview processes")
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    print(f"\npreview dashboard: http://localhost:{data.get('dashboard_port')}")
    for preview in data.get("previews", []):
        print(f"  {preview.get('label')}: {preview.get('ui_url')} | {preview.get('api_url')}")
        print(f"    logs: {preview.get('api_log')} | {preview.get('ui_log')}")


def stop_process(pid: int) -> None:
    """Terminate a process if it is still alive."""

    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    except PermissionError:
        print(f"Could not stop pid {pid}: permission denied.")
