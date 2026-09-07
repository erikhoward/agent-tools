---
name: git-commit
description: Write Conventional Commits messages that match the repository's local types, scopes, subject limit, body, and breaking-change conventions.
license: MIT
compatibility: opencode
---

# Conventional Commit Messages

This skill formats messages. It does not authorize staging, committing, amending, or pushing.

Use the repository's existing convention when it is stricter. Otherwise use:

```text
<type>[(scope)][!]: <description>

[body]

[trailers]
```

Allowed types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, and `revert`.

## Rules

- Describe the primary user or repository effect, not the files changed.
- Use a lowercase imperative description without a final period.
- Keep the complete subject, including type and scope, at 72 characters or fewer unless repository policy differs.
- Use a short, established scope only when it adds useful context.
- Keep one logical change per commit. Necessary tests and documentation can share the production change's type.
- Put rationale and behavioral detail in the body. Wrap it for readability when needed.
- Put each trailer on its own line after a blank line.
- Mark a breaking change with `!`, a `BREAKING CHANGE:` trailer, or both. When a trailer is present, state the migration impact.
- Preserve issue, co-author, sign-off, and revert trailers exactly as required by the repository.

Inspect recent repository messages before choosing a scope or ambiguous type. Do not split a coherent change only because several type labels could apply.

Read `references/advanced-patterns.md` only for unusual trailers, reverts, or monorepo scope policy.

Examples:

```text
fix(installer): preserve foreign links during updates
refactor!: remove retired agent aliases
```

Conforms to Conventional Commits 1.0.0. Adapted under MIT terms.
