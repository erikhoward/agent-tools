# agent-tools

A curated set of opencode [agents](agents/), [commands](commands/), [skills](skills/), and a global [AGENTS.md](AGENTS.md) — the flow workflow (ideate → plan → implement), git helpers, and language/clean-code skills.

![CI](https://github.com/erikhoward/agent-tools/actions/workflows/validate.yml/badge.svg)

See [CHANGELOG.md](CHANGELOG.md) for release history, or the [GitHub Releases](https://github.com/erikhoward/agent-tools/releases) page.

## Prerequisites

- **opencode** installed and configured
- **bash** 3.2+ (macOS default) or 4.0+ (Linux)
- **git** (for cloning and version control)
- **curl** (for the one-line install) — or use `--source` to clone manually

## What's Included

**13 agents**, **6 commands**, **13 skills** — see [AGENTS.md](AGENTS.md) for the full roster and tier model.

| Type | Count | Purpose |
|---|---|---|
| Agents | 13 | Orchestrators, consultants, analysts, coders |
| Commands | 6 | `/flow-ideate`, `/flow-plan`, `/flow-implement`, `/git-commit`, `/git-push`, `/git-commit-push` |
| Skills | 13 | Clean-code & writing (solid, bare-bones), language conventions (go, python, rust, typescript), workflow guides (flow-*), tooling (github, git-hooks, golangci-lint, git-commit) |

## Install (global)

Makes everything available in every opencode project by symlinking into `~/.config/opencode/`.

```sh
curl -fsSL https://raw.githubusercontent.com/erikhoward/agent-tools/main/install.sh | bash
```
> **Security tip:** The one-liner above fetches from `main`. `v1.0.0` is the current release. For production use, pin to a release tag (e.g., replace `/main/` with `/v1.0.0/`) or use the `--source` alternative below to review the code before running.

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

### Releases

Releases are cut from git tags (`v*`). Each GitHub Release attaches `install.sh`. The changelog is auto-generated from conventional commits. To install a specific release, pin the install URL to that tag.

## Install (project-local)

Makes agent-tools available to one project by symlinking into the project's `.opencode/` instead of the global config. Change to your project, then run the installer from the clone:

```sh
cd <your-project>
bash ~/.local/share/agent-tools/install.sh --local
```

The script symlinks agents, commands, and skills into `<git-root>/.opencode/{agents,commands,skills}`. If the project is not a git repo, it falls back to the current directory's `.opencode/`. Run it from inside the project. From any subdirectory, the script finds the repo root with git.

Then **restart opencode** so the new config loads.

AGENTS.md is **not** installed locally. The project's own `AGENTS.md` takes precedence, and `.opencode/AGENTS.md` is not an opencode rules location. A global install provides the default for projects without their own `AGENTS.md`.

In local mode, `--force` never overwrites real files. It replaces symlinks only and warns on real files.

### Uninstall

```sh
bash ~/.local/share/agent-tools/install.sh --uninstall --local
```

Run it from inside the project. It removes only the symlinks this tool created. Real files and the `.opencode/` directory stay in place. If the source clone is missing, it fails closed with an error. Pass `--source <path>`.

> **Warning:** the `.opencode/` symlinks point to your personal clone, outside the repo. If committed to git, they dangle for other clones. Consider gitignoring `.opencode/`.

### Update

```sh
bash ~/.local/share/agent-tools/install.sh --update --local   # git pull + re-link
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
| `--local` | Install into the current project's `.opencode/` instead of the global config |
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


