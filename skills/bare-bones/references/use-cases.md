# Use Cases

Adaptations of the core rules to text types beyond aircraft manuals. Each case
names the mode and the key changes. Core conventions live in `../SKILL.md`.

## Error messages and CLI output

Mode: procedural. An error message is a 2 a.m. instruction to a stressed reader.

Pattern: state what happened (simple past), state the cause if known, give the
fix as an imperative.

**Before:** Oops! Something went wrong while attempting to establish a connection. Please ensure your credentials are properly configured and try again.
**After:** Connection to the database failed. The password for user `app` was not correct. Set `DB_PASSWORD` and connect again.

Never invent the cause. If the cause is unknown, say what the program did and
what the reader can inspect: "The upload failed after three retries. Read the
log at `/var/log/mailgate.log`."

## Runbooks and standard operating procedures

Mode: strict procedural. This is STE's home turf — an on-call runbook is a
maintenance manual.

- Every step imperative, one instruction per step, conditions first.
- Warnings before the step: risk word first, then the command, then the risk.
- 20-word limit enforced hard — an operator under pager stress reads each
  sentence once.
- Order steps so the system is in a safe state after every step. If the order
  you were given breaks this, use the safe order, open with the warning, and
  report the change.

## Incident reports and postmortems

Mode: descriptive. Simple past only — a timeline in present perfect hides when
things happened.

**Before:** We have identified an issue that may have impacted some users' ability to access the service.
**After:** Between 14:02 and 14:31 UTC, 12% of requests failed. A deploy at 14:00 removed the cache warmup step.

STE bans hedges that invent certainty. Do not let the ban turn an uncertain cause
into a certain one: "The cause is unknown" is the compliant sentence.

## Commit messages and PR descriptions

Mode: descriptive body, imperative subject. Convention already matches STE:
imperative subject line, plain past facts in the body. Apply the substitution
table and the 25-word limit to the body. Delete "this PR aims to".

## API changelogs and release notes

Mode: descriptive. One entry, one change, one sentence where possible.
"Breaking:" entries follow the warning pattern — command first: "Update your
calls to `v2/users`. The `name` field split into `first_name` and `last_name`."

Keep every version number, deprecation date, and affected endpoint. These are
exactly the facts a shorter sentence tends to lose.

## Instructions for AI agents

Mode: procedural. A system prompt is a procedure for a reader that cannot ask
questions.

- One instruction per sentence keeps rules independently quotable and hard to
  half-follow.
- One word, one meaning stops the model treating "check", "verify", and
  "validate" as three operations.
- Condition-first ("If the build fails, stop") beats trailing conditions, which
  models drop.
- No "should" — a model reads "should" as optional. Write "must" or delete the
  rule.

## Agent-to-agent text

Mode: descriptive, with procedural rules for anything the receiver must act on.
The receiver has no back-channel to ask "did you mean X or Y".

- Name the actor in every sentence. "The tool returns the artifact", not "the
  artifact is returned".
- Give every pronoun an explicit referent, or repeat the noun. Prefer "this
  response" over bare "this".
- One instruction per sentence, so a receiver that follows half the message
  still follows whole instructions.
- State the failure branch as its own sentence: "If the strategy does not allow
  automatic resolution, the tool reports the conflict."

## Support macros and status-page updates

Mode: descriptive, 25-word limit. Non-native readers are the majority of many
user bases. No "we sincerely apologize for any inconvenience this may have
caused" — "The API was down for 18 minutes. Uploads made during this time were
saved and will process today."

## Translation and localization prep

Mode: strict. STE's original purpose was making English readable for non-native
maintenance crews, and it doubles as pre-editing for machine translation. One
meaning per word plus complete grammar removes most translation ambiguity. If
your docs get localized, STE cuts the error rate and the cost.

## UI copy and empty states

Mode: procedural, hard length limits. Buttons and labels are technical names
(exempt). Body copy follows the rules: "No projects yet. Create a project to
start." Nothing else survives at this length anyway.

## Where STE does not fit

Marketing pages, launch posts, blog voice, brand writing. STE deletes persuasion
on purpose. Write those in your own voice — then use STE for the docs the landing
page links to.

Adapted from [wilmai/ste](https://github.com/wilmai/ste) (MIT).
