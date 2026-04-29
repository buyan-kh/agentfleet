# AgentFleet

Run multiple coding agents in isolated git worktrees from one CLI.

AgentFleet creates one worktree per agent slot, launches Claude/Codex/other CLI
agents in parallel, and can start a local preview dashboard for any project stack.

GitHub: https://github.com/buyan-kh/agentfleet

If AgentFleet helps your multi-agent workflow, please star the project.

## Requirements

- Node.js 18+
- Python 3.11+
- Git
- The agent CLIs you configure, such as `claude` and `codex`
- Optional: `tmux`, Ghostty, or iTerm for terminal launching

## Install

```bash
npm install -g @buyan14/agentfleet
```

Then run:

```bash
agentfleet --help
```

## Quick Start

From inside any git repo:

```bash
agentfleet doctor
agentfleet setup --claude 2 --codex 2
agentfleet launch --terminal ghostty --claude 2 --codex 2
```

For one terminal container instead of separate Ghostty windows:

```bash
agentfleet launch --terminal tmux --claude 2 --codex 2
```

## Preview Dashboard

If your repo has preview commands configured:

```bash
agentfleet preview --claude 2 --codex 2
```

AgentFleet prints and opens the local dashboard:

```text
http://localhost:3999
```

Preview is service-based. AgentFleet does not know whether your app uses Vite,
Next.js, Rails, FastAPI, Django, Go, Rust, Docker Compose, a mobile companion
server, or only static frontend code, so describe the services in
`agentfleet.toml`:

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
dir = "app"
port_base = 3000
command = "npm run dev -- --port {port}"
primary = true
env = { NEXT_PUBLIC_API_URL = "{api_url}" }
```

Each service runs once per worktree. AgentFleet assigns ports by adding the
worktree slot number to `port_base`, so `web` with `port_base = 3000` becomes
`3001`, `3002`, and so on.

Available placeholders in service commands and env values:

- `{port}` / `{service_port}`: this service's assigned port.
- `{service_url}`: this service's localhost URL.
- `{api_url}`: URL for a service named `api`, `backend`, or `server`.
- `{ui_url}`: URL for the primary service.
- `{worktree}`: absolute path to the worktree.

Supported shapes:

- Frontend-only: one service with `primary = true`.
- Backend-only: one service with `primary = true`; the dashboard embeds whatever that service serves.
- UI + API: two services, with the UI marked `primary = true` and an env value pointing to `{api_url}`.
- Multi-service apps: add as many `[[preview.services]]` blocks as needed.
- Docker-only stacks: use a service command like `docker compose up --build` and expose a configured port.

If the dashboard loads but a service fails, check the per-slot logs printed by
`agentfleet preview`, then verify:

- Every service `dir` exists in every worktree you are previewing.
- Every service `command` binds to `{port}`.
- Frontend env names match what the app actually reads.
- Exactly one browser-facing service has `primary = true`, or AgentFleet will embed the last service.

## AI Agent Setup Prompt

Paste this into your coding agent inside the repo where you want AgentFleet:

```text
Configure AgentFleet preview for this repository.

1. Inspect the repo structure and identify:
   - every service needed for a useful local preview
   - each service directory
   - each command that starts a service on a caller-provided port
   - any env vars services need to talk to each other
   - which service should be embedded in the browser dashboard
2. Create or update agentfleet.toml.
3. Keep the default fleet size at 2 Codex agents and 2 Claude agents.
4. In [preview], set dashboard_port = 3999.
5. Add [[preview.services]] blocks. For each service set:
   - name
   - dir
   - port_base
   - command using {port}
   - env values if needed, using placeholders like {api_url} or {service_url}
   - primary = true on the browser-facing service
6. Do not guess silently. If the project is frontend-only, backend-only, mobile, Docker-only, or multi-service, configure the closest useful preview shape and explain the tradeoff.
7. Run `agentfleet doctor` and explain any failures.
```

## Config

Create a starter config:

```bash
agentfleet init
```

This writes `agentfleet.toml` in the current repo. Example:

```toml
project_name = "my-repo"
worktree_root = "../.agentfleet-worktrees"
base_ref = "origin/main"

[[agents]]
kind = "codex"
count = 2
command = "codex"
branch_prefix = "codex/task"

[[agents]]
kind = "claude"
count = 2
command = "claude"
branch_prefix = "claude/task"

[preview]
dashboard_port = 3999

[[preview.services]]
name = "api"
dir = "api"
port_base = 8000
command = "python -m uvicorn app.main:app --host 127.0.0.1 --port {port} --reload"

[[preview.services]]
name = "web"
dir = "app"
port_base = 3000
command = "npm run dev -- --port {port}"
primary = true
env = { NEXT_PUBLIC_API_URL = "{api_url}" }
```

## Common Commands

```bash
agentfleet doctor
agentfleet setup
agentfleet launch --terminal print
agentfleet status
agentfleet preview
agentfleet stop
agentfleet clean
```

