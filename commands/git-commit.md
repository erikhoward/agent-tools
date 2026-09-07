---
description: Review and commit only the staged snapshot with an approved conventional message
agent: build
subtask: true
---

# Commit Staged Changes

This command can create one commit. It must not stage, amend, or push.

1. Inspect `git status --short`, the complete staged diff, staged object sizes, and recent messages at runtime. If the index is empty, stop.
2. Use a repository-configured secret scanner when available. Otherwise inspect staged filenames and added staged content for focused credential indicators. Redact values. Explain that this is not a complete secret scan. Block a confirmed secret.
3. Summarize the staged behavior and exceptions. Load `git-commit` to propose a message.
4. Ask the user to commit, edit the message, or cancel. Wait for explicit approval.
5. Recheck the staged snapshot. If it changed, show the change and ask again.
6. Respect signing and hooks. Do not use bypass flags unless the user explicitly requests them after seeing the failure.
7. Run `git commit` with the approved message. On hook or signing failure, show the output and stop. Do not retry automatically.
8. If the result is uncertain, compare HEAD and the index with their pre-command state before claiming success or retrying.

On success, report the commit hash and subject. Do not push.
