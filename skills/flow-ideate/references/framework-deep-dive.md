# Framework Deep Dive: Flow Ideation

Detailed mechanics, worked examples, and recovery strategies for the
Flow Ideation framework.

---

## Table of Contents

1. [Move 1 — Expand: Detailed Mechanics](#move-1--expand-detailed-mechanics)
2. [Move 2 — Ground: Detailed Mechanics](#move-2--ground-detailed-mechanics)
3. [Move 3 — Stress: Detailed Mechanics](#move-3--stress-detailed-mechanics)
4. [Move 4 — Crystallize: Detailed Mechanics](#move-4--crystallize-detailed-mechanics)
5. [Example Turns: Strong vs. Weak](#example-turns-strong-vs-weak)
6. [Recovering Stalled Sessions](#recovering-stalled-sessions)
7. [Resuming From a CONCEPT_BRIEF](#resuming-from-a-concept_brief)
8. [Using the Question Tool Effectively](#using-the-question-tool-effectively)

---

## Move 1 — Expand: Detailed Mechanics

### The Reframe Technique

The most valuable thing the LLM does in Expand is reframe the user's solution
back into a problem. Users often arrive with a solution in mind and describe it
as the idea. The LLM's job is to surface the underlying problem so the solution
space is not artificially narrowed.

**Reframe pattern**:

1. Echo the user's stated idea briefly
2. State the problem it implies: "Which means the real problem is: [problem]"
3. Offer an alternative problem framing: "Or is it actually: [different problem]?"
4. Ask which framing is right

**Example**:
> User: "I want a notification system that tells users when their data changes."
>
> LLM: "That implies the real problem is: users miss important changes because
> they're not watching the data at the right time. Or is it actually: users
> don't trust the data because they can't tell if it's current? Which one?"

The second framing opens a completely different solution space. Without the
reframe, both paths look the same from the outside.

### How Many Alternatives to Generate

Generate 3–5 alternatives in Expand. Fewer than 3 forces premature narrowing.
More than 5 overwhelms the user and dilutes focus.

The alternatives should span a range:

- **Obvious**: The most natural interpretation of the idea
- **Adjacent**: A variation that shifts one key assumption
- **Unconventional**: A direction that solves the same problem a different way
- **Contrarian**: An approach that questions whether the problem is real

Always include at least one unconventional or contrarian option. It often
surfaces the most useful insight, even if it gets rejected.

### What "Specific Enough to Attack" Means

Move to Stress when the idea has:

- A clear subject (what is being built or changed)
- A clear goal (what problem it solves)
- At least one assumption that can be challenged

If the idea is still "we want to improve the user experience", it is not
specific enough. Push in Expand until the idea has a concrete direction.

---

## Move 2 — Ground: Detailed Mechanics

Ground is the refinement opening move. Its discipline is **study first, judge
second** — most bad improvement advice comes from opining on an artifact that
was never actually read.

### Studying the Artifact

- **Code**: read it before saying anything about it. The works/weak map must
  cite files and functions. If the surface is too large to read fully, read the
  entry points and the parts the user cares about — and say what you did not
  read.
- **Document or prior brief**: read it in full. Note what has aged badly —
  decisions that made sense when written but whose context has changed.
- **Process or team practice**: ask for one concrete recent example before
  generalizing. "Code review is slow" becomes attackable only as "last week's
  PR sat 4 days waiting on reviewer assignment".

### Stating the Original Intent

Before evaluating, state what the thing was *supposed* to do — from the code,
the brief, or the user. Evaluation is the gap between intent and current
state. Two failure modes to avoid:

- Judging against an intent the thing never had ("this notification system
  doesn't batch" — it was never meant to).
- Assuming the original intent is still the right intent (requirements drift;
  the most valuable refinement sometimes re-aims the thing).

### Evidence-Based Works/Weak Mapping

| Weak | Strong |
| --- | --- |
| "The error handling is bad" | "The retry path in X swallows errors (file:func); three callers silently depend on that" |
| "It's kind of messy" | "Two modules both define their own config loading; they can disagree at runtime" |
| "Performance could be better" | "The list endpoint does N+1 queries — here's the loop (file:func)" |

If you cannot cite evidence for a weakness, either go read until you can, or
mark it explicitly as an unverified suspicion.

### Improvement Direction Generation

Generate 3–5 directions spanning:

- **Incremental**: fix the weak spots in place, keep the shape
- **Structural**: change the shape — extract, merge, replace a component
- **Contrarian**: simplify drastically, reduce scope, or retire the thing

Always include one contrarian option. In refinement, "this costs more than it
returns — retire it" is sometimes the correct answer, and it is the answer
users most need to hear from someone other than themselves.

One legitimate Ground outcome is **"the thing is fine"**: intent still holds,
weak spots are minor, no direction beats doing nothing. In that case, skip
Stress, crystallize as-is, and record the verdict — a clean bill of health is
a valid concept result.

### What "Specific Enough to Attack" Means

Move to Stress when the chosen direction has:

- A clear subject (what is being changed)
- A clear goal (which weakness or gap it addresses)
- At least one assumption that can be challenged

---

## Move 3 — Stress: Detailed Mechanics

### Choosing the Two Attack Angles

Attack from exactly two angles per Stress turn. More than two overwhelms the
conversation. Fewer than two feels like incomplete scrutiny.

The two standard angles are:

1. **Structural flaw**: Something wrong with how the idea is put together —
   a logical inconsistency, an architectural problem, a conflict with known
   constraints
2. **False assumption**: A premise the idea depends on that may not be true

Other valid angle pairs when the standard ones don't fit:

- Structural flaw + competitive alternative (what would a different approach do?)
- False assumption + scope problem (is this idea trying to solve too many things?)

### Language of Direct Objection

The LLM must not soften objections. Compare:

| Weak | Strong |
| --- | --- |
| "One consideration might be that users don't always..." | "This breaks if users don't check the dashboard daily. That's most users." |
| "There could potentially be performance concerns..." | "This query will be slow at scale. Here's why: [specific reason]." |
| "It's worth thinking about whether..." | "This assumption is false. Most users won't configure this manually." |

Direct language is not aggressive — it is clear. The user can push back,
defend, or concede. They cannot do any of that to a hedged non-statement.

### Handling Defense vs. Concession

When the user defends an objection:

1. Test the defense: does it actually answer the objection or just restate confidence?
2. If the defense holds: acknowledge it explicitly and fold it into the idea
3. If the defense doesn't hold: name that — "That defense still leaves [specific gap]"

When the user concedes:

1. Acknowledge the concession as progress, not defeat
2. Ask: "Does this break the idea, or is it a constraint we design around?"
3. If it's a constraint: note it for the CONCEPT_BRIEF's Known Constraints

### When the Idea Collapses

Sometimes Stress reveals there is no viable core — the idea was built on a
false premise that cannot be salvaged. Signs of collapse:

- The user cannot defend the core assumption after two rounds
- Every alternative framing also fails under the same objection
- The user themselves says "actually, I'm not sure this is the right problem"

When this happens, name it directly: "The core premise hasn't held under
pressure. I think we need to go back to Expand with a different framing.
The useful thing we learned is: [what the failed idea revealed]."

The failed idea is not wasted — it always reveals something about the real
problem. Carry that forward into the next Expand cycle.

---

## Move 4 — Crystallize: Detailed Mechanics

### Writing the One-Paragraph Restatement

The restatement is the hardest part of Crystallize. It must:

- Capture the idea after all Stress refinements
- Be written as if for someone who was not in the conversation
- Contain no hedging ("might", "could", "potentially")
- Fit in 2–3 sentences

The test: can the user read this paragraph and immediately start planning
implementation? If not, something is still vague.

**Weak restatement**:
> "We're thinking about a system that might help users track changes to their
> data in some kind of real-time or near-real-time way."

**Strong restatement**:
> "A change-tracking layer that pushes structured diffs to subscribed users
> whenever a watched record is updated. Notifications include what changed,
> who changed it, and a direct link to the record. Users subscribe per-record,
> not globally."

### Drilling Ambiguities

After the restatement, identify ambiguities — things the paragraph implies but
does not specify. Ask one question per ambiguity, in order of importance.

**Pattern**: "The restatement says [X]. Does that mean [option A] or [option B]?"

Use the `question` tool with explicit options when the answer is a choice.
Ask as a free question only when the answer is open-ended and both parties
genuinely don't know.

### Confirming the Final Brief

Before writing the brief, ask explicitly: "Is this the idea you want to move
forward with?" Use the `question` tool with Yes / Not quite / Start over.

If the answer is "Not quite", ask one sharp question: "What specifically is wrong?"
Do not produce a revised brief until the specific gap is named.

Write the brief file, append the Session Log line, promote Status to
`ready-to-plan` if Open Questions is empty, and give the user the brief's path
plus the next command: `/flow-plan <name>`.

---

## Example Turns: Strong vs. Weak

### Expand — Strong Turn

> User: "I want to add a dashboard for admins to see user activity."
>
> LLM: "That implies the problem is: admins can't see what users are doing and
> that creates [support burden / security risk / unknown]. Before generating
> options — which problem is it?
>
> Options: (a) Support burden — admins get questions they can't answer without
> seeing activity. (b) Security audit — admins need a record of who did what.
> (c) Product insight — the team wants to understand usage patterns."

The LLM reframes before generating alternatives, which prevents generating
three dashboard variants when the real answer might be an audit log.

### Ground — Strong Turn

> User: "I want to improve our notification system. It's annoying."
>
> LLM: "I read the notification module. Original intent, as far as the code
> shows: tell users about state changes they can't see otherwise. What works:
> delivery is reliable and the preference page lets users mute per-category.
> What's weak: everything fires in real time regardless of urgency — a
> migration finishing and a comment on your PR arrive identically, which is
> likely the 'annoying' part. Three directions: (a) batch low-urgency
> notifications into a digest, (b) add an urgency model and a quiet-hours
> policy, (c) contrarian — most of these notifications don't need to exist;
> cut the bottom half by engagement data and see if anyone notices. Which
> direction matches what you mean by 'annoying'?"

The LLM read the artifact, separated intent from current state, cited
evidence for the weakness, and generated directions spanning incremental,
structural, and contrarian — including the retire option.

### Stress — Strong Turn

> LLM: "Two problems with this design. First, structural: this assumes admins
> check the dashboard proactively. If they don't, the visibility gain is zero.
> Second, assumption: 'user activity' means different things to the support
> team vs. the security team. You can't build one view that serves both well.
> Which of these is more important to address first?"

Specific. Two angles only. Ends with a decision fork using the `question` tool.

### Crystallize — Strong Turn

> LLM: "Current best version: an activity log page scoped to the security use
> case — immutable records of user actions (login, data export, record deletion)
> with timestamp, user, and record reference. Not a real-time dashboard; a
> searchable audit trail. Does this still match what you're building?"

Short restatement. Scope is explicit. Ends with a yes/no confirmation.

---

## Recovering Stalled Sessions

### Stall Type 1: User Keeps Agreeing

Symptom: The user accepts every LLM proposal without pushback. The session
feels smooth but the idea is not getting sharper.

Recovery: Introduce an unconventional or contrarian option in Expand, or
raise a stronger objection in Stress. Make it harder to agree.

Explicit prompt: "I've been pushing in one direction. Let me argue against
my own proposal: [objection]. Does that change anything?"

### Stall Type 2: Conversation Is Circular

Symptom: The same objection or idea keeps resurfacing without resolution.

Recovery: Name it. "We've circled back to [X] three times. Let's resolve it
directly: is [X] a dealbreaker, a known constraint, or something we're
deferring? Pick one."

Use the `question` tool to force a choice.

### Stall Type 3: Too Many Open Threads

Symptom: The conversation has branched into multiple unresolved directions.
Nobody is sure what the current best idea is.

Recovery: Stop and re-anchor. "Let me state where I think we are: [one
paragraph]. Is this accurate?" Then close open threads one by one before
proceeding.

### Stall Type 4: User Wants to Skip Stress

Symptom: User says "this is fine, let's move on" before major objections
are raised.

Recovery: Do not skip Stress. State one targeted objection: "Before we
move on — one thing I'd want us to address: [specific objection]. It's
quick. Worth 30 seconds?"

A user who has considered and dismissed an objection is different from a
user who has never been asked. The former is confident; the latter is
exposed.

---

## Resuming From a CONCEPT_BRIEF

Resumed sessions have their own failure modes. The brief is the antidote to
all of them — use it.

### Stall Type 5: Relitigating Settled Decisions

Symptom: The session re-opens a decision that the Key Decisions table already
closed. Feels like progress; actually erodes the concept.

Recovery: Point at the row. "We settled this on <date>: <chosen> over
<rejected> because <reason>. Has something changed?" If yes, update the row
with the new reason. If no, move on.

### Stall Type 6: Drifting From the Log

Symptom: The conversation wanders into territory no Session Log entry
covers — scope the brief never had.

Recovery: Re-read the What It Is section aloud. "The brief says we're building
X. This sounds like a different concept — new brief, or a scope change we
should record?"

### Resumption Discipline

- Start from **Status + Open Questions**, never from a blank slate.
- One Session Log line per session, no exceptions — briefs without logs
  drift from their own decisions.
- If Open Questions is empty but Status is not `ready-to-plan`, either
  crystallize and promote it, or write down the new open question that is
  blocking promotion.
- Ending a resumed session without updating the brief file is a failed
  session — the chat summary is not the artifact.

---

## Using the Question Tool Effectively

### When to Use It

Use the `question` tool at every decision fork — any point where the
conversation could go in two or more meaningfully different directions.

Required uses:

- Choosing which direction to explore after Expand
- Deciding whether an objection breaks the idea or is a constraint
- Phase transition confirmations
- Final "move forward?" confirmation in Crystallize

Optional uses:

- Ranking which ambiguity to resolve first
- Choosing between two restatement wordings

### Format Guidelines

- **Header**: 3–5 words describing the decision (e.g., "Direction to explore")
- **Options**: 2–4 choices, each with a 1-sentence description
- **Custom enabled**: Always leave custom enabled so the user can redirect

### When NOT to Use It

Do not use the `question` tool when:

- The answer is open-ended and both parties genuinely don't know
- The user is mid-explanation and a choice would interrupt their thinking
- The question has one obvious right answer (just state it)

In those cases, ask a plain question or make a direct assertion.
