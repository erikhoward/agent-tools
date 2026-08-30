---
name: bare-bones
description: Use when writing, rewriting, or reviewing technical prose — documentation, READMEs, runbooks, procedures, error messages, release notes, incident reports, API guides, PR descriptions, changelogs, and agent instructions. Applies ASD-STE100 Simplified Technical English rules: short sentences, active voice, simple tenses, one word one meaning, no semicolons, no phrasal verbs, condition-first commands. Triggers on "make this not sound like AI", "de-slop this draft", "simplify this", "STE", "ASD-STE100", "Simplified Technical English", "make docs clear". Not for marketing or creative copy.
license: MIT
compatibility: opencode
metadata:
  standard: ASD-STE100 Issue 9 (2025-01-15)
  sources:
    - https://github.com/wilmai/ste
    - https://github.com/danyuchn/asd-ste100-skill
    - https://github.com/mshojaei77/adhd-friendly-ste-technical-writer
  audience: developers
---

# Bare-Bones Style

STE is the controlled language the aerospace industry uses so a tired non-native
reader cannot misread an instruction. The rules remove ambiguity, and AI writing
slop dies as a side effect: long sentences, synonym rotation, hedges, filler.
Write for a reader who gets one pass. For general design principles, combine
with the `solid` skill.

## When to use

- Writing or reviewing technical docs, READMEs, runbooks, procedures
- Error messages and CLI output
- Agent instructions, prompts, AGENTS.md, skills
- PR descriptions, commit messages, changelogs, release notes
- Incident reports and postmortems
- API guides and reference docs

Not for marketing, creative, or brand copy — STE deletes persuasion by design.

## Two modes

| Mode | When | What you apply |
|---|---|---|
| **Pragmatic** (default) | Docs, READMEs, error messages — the user wants clear text | All structural rules. Domain words stay (`webhook`, `idempotent`). |
| **Strict** | The user names STE, ASD-STE100, or compliance | Structural rules + full vocabulary discipline. Tell the user that full compliance needs the official dictionary (free at asd-ste100.org). |

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

## Slop-to-simple substitutions

This table maps words AI docs overuse to plain replacements. If the word carries
no fact, delete it instead of replacing.

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

## Keep precision over compliance

A rule of this skill, not of ASD-STE100. Never drop any of these to satisfy a
rule:

- a safety condition or precondition
- a scope qualifier ("for Postgres 14 and later")
- a number, unit, version, threshold, or date
- an exception or edge case
- a named actor, when who acts matters

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

1. Pick the mode (Pragmatic or Strict).
2. Read the input once for meaning — do not rewrite before you understand what
   it must still say.
3. Classify each passage and flag every violation from the rules and the scan
   checklist.
4. Rewrite preserving meaning exactly. **Check modality before you commit** — a
   shorter sentence that upgrades a hedge to a fact is a different claim, not a
   simplification.
5. Output the rewritten text.
6. If the input already complies, say so. Do not force edits onto compliant
   text.

## Output format

**Default: the rewritten text, and nothing else.** No preamble, no mode
announcement, no violation count. The one permitted addition: a `Kept as-is:`
line when step 4 kept a longer phrasing on purpose, naming the phrase and the
precision that would have been lost. Omit it when there is nothing to report.

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

This step is not optional. Run these five checks on the draft:

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

For a full audit, run `references/checklist.md`.

## Agent discipline

Rules that specifically counter common agent failure modes in technical writing:

- **Write for one pass.** Each sentence must survive a single read — the reader
  cannot scroll back.
- **Never drop a fact to shorten a sentence.** Precision outranks compliance;
  split or restructure first, break the rule second, report it third.
- **Check modality before you rewrite.** Hedges ("may have failed") carry the
  author's confidence — cutting them changes the claim. This is the most common
  STE rewrite failure.
- **Pick one verb and keep it.** Synonym rotation (check/verify/confirm) forces
  the reader to guess whether they mean the same action.
- **Do not cite rule numbers from memory.** The numbering is unintuitive and
  models invent it. Cite only rule numbers that appear in this file. For
  compliance audits, tell the user to confirm against the official standard.

## Extended guidance

- **`references/checklist.md`** — full verification pass: mechanical search
  patterns, countable checks, judgment checks, precision audit
- **`references/use-cases.md`** — adaptations for error messages, runbooks,
  incident reports, release notes, agent instructions, agent-to-agent text,
  translation prep, UI copy
- **`references/before-after.md`** — worked before/after examples: official STE
  rules applied, and agent-output rewrites

## References

- **ASD-STE100 official site**: https://www.asd-ste100.org/
- **ASD-STE100 — About STE**: https://www.asd-ste100.org/about_STE.html
- **ASD-STE100 — Downloads**: https://www.asd-ste100.org/STE_downloads.html
- **Simplified Technical English — Wikipedia**: https://en.wikipedia.org/wiki/Simplified_Technical_English
- **W3C Cognitive Accessibility**: https://www.w3.org/TR/coga-usable/

Adapted from [wilmai/ste](https://github.com/wilmai/ste), [danyuchn/asd-ste100-skill](https://github.com/danyuchn/asd-ste100-skill), and [mshojaei77/adhd-friendly-ste-technical-writer](https://github.com/mshojaei77/adhd-friendly-ste-technical-writer) (all MIT).
