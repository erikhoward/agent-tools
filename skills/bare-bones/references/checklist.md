# Verification Checklist

Mechanical, countable, and judgment checks for a draft, plus a precision audit
against the source. Core conventions live in `../SKILL.md`.

## Mechanical checks (searchable)

Search the draft for each pattern. Every hit outside code blocks and quoted text
is a violation.

| Search for | Violation | Fix |
|---|---|---|
| `'ll`, `'re`, `'ve`, `n't`, `it's` | Contraction (Rule 4.2) | Expand it |
| `has been`, `have been`, `had been` | Present/past perfect (Rule 3.4) | Simple past or simple present |
| `has` / `have` + past participle | Present perfect (Rule 3.4) | Simple past |
| `should`, `would`, `may`, `might`, `could` | Unapproved modal (Rule 3.2) | See the modal ladder in `../SKILL.md` |
| `is being`, `are being`, `was being` | Progressive passive (Rules 3.4, 3.5) | Active, simple tense |
| `, making`, `, allowing`, `, enabling`, `, ensuring` | "-ing" clause as verb (Rule 3.5) | New sentence with a real subject |
| `;` | Semicolon (Rule 8.1) | Two sentences |
| `e.g.`, `i.e.`, `etc.` | Latin abbreviation (GR-6) | "for example", "that is", name the items |
| `simply`, `easily`, `seamlessly`, `robust` | Filler (no fact) | Delete |
| ` if `, ` when ` (mid-sentence) | Trailing condition (Rule 5.4) | Move the condition to the start, add a comma |
| `perform`, `conduct`, `provide` + noun | Nominalization (Rule 3.7) | Use the verb: "compress the file" |
| `spin up`, `stand up`, `reach out`, `dive into` | Phrasal verb (Rule 9.3) | Single plain verb |

## Countable checks

1. **Sentence length.** Procedural limit 20, descriptive 25, notes 25.
   Backticked commands, numbers with units, and identifiers count as one word
   each (Rule 8.6).
2. **Paragraph size.** Maximum 6 sentences per paragraph (Rule 6.6).
3. **Noun chains.** Any chain over 3 words → break it with prepositions
   (Rule 2.1).
4. **Instructions per sentence.** One, unless the actions are simultaneous
   (Rule 5.2).

## Judgment checks

1. **Classification.** Is each passage cleanly procedural or descriptive?
   Procedures imperative, descriptions never imperative.
2. **Voice.** Any passive sentence: is the actor truly unknown, and is the
   passage descriptive? Otherwise make it active (Rule 3.6).
3. **Condition placement.** Every `if`/`when` stands before its command, with a
   comma (Rule 5.4).
4. **Synonym rotation.** One term per concept across the whole document
   (Rules 1.11, 9.4). Scan for check/verify/confirm, config/settings,
   run/execute.
5. **Warnings.** Risk word first, then the command or condition, then the risk
   (Rules 7.1–7.3).
6. **Step order.** In a procedure, does each step leave the system in a safe
   state? If the safe order differs from the order you were given, use the safe
   order and say so.
7. **Completeness.** Articles present, "that" present after "make sure", no
   telegraph style (Rule 4.2).
8. **Untouchables intact.** Code, identifiers, quoted errors, and proper nouns
   are unchanged.
9. **Grammar over rulings.** No part-of-speech ruling may produce ungrammatical
   English. If it does, restructure (Rule 9.1).

## Precision audit (run last)

Compare the draft against the source, fact by fact. Confirm each of these
survived the rewrite:

- every safety condition and precondition
- every scope qualifier (version, region, platform, plan tier)
- every number, unit, threshold, and date
- every exception and edge case
- every named actor, where who acts matters

Anything dropped goes back in. Anything kept in violation of a rule goes in the
`What I did not simplify` block, one line per item: the fact, the rule broken,
the reason. Omit the block when the rewrite is clean.

## When reporting violations (check mode)

For each violation give: the rule number, the offending text, and a compliant
rewrite. Cite only rule numbers that appear in `../SKILL.md`.

End the report with this statement when the user asked for STE compliance: "No
tool can guarantee ASD-STE100 compliance. Final approval rests with the writer.
Confirm each rule number against the official standard, a free download at
asd-ste100.org."

Adapted from [wilmai/ste](https://github.com/wilmai/ste) (MIT).
