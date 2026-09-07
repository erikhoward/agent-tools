---
name: rust
description: Apply repository-aware Rust conventions for ownership, error and panic boundaries, unsafe code, async tasks, public APIs, tests, and verification.
license: MIT
compatibility: opencode
metadata:
  source: https://github.com/tiangolo/agents
---

# Rust

Follow the workspace's Rust version, feature policy, public API conventions, lint configuration, and CI commands. Preserve compatibility unless the task authorizes a break.

## Contracts

- Express ownership and borrowing directly. Clone only when ownership transfer or measured simplicity justifies it.
- Return recoverable failures. Reserve panic for violated invariants and unrecoverable process contracts. Avoid production `unwrap` and `expect` unless a nearby explanation proves the invariant.
- Preserve error sources and useful context without leaking secrets. Redact secret-bearing `Debug` output.
- Keep `unsafe` blocks minimal. State the safety invariant at the boundary and test the safe API around it. Do not weaken soundness to satisfy a signature.
- Give spawned tasks an owner and shutdown path. Dropping a task handle does not necessarily cancel the task. Bound channels and concurrency.
- Do not hold blocking lock guards across `.await`. Keep async-aware guards short and justify any guard retained across an await point.
- Treat cancellation safety as API behavior when futures can be dropped mid-operation.
- Keep public paths, feature flags, serialized formats, and error behavior deliberate. Avoid speculative generics and abstractions.
- Use narrow lint allowances with a reason. Do not hide warnings globally.

Read references only for the affected surface: `api-design.md`, `async-and-performance.md`, or `agent-discipline.md`.

## Verification

Use repository commands first. Common fallbacks are:

```text
cargo fmt --check
cargo clippy --all-targets --all-features -- -D warnings
cargo test --all-features
```

Run Miri or sanitizer checks when changed unsafe code requires them and the environment supports them. Report unavailable checks instead of installing tools or claiming success.

Adapted from tiangolo/agents (MIT).
