# AgentFleet

One CLI manages **coding agents across isolated git worktrees**: init config, spawn terminals, preview multi-service stacks, and sanity-check tooling.

---

## Requirements

| | |
|---|---|
| **Runtime** | Node.js **18+**, Python **3.11+**, **Git** |
| **Agents** | CLIs you list in config (defaults assume **Claude Code** & **Codex** on `PATH`) |
| **Context** | Run commands **inside a git repository** |

---

## Install

```bash
npm install -g @buyan14/agentfleet@latest
agentfleet --help
```

The global package ships the Python modules; the launcher sets `PYTHONPATH` so **`python3` must be available** (`AGENTFLEET_PYTHON` overrides the interpreter).

**Dev / without npm:** clone this repo, then `PYTHONPATH=. python -m agent_fleet.cli`.

Details, PATH checks, and uninstall: **[docs/installation.md](docs/installation.md)**.

---

## Quick start

```bash
git clone <your-repo> && cd <your-repo>
agentfleet init
agentfleet doctor
agentfleet setup
agentfleet launch --terminal ghostty-splits --ghostty-size 180x50
agentfleet preview
```

| Command | Purpose |
|---------|---------|
| `init` | Write `agentfleet.toml` |
| `doctor` | Verify CLIs, Python, repos |
| `setup` | Create worktrees for the fleet |
| `launch` | Open terminals (see terminals below) |
| `preview` | Dashboard + preview services (needs `[[preview.services]]`) |

---

## Terminals (`launch`)

| `--terminal` | Notes |
|----------------|-------|
| `ghostty-splits` | One window, tiled panes (macOS may need **Accessibility**) |
| `ghostty` | One window per agent |
| `tmux` | Single tmux session |
| `iterm` | iTerm tabs/windows |
| `print` | Print commands only |

---

## Preview services

Define stack in **`agentfleet.toml`** (frontend, API, Docker, mobile proxies—anything):

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

Reserved placeholders include `{port}`, `{service_url}`, `{api_url}`, `{ui_url}`, `{worktree}`.

---

## Hand off to your AI

Paste into the assistant working on **this repo**:

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

(Same checklist appears after **`agentfleet init`** and **`agentfleet preview`** when preview is unset.)

---

## More commands

```bash
agentfleet status
agentfleet stop
agentfleet clean
agentfleet tasks --out agentfleet-tasks.yaml
agentfleet upgrade          # npm global → latest
```

---

## Troubleshooting

1. **`agentfleet doctor`** — single source of truth for misconfig.
2. **Stale global install:** `npm install -g @buyan14/agentfleet@latest` or `agentfleet upgrade`.
3. **Not in a repo:** AgentFleet resolves paths from **`git`**; run inside a checkout.

MIT · If AgentFleet helps your workflow, a star on the repo is appreciated.
