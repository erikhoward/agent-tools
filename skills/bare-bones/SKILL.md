---
name: bare-bones
description: 'Use when writing, rewriting, or reviewing any prose — technical docs (documentation, READMEs, runbooks, procedures, error messages, release notes, incident reports, API guides, PR descriptions, changelogs, agent instructions) or general prose (blog posts, essays, emails, announcements, launch posts). Removes AI-slop patterns in both: synonym rotation, hedges, filler, binary contrasts, throat-clearing, fake-profound endings. Technical prose follows ASD-STE100 Simplified Technical English: short sentences, active voice, simple tenses, one word one meaning, no semicolons, no phrasal verbs, condition-first commands. General prose gets a minimum effective edit that preserves the writer voice. Triggers on "make this not sound like AI", "de-slop this draft", "is this AI slop", "simplify this", "STE", "ASD-STE100", "Simplified Technical English", "make docs clear", "edit my draft", "tighten this".'
license: MIT
compatibility: opencode
metadata:
  standard: ASD-STE100 Issue 9 (2025-01-15)
  sources:
    - https://github.com/wilmai/ste
    - https://github.com/danyuchn/asd-ste100-skill
    - https://github.com/mshojaei77/adhd-friendly-ste-technical-writer
    - https://github.com/petergyang/no-ai-slop
  audience: developers
---

# Bare-Bones Style

Two traditions, one enemy. STE is the controlled language the aerospace
industry uses so a tired non-native reader cannot misread an instruction; the
rules remove ambiguity, and machine-writing habits die as a side effect. The
human-editor tradition (adapted from no-ai-slop) does the same job for general
prose: cut the patterns that make text sound machine-made, keep the voice that
makes it sound like one person. Both modes write for a reader who gets one
pass. For general design principles, combine with the `solid` skill.

## When to use

- Writing or reviewing technical docs, READMEs, runbooks, procedures
- Error messages and CLI output
- Agent instructions, prompts, AGENTS.md, skills
- PR descriptions, commit messages, changelogs, release notes
- Incident reports and postmortems
- API guides and reference docs
- Blog posts, essays, emails, announcements, launch posts
- Any draft the user wants de-slopped, tightened, or checked for AI patterns

Technical text gets the STE rules below. General prose gets the General mode:
the same slop removal, but the writer's voice survives the edit.

## Two jobs

| Job | When | What you do |
|---|---|---|
| **Edit** (default) | The user shares a draft | Rewrite it under the mode rules and return the edited text |
| **Detect** | The user asks whether text is AI slop, or asks to audit, scan, or flag without rewriting | Name each pattern from this skill, quote the line, give the fix in a few words. Do not rewrite. Do not score. Do not guess whether AI wrote it — detectors guess, named patterns are evidence the user can check. Offer to edit after. |

## Pick the mode

| Mode | When | What you apply |
|---|---|---|
| **General** | Posts, essays, emails, announcements — text with a person behind it | Shared rules + the word lists + the patterns. The writer's voice survives the edit. STE vocabulary, tense, and modal rules do not apply. |
| **Technical — Pragmatic** (default for docs) | Docs, READMEs, error messages — the user wants clear text | All structural rules. Domain words stay (`webhook`, `idempotent`). |
| **Technical — Strict** | The user names STE, ASD-STE100, or compliance | Structural rules + full vocabulary discipline. Tell the user that full compliance needs the official dictionary (free at asd-ste100.org). |

Judge each passage by its job. Text that operates a system or reports its
behavior (procedures, reference docs, error messages) is technical. Text that
carries a person's voice, opinion, or story is general. A launch post is
general; the quickstart inside it is technical. When you cannot tell, use
General — it edits less, so it does less damage.

## Rules both modes share

Apply these before any mode-specific rule:

- **Active voice, human actor.** "The team shipped it Tuesday" beats "the
  decision emerged". Never let inanimate things do human verbs.
