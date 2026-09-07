---
name: golangci-lint
description: Configure or diagnose golangci-lint with repository-pinned versions, incremental adoption, formatter separation, narrow suppressions, and reproducible local and CI verification.
license: MIT
compatibility: opencode
---

# golangci-lint

Use this skill only for golangci-lint setup, migration, or failures. Use the repository's pinned version and `.golangci.yml` or `.golangci.yaml`. Check the installed version before changing schema. Do not install `latest` or replace an established configuration without approval.

## Rules

- Start from the repository's current policy. Add linters to address a stated risk, not to maximize count.
- For version 2 configuration, keep formatters in the formatter section. Distinguish lint, formatting, and automatic fixes.
- Treat migration commands as in-place writes. Review and version the result before use.
- Adopt stricter checks incrementally. Do not mix a requested configuration change with unrelated cleanup across the codebase.
- Investigate the loaded config and effective exclusions when local and CI output differ.
- Use `//nolint:<linter> // reason` only for a specific, justified exception. Avoid blanket test-directory exclusions and stale suppressions.
- Keep security and error checks enabled unless a documented project policy provides equivalent coverage.
- Match CI's Go version, module mode, working directory, and generated-code policy.

Read `references/advanced-configuration.md` only for version-specific schema, exclusions, CI, or incremental rollout details.

## Verification

Run the repository's command first. A common diagnostic sequence is:

```text
golangci-lint version
golangci-lint config verify
golangci-lint run --verbose
```

Use commands supported by the pinned version. Limit fixes and formatting to intended files. Report unavailable tools rather than installing them.

Adapted from golangci-lint documentation and project examples (MIT).
