# agent-tools

A curated set of opencode [agents](agents/), [commands](commands/), [skills](skills/), and a global [AGENTS.md](AGENTS.md) — the flow workflow (ideate → plan → implement), git helpers, and language/clean-code skills.

![CI](https://github.com/erikhoward/agent-tools/actions/workflows/validate.yml/badge.svg)

## Prerequisites

- **opencode** installed and configured
- **bash** 3.2+ (macOS default) or 4.0+ (Linux)
- **git** (for cloning and version control)
- **curl** (for the one-line install) — or use `--source` to clone manually

## What's Included

**13 agents**, **6 commands**, **12 skills** — see [AGENTS.md](AGENTS.md) for the full roster and tier model.

| Type | Count | Purpose |
|---|---|---|
| Agents | 13 | Orchestrators, consultants, analysts, coders |
| Commands | 6 | `/flow-ideate`, `/flow-plan`, `/flow-implement`, `/git-commit`, `/git-push`, `/git-commit-push` |
| Skills | 12 | Language conventions (go, python, rust, typescript), workflow guides (solid, flow-*), tooling (github, git-hooks, golangci-lint, git-commit) |

## Install (global)

Makes everything available in every opencode project by symlinking into `~/.config/opencode/`.

```sh
curl -fsSL https://raw.githubusercontent.com/erikhoward/agent-tools/main/install.sh | bash
```
> **Security tip:** The one-liner above fetches from `main`. For production use, pin to a specific release tag (e.g., replace `/main/` with `/v1.0.0/`) or use the `--source` alternative below to review the code before running.

Or, from a clone:

```sh
git clone https://github.com/erikhoward/agent-tools.git && cd agent-tools
./install.sh
```

Then **restart opencode** so the new config loads.

### Security-Conscious Install

If you prefer not to pipe curl output directly to bash, clone and verify first:

```bash
git clone https://github.com/erikhoward/agent-tools.git ~/.local/share/agent-tools
# Review the install script before running it
less ~/.local/share/agent-tools/install.sh
bash ~/.local/share/agent-tools/install.sh --source ~/.local/share/agent-tools
```

## Local Development

```bash
# Set up pre-commit hooks
git config core.hooksPath .githooks

# Run the validator
python3 scripts/validate.py

# Run install.sh tests (requires bats-core)
bats test/
```

### What it does

- Clones the repo to `~/.local/share/agent-tools` (if not already local) and symlinks:
  - `agents/*.md`        → `~/.config/opencode/agents/`
  - `commands/*.md`      → `~/.config/opencode/commands/`
  - `skills/<name>/`     → `~/.config/opencode/skills/<name>/`  (whole dirs, so `references/` come along)
  - `AGENTS.md`          → `~/.config/opencode/AGENTS.md`  (global rules — see note below)
- `build` and `plan` **override opencode's built-in primary agents** by design, so `/flow-implement` and `/flow-plan` run these orchestrators.

### Update

```sh
./install.sh --update        # git pull + re-link (picks up new files)
# or just:
cd ~/.local/share/agent-tools && git pull   # symlinks follow automatically
```

### Uninstall

```sh
./install.sh --uninstall     # removes only this tool's symlinks; leaves your clone in place
```

### Options

| Flag | Effect |
|---|---|
| `--source <path>` | Use an existing checkout instead of cloning |
| `--clone-dir <path>` | Where to clone (default `~/.local/share/agent-tools`) |
| `--force` | Overwrite existing files/symlinks in the target |
| `--update` | `git pull` the clone, then re-link |
| `--uninstall` | Remove the symlinks created by this tool |
| `--dry-run` | Show what would happen without changing anything |

## Windows

Use [WSL](https://opencode.ai/docs/windows-wsl) — opencode's own recommended path. Inside WSL, `~/.config/opencode/` is the same POSIX location and the install script above works unchanged. The script intentionally does not ship a PowerShell variant; native (non-WSL) Windows isn't a supported opencode target.

## Why a symlink script, not a marketplace

Community marketplaces (e.g. `opencode-marketplace`) namespace files on install (`build.md` → `agent-tools--build.md`). That defeats the core purpose here: `build.md` and `plan.md` must keep their exact names to **override opencode's built-in agents**. Symlinking preserves filenames and lets you update with a plain `git pull`.

## Notes

- **Global AGENTS.md precedence**: a project's own `AGENTS.md` takes precedence over the global one. So this install provides a global *default* for projects without their own `AGENTS.md`; it does not override project-level rules. If you want these guidelines always applied, add the global file to `instructions` in your `~/.config/opencode/opencode.json`.
- opencode loads config at startup. After any change to agents/commands/skills/AGENTS.md, **restart opencode** for it to take effect.
```


