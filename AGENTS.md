# Agent Guidelines

These guidelines address common LLM coding mistakes described in
[Andrej Karpathy's observations](https://x.com/karpathy/status/2015883857489522876).

## Core Contract

- Confirm the goal, scope, constraints, and acceptance criteria before changes.
- State material assumptions. Ask the user when intent or authorization is unclear.
- Make the smallest correct change. Do not add speculative features, abstractions, compatibility, or error handling.
- Preserve user and concurrent-agent changes. Touch only assigned files. Stop on a direct ownership conflict.
- For behavior changes, use a failing behavior test first, then minimal implementation and refactoring. A reviewed plan can set another test order, but verification is never optional.
- Test observable behavior, not implementation details. Run focused checks, then relevant integration checks. Report checks that were not run.
- Keep writing terse and factual. Preserve every condition, exception, threshold, version, warning, and source attribution.

Fresh workers do not inherit loaded skills or these guidelines. Every dispatch must include the worker role, allowed files, requirements, acceptance criteria, minimal-change rule, test order, required verification, and stop conditions. Give each file one writer. Use bounded parallel batches only for non-overlapping work.

## Repo Assets

Load an asset only when its focused guidance helps the task.

### Skills

| Skill | Scope |
|---|---|
| `bare-bones` | Clear technical and general writing |
| `git-commit`, `git-hooks`, `github` | Git and GitHub work |
| `go`, `python`, `rust`, `typescript`, `golangci-lint` | Language and lint guidance |
| `flow-ideate`, `flow-plan`, `flow-implement` | Concept, plan, and implementation workflows |

### Agents

| Agent | Scope |
|---|---|
| `principal-architect` | System and component architecture |
| `database-architect`, `security-expert` | Data and security consultation |
| `code-analyst`, `performance-engineer`, `ui-ux-designer` | Read-only analysis |
| `@general`, `@explore` | Built-in implementation, testing, infrastructure, and exploration workers |

Core design and testing guidance is adapted from [ramziddin/solid-skills](https://github.com/ramziddin/solid-skills) (MIT).

### Commands

| Command | Action |
|---|---|
| `/flow-ideate`, `/flow-plan`, `/flow-implement` | Run a flow workflow |
| `/git-commit`, `/git-push`, `/git-commit-push` | Commit or push with explicit authorization |
