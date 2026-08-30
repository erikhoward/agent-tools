---
description: Push committed changes to remote — never stages or commits anything
agent: build
---

# Push the committed (but not yet pushed) changes to the remote repository

**HARD CONSTRAINT**: This command only pushes. It MUST NOT stage files, create commits, amend commits, or modify the working tree or index in any way. If there is nothing to push, say so and stop.

## Step 1: Check Repository State

!`git status --short`
!`git branch -vv`
!`git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null || echo "NO_UPSTREAM"`
!`git log --oneline @{u}..HEAD 2>/dev/null`

Interpret:

- **No upstream** (the upstream check printed `NO_UPSTREAM`): respond with the
  local branch name and ask whether to set upstream and push with
  `git push -u origin <branch>`. If yes, skip to Step 6.
- **Upstream set, but no unpushed commits** (the log is empty): respond:

```text
Nothing to push. Your local branch is already up to date with the remote.

To create commits first, use:
  /git-commit        — commit already-staged changes
  /git-commit-push   — commit staged changes and push in one step
```

Stop.

## Step 2: Scan Commits for Anomalies

Check files in unpushed commits:

**Large files (>1 MB):**
!`git log @{u}..HEAD --name-only --pretty=format:"" 2>/dev/null | sort -u | grep -v "^$" | xargs -I{} find {} -maxdepth 0 -size +1M 2>/dev/null`

**Suspicious filenames:**
!`git log @{u}..HEAD --name-only --pretty=format:"" 2>/dev/null | sort -u | grep -v "^$" | grep -Ei "\.env$|\.env\.|credentials|secrets|\.pem$|\.key$|\.p12$|\.pfx$|id_rsa|id_dsa|id_ecdsa|\.password|api_key|token" | head -20`

**Secret-like patterns:**
!`git diff @{u}..HEAD 2>/dev/null | grep -Ei "(password|secret|api_key|access_token|private_key|client_secret)\s*[:=]\s*['\"]?[A-Za-z0-9+/]{8,}" | head -10`

If anomalies found, include warnings in summary.

## Step 3: Present Summary and Ask for Confirmation

```text
## Push Summary

### Commits to Push
[List each unpushed commit: hash — subject line]

### Target
- Branch : [local branch name]
- Remote : [remote name, e.g. origin]
- URL    : [remote URL]

### Anomaly Check
- Large files (>1 MB) : [list or "None"]
- Suspicious filenames: [list or "None"]
- Secret-like content : [list or "None"]
```

If anomalies found, add warning block before asking.

Ask:

```text
Proceed with git push? (yes / no)
```

Wait for response.

- If yes: proceed to Step 4.
- If no: stop and inform push cancelled.

## Step 4: Check if Remote Has Diverged

Check if remote has commits local does not:
!`git fetch`
!`git log --oneline HEAD..@{u} 2>/dev/null`

If shows commits, rebase required. Proceed to Step 5. Otherwise skip to Step 6.

## Step 5: Rebase onto Remote (if required)

Rebasing rewrites local history — it needs its own confirmation, separate from
the push approval in Step 3. Ask:

```text
Remote has [N] new commit(s). Rebase your local commits on top before pushing? (yes / no)
```

- If yes, rebase local commits on top:
  1. Run `git rebase @{u}`.
  2. If clean, confirm:

     ```text
     Rebase complete. Local commits replayed on top of [remote]/[branch].
     ```

     Proceed to Step 6.
  3. If conflicts:
     - Show conflicting files: `git diff --name-only --diff-filter=U`
     - Present conflicts to user.
     - Resolve in affected files.
     - Stage resolutions: `git add <resolved-files>`
     - Continue: `git rebase --continue`
     - Repeat until complete.
     - Abort if user wants: `git rebase --abort`
- If no: stop and inform the user the push was cancelled. Suggest they pull
  or merge manually if they prefer not to rebase.

Additional rules:

- Do not use `git rebase -i`. Use plain `git rebase @{u}`.
- Do not amend or squash unless explicitly asked.

## Step 6: Push

1. Run `git push`.
2. If rejected after rebase:
   - Show error.
   - Explain cause.
   - Ask what to do.
   - Never force push unless explicitly asked and not main/master. If asked for main/master, warn and confirm twice.
3. If succeeds:

   ```text
   Pushed: [branch] -> [remote]/[branch]  ([N] commit(s))
   ```

4. If fails otherwise:

   - Show error.
   - Suggest remediation.
   - Do not retry.