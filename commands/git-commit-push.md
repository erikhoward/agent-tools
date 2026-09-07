---
description: Commit the approved staged snapshot, then review and separately approve its push
agent: build
subtask: true
---

# Commit Then Push

Run the `/git-commit` workflow first. If nothing is staged, the commit fails, or the user cancels, stop without pushing.

After a successful commit, run the `/git-push` workflow from a fresh repository-state check. Commit approval does not approve push. Ask for separate push approval.

If push is cancelled or blocked, report that the commit remains local. Preserve every constraint from both workflows. Never stage extra files, bypass signing or hooks without explicit authorization, synchronize divergence, or force push by default.
