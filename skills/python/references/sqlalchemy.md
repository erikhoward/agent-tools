# SQLAlchemy Lifecycle

Use the project's SQLAlchemy and migration versions. Follow its existing sync or async session pattern.

- Create sessions at request or job boundaries. Pass them to data operations. Do not hide a global mutable session.
- Make transaction ownership explicit. A helper must not commit a caller-owned transaction unless its contract says so.
- Roll back failed transactions before reuse. Close sessions and engines through application lifecycle cleanup.
- Choose loading strategies intentionally. Avoid lazy database I/O after the session lifetime and detect query multiplication in integration tests.
- Use parameterized SQL and typed SQLAlchemy expressions. Do not concatenate untrusted input into SQL.
- Model database invariants with constraints, not application checks alone. Name constraints when migration tooling depends on stable names.
- Review indexes against actual query predicates and ordering. Include write and storage cost.
- Migrations require an ordered upgrade, compatibility assumptions, data validation, and recovery path. Do not apply or roll back migrations merely because this reference was loaded.

Test transaction boundaries, constraint failures, loading behavior, and migrations with the repository's database fixtures. Keep production credentials and data out of tests.

Adapted from manikosto/claude-code-python-stack.
