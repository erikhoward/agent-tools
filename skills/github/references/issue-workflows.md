# Issue Management Workflows

Comprehensive guide to creating, triaging, and managing issues with `gh issue`.

## Creating Issues

### Basic creation

```bash
gh issue create --title "Login button broken on mobile"
```

Prompts for body if not provided.

### Create with full details

```bash
gh issue create \
  --title "Bug: Parser fails on empty input" \
  --body "## Description\nThe parser crashes when given empty string.\n\n## Steps to Reproduce\n1. Call parser('')\n2. See crash\n\n## Expected\nShould return empty result" \
  --label bug,critical \
  --assignee @me \
  --milestone "v2.0"
```

**Flag reference:**
- `--title <text>` — issue title (required or prompted)
- `--body <text>` — issue body/description
- `--body-file <file>` — read body from file
- `--label <name>` — add label (repeatable)
- `--assignee <login>` — assign user (repeatable, `@me` = self)
- `--milestone <name>` — add to milestone
- `--template <name>` — use issue template
- `--web` — open in browser instead of creating
- `--editor` — open text editor for title + body
- `--project <title>` — add to project

### Using issue templates

Your repo may have issue templates in `.github/ISSUE_TEMPLATE/`:

```bash
# List available templates
ls .github/ISSUE_TEMPLATE/

# Create from template
gh issue create --template bug_report

# Or
gh issue create --template feature_request --title "Dark mode"
```

### Create from file

```bash
# Read body from file
gh issue create --title "New issue" --body-file issue-body.md

# Or from stdin
cat issue-body.md | gh issue create --title "New issue" --body-file -
```

---

## Viewing & Listing Issues

### List with filters

```bash
# Open issues (default)
gh issue list

# All states
gh issue list --state all

# Closed issues only
gh issue list --state closed

# By assignee
gh issue list --assignee @me
gh issue list --assignee alice

# By label
gh issue list --label bug
gh issue list --label bug --label critical

# By milestone
gh issue list --milestone "v2.0"

# Search
gh issue list --search "is:open author:@me"

# Limit results
gh issue list --limit 50
```

**Filter flags:**
- `--state <open|closed|all>` — default: open
- `--assignee <user>` — filter by assignee
- `--author <user>` — filter by creator
- `--label <name>` — filter by label (repeatable)
- `--milestone <name>` — filter by milestone
- `--search <query>` — advanced search syntax
- `--limit <n>` — max results (default: 30)
- `--web` — open list in browser

### View issue details

```bash
# View by number
gh issue view 42

# View by URL
gh issue view https://github.com/owner/repo/issues/42

# With comments
gh issue view 42 --comments

# As JSON
gh issue view 42 --json number,title,state,assignees,labels
```

---

## Editing Issues

### Edit title and body

```bash
gh issue edit 42 --title "Updated title"
gh issue edit 42 --body "New description"
gh issue edit 42 --body-file updated.md
```

### Edit metadata

```bash
# Add/remove assignee
gh issue edit 42 --add-assignee alice
gh issue edit 42 --remove-assignee alice

# Add/remove labels
gh issue edit 42 --add-label bug --add-label critical
gh issue edit 42 --remove-label bug

# Set milestone
gh issue edit 42 --milestone "v3.0"
```

### Bulk edit with JSON

```bash
# Update all open issues from @me to alice
gh issue list --assignee @me --json number | \
  jq -r '.[] | .number' | \
  xargs -I {} gh issue edit {} --add-assignee alice --remove-assignee @me
```

---

## Triaging Issues

### Close an issue

```bash
gh issue close 42
```

### Reopen a closed issue

```bash
gh issue reopen 42
```

### Add comment

```bash
gh issue comment 42 --body "This is a duplicate of #40"
```

### Lock conversation (prevent comments)

```bash
gh issue lock 42
```

### Unlock

```bash
gh issue unlock 42
```

### Pin issue (highlight in repo)

```bash
gh issue pin 42
```

### Unpin

```bash
gh issue unpin 42
```

---

## Linking Branches to Issues

### Link a branch to an issue

```bash
# Create the issue, then create a linked branch (develop is a separate subcommand)
gh issue create --title "Implement feature"
gh issue develop <issue-number>
# Default branch name: <issue-number>-<slugified-title>; customize with -n, --name
```

### Manage linked branches

```bash
# List branches linked to an issue
gh issue develop 42 --list

# Create a linked branch with a custom name
gh issue develop 42 --name feature/my-work

# Unlink branch
# Not directly via gh; use web UI
```

---

## Advanced Patterns

### Bulk create issues from template

```bash
# Create 5 issues
for i in {1..5}; do
  gh issue create --template bug_report --title "Bug #$i"
done
```

### List issues by status using JSON

```bash
# Issues without assignee
gh issue list --json number,title,assignees --jq '.[] | select(.assignees == []) | "#\(.number) \(.title)"'

# Issues with specific label
gh issue list --json number,title,labels --jq '.[] | select(.labels[].name | contains("critical")) | "#\(.number) \(.title)"'

# Count issues by label
gh issue list --json labels --jq '[.[].labels[].name] | group_by(.) | map({label: .[0], count: length})'
```

### Bulk close issues with pattern

```bash
# Close all issues with "wontfix" label
gh issue list --label wontfix --json number | \
  jq -r '.[] | .number' | \
  xargs -I {} gh issue close {}
```

### Auto-close via PR

Link issue in PR description:

```bash
gh pr create \
  --title "Fix parser" \
  --body "Closes #42

This PR resolves the issue by refactoring the parser logic."
```

When the PR merges, issue #42 automatically closes.

### Export issues to CSV

```bash
gh issue list --state all --json number,title,state,assignees,labels,createdAt \
  --jq '.[] | [.number, .title, .state, ([.assignees[].login] | join(";")), ([.labels[].name] | join(";")), .createdAt] | @csv'
```

### Filter issues by creation date

```bash
# Issues created in the last 7 days
SEVEN_DAYS_AGO=$(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%SZ)  # GNU/Linux
SEVEN_DAYS_AGO=$(date -u -v-7d +%Y-%m-%dT%H:%M:%SZ)             # macOS
gh issue list --state all --json number,title,createdAt \
  --jq ".[] | select(.createdAt > \"$SEVEN_DAYS_AGO\") | \"#\(.number) \(.title)\""
```

### Monitor issue updates

No polling loop needed — `gh issue list` and `gh issue view` are cheap to call on demand.

---

## Issue Templates

For authoring issue templates (classic markdown and issue forms), see GitHub's issue-forms documentation: https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms

---

## Transfer Issue to Another Repository

```bash
# Move issue to another repo
gh issue transfer 42 owner/other-repo
```

This is useful for managing cross-repo issues.