---
description: Commit staged changes, then push — runs both workflows in sequence
agent: build
subtask: true
---

# Commit staged changes, then push them to the remote

Run two workflows in sequence. Both confirmations are still required — this
command never skips the gates.

## Phase 1 — Commit

Follow the `/git-commit` command workflow exactly: check staged changes, scan
for anomalies, propose a conventional commit message, get confirmation, commit.

If there is nothing to stage or the user cancels, stop — do not push.

## Phase 2 — Push

After a successful commit, follow the `/git-push` command workflow exactly:
check for unpushed commits, scan them for anomalies, present the push summary,
get confirmation, handle divergence (with its own rebase confirmation), push.

If the user cancels the push, the commit stays — inform them it is local only
and can be pushed later with `/git-push`.

## Constraints

- Same constraints as both underlying commands: never `--no-verify` or
  `--no-gpg-sign`, never stage additional files, never force push unless
  explicitly asked (and never lightly on main/master).
- Stop at the first cancelled confirmation. Do not batch or soften the gates
  because this is a combined command.
