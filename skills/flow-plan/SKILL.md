---
name: flow-plan
description: Create a reviewable implementation plan from a concept, path, or request, with consultation only for relevant risks.
license: MIT
compatibility: opencode
---

# Flow Plan

Create a plan in `.opencode/plans/`. Planning can inspect the repository and write the plan, but it must not implement the work.

## Locate Context First

Use `$1` as the feature name when supplied. Before asking questions, inspect user-supplied paths, `.opencode/concepts/$1.md`, and `.opencode/plans/$1.md`. If `$1` is absent, look for a clear matching brief or plan. Do not guess between matches.

Reuse the supplied name. Read relevant repository files and current version-control state with available tools. Reuse prior exploration and evidence when still current. Treat brief decisions as requirements unless the user reopens them. Ask only about unresolved intent, missing acceptance criteria, or material conflicts.

An existing plan is saved state. It is not approved. Preserve its approval status and never infer approval from its existence.

## Define The Work

Record the goal, scope, exclusions, decisions and reasons, acceptance criteria, blockers, and open questions. Split implementation into task IDs with dependencies, sole-writer file ownership, required behavior tests, and verification commands. Default to a failing behavior test before implementation. State a different sequence only when the work or reviewed plan requires it.

Address these topics when relevant: architecture, interfaces, data and migration, security, performance, infrastructure, observability, tests, compatibility, rollout, and rollback. Omit empty boilerplate sections. Principal architecture covers system strategy, service boundaries, and cross-component design.

## Consult By Risk

Consult only when repository evidence is insufficient or a material domain risk exists. Use `principal-architect` for all architecture, `database-architect` for data risk, `security-expert` for security risk, `performance-engineer` for measured performance risk, `ui-ux-designer` for interaction risk, and `code-analyst` for unfamiliar code surfaces.

Consultants and planning analysts are read-only. They think, advise, and review. Their prompt must deny edits, shell commands, and delegation. For infrastructure or testing analysis, assign that domain to a retained read-only analyst. Do not dispatch a mandatory panel. Run consultations in a bounded parallel batch only when their domains do not overlap. Reconcile conflicts in the plan.

Every fresh-agent prompt must include the role, exact question, allowed files, requirements, evidence, minimal-scope rule, expected output, verification needs, and stop conditions. Fresh agents do not inherit skills or repository instructions.

## Legacy Preflight

Before resuming an old plan, show mappings and get confirmation before execution:

- `solution-architect` consultation maps to `principal-architect`.
- `devops-engineer` planning maps to a retained read-only analyst with an infrastructure assignment.
- `test-engineer` planning maps to a retained read-only analyst with a testing assignment.
- `devops-engineer` implementation maps to built-in `general` with infrastructure-only files.
- `test-engineer` implementation maps to built-in `general` with test-only files and no production-code changes.

Unknown names, including `developer-prime` and `developer-fast`, require plan revision. A task that edits a retired file also requires revision. Do not rewrite old plans or create aliases automatically. Preserve task IDs, acceptance criteria, and completion state.

## Plan Format

Write `.opencode/plans/<kebab-name>.md`. Include:

- status and explicit approval state
- goal, scope, and exclusions
- repository context and relevant decisions
- architecture and domain sections only when relevant
- ordered tasks with IDs, dependencies, allowed files, tests, and verification
- acceptance criteria and integration checks
- migration, rollout, and rollback when relevant
- blockers, open questions, checkpoint evidence, and next action

Mark unresolved intent or authorization as a blocker. A plan can be ready for review only when implementation can proceed without guessing. Saving does not approve it. Ask the user to review it. Record approval only after an explicit user statement.

## Checkpoint And Completion

Before a pause, save consulted task IDs, evidence, decisions, blockers, and the next action. On resume, reconcile the checkpoint with current files and agent results.

Report the exact plan path, approval state, blockers, and checks used to validate the plan. Offer `/flow-implement <name>` only after explicit approval. Never implement from this workflow.
