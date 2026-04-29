# AgentFleet

Shipping with multiple AI coding agents usually means juggling terminals, repos, and local previews by hand. You want Claude in one tree, Codex in another, and your app stack running somewhere you can click—without becoming a glue script engineer.

**AgentFleet is how you run that.** One CLI initializes a fleet of agents on git worktrees, opens the right terminals, spins up preview services from config, and runs `doctor` so broken setups surface before you burn an hour guessing.

Fork it or install from npm. MIT.

**Who this is for:**

- **Solo builders** running more than one agent or more than one worktree against the same codebase
- **Tech leads** who want a repeatable, shareable fleet layout (`agentfleet.toml` in the repo)
- **Teams** where “preview this PR” ought to mean a dashboard and ports, not a wiki page nobody updates

Repository: **[github.com/buyan-kh/agentfleet](https://github.com/buyan-kh/agentfleet)**

## Quick start

1. Install AgentFleet (see below—under a minute)
2. In a project repo: `agentfleet init`
3. `agentfleet doctor` — fix whatever it reports
4. `agentfleet setup` — create worktrees for the fleet
5. `agentfleet launch --terminal ghostty-splits --ghostty-size 180x50` — or `tmux` / `iterm` / `print`
6. `agentfleet preview` — after you add `[[preview.services]]`, this is your dashboard + services

Stop there. If `doctor` is green and you can launch, you’ll know if this fits your stack.

## Install — under a minute

**Requirements:** [Node.js](https://nodejs.org/) **18+**, [Python](https://www.python.org/) **3.11+**, [Git](https://git-scm.com/) — plus the **agent CLIs** you configure (defaults assume **Claude Code** and **Codex** on `PATH`). Run commands **inside a git repository**.

### Step 1: Global install (recommended)

```bash
npm install -g @buyan14/agentfleet@latest
agentfleet --help
```

The npm package bundles the Python package; the launcher sets `PYTHONPATH`. You need `python3` on `PATH` (override with `AGENTFLEET_PYTHON` if you use a specific interpreter).

### Step 2: From source (contributors or no npm)

```bash
git clone https://github.com/buyan-kh/agentfleet.git
cd agentfleet
PYTHONPATH=. python -m agent_fleet.cli --help
```

Optional editable install: `pip install -e .`

**Full paths:** upgrade, uninstall, interpreter quirks — **[docs/installation.md](docs/installation.md)**

## See it work

```
You:    cd ~/src/my-app && agentfleet init
        [writes agentfleet.toml]

You:    agentfleet doctor
AgentFleet: Doctor: OK   (or concrete fix hints)

You:    agentfleet setup && agentfleet launch --terminal print
        [prints the exact agent commands per worktree—paste or wire to your UI]

You:    agentfleet preview
        [before [[preview.services]]: short message + boxed checklist for your AI to finish config]
        [after: dashboard on preview.dashboard_port, services on port_base + slot]

You:    agentfleet status
        [fleet + worktrees at a glance]
```

One config file, one workflow: **init → doctor → setup → launch → preview**. Nothing falls through the cracks because `doctor` runs before you pretend the fleet is ready.

## The workflow

| Phase | Command | What it does |
|-------|---------|----------------|
| Configure | `agentfleet init` | Writes `agentfleet.toml` at the repo root |
| Verify | `agentfleet doctor` | CLIs, Python, git, paths |
| Worktrees | `agentfleet setup` | Creates the fleet’s worktrees |
| Terminals | `agentfleet launch` | Ghostty, tmux, iTerm, or print-only |
| Preview | `agentfleet preview` | Dashboard + services from TOML |
| Ops | `agentfleet status` / `stop` / `clean` | Fleet lifecycle |

## Terminals (`launch`)

| `--terminal` | Notes |
|----------------|-------|
| `ghostty-splits` | One window, tiled panes (macOS may need **Accessibility**) |
| `ghostty` | One window per agent |
| `tmux` | Single tmux session |
| `iterm` | iTerm tabs/windows |
| `print` | Print commands only — no terminal launch |

## Preview services

Stack-agnostic: describe anything in **`agentfleet.toml`** (API, web, Docker, helpers).

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

Same checklist appears after **`agentfleet init`** and **`agentfleet preview`** when preview is not configured.

## More commands

```bash
agentfleet status
agentfleet stop
agentfleet clean
agentfleet tasks --out agentfleet-tasks.yaml
agentfleet upgrade          # npm global → latest
```

## Docs

| Doc | What it covers |
|-----|----------------|
| [Installation](docs/installation.md) | npm vs source, upgrade, uninstall, interpreter override |

The rest of AgentFleet usage is documented on **this page** (install → workflow → preview).

## Troubleshooting

**`doctor` fails?** Fix what it prints (missing CLI, wrong Python, not in a git repo).

**Stale global install?** `npm install -g @buyan14/agentfleet@latest` or `agentfleet upgrade`.

**Wrong Python picked up?** Set `AGENTFLEET_PYTHON` to your 3.11+ binary.

**Skills / agents not found?** Ensure `command=` in `agentfleet.toml` matches tools on your `PATH`.

## License

MIT. Ship something.