- **Verbs over noun forms.** "Decided" not "made a decision"; "can" not "has
  the ability to".
- **One name per thing.** No synonym rotation: the agent/assistant/tool
  shuffle collapses to one name.
- **Concrete beats abstract.** "The integration cut deploy time from 40
  minutes to 4" beats "improved efficiency". Names, numbers, dates,
  mechanisms, examples.
- **Show, do not label.** Cut commentary that tells the reader a point is
  important, surprising, or obvious. The facts carry the emphasis.
- **Portability test.** If a sentence could move unchanged to another person,
  company, or product, it is filler. Cut it or replace it with a fact or a
  judgment specific to this subject.
- **Name the source or cut the claim.** "Experts agree", "studies show" —
  name the source, or delete the claim. Never invent one.
- **Protect the facts.** Never drop a number, unit, version, threshold,
  condition, exception, or safety warning to make a sentence shorter.

## General mode — edit like a human editor

The goal is not polished generic prose. It is the same person, clearer.

- **Preserve the writer's voice.** Notice the vocabulary, cadence, bluntness,
  humor, uncertainty, digressions, level of polish. Keep the traits that feel
  personal. Do not make every paragraph equally tidy.
- **Make the minimum effective edit.** Fix slop, errors, repetition, and
  unclear passages. Leave strong human sentences alone. Cutting must be
  proportional to the slop.
- **Keep what STE would ban.** Contractions, fragments, first person, spoken
  rhythm, "I think" and "maybe" when they carry real uncertainty or the
  writer's rhythm. No approved-vocabulary list, no tense ban, no modal ladder
  in this mode.
- **Untangle without flattening.** Split a sentence only when it is genuinely
  hard to follow. Keep a clear spoken cadence and changes of pace.
- **Preserve the edge.** Strong opinions, blunt language, humor,
  self-interruptions, and honest admissions stay. Do not replace them with
  safer or more professional wording.
- **Keep the structure unless it hurts the piece.** Preserve the writer's
  progression and detours. If you reorganize, say why in the What changed
  section.
- **Lead with the point when the setup adds nothing.** Keep a personal aside
  that creates context, tension, or character.

**Ask before you edit** — one question, then proceed. If the audience or
format is unclear: "Who is this for and where will it be published?" If the
goal is unclear: "What should the reader think, feel, or do after reading?"

## Words to cut (both modes)

**Delete outright** — AI-tell vocabulary with no plain replacement. If the
word carries a fact, replace it with the fact: foster, empower, streamline,
cutting-edge, paradigm shift, game changer, this is huge, this changes
everything, tapestry, realm, beacon, multifaceted, meticulous, intricate,
paramount, transformative, elevate, embark, supercharge, harness,
ever-evolving.

**Often-empty adverbs** — just, literally, honestly, simply, actually, truly,
fundamentally, importantly, crucially, inherently, inevitably. Cut them when
they add nothing. Keep them when they carry emphasis, uncertainty, contrast,
or the writer's spoken rhythm (general mode).

**Often-empty phrases** — it's worth noting, it's important to note, at the
end of the day, when it comes to, at its core, in today's world, in the age
of, in the world of, the reality is, the truth is, in terms of, with regard
to, going forward, in this article, let's dive in. Cut them when they delay
the point. Keep an occasional phrase when it is part of the writer's
recognizable voice and the sentence still earns its place (general mode).

## Slop-to-simple substitutions

This table maps words AI docs overuse to plain replacements. Technical mode
applies it in full. General mode applies it when the plain word keeps the
voice. If the word carries no fact, delete it instead of replacing.

