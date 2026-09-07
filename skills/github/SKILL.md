---
name: github
description: Use gh with explicit repository context, bounded machine-readable output, complete review evidence, safe waits, and no implicit mutations.
license: MIT
compatibility: opencode
---

# GitHub CLI

The model already knows `gh` syntax. This skill covers agent execution risks.

## Rules

- Set explicit repository context with `--repo owner/name` when the current checkout is not authoritative.
- Request only needed fields with `--json`. Use `--jq` when projection simplifies nested output, not as ceremony.
- Bound listings and status output. Do not truncate diffs, failure logs, or other evidence required for a complete review. Inspect large evidence in sections.
- Use noninteractive flags. Set `GH_PAGER=cat` and disable update notices for automation where appropriate.
- Give waits a time budget. Treat pending, failed, cancelled, and timed-out checks as distinct outcomes.
- Prefer structured request bodies and unique temporary files in the environment's approved temporary directory.
- Never print tokens, authorization headers, signed URLs, or secret values.
- Do not enable auto-merge, delete branches, close issues, publish releases, merge, or push unless the user authorizes that specific mutation.
- Select merge method explicitly when merging is authorized. Never rely on an interactive prompt.
- Inspect all commits and the full base-branch diff before creating or reviewing a pull request.

Keep command output proportional to the question. A short listing can be limited. Evidence used to approve a change must remain complete.
