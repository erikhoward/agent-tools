---
name: flow-ideate
description: Use when the user wants to shape a fuzzy idea into a concept (greenfield) or evaluate and improve an existing feature, system, document, or prior concept (refinement) — collaborative ideation via the Ground/Expand → Stress → Crystallize framework, producing a persistent CONCEPT_BRIEF in .opencode/concepts/ that survives across sessions. Triggers include "ideate", "let's think through this together", "help me shape this idea", "evaluate/improve this", "pick up the <name> concept".
---

# Flow — Ideate

A structured framework for LLM-user collaborative idea shaping with a
persistent artifact. The goal is genuine co-creation: both parties contribute,
challenge each other, and converge on the strongest possible idea — then write
it down so it survives the session.

Two doors in:

- **Greenfield** — fuzzy idea → attackable concept
- **Refinement** — existing thing (feature, code, document, process, or prior
  concept) → evaluated, improved direction

One artifact out: a **CONCEPT_BRIEF** saved to `.opencode/concepts/`.

---

## Core Principle

Neither the LLM nor the user has the full picture alone. The user holds domain
context, intuition, and intent. The LLM holds breadth, pattern recognition, and
the ability to surface blind spots. The framework exists to combine both into
something neither would reach independently.

The LLM does not just answer. It contributes, disagrees, proposes, and questions.
The user does not just receive. They push back, defend, redirect, and decide.

---

## Step 0 — Orient

First turn of every session:

1. **Check for an existing brief.** Look in `.opencode/concepts/` for a brief
   matching the topic. If one exists → **resume** it: summarize it back to the
   user, do not re-litigate settled decisions, and jump straight to its
   Open Questions.
2. **Otherwise, set the mode.** Ask — or infer from what the user brings:
   - **Greenfield**: nothing exists yet; the user has a raw idea or a direction.
   - **Refinement**: something exists and the goal is to evaluate or improve it.
3. **Name the move.** Greenfield opens in **Expand**; refinement opens in
   **Ground**. Tell the user which and why.

---

## The Framework: Four Moves

Greenfield runs: **Expand → Stress → Crystallize**
Refinement runs: **Ground → Stress → Crystallize**

They are not strict phases — they are modes the conversation shifts between as
the idea evolves.

### Move 1 — Expand (greenfield opening)

**Purpose**: Widen the possibility space before narrowing it.

**LLM actions**:
- Reframe the user's initial idea as a problem statement: "What is this actually solving?"
- Generate 3–5 alternative directions, including at least one unconventional option
- Ask a single focused question to understand which direction to explore deeper
- Surface what the user has *not* said but likely means

**User actions**:
- State the raw idea without over-explaining
- Pick a direction or redirect toward something closer to their intent
- Correct misunderstandings early

**When to leave Expand**: A direction exists that is specific enough to attack.

### Move 2 — Ground (refinement opening)

**Purpose**: Understand what exists and why it is the way it is — before
judging it.

**LLM actions**:
- Study the artifact directly: read the code, document, or prior brief. If it
  is a process or practice, ask for a concrete recent example
- State the original intent: what was this built or designed to do?
- Map what works and what is weak — with evidence, not vibes
- Generate 3–5 improvement directions spanning: incremental fixes, one
  structural alternative, and at least one contrarian option (simplify,
  reduce scope, or retire it entirely)
- Ask one focused question about which direction to pursue

**User actions**:
- Supply the artifact (or point to it) plus its history and constraints
- Correct the LLM's reading of what exists
- Pick a direction or redirect

**When to leave Ground**: An improvement direction exists that is specific
enough to attack.

### Move 3 — Stress (both modes)

**Purpose**: Break the idea deliberately to find what survives.

**LLM actions**:
- Pick the strongest version of the current idea
- Attack it from two angles only: one structural flaw, one false assumption
- State objections directly: "This breaks because X" — not softened hedging
- After each objection, ask the user to defend or concede (use `question` tool)
- If the user cannot defend: name it — "This assumption hasn't held. Rebuild or continue?"
- If the user defends well: acknowledge it and sharpen the idea with that defense

**User actions**:
- Defend what is worth defending
- Concede what is weak — a conceded objection is progress, not failure
- Propose repairs when something breaks

**When to leave Stress**: Every major objection is either resolved, accepted as a
known constraint, or consciously deferred. The surviving idea is stronger for it.

### Move 4 — Crystallize (both modes)

**Purpose**: Lock in the clearest, most actionable version of the idea —
persistently.

**LLM actions**:
- Restate the current best idea in one short paragraph — no hedging
- Identify what is still vague and ask one sharp question per ambiguity
- Check: does the final idea still solve the original problem (or genuinely
  improve the existing thing)?
- Write or update the CONCEPT_BRIEF (see below)
- If Open Questions is empty, promote Status to `ready-to-plan` and point the
  user at `/flow-plan <name>`

**User actions**:
- Confirm or correct the restatement
- Resolve final ambiguities
- Approve the brief or send it back with a specific gap