| Slop | Write instead |
|---|---|
| leverage, utilize | use |
| in order to | to |
| prior to, subsequent to | before, after |
| ensure | make sure that |
| obtain, acquire | get |
| commence, initiate | start |
| demonstrate | show |
| additionally, furthermore, moreover | also |
| it is worth noting that | (delete) |
| simply, seamlessly, effortlessly | (delete) |
| robust, powerful, comprehensive, performant | (delete, or give the measurement) |
| functionality | function, feature |
| enables you to, allows you to | you can |
| is designed to, aims to | (delete — say what it does) |
| facilitate | help, make possible |
| dive into, delve into | read, examine |
| spin up, stand up | start, install |
| reach out | ask, contact |
| in the event that | if |
| due to the fact that | because |
| and/or | Pick one, or write "X, or Y, or both" |
| e.g. / i.e. / etc. | for example / that is / (name the items) |

Collapse these rotations to one term each (Rules 1.11, 9.4):
check/verify/confirm/validate/ensure → pick one;
config/configuration/settings/options → pick one;
run/execute/invoke/launch → pick one.

## Patterns to cut (both modes, strongest in general prose)

Machine-writing habits. In technical mode, several overlap with STE rules
(trailing `-ing` clauses, run-ons, filler); this list catches the rest.

1. **Binary contrasts.** "This is not X. It's Y." / "The question isn't X,
   it's Y." State Y directly. "The question isn't the model. It's the eval."
   becomes "The eval matters more than the model."
2. **Throat-clearing openers.** "Here's the thing," "Let me be clear," "I'll
   be honest," "The uncomfortable truth is." Cut them and state the point.
3. **Faux-insight setups.** "This is the part most people skip," "What most
   people get wrong," "Here's what nobody tells you." Cut the setup; make the
   claim stand on its own.
4. **Colon reveals.** A noun phrase, a colon, then a lowercase dramatic
   reveal: "The best part: it learns." Rewrite as a plain sentence. Use
   colons for lists, labels, and quotes.
5. **Superficial analysis.** Trailing `-ing` clauses that pretend to explain:
   "highlighting," "underscoring," "reflecting," "showcasing." "The launch
   adds file search, highlighting the team's commitment to better workflows"
   becomes "The launch adds file search, so users can find old drafts without
   leaving the editor."
6. **Importance puffery.** "Stands as a testament," "marks a pivotal
   moment," "plays a vital role," "underscores its significance." State the
   fact and let the reader judge. "The launch marks a pivotal moment" becomes
   "The launch is the company's first paid product."
7. **Interpretive metadiscourse.** Lines that step outside the subject to
   tell the reader what to notice: "That last part matters more than it
   sounds," "The key point is," "As you can see," redundant "In other words."
   Delete the aside. If the point is unclear, replace it with support already
   in the content.
8. **Weasel attribution.** "Experts agree," "industry reports suggest,"
   "widely regarded as," "studies show." Name the source or cut the claim. If
   the user has no source, ask instead of inventing one.
9. **Fake-strong verbs.** Prefer "is" and "has" when they are clearer. "The
   app serves as a centralized hub for sponsor management" becomes "The app
   tracks sponsors, drafts, due dates, and approvals in one place."
10. **Synonym cycling.** If the clear word is right, repeat it. "The agent
    reviews the draft. The assistant scores the piece. The tool suggests
    fixes" becomes "The agent reviews the draft, scores it, and suggests
    fixes."
11. **Negative listing.** "Not a X. Not a Y. A Z." Just say Z.
12. **Dramatic fragmentation.** "X. And Y. And Z." / "That's it. That's the
    whole thing." Use complete sentences — unless the fragment is the
    writer's own rhythm (general mode).
13. **Robotic rhythm.** Repeated sentence shapes, identical paragraph
    structures, stacked punchy fragments. Vary the shape only when it helps
    the point.
14. **Rhetorical setups.** "What if I told you...", "Think about it:",
    "Plot twist:", and self-answered "Question? Answer." pairs. Drop them and
    make the point.
15. **Fake-profound kickers.** Delete the final "deep" line that turns the
    point into a cute metaphor or mic-drop. Do not rewrite it into a better
    metaphor. End on the clearest concrete sentence already in the draft.
