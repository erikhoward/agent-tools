---
name: github
description: |
  Token-efficient and hang-safe gh CLI usage in agentic contexts. Load when
  running gh commands. This skill covers output discipline and agent traps
  only — command syntax is standard gh; use `gh --help` for it.
license: MIT
compatibility: opencode
metadata:
  audience: developers
  tool: gh
  tested-version: "2.97.0"
---

# GitHub CLI (gh) Skill

The base model already knows gh command syntax. This skill adds what it does
not reliably know: keeping gh output small and preventing agent hangs.

## Agentic Output Principles

When using gh in an agentic context, **token efficiency is critical**. Always apply these rules:

### Core Rules

1. **Never use raw JSON without `--jq`.** `--json` alone produces verbose nested objects with IDs, bot flags, and unused fields. Always chain: `--json <minimal-fields> --jq '<filter>'`.

2. **Request only the fields you need.** Check the Minimal Fields table below. Adding extra fields multiplies output size with no benefit.

3. **Bound large outputs.** Commands like `gh run view --log`, `gh pr diff`, `gh api --paginate` can emit megabytes. Always pipe through `| head -n 100`, `grep <pattern>`, or use `--jq 'first(.[])'`.

4. **Prefer text output for existence/status checks.** `gh pr list` (no flags) outputs compact tab-separated text (~80 chars/line). The same with `--json` (~300+ chars/line). Use text unless you need to branch on a specific field.

5. **Set agentic environment baseline** before running gh commands:
   ```bash
   export NO_COLOR=1               # no ANSI escape codes
   export GH_NO_UPDATE_NOTIFIER=1  # suppress update banners
   export GH_PAGER=cat             # disable interactive paging
   ```
   This eliminates color codes, update notifications, and paging prompts — all add noise tokens.

### Minimal Fields by Task

| Task | Command | Notes |
|---|---|---|
| Does PR exist? | `gh pr list --head <branch> --json number --jq 'length'` | Returns 0 or 1, tiny output |
| PR list summary | `gh pr list --json number,title,state` | Omit author, labels, timestamps unless needed |
| PR merge status | `gh pr view 42 --json mergeable,reviewDecision` | Only fields needed for merge decision |
| PR author | `gh pr list --json author --jq '.[].author.login'` | Extract just login, not id/is_bot/name |
| PR labels | `gh pr list --json labels --jq '.[].labels[].name'` | Project to label names only |
| Issue exists + state | `gh issue list --json number,state` | Two fields, minimal output |
| Issue assignees | `gh issue list --json assignees --jq '.[].assignees[].login'` | Project to logins only |
| Release latest | `gh release list --json tagName,isLatest --jq 'first'` | Single object, not array |
| CI run status | `gh run list --limit 1 --json status,conclusion` | Two fields, limit results |
| Workflow enabled? | `gh workflow list --json name,state` | Minimal info for decision |

## Tips & Gotchas

- **Branch vs. repo context:** Many commands infer repo from `.git/config`. Use `-R owner/repo` to override.
- **Pagination:** Use `--paginate` with `--json` and `--slurp` to fetch all results as a single array.
- **Merge method — always be explicit:** Bare `gh pr merge 42` prompts interactively and will hang an agent. Always pass `--merge`, `--squash`, or `--rebase` (plus `--delete-branch` to clean up). Use `--auto` to enable auto-merge when checks pass.
- **Draft PRs:** Use `--draft` on create; `gh pr ready <number>` un-drafts, `gh pr ready <number> --undo` converts back to draft.
- **Release notes:** `gh release create v1.2.3 --generate-notes` builds notes from merged PRs/commits; add `--latest` to mark latest.
- **Waiting on CI:** Use `gh run watch <run-id> --exit-status` or `gh pr checks <number> --watch` instead of polling loops. Non-zero exit on failure — see `gh help exit-codes` for scripting.
- **Linking issues:** Include `Fixes #N` or `Closes #N` in PR body to auto-close issue on merge.
- **Private tokens:** Always use `GH_TOKEN` (preferred) or store in `gh auth login`. Never commit tokens to git.
- **Enterprise GitHub:** Set `GH_HOST=github.company.com` for GitHub Enterprise.
- **`gh api` and JSON arrays:** Never use `-F field='["a","b"]'` for array payloads — `-F` sends the value as a string literal, not parsed JSON. GitHub API returns HTTP 422 "not an array". Use `--input /tmp/payload.json` instead.

## Learn More

- Official docs: https://cli.github.com/manual
- `gh help exit-codes` and `gh <command> --help` for scripting semantics
