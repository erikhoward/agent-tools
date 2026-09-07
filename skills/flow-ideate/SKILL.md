---
name: flow-ideate
description: Shape a new idea or improve an existing artifact through focused collaboration, then save a concept brief for later planning.
license: MIT
compatibility: opencode
---

# Flow Ideate

Turn an unclear idea or an existing artifact into a precise concept. Work with the user. Challenge weak assumptions, preserve settled decisions, and save state in `.opencode/concepts/`.

## Start Or Resume

Use `$1` as the concept name when supplied. Before asking questions, inspect any user-supplied path and `.opencode/concepts/<name>.md`. If `$1` is absent, look for a brief that clearly matches the request. Do not invent a match.

If a brief exists, read its status, decisions, constraints, open risks, open questions, session log, and next step. Resume from unresolved items. Do not reopen a decision unless the user supplies new facts or asks to reconsider it.

Choose one mode:

- Greenfield: define the problem, users, intended outcome, and boundaries.
- Refinement: read the artifact first, recover its intent, and identify evidence of strengths and gaps.

Ask one focused question at a time only when the answer is not in the request, artifact, or brief. Keep uncertainty explicit.

## Shape The Concept

Propose only useful alternatives. There is no required count. Include a simpler direction when scope may be excessive. Compare options against the user's goal and constraints. State disagreements with reasons, not certainty.

Stress the leading direction against its material assumptions, structural weakness, user value, operational cost, and failure modes. Cover only relevant risks. Ask the user to decide tradeoffs that depend on intent. Record deferred issues as risks or open questions instead of treating them as resolved.

Crystallize when the concept has:

- a short, consistent description
- a defined problem or improvement
- clear scope and constraints
- decisions with reasons
- known risks and unresolved questions
- one next action

The user owns product decisions. Do not claim approval from silence or from saving a file.

## Save The Brief

Write `.opencode/concepts/<kebab-name>.md` with this structure:

```markdown
# Concept: <name>

**Status:** draft | refined | ready-to-plan | parked | superseded
**Mode:** greenfield | refinement
**Origin:** <request, artifact, or prior brief>
**Updated:** <date>

## What It Is
## Problem Or Improvement
## Scope
## Key Decisions
## Known Constraints
## Open Risks
## Open Questions
## Session Log
## Next Step
```

Preserve existing creation metadata and useful history. Append one concise session-log entry. Do not delete parked or superseded briefs. Name the replacement when a brief is superseded.

Set `ready-to-plan` only when no unresolved question blocks planning and the user confirms the concept. A saved brief is an artifact, not user approval. Report its exact path. If it is ready, offer `/flow-plan <name>`.

## Checkpoint And Resume

Before a pause, record the status, settled decisions, current direction, unresolved questions, evidence or paths examined, and the next action. On resume, reconcile these fields with the current files and user request. If they conflict, describe the conflict and ask about intent.

## Boundaries

- Do not implement code or produce an implementation plan.
- Do not force phase announcements, option counts, agent panels, or false consensus.
- Do not replace facts with polished generalities. Preserve conditions, exceptions, numbers, and attribution.
- Read existing artifacts before evaluating them.
- End with the saved path, current status, unresolved items, and next step.