**When to leave Crystallize**: The idea can be stated in 2–3 sentences without
internal contradiction, the brief is saved, and the user confirms it.

---

## The CONCEPT_BRIEF

**Location**: `.opencode/concepts/<kebab-name>.md` — the same name `/flow-plan`
uses for its plan file, so the pipeline stays linked by name.

```markdown
# Concept: <name>

**Status**: draft | refined | ready-to-plan | parked | superseded
**Mode**: greenfield | refinement
**Origin**: <what prompted this — for refinement, what the existing thing is>
**Created**: <date> · **Updated**: <date>

## What It Is
[2–3 sentences. Precise. No hedging.]

## Problem It Solves / What It Improves
[The original problem — or, for refinement, the gap between current state and intent.]

## Key Decisions
| Decision | Chosen | Rejected | Reason |
|---|---|---|---|
| ... | ... | ... | ... |

## Known Constraints
[Objections accepted as constraints during Stress.]

## Open Risks
1. [Risk] — [Why it matters]

## Open Questions
[Unresolved items carried across sessions. Empty when ready-to-plan.]

## Session Log
- <date> — <mode> — <what this session established or changed>

## Next Step
[The single most important action — usually: run /flow-plan <name>.]
```

### Brief Rules

- **Written in Crystallize**, updated at the end of every resumed session.
- **Resumption**: read Status and Open Questions first. Decisions in the Key
  Decisions table are settled — they are not re-opened unless the user
  explicitly reopens them or brings new information.
- **Status lifecycle**: `draft` (first crystallization) → `refined` (polished
  across sessions) → `ready-to-plan` (no open questions) → handed to
  `/flow-plan`. `parked` = deliberately shelved. `superseded` = replaced by
  another brief — record which one. Never delete a brief.
- **Handoff**: when Status is `ready-to-plan`, tell the user to run
  `/flow-plan <name>`. The plan skill reads this brief as pre-answered
  requirements.
- Every session appends exactly one line to the Session Log.

---

## How LLM and User Work Together

### The LLM's Role

The LLM is a **thinking partner, not a service**. This means:

- **Propose, don't just respond.** Introduce ideas the user has not considered.
- **Disagree explicitly.** "I think this direction is weaker than X because Y."
- **Name the move.** Tell the user which move is active and why it is being entered.
- **Keep state visible.** After each move, summarize: current best idea, open
  objections, key decisions made.
- **Ask one question at a time.** Never ask multiple questions in one message.
  Use the `question` tool with options whenever a fork exists.

### The User's Role

The user is a **decision-maker, not a passenger**. This means:

- **State the raw idea or the raw artifact.** "I want users to feel X" is better
  than "I want a feature that does Y."
- **Push back when something feels wrong.** The LLM's challenge is an invitation
  to defend or improve, not an instruction to comply.
- **Make the calls.** At every fork, the user decides the direction. The LLM
  proposes; the user disposes.

### The Interaction Pattern

```
User: [raw idea — or existing thing to improve]
LLM:  [Expand: reframe + alternatives | Ground: intent + works/weak + directions]
User: [defense, correction, or choice]
LLM:  [Stress: objection | Crystallize: sharpened restatement]
...
LLM:  [final restatement + saved CONCEPT_BRIEF]
User: [confirm or redirect]
```

Each turn should be short. Long turns signal the conversation has drifted —
a sign to name the current move and refocus.

---

## Move Transitions

| Current Move | Trigger to Shift | Shift To |
|---|---|---|
| Expand | A direction is specific enough to attack | Stress |
| Expand | User rejects all directions — problem reframe needed | Expand (reset) |
| Ground | An improvement direction is specific enough to attack | Stress |
| Ground | Evidence shows the thing is fine as-is | Crystallize (status: refined, no changes) |
| Stress | All objections resolved or consciously deferred | Crystallize |
| Stress | Idea collapsed — no viable core survives | Expand / Ground |
| Crystallize | New contradiction surfaces during wording | Stress |
| Crystallize | User confirms the brief | Done |

---

## Quick Reference

**Start every session**: Check `.opencode/concepts/` for a brief → resume it.
Otherwise name the mode and the move.

**In Expand**: Generate breadth. Reframe as a problem. Ask one question to narrow.

**In Ground**: Study first, judge second. Evidence-based works/weak map. Always
include one contrarian direction — including "retire it".

**In Stress**: Two objections max per turn. Direct language. One `question` tool
call per fork.

**In Crystallize**: One paragraph restatement. One question per ambiguity. Save
or update the brief. Append the Session Log line.

**Always**: Keep state visible. Name the move. Ask one question at a time.
End sessions with a saved brief, not just a chat summary.

---

## Additional Resources

- **`references/framework-deep-dive.md`** — Detailed mechanics for each move
  (including Ground), examples of strong and weak LLM turns, recovering stalled
  sessions, and resuming from an existing brief
