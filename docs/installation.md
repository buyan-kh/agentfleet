# Installation

Minimal paths to a working **`agentfleet`** on your machine.

---

## Recommended: npm global

```bash
npm install -g @buyan14/agentfleet@latest
```

Verify:

```bash
which agentfleet
agentfleet --help
python3 --version   # ≥ 3.11
```

---

## What gets installed

- **JS shim** on `PATH` (`bin/agentfleet.js`): invokes Python with `PYTHONPATH` set to the package root so **`agent_fleet`** loads from that install—not from arbitrary site-packages.

You still need a **working `python3`** (or `python`) on PATH. Override if needed:

```bash
export AGENTFLEET_PYTHON=/opt/homebrew/bin/python3.11
```

---

## From source (contributors)

```bash
git clone https://github.com/buyan-kh/agentfleet.git && cd agentfleet
PYTHONPATH=. python -m agent_fleet.cli --help
```

Optional editable install:

```bash
pip install -e .
agentfleet --help
```

---

## Upgrade

```bash
npm install -g @buyan14/agentfleet@latest
# or
agentfleet upgrade
```

---

## Uninstall

```bash
npm uninstall -g @buyan14/agentfleet
```

---

## When `doctor` fails

Run **`agentfleet doctor`** inside your **project repo** after install. Typical fixes: install missing CLIs (`claude`, `codex`), fix Python version, grant terminal app permissions (Ghostty splits on macOS).

See **[README](../README.md)** for full usage.
