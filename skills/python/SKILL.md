---
name: python
description: Apply repository-aware Python conventions for typing, exceptions, resources, async work, tests, packaging, and verification. Use for Python code and pyproject.toml changes.
license: MIT
compatibility: opencode
metadata:
  sources:
    - https://github.com/affaan-m/ECC
    - https://github.com/manikosto/claude-code-python-stack
---

# Python

Follow the repository's supported Python versions, dependency manager, formatter, type checker, test framework, and established design. Do not introduce a framework, exception hierarchy, repository abstraction, or dependency unless the task requires it.

## Contracts

- Use clear `snake_case` names, `CapWords` types, and predicate names for booleans.
- Annotate public APIs and non-obvious boundaries. Prefer inferred local types. Use syntax supported by the project's minimum Python version.
- Catch specific exceptions. Preserve causes with `raise ... from error` when translating failures. Never swallow exceptions. Do not expose secrets or large payloads in error text.
- Use context managers or explicit `try/finally` cleanup for files, locks, sessions, clients, and transactions.
- Prefer the standard library and existing dependencies. Follow existing protocols and data models rather than importing patterns from another language.
- Keep async operations non-blocking. Reuse long-lived HTTP clients where ownership permits it. Bound concurrency, set intentional timeouts, and retry only operations safe to repeat.
- Keep transaction and session ownership explicit. Avoid hidden commits and lazy I/O outside the intended lifetime.
- Use narrow suppressions only when the issue cannot be expressed safely. Include the rule and reason.

Read `references/async-and-concurrency.md` only for async lifecycle or retry work. Read `references/sqlalchemy.md` only for SQLAlchemy session, loading, or transaction decisions.

## Verification

Use repository scripts and configuration first. Typical checks are a focused pytest invocation, then configured Ruff formatting/linting and the configured type checker. Do not require Ruff, isort, Black, mypy, and pytest simultaneously when the project does not use them. Format changed files only. Report checks that are unavailable or not run.

Adapted from affaan-m/ECC and manikosto/claude-code-python-stack.
