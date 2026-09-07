---
name: flow-implement
description: Execute an approved plan with bounded built-in general workers, explicit ownership, checkpoints, and behavior verification.
license: MIT
compatibility: opencode
---

# Flow Implement

Execute an explicitly approved plan from `.opencode/plans/`. The build agent orchestrates. Built-in `general` workers implement. Consultants remain read-only.

## Preflight

Use `$1` to inspect `.opencode/plans/$1.md` before asking questions. If `$1` is a path, read that path. If absent, locate a clear matching plan from the request. Do not guess between plans.

Read the full plan and its checkpoint. A saved plan is not approved. Stop if approval is absent, blockers remain, acceptance criteria are unclear, or required ownership overlaps. Ask the user about intent or authorization. Do not ask questions already answered by the plan or current repository evidence.

For an old plan, show this mapping and get confirmation before execution:

- `solution-architect` consultation maps to `principal-architect`.
- `devops-engineer` planning maps to a retained read-only analyst with an infrastructure assignment.
- `test-engineer` planning maps to a retained read-only analyst with a testing assignment.
- `devops-engineer` implementation maps to built-in `general` with infrastructure-only ownership.
- `test-engineer` implementation maps to built-in `general` with test-only ownership and no production-code changes.

Unknown names, including `developer-prime` and `developer-fast`, or tasks that edit retired files require plan revision. Do not rewrite the plan or create aliases automatically. Preserve task IDs, acceptance criteria, and completion state.

## Prepare Batches

Reconcile plan tasks with current files and prior evidence. Reuse valid exploration. Create bounded batches of independent tasks. Tasks in one batch must have non-overlapping allowed files. Give every file one writer.

The host permits one Todo item in `in_progress`. Represent the active orchestration batch as that item. Record child task IDs, worker task IDs, ownership, and evidence inside it. Complete or checkpoint the batch before another batch starts.

Use the built-in `general` worker for implementation. Every fresh-worker prompt must contain:

```text
Role: <implementation role>
Task: <plan task IDs and exact outcome>
Allowed files: <exclusive paths; no other writes>
Requirements: <behavior, interfaces, constraints, acceptance criteria>
Method: make the smallest correct change; avoid unrelated refactors and speculative abstractions.
Tests: write a failing behavior test first unless the approved plan sets another order.
Verification: <focused tests and relevant static checks; return command results and behavior evidence>
Stop: stop on unclear intent, ownership conflict, out-of-scope need, risky unplanned decision, or failed required check.
```

Children do not inherit loaded skills or repository instructions. Put all critical constraints in the prompt. Add focused technology guidance only when needed. Do not require generic skill loads.

## Execute And Verify

Dispatch one bounded batch at a time. Parallelize only non-overlapping tasks. Each worker returns changed files, test evidence, failures, deviations, and unresolved concerns.

Check worker evidence before integration. Run focused missing checks, then relevant integration checks. Do not repeat an identical check without a reason. Verify observable behavior, acceptance criteria, minimal scope, and the final diff. Do not mark a task complete from a worker claim alone.

If one branch fails, record the failure and continue independent work that is safe. Bound local diagnosis. Consult a relevant specialist for material security, data, performance, or architecture risk, or for an unresolved technical problem. Principal architecture handles all architecture questions. Consultants advise and review without edits, shell commands, or delegation.

Never report final success while a required check, blocker, or worker failure remains unresolved. Do not hide unavailable checks.

## Checkpoint And Resume

After each batch, persist task IDs, worker task IDs, ownership, changed files, evidence, completion state, blockers, and next action in the plan checkpoint. On resume, inspect current files and reconcile prior results before dispatch. Do not rerun completed work blindly.

## Finish

Run the plan's integration checks and inspect version-control status and diff. Confirm that only intended files changed. Preserve concurrent changes. Do not commit, push, install, deploy, or change configuration without explicit authorization.

Report completed and blocked task IDs, changed files, behavior and check results, deviations, unresolved concerns, and the next action. Success requires all acceptance criteria and required checks to pass.