16. **Summary-recap endings.** "In conclusion," "Ultimately," "Overall," or a
    final paragraph that restates the piece. The reader was just there. End
    on the last concrete point, takeaway, or next action.
17. **Formatting slop.** Emoji in headings, bold sprinkled mid-sentence,
    bullet lists where two sentences of prose would read better, headers over
    two-sentence sections. Format follows the content.
18. **Em dashes as a rhythm crutch.** In short copy, use none. In longer
    drafts, 1-2 when they clearly beat commas, periods, or parentheses.
    Remove clusters and decorative dashes.

## Scan checklist

Six mechanical habits cover most of what makes machine-written English hard to
parse. Scan for all six before you rewrite.

1. **Synonym rotation** — the same thing gets several names in one document.
   Fix: pick one name, use it every time.
2. **Hedge stacking** — helper verbs pile up until the sentence asserts nothing.
   Fix: state the claim, or delete it.
3. **Nominalization** — an action frozen into a noun ("perform an analysis of").
   Fix: use the verb ("analyze").
4. **Marketing adjectives** — words that claim quality instead of showing it
   (seamless, robust, blazing-fast). Fix: delete, or replace with the
   measurement.
5. **Run-on sentences** — several ideas joined by semicolons or em dashes. Fix:
   one idea per sentence.
6. **Soft phrasal verbs** — spin up, reach out, dive into. Fix: use the single
   plain verb (start, contact, read).

## Classify the text

| | Procedural (instructions) | Descriptive (explanations) |
|---|---|---|
| Verb form | Imperative: "Install the pump." | Simple present, past, or future |
| Sentence limit | 20 words (Rule 5.1) | 25 words (Rule 6.3) |
| Unit rule | One instruction per sentence (Rule 5.2) | One topic per paragraph, max 6 sentences (Rules 6.5, 6.6) |

Every other rule depends on this classification. Do not mix the two in one
passage. A "Getting started" section is procedural; an "Architecture" section is
descriptive. A note inside a procedure is descriptive (25-word limit, no
imperative).

## Structural rules

| Rule | Do | Don't |
|---|---|---|
| Active voice (Rule 3.6) | "The agent deletes the file." | "The file is deleted." — unless the actor is genuinely unknown |
| No phrasal verbs (Rule 9.3) | "Remove the panel." / "Start the job." | "Take off the panel." / "Spin up the job." |
| One instruction per sentence (Rule 5.2) | "Open the file. Read line 3." | "Open the file and read line 3, then check it." |
| Sentence length | 20 words procedural, 25 descriptive | Long compound or subordinate-clause sentences |
| No semicolons (Rule 8.1) | Split into two sentences | Any semicolon — STE bans the mark outright |
| Noun clusters (Rule 2.1) | Max 3 words; break longer with prepositions | 4+ word noun stacks |
| No ellipsis or contractions (Rule 4.2) | Keep the subject, verb, article, and "that" | Drop words to save space; "don't", "it's" |
| Keep modality | "The request may have failed." stays | Promote a hedge to a fact |
| Paragraph limits (Rules 6.5, 6.6) | One topic, max 6 sentences | Multi-topic paragraphs |
| Lists (Rule 4.3) | Numbered or bulleted list for 3+ steps or conditions | A sequence buried in one prose sentence |

## Lexical rules

A direction of travel without the official ~900-word dictionary (copyrighted by
ASD, not reproduced here).

| Rule | Do | Don't | Why weaker here |
|---|---|---|---|
| One word, one meaning (Rules 1.3, 1.11) | Pick one verb for one action and reuse it | Rotate check/verify/confirm for the same action | Consistency is checkable; the approved word is not, without the dictionary |
| One part of speech (Rule 1.2) | "Apply oil to the valve" (oil = noun) | "Oil the valve" (oil = verb) | Whether "oil" is noun-only is a dictionary fact |
| Verb, not noun (Rule 3.7) | "Inspect the filter." | "Perform an inspection of the filter." | Preferring the verb is safe; the approved verb needs the dictionary |
| Domain terms (Rules 1.5, 1.8, 1.12) | Keep technical nouns/verbs; define once if not common English | Use jargon without defining it | The glossary allowance is real STE, but the base dictionary is absent |

