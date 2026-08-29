# CONTRIBUTING

PRs are welcome. This repo ships opencode configuration (agents, commands, skills) — no runtime code.

## Frontmatter Schema Requirements

**Agents** (`agents/*.md`):
- Required: `description` (non-empty string), `mode` (`primary`, `subagent`, or `all`)
- Optional: `model` (`org/model-name`), `permission` (nested map with `allow`/`ask`/`deny` values)

**Commands** (`commands/*.md`):
- Required: `description` (non-empty), `agent` (must reference `agents/<name>.md`)
- Optional: `model`

**Skills** (`skills/*/SKILL.md`):
- Required: `name` (must match parent directory name), `description` (non-empty)
- Optional: `license`, `compatibility`, `metadata`

## Filename Constraints

- `build.md` and `plan.md` filenames are load-bearing — opencode commands reference them by name. Do not rename.
- Skill directory names must match the `name` field in SKILL.md frontmatter.
- Agent filenames are referenced by commands via the `agent:` field.

## Tier Model for New Agents

- **Orchestrators** (build, plan): Explicit `model:` field — workflow owners with fixed reasoning level.
- **Tier 2 consultants**: Explicit `model:` field — one reasoning step above orchestrator for deeper analysis.
- **Tier 1 analysts**: Inherit `model:` from session / invoker — context-adaptive model inheritance.
- See AGENTS.md Model Strategy for details.

## Validation

Run `python3 scripts/validate.py` before submitting. It checks frontmatter schema, cross-references, roster consistency, and internal links. Fix all errors (E) before opening a PR.

Run `bats test/` to verify install.sh behavior (requires `brew install bats-core` or apt equivalent).

## Pre-commit Hooks

To set up local pre-commit hooks: `git config core.hooksPath .githooks`

This runs validate.py and shellcheck on staged files.

## CI

CI runs automatically on PRs. The `validate` job (validate.py + shellcheck + bats) must pass. The `links` job (external URL check) is non-blocking.

## Commit Style

Use conventional commits (e.g., `fix: correct model ID in plan.md`, `feat: add python skill`, `docs: update README`).