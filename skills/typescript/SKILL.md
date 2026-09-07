---
name: typescript
description: Apply repository-aware TypeScript conventions for checked boundaries, useful types, async behavior, imports, suppressions, React code, tests, and verification.
license: MIT
compatibility: opencode
metadata:
  source: https://github.com/anthropics/skills
---

# TypeScript

Follow the repository's TypeScript version, module system, strictness, runtime validator, package manager, formatter, linter, and test framework. Do not change those choices unless requested.

## Contracts

- Treat external input, parsed JSON, caught errors, storage, and network responses as `unknown` until checked. A generic type argument or assertion is not runtime validation.
- Avoid `any`, non-null assertions, and casts that claim facts not established by control flow or validation. When an assertion is necessary, keep it local and state the invariant.
- Annotate public APIs and boundaries. Let clear local values infer. Use generics only when type parameters express a useful relationship.
- Represent mutually exclusive states with discriminated unions when that prevents invalid combinations. Do not add type machinery that exceeds the domain need.
- Use `import type` where it prevents runtime imports and matches repository style.
- Await, return, or intentionally observe every promise. Define error ownership at async boundaries. Preserve abort and cleanup behavior.
- Follow the existing React patterns and compiler guidance. Do not add memoization by default.
- Use targeted suppressions with the rule and reason. Never use a suppression to avoid understanding an error.

Read `references/error-handling.md` only for boundary-validation or Result-versus-exception decisions.

## Verification

Use repository scripts first. Run focused tests, the configured type check, lint, and format check that apply to changed files. Do not assume npm, ESLint, Prettier, Vitest, or Jest. Do not install tools or rewrite configuration to satisfy this skill. Report checks not run.

Adapted from Anthropic skills (MIT).