## Simple tenses

Permitted forms: infinitive, imperative, simple present, simple past, simple
future, past participle as adjective. No present perfect, no other compound
forms (Rule 3.4). An "-ing" form is legal only as a technical noun ("logging"),
never as a verb (Rule 3.5).

**Before:** The migration has completed and the table is being rebuilt.
**After:** The migration is complete. The database rebuilds the table.

Exception: when the compound form carries information the simple form cannot —
current relevance, or a hedge like "may have failed" — keep it and flag the
departure. When the tense rule and the modality rule conflict, modality wins.

## The modal ladder

Approved modals: `can`, `will`, `must`. Banned: `should`, `would`, `may`,
`might`, `could`.

| You wrote | STE writes |
|---|---|
| should (requirement) | must |
| should (recommendation) | Delete it, or state it as fact: "X is better because Y." |
| may / might / could (possibility) | can |
| would (hypothetical) | Restructure: "If X occurs, Y occurs." |

## Keep precision over compliance

A rule of this skill, not of ASD-STE100. It drives both modes. Never drop any
of these to satisfy a rule:

- a safety condition or precondition
- a scope qualifier ("for Postgres 14 and later")
- a number, unit, version, threshold, or date
- an exception or edge case
- a named actor, when who acts matters

In General mode the same principle holds: never smooth a useful detail into
generic importance. "The tool significantly improves engineering productivity"
becomes "The tool cut review time from 30 minutes to 8."

When a rule and one of these collide, keep the fact and break the rule. Two
escapes come first: split the sentence (Rule 4.3 or 5.2), or restructure it
(Rule 9.1). Use them before you accept a violation. Then report it in a
`What I did not simplify` block at the end — one line per item: the fact, the
rule broken, the reason. Omit the block when nothing was kept.

## Untouchables

These are technical names (Rules 1.5, 8.6). Leave them exact, even when they
break vocabulary rules:

- Code blocks, inline code, identifiers, CLI commands, flags, file paths
- Quoted error messages and log lines
- Product names, API endpoint names, config keys

Each counts as one word toward the sentence limit, so long identifiers do not
blow the budget.

## Process

1. If the user gave no draft, ask for it.
2. Read the input once for meaning — do not rewrite before you understand what
   it must still say.
3. Pick the job (Edit or Detect) and the mode.
4. For a Detect request: name each pattern with a quoted line and a short fix.
   Do not rewrite. Stop and offer to edit.
5. For an Edit: flag every violation from the shared rules, the word lists, the
   pattern list, and your mode's rules.
6. Rewrite preserving meaning exactly. **Check modality before you commit** — a
   shorter sentence that upgrades a hedge to a fact is a different claim, not a
   simplification.
7. Run the self-check, then output. If the input already complies, say so. Do
   not force edits onto compliant text.

## Output format

**Default: the rewritten text, and nothing else.** No preamble, no mode
announcement, no violation count.

- **General mode:** append a short **What changed** section — one line per
  class of change, not per word. Name any reorganization and why.
- **Technical mode:** append a `Kept as-is:` line when you kept a longer
  phrasing on purpose, naming the phrase and the precision that would have
  been lost. Omit it when there is nothing to report.

**Detect requests:** a findings report — each pattern named, the offending
line quoted, a short fix. No rewrite, no score, no authorship guess. Offer to
edit the draft after.

**On request:** a rule-violation table:

```markdown
| Rule violated | Original | Simplified |
|---|---|---|
| Present perfect tense | "We have received the request." | "We received the request." |
| Noun cluster (4+ words) | "the agent task queue priority handler" | "the handler that sets task-queue priority" |
```

