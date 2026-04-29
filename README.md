# AgentFleet

Run multiple coding agents in isolated git worktrees from one CLI.

AgentFleet creates one worktree per agent slot, launches Claude/Codex/other CLI
agents in parallel, and can start a local preview dashboard for review.

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
agentfleet setup --claude 3 --codex 3
agentfleet launch --terminal ghostty --claude 3 --codex 3
```

For one terminal container instead of separate Ghostty windows:

```bash
agentfleet launch --terminal tmux --claude 3 --codex 3
```

## Preview Dashboard

If your repo has preview commands configured:

```bash
agentfleet preview --claude 3 --codex 3
```

Then open:

```text
http://localhost:3999
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
api_dir = "api"
ui_dir = "app"
api_command = "python -m uvicorn app.main:app --host 127.0.0.1 --port {api_port} --reload"
ui_command = "npm run dev -- -p {ui_port}"
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

## Publish

```bash
cd /Users/buyantogtokh/Projects/AgentFleet
npm publish --access public
```

