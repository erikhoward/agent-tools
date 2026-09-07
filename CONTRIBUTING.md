# CONTRIBUTING

PRs are welcome. This repo ships opencode configuration (agents, commands, skills) — no runtime code.

## Frontmatter Schema Requirements

**Agents** (`agents/*.md`):
- Required: `description` (non-empty string), `mode` (`primary`, `subagent`, or `all`)
- Optional: `model` (`org/model-name`), `permission` (nested map with `allow`/`ask`/`deny` values)

**Commands** (`commands/*.md`):
- Required: `description` (non-empty), `agent` (must reference `agents/<name>.md` or a built-in opencode agent: `build`, `plan`, `general`, `explore`, `scout`)
- Optional: `model`

**Skills** (`skills/*/SKILL.md`):
- Required: `name` (must match parent directory name), `description` (non-empty)
- Optional: `license`, `compatibility`, `metadata`

## Filename Constraints

- Skill directory names must match the `name` field in SKILL.md frontmatter.
- Agent filenames are referenced by commands via the `agent:` field.

## Agent Boundaries

- Built-in `build` and `plan` agents orchestrate the flow skills.
- Built-in `general` implements scoped code, test, and infrastructure tasks.
- Custom consultants are read-only. Their frontmatter denies editing, shell commands, delegation, and LSP mutations.
- Add a model override only when an evaluation or operational constraint justifies it.
- When an asset is retired, update active references, rosters, installer cleanup, tests, and migration documentation in the same change.

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

## Cutting a Release

The changelog is prepared locally before tagging. The Release workflow only generates the release notes and creates the GitHub Release with `install.sh` attached — it cannot push to `main` (branch protection blocks the workflow bot).

Requires [git-cliff](https://git-cliff.org) (`brew install git-cliff`).

Prepare the changelog BEFORE creating the tag. Once a tag exists on the commits, they are no longer "unreleased" and `--unreleased` returns nothing.

```sh
VERSION="1.2.0"  # example

# 1. Prepend the new version's section
git cliff --unreleased --tag "v${VERSION}" --prepend CHANGELOG.md

# 2. Append the reference link (--prepend omits the footer)
PREV_TAG="$(git describe --tags --abbrev=0 HEAD)"
LINK="[${VERSION}]: https://github.com/erikhoward/agent-tools/compare/${PREV_TAG}..v${VERSION}"
grep -qF "${LINK}" CHANGELOG.md || printf '%s\n' "${LINK}" >> CHANGELOG.md

# 3. Commit and push (chore: keeps this commit out of the generated changelog)
git add CHANGELOG.md
git commit -m "chore(changelog): update for v${VERSION}"
git push origin main

# 4. Tag and push — this triggers the Release workflow
git tag -a "v${VERSION}" -m "v${VERSION}"
git push origin "v${VERSION}"
```

If no previous tag exists, use a commits link instead: `https://github.com/erikhoward/agent-tools/commits/v${VERSION}`.