Follow the table with a one-line note on anything you deliberately did not
simplify, and why.

## Self-check before delivery

This step is not optional. Run the checks for your mode.

**Technical mode:**

1. Count words in the three longest sentences. Over the 20/25 limit → split
   them.
2. Search for: contractions (`'ll`, `'re`, `'ve`, `n't`, `'s`), `has been`,
   `have been`, `should`, `-ing` verbs after a comma, semicolons.
3. Search for every `if` and `when`. Each stands at the START of its sentence,
   before the command. "Increase the timeout if the network is slow" → "If the
   network is slow, increase the timeout."
4. Search for the verbs you did not pick (the check/verify/confirm set). Replace
   every hit with your chosen verb.
5. Compare against the source, fact by fact: every condition, qualifier,
   number, exception, and actor still present. Anything dropped goes back in.
   Anything kept against a rule goes in the `What I did not simplify` block.

**General mode:**

1. Would the writer recognize the draft as their own voice?
2. Did strong human sentences stay untouched — no forced consistency, no
   equal tidiness?
3. Is the cutting proportional to the slop?
4. Does every generic sentence pass the portability test, or was it cut or
   made specific?
5. Did the edit add no claims, examples, stats, or opinions? Compare against
   the source, fact by fact.

For a full audit, run `references/checklist.md`.

## Agent discipline

Rules that specifically counter common agent failure modes in writing:

- **Write for one pass.** Each sentence must survive a single read — the reader
  cannot scroll back.
- **Never drop a fact to shorten a sentence.** Precision outranks compliance;
  split or restructure first, break the rule second, report it third.
- **Check modality before you rewrite.** Hedges ("may have failed") carry the
  author's confidence — cutting them changes the claim. This is the most common
  STE rewrite failure.
- **Pick one verb and keep it.** Synonym rotation (check/verify/confirm) forces
  the reader to guess whether they mean the same action.
- **Do not sand the voice off.** In General mode, if the edit makes every
  paragraph sound like the editor, undo it. The product is the writer, clearer
  — not the editor.
- **Do not guess authorship.** In the Detect job, named patterns are evidence.
  "This is AI" is a guess. Name the patterns; let the user judge.
- **Do not cite rule numbers from memory.** The numbering is unintuitive and
  models invent it. Cite only rule numbers that appear in this file. For
  compliance audits, tell the user to confirm against the official standard.

## Extended guidance

- **`references/checklist.md`** — full verification pass for both modes:
  mechanical search patterns, countable checks, judgment checks, precision
  audit, general-mode voice checks, detect-report checks
- **`references/use-cases.md`** — adaptations for error messages, runbooks,
  incident reports, release notes, agent instructions, agent-to-agent text,
  translation prep, UI copy, and general prose (blog posts, email, launch
  posts)
- **`references/before-after.md`** — worked before/after examples: official STE
  rules applied, agent-output rewrites, and a general-mode de-slop

## References

- **ASD-STE100 official site**: https://www.asd-ste100.org/
- **ASD-STE100 — About STE**: https://www.asd-ste100.org/about_STE.html
- **ASD-STE100 — Downloads**: https://www.asd-ste100.org/STE_downloads.html
- **Simplified Technical English — Wikipedia**: https://en.wikipedia.org/wiki/Simplified_Technical_English
- **W3C Cognitive Accessibility**: https://www.w3.org/TR/coga-usable/
- **no-ai-slop (source of the General mode)**: https://github.com/petergyang/no-ai-slop

Adapted from [wilmai/ste](https://github.com/wilmai/ste), [danyuchn/asd-ste100-skill](https://github.com/danyuchn/asd-ste100-skill), [mshojaei77/adhd-friendly-ste-technical-writer](https://github.com/mshojaei77/adhd-friendly-ste-technical-writer), and [petergyang/no-ai-slop](https://github.com/petergyang/no-ai-slop) (all MIT).
