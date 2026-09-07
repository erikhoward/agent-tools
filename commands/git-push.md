---
description: Review and push committed changes without modifying commits, the index, or working tree
agent: build
subtask: true
---

# Push Committed Changes

This command only pushes. It must not stage, commit, amend, rebase, merge, reset, or modify the working tree or index.

1. Inspect status, current branch, remotes, upstream, and local commits at runtime. Do not guess a target.
2. Fetch the selected remote without changing local commits. Refresh divergence and the exact outgoing commit range.
3. If the remote has commits that local HEAD lacks, report divergence and stop. Offer a separate synchronization workflow. Do not resolve it here.
4. If no upstream exists, identify the proposed remote branch and derive the outgoing range from its actual remote state. Stop if the range is uncertain.
5. Inspect every outgoing commit and its committed blobs, not only the endpoint diff. Use a configured secret scanner when available. Otherwise perform a focused, redacted credential and large-object check. A secret added and later removed still blocks the push. State scan limits.
6. Present target, remote URL, exact commits, and warnings. Ask for explicit push approval.
7. Refresh remote state before execution. If target, range, or divergence changed, show the new summary and ask again.
8. Run the normal push, using `-u` only for the approved new upstream. Never force push unless the user explicitly asks and separately confirms the exact rewritten range. Do not force push protected branches.

On failure, show the error and stop. Do not retry or mutate history.
