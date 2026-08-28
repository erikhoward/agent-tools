# Complete Git Hooks Reference

Comprehensive guide to all Git hooks, their parameters, and use cases.

## Table of Contents

- [Client-Side Hooks](#client-side-hooks)
  - [Commit Workflow Hooks](#commit-workflow-hooks)
  - [Email Workflow Hooks](#email-workflow-hooks)
  - [Other Client Hooks](#other-client-hooks)
- [Server-Side Hooks](#server-side-hooks)
- [Niche Hooks](#niche-hooks)
- [Hook Parameters Quick Reference](#hook-parameters-quick-reference)

## Client-Side Hooks

Client-side hooks run on developer machines. `--no-verify` only skips specific hooks: `git commit --no-verify` skips `pre-commit` and `commit-msg`; `git push --no-verify` skips `pre-push`.

### Commit Workflow Hooks

#### pre-commit

**When**: Before commit message editor opens  
**Purpose**: Validate staged changes, run linters, check code style  
**Parameters**: None  
**stdin**: None  
**Can abort**: Yes (exit non-zero)

**Common uses**:
- Run linters (ESLint, Prettier, Black)
- Check code syntax
- Validate file formats
- Run quick unit tests
- Check for debugging statements
- Verify no large files are staged

**Example**:
```bash
#!/bin/bash
set -e

# Lint staged JavaScript files
STAGED_JS=$(git diff --cached --name-only --diff-filter=ACM | grep '\.js$' || true)

if [ -n "$STAGED_JS" ]; then
    echo "$STAGED_JS" | xargs eslint || exit 1
fi

exit 0
```

**Access staged files**:
```bash
# All staged files
git diff --cached --name-only

# Staged files by extension
git diff --cached --name-only --diff-filter=ACM | grep '\.py$'

# Staged files with content
git diff --cached
```

#### prepare-commit-msg

**When**: After default message generated, before editor opens  
**Purpose**: Modify commit message template automatically  
**Parameters**:
1. `$1` - Path to commit message file (read/write)
2. `$2` - Commit message source (`message`, `template`, `merge`, `squash`, `commit`)
3. `$3` - Commit SHA (only if `-c`, `-C`, or `--amend`)

**stdin**: None  
**Can abort**: Yes

**Common uses**:
- Add issue tracker references from branch name
- Insert template based on commit type
- Add co-author lines
- Include affected components

**Example**:
```bash
#!/bin/bash

COMMIT_MSG_FILE=$1
SOURCE=$2

# Extract issue number from branch name
BRANCH=$(git symbolic-ref --short HEAD)
ISSUE=$(echo "$BRANCH" | grep -oE '[A-Z]+-[0-9]+')

if [ -n "$ISSUE" ] && [ "$SOURCE" != "message" ]; then
    # Prepend issue number to existing message
    ORIGINAL=$(cat "$COMMIT_MSG_FILE")
    echo "$ISSUE: $ORIGINAL" > "$COMMIT_MSG_FILE"
fi

exit 0
```

**Commit sources**:
- `message` - User provided with `-m` flag
- `template` - Loaded from template file
- `merge` - Automatic merge commit message
- `squash` - Squash commit message
- `commit` - Using `-c`, `-C`, or `--amend`

#### commit-msg

**When**: After user enters commit message  
**Purpose**: Validate commit message format  
**Parameters**:
1. `$1` - Path to commit message file (read/write)

**stdin**: None  
**Can abort**: Yes

**Common uses**:
- Enforce commit message conventions (Conventional Commits, Angular style)
- Check message length limits
- Validate issue tracker references
- Ensure ticket numbers present
- Spell check commit messages

**Example - Conventional Commits**:
```bash
#!/bin/bash

MSG_FILE=$1
COMMIT_MSG=$(head -n1 "$MSG_FILE")

# Canonical pattern, kept in sync with the parent SKILL.md / git-commit skill (Conventional Commits 1.0.0)
PATTERN='^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([^)]+\))?!?: .{1,72}$'

if ! echo "$COMMIT_MSG" | grep -qE "$PATTERN"; then
    cat <<EOF
❌ Invalid commit message format

Expected: type(scope)!: description (subject max 72 chars, first line only)

Types:
  feat:     New feature
  fix:      Bug fix
  docs:     Documentation changes
  style:    Code style changes (formatting, semicolons, etc)
  refactor: Code refactoring
  perf:     Performance improvements
  test:     Adding or updating tests
  build:    Build system or dependency changes
  ci:       CI configuration changes
  chore:    Maintenance tasks
  revert:   Revert a previous commit

Example: feat(auth): add OAuth2 login support
Breaking: feat(api)!: remove deprecated endpoints
EOF
    exit 1
fi

exit 0
```

#### post-commit

**When**: After commit is created  
**Purpose**: Notifications, logging  
**Parameters**: None  
**stdin**: None  
**Can abort**: No (commit already created)

**Common uses**:
- Send notifications (Slack, email)
- Update project documentation
- Log commit statistics
- Trigger local builds
- Update issue tracker

**Example**:
```bash
#!/bin/bash

# Get commit info
COMMIT_SHA=$(git rev-parse HEAD)
COMMIT_MSG=$(git log -1 --pretty=%B)
AUTHOR=$(git log -1 --pretty=%an)

# Send notification
curl -X POST https://hooks.slack.com/services/YOUR/WEBHOOK/URL \
    -H 'Content-Type: application/json' \
    -d "{\"text\":\"New commit by $AUTHOR: $COMMIT_MSG\"}"

exit 0
```

### Email Workflow Hooks

#### applypatch-msg

**When**: Before `git am` applies patch  
**Purpose**: Validate patch commit message  
**Parameters**:
1. `$1` - Path to proposed commit message

**stdin**: None  
**Can abort**: Yes

**Common uses**:
- Ensure patches meet commit message standards
- Add trailers (Signed-off-by, Reviewed-by)

#### pre-applypatch

**When**: After patch applied, before commit created  
**Purpose**: Inspect or test the tree  
**Parameters**: None  
**stdin**: None  
**Can abort**: Yes

**Common uses**:
- Run tests on incoming patches
- Validate patch doesn't break build

#### post-applypatch

**When**: After patch applied and committed  
**Purpose**: Notifications  
**Parameters**: None  
**stdin**: None  
**Can abort**: No

### Other Client Hooks

#### pre-rebase

**When**: Before rebasing  
**Purpose**: Prevent dangerous rebases  
**Parameters**:
1. `$1` - Upstream branch being rebased onto
2. `$2` - Branch being rebased (empty if rebasing current branch)

**stdin**: None  
**Can abort**: Yes

**Common uses**:
- Prevent rebasing published branches
- Warn about rebasing onto wrong branch
- Check for uncommitted changes

**Example**:
```bash
#!/bin/bash

UPSTREAM=$1
BRANCH=${2:-$(git symbolic-ref --short HEAD)}

# Prevent rebasing main branch
if [ "$BRANCH" = "main" ] || [ "$BRANCH" = "master" ]; then
    echo "❌ Rebasing main branch is not allowed"
    exit 1
fi

# Check if branch has been pushed
if git rev-parse --verify "origin/$BRANCH" >/dev/null 2>&1; then
    echo "⚠️  Warning: Branch has been pushed to remote"
    echo "Rebasing published branches can cause problems for collaborators"
    read -p "Continue anyway? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

exit 0
```

#### post-rewrite

**When**: After commands that rewrite commits (`git commit --amend`, `git rebase`)  
**Purpose**: Update references, logs  
**Parameters**:
1. `$1` - Command that triggered rewrite (`amend` or `rebase`)

**stdin**: One line per rewritten commit:
```
<old-sha> <new-sha>
```

**Can abort**: No

**Example**:
```bash
#!/bin/bash

COMMAND=$1

while read old_sha new_sha; do
    echo "Commit $old_sha rewritten to $new_sha by $COMMAND"
    # Update custom tracking, logs, etc.
done

exit 0
```

#### post-checkout

**When**: After `git checkout` or `git switch`  
**Purpose**: Adjust working directory, clean up generated files  
**Parameters**:
1. `$1` - Ref of previous HEAD
2. `$2` - Ref of new HEAD
3. `$3` - Branch checkout flag (1 for branch, 0 for file)

**stdin**: None  
**Can abort**: No

**Common uses**:
- Clean up build artifacts
- Update dependencies
- Switch environment configs
- Remove generated files

**Example**:
```bash
#!/bin/bash

PREV_HEAD=$1
NEW_HEAD=$2
IS_BRANCH=$3

if [ "$IS_BRANCH" = "1" ]; then
    echo "Checked out branch"
    
    # Clean Python bytecode
    find . -name '*.pyc' -delete
    find . -name '__pycache__' -type d -exec rm -rf {} +
    
    # Update dependencies if package.json changed
    if git diff --name-only "$PREV_HEAD" "$NEW_HEAD" | grep -q 'package.json'; then
        echo "package.json changed, updating dependencies..."
        npm install
    fi
fi

exit 0
```

#### pre-merge-commit

**When**: Before a merge commit is created, after merge conflicts have been resolved  
**Purpose**: Validate the merge result before the merge commit is created  
**Parameters**: None  
**stdin**: None  
**Can abort**: Yes (exit non-zero; bypass with `git merge --no-verify`)

**Common uses**:
- Check for required build artifacts (e.g., generated code must be up to date)

**Example**:
```bash
#!/bin/bash

# Fail if generated code is stale before the merge commit is created
if ! ./scripts/check-generated-code.sh; then
    echo "❌ Generated code is stale — regenerate before merging"
    exit 1
fi

exit 0
```

#### post-merge

**When**: After successful merge  
**Purpose**: Update dependencies, restore permissions  
**Parameters**: 
1. `$1` - Squash merge flag (1 if squash merge, 0 otherwise)

**stdin**: None  
**Can abort**: No

**Common uses**:
- Update dependencies after merge
- Restore file permissions
- Clean up conflicts markers
- Rebuild project

**Example**:
```bash
#!/bin/bash

SQUASH=$1

# Check if package files changed
FILES_CHANGED=$(git diff-tree -r --name-only --no-commit-id ORIG_HEAD HEAD)

if echo "$FILES_CHANGED" | grep -qE 'package\.json|package-lock\.json'; then
    echo "Dependencies changed, running npm install..."
    npm install
fi

if echo "$FILES_CHANGED" | grep -q 'requirements.txt'; then
    echo "Python dependencies changed, updating..."
    pip install -r requirements.txt
fi

exit 0
```

#### pre-push

**When**: Before pushing to remote  
**Purpose**: Validate commits, run tests, prevent force push  
**Parameters**:
1. `$1` - Remote name (e.g., `origin`)
2. `$2` - Remote URL

**stdin**: One line per ref being pushed:
```
<local-ref> <local-sha> <remote-ref> <remote-sha>
```

**Can abort**: Yes

**Common uses**:
- Run test suite before push
- Prevent force push to protected branches
- Validate commit messages
- Check for TODOs or debug code
- Ensure all tests pass

**Example - Prevent force push** (condensed; full annotated version in the parent SKILL.md, "Preventing Force Push to Main"):
```bash
#!/bin/bash

while read local_ref local_sha remote_ref remote_sha; do
    remote_branch=$(echo "$remote_ref" | sed 's|refs/heads/||')

    if echo "$remote_branch" | grep -qE '^(main|master|production|staging)$'; then
        # Reject branch deletion
        if [ "$local_sha" = "0000000000000000000000000000000000000000" ]; then
            echo "❌ Deleting $remote_branch is not allowed"
            exit 1
        fi

        # Reject force push (non-fast-forward); remote_sha is all zeros for new branches
        if [ "$remote_sha" != "0000000000000000000000000000000000000000" ] && \
           ! git merge-base --is-ancestor "$remote_sha" "$local_sha"; then
            echo "❌ Force push to $remote_branch is not allowed"
            exit 1
        fi
    fi
done

exit 0
```

**Example - Run tests**:
```bash
#!/bin/bash

echo "🧪 Running tests before push..."

npm test || {
    echo "❌ Tests failed. Fix tests before pushing."
    exit 1
}

echo "✅ All tests passed"
exit 0
```

## Server-Side Hooks

Server-side hooks run on the remote repository and cannot be bypassed by clients.

Server-side hooks (pre-receive, update, post-receive, post-update) are documented in depth in references/server-side-hooks.md.

## Niche Hooks

- `pre-auto-gc` - Runs before automatic garbage collection (`git gc --auto`)
- `reference-transaction` - Runs when a reference transaction is prepared, committed, or aborted
- `push-to-checkout` - Runs on the server when a push updates the currently checked-out branch (`receive.denyCurrentBranch = updateInstead`)
- `post-index-change` - Runs after the index changes (except via `git status`)
- `fsmonitor-watchman` - Integrates the Watchman file monitor to speed up `git status`
- `proc-receive` - Handles pushes to special refs (e.g., Gerrit-style `refs/for/...`)
- `sendemail-validate` - Validates recipient addresses before `git send-email` sends

## Hook Parameters Quick Reference

| Hook | Parameters | stdin | Can Abort |
|------|-----------|-------|-----------|
| `pre-commit` | None | None | Yes |
| `prepare-commit-msg` | msg_file, source, sha | None | Yes |
| `commit-msg` | msg_file | None | Yes |
| `post-commit` | None | None | No |
| `applypatch-msg` | msg_file | None | Yes |
| `pre-applypatch` | None | None | Yes |
| `post-applypatch` | None | None | No |
| `pre-rebase` | upstream, branch | None | Yes |
| `post-rewrite` | command | old-new pairs | No |
| `post-checkout` | prev_head, new_head, flag | None | No |
| `pre-merge-commit` | None | None | Yes |
| `post-merge` | squash_flag | None | No |
| `pre-push` | remote_name, url | ref pairs | Yes |
| `pre-receive` | None | ref triples | Yes |
| `update` | ref, old_sha, new_sha | None | Yes |
| `post-receive` | None | ref triples | No |
| `post-update` | refs... | None | No |

## Testing Hooks

For full debug snippets, see the parent SKILL.md ("Testing Individual Hooks", "Environment Variables"). Quick one-liners:

```bash
GIT_TRACE=1 git commit -m "test"   # trace hook execution
env | grep GIT                     # dump Git-related environment variables
```