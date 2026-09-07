# golangci-lint Configuration Notes

Confirm the pinned golangci-lint major version before using these fields. Validate the resulting configuration with that version.

- Version 2 separates `formatters` from `linters`.
- Prefer explicit enabled linters and repository-owned exclusions over copying a large preset.
- Anchor path exclusions to the repository layout. Check generated-file handling and module download mode.
- Keep `errcheck`, `govet`, `staticcheck`, and applicable security checks unless equivalent policy exists.
- For incremental adoption, limit findings to changed code or a reviewed baseline. Remove the baseline when the repository is clean.
- Require linter names and reasons on `nolint` directives. Enable stale-exclusion or unused-suppression checks when the pinned version supports them.
- Match local and CI Go versions, build tags, generated sources, working directory, and timeout.
- In containers, avoid root-owned caches or generated files in the checkout.

Migration commands can rewrite the file. Run them only with authorization, inspect the diff, and keep rollback through version control.
