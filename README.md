# AgentFleet

Run parallel AI coding agents on **git worktrees**: one CLI for init, terminals, previews, and a `doctor` check so setup fails fast instead of silently.

Open source · MIT · **[github.com/buyan-kh/agentfleet](https://github.com/buyan-kh/agentfleet)**

## Install

**Recommended (global npm):**

```bash
npm install -g @buyan14/agentfleet@latest
agentfleet --help
```

**From source:** clone the repo, then `PYTHONPATH=. python -m agent_fleet.cli --help`, or `pip install -e .`.

More paths (upgrade, uninstall, interpreters): **[docs/installation.md](docs/installation.md)**

## Quick start

Inside a git repo:

1. `agentfleet init`
2. `agentfleet doctor`
3. `agentfleet setup`
4. `agentfleet launch --terminal ghostty-splits --ghostty-size 180x50` · or `tmux` · `iterm` · `print`
5. `agentfleet preview` — add `[[preview.services]]` in `agentfleet.toml` for dashboard + apps

Workflow in one line: **`init → doctor → setup → launch → preview`**

## Workflow

| Phase | Command | What it does |
|-------|---------|--------------|
| Configure | `agentfleet init` | Writes `agentfleet.toml` |
| Verify | `agentfleet doctor` | CLIs, Python, git, paths |
| Worktrees | `agentfleet setup` | Fleet worktrees |
| Terminals | `agentfleet launch` | Ghostty, tmux, iTerm, or print-only |
| Preview | `agentfleet preview` | Dashboard + services from TOML |
| Ops | `agentfleet status` / `stop` / `clean` | Fleet lifecycle |

## Example session

```
cd ~/src/my-app && agentfleet init
agentfleet doctor
agentfleet setup && agentfleet launch --terminal print
agentfleet preview
agentfleet status
```

Before `preview.services`: you get a short checklist to finish config. After: dashboard + ports from `agentfleet.toml`.

## Terminals (`launch`)

| `--terminal` | Notes |
|----------------|-------|
| `ghostty-splits` | One window, tiled panes (macOS may need Accessibility) |
| `ghostty` | One window per agent |
| `tmux` | Single session |
| `iterm` | Tabs/windows |
| `print` | Print commands only |

## Preview services

Anything you can describe in **`agentfleet.toml`** (API, web, helpers).

```toml
[preview]
dashboard_port = 3999

[[preview.services]]
name = "api"
dir = "api"
port_base = 8000
command = "python -m uvicorn app.main:app --host 127.0.0.1 --port {port} --reload"

[[preview.services]]
name = "web"
dir = "frontend"
port_base = 3000
command = "npm run dev -- --port {port}"
primary = true
env = { NEXT_PUBLIC_API_URL = "{api_url}" }
```

Placeholders: `{port}`, `{service_url}`, `{api_url}`, `{ui_url}`, `{worktree}`.

## Hand off to your AI

Paste into your coding assistant:

```
Configure AgentFleet for this repository.

1. Create or update agentfleet.toml.
2. Keep the default fleet at 2 Codex agents and 2 Claude agents unless this repo needs something else.
3. Inspect the project and add [[preview.services]] for the local services needed to preview work.
4. For each preview service set name, dir, port_base, command using {port}, and env values if needed.
5. Mark the browser-facing service with primary = true.
6. Run `agentfleet doctor` and explain any failures.
7. If this is frontend-only, backend-only, Docker-only, mobile, or multi-service, configure the closest useful setup and explain the tradeoff.
```

Same checklist appears after **`agentfleet init`** and **`agentfleet preview`** when preview is not configured.

## More commands

```bash
agentfleet status
agentfleet stop
agentfleet clean
agentfleet tasks --out agentfleet-tasks.yaml
agentfleet upgrade
```

## Docs

| Doc | What it covers |
|-----|----------------|
| [Installation](docs/installation.md) | npm vs source, upgrade, uninstall, interpreter override |

## Prerequisites

You'll need **[Node.js](https://nodejs.org/)** (18+), **[Python](https://www.python.org/)** (3.11+), **[Git](https://git-scm.com/)**, `python3` on `PATH` (or set `AGENTFLEET_PYTHON`), and whichever **agent CLIs** you configure (defaults assume Claude Code and Codex on `PATH`). Run **`agentfleet`** from inside a **git repository**.

## Troubleshooting

**`doctor` fails?** Fix what it prints (missing CLI, wrong Python, not in a git repo).

**Stale global install?** `npm install -g @buyan14/agentfleet@latest` or `agentfleet upgrade`.

**Wrong Python picked up?** Set `AGENTFLEET_PYTHON` to your 3.11+ binary.

**Skills / agents not found?** Ensure `command=` in `agentfleet.toml` matches tools on your `PATH`.

## License

MIT.
