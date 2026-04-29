# AgentFleet

Run multiple coding agents in isolated git worktrees from one CLI.

GitHub: https://github.com/buyan-kh/agentfleet

If AgentFleet helps your workflow, please star the project.

## Install

```bash
npm install -g @buyan14/agentfleet
agentfleet --help
```

Requires Node.js 18+, Python 3.11+, Git, and the agent CLIs you configure.

## Give This To Your AI Agent

Paste this into the repo where you want AgentFleet:

```text
Configure AgentFleet for this repository.

1. Create or update agentfleet.toml.
2. Keep the default fleet at 2 Codex agents and 2 Claude agents unless this repo needs something else.
3. Inspect the project and add [[preview.services]] for the local services needed to preview work.
4. For each preview service set name, dir, port_base, command using {port}, and env values if needed.
5. Mark the browser-facing service with primary = true.
6. Run `agentfleet doctor` and explain any failures.
7. If this is frontend-only, backend-only, Docker-only, mobile, or multi-service, configure the closest useful setup and explain the tradeoff.
```

## Quick Start

```bash
agentfleet init
agentfleet doctor
agentfleet setup
agentfleet launch --terminal ghostty-splits
agentfleet preview
```

Terminal options:

- `ghostty-splits`: one Ghostty window with native split panes. Experimental on macOS; may need Accessibility permission.
- `ghostty`: separate Ghostty windows.
- `tmux`: one tmux session.
- `iterm`: separate iTerm tabs/windows.
- `print`: print the commands instead of launching.

## Preview Services

AgentFleet is stack-agnostic. Describe any service shape in `agentfleet.toml`:

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

Placeholders: `{port}`, `{service_url}`, `{api_url}`, `{ui_url}`, `{worktree}`.

This supports frontend-only, backend-only, UI+API, Docker commands, mobile companion servers, and multi-service apps.

## Useful Commands

```bash
agentfleet status
agentfleet stop
agentfleet clean
agentfleet tasks --out agentfleet-tasks.yaml
```

`agentfleet tasks` only writes a task scaffold today. A future version can use that file to dispatch work across agents.

