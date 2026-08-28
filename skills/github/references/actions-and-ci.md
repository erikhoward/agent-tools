# GitHub Actions and CI/CD Workflows

Manage GitHub Actions workflows, runs, and secrets with `gh run`, `gh workflow`, `gh secret`, and `gh variable`.

## Working with Workflow Runs

### List recent runs

```bash
# List all recent runs
gh run list

# Limit results
gh run list --limit 10

# Filter by status
gh run list --status success
gh run list --status failure
gh run list --status completed

# Filter by branch
gh run list --branch main

# Filter by workflow
gh run list --workflow ci.yml
```

**Status options:** `queued`, `in_progress`, `completed`, `success`, `failure`, `cancelled`, `timed_out`

### View run details

```bash
# View specific run
gh run view 12345

# View run logs
gh run view 12345 --log

# View logs for step
gh run view 12345 --log --job <job-id>

# With JSON
gh run view 12345 --json status,conclusion,startedAt
```

### Watch run progress

```bash
# Watch until completion
gh run watch 12345

# With interval
gh run watch 12345 --interval 5
```

### Re-run a failed run

```bash
# Rerun the entire run (all jobs)
gh run rerun 12345

# Rerun failed jobs only
gh run rerun 12345 --failed
```

### Cancel a running workflow

```bash
gh run cancel 12345
```

### Delete a workflow run

```bash
gh run delete 12345
```

### Download artifacts

```bash
# Download all artifacts from run
gh run download 12345

# Download to specific directory
gh run download 12345 --dir ~/artifacts

# Download specific artifact
gh run download 12345 --name "test-results"

# Skip existing
gh run download 12345 --skip-existing
```

---

## Managing Workflows

### List workflows

```bash
# List all workflows
gh workflow list

# Show all (including disabled)
gh workflow list --all
```

### View workflow details

```bash
gh workflow view ci.yml

# With JSON (via workflow list)
gh workflow list --json name,state
```

### Trigger workflow manually

Requires workflow with `workflow_dispatch` trigger:

```bash
# Trigger workflow
gh workflow run ci.yml

# Trigger on specific branch
gh workflow run ci.yml --ref main

# Trigger with inputs
gh workflow run deploy.yml \
  --ref main \
  -f environment=production \
  -f version=1.0.0
```

**Passing inputs:**
- `-f string_input=value` — string input
- `-f number_input=42` — number input
- `-f bool_input=true` — boolean input

### Enable/disable workflow

```bash
# Enable workflow
gh workflow enable ci.yml

# Disable workflow
gh workflow disable ci.yml
```

---

## Workflow File with workflow_dispatch

Create a workflow that can be triggered manually:

`.github/workflows/manual-deploy.yml`:

```yaml
name: Manual Deploy

on:
  workflow_dispatch:
    inputs:
      environment:
        description: "Deployment environment"
        required: true
        default: staging
        type: choice
        options:
          - staging
          - production
      version:
        description: "Version to deploy"
        required: true
        type: string

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to ${{ inputs.environment }}
        run: |
          echo "Deploying version ${{ inputs.version }} to ${{ inputs.environment }}"
```

Then trigger via gh:

```bash
gh workflow run manual-deploy.yml \
  -f environment=production \
  -f version=v1.0.0
```

---

## Secrets Management

### Set a repository secret

```bash
# Interactive
gh secret set DATABASE_URL

# Pass value via stdin
echo "my-secret-value" | gh secret set API_KEY

# Pass value directly
gh secret set API_KEY --body "my-secret-value"

# For specific environment
gh secret set API_KEY --body "prod-key" --env production
```

### List secrets

```bash
# List all secrets (names only, not values)
gh secret list

# For specific environment
gh secret list --env production
```

### Delete a secret

```bash
gh secret delete API_KEY

# For specific environment
gh secret delete API_KEY --env production
```

### Use secrets in workflows

In `.github/workflows/deploy.yml`:

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy
        run: |
          curl -X POST https://api.example.com/deploy \
            -H "Authorization: Bearer ${{ secrets.API_KEY }}"
```

---

## Repository Variables

Store non-sensitive configuration as variables:

### Set a variable

```bash
gh variable set ENV_NAME --body "production"

# For specific environment
gh variable set LOG_LEVEL --body "debug" --env development
```

### List variables

```bash
gh variable list

# For specific environment
gh variable list --env staging
```

### Delete a variable

```bash
gh variable delete ENV_NAME
```

### Use variables in workflows

```yaml
env:
  LOG_LEVEL: ${{ vars.LOG_LEVEL }}
  ENVIRONMENT: ${{ vars.ENVIRONMENT }}

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Log level is
        run: echo "Level: $LOG_LEVEL"
```

---

## GitHub Actions Caches

Manage workflow caches:

### List caches

```bash
gh cache list

# For specific branch
gh cache list --ref refs/heads/main

# Sort by size
gh cache list --sort size_in_bytes --order desc
```

### Delete cache

```bash
# Delete specific cache
gh cache delete <cache-key>

# Delete all caches for branch
gh cache list --ref refs/heads/main --json key --jq '.[].key' | xargs -I {} gh cache delete {}
```

---

## Advanced Patterns

### Monitor workflow runs

A polling loop re-prints the same latest failed run every interval. Check on demand instead, or wait on a specific run:

```bash
# Check recent failed runs on demand
gh run list --status failure --limit 5

# Wait for a specific run to finish (exits non-zero on failure)
gh run watch <run-id> --exit-status
```

### Bulk trigger workflows

```bash
#!/bin/bash
# Trigger workflow on multiple branches

for branch in main develop staging; do
  gh workflow run ci.yml --ref $branch
  echo "Triggered on $branch"
done
```

### Get run statistics

```bash
# Success rate for workflow
TOTAL=$(gh run list --workflow ci.yml --json status | jq 'length')
SUCCESS=$(gh run list --workflow ci.yml --status success --json status | jq 'length')
echo "Success rate: $(( SUCCESS * 100 / TOTAL ))%"
```

### Automated retry on failure

```bash
#!/bin/bash
# Rerun failed workflow until success

RUN_ID=$1
MAX_RETRIES=3
RETRY=0

while [ $RETRY -lt $MAX_RETRIES ]; do
  STATUS=$(gh run view $RUN_ID --json conclusion --jq '.conclusion')
  
  if [ "$STATUS" = "success" ]; then
    echo "Run succeeded!"
    break
  fi
  
  if [ "$STATUS" = "failure" ]; then
    RETRY=$((RETRY + 1))
    echo "Attempt $RETRY: Rerunning..."
    gh run rerun $RUN_ID --failed
    sleep 30
  fi
done
```

### Export run logs

```bash
#!/bin/bash
# Download and archive logs from recent runs

WORKFLOW="ci.yml"
LIMIT=5

gh run list --workflow $WORKFLOW --limit $LIMIT --json number | jq -r '.[] | .number' | while read run; do
  mkdir -p "logs/run-$run"
  gh run view $run --log > "logs/run-$run/output.log"
  echo "Saved logs for run $run"
done
```

### Setup matrix builds with triggers

Matrix builds are GitHub Actions workflow authoring, not gh usage — see the GitHub Actions docs: https://docs.github.com/en/actions

### Secrets for different environments

```bash
# Set production secret
gh secret set DATABASE_URL --body "prod-db" --env production

# Set staging secret
gh secret set DATABASE_URL --body "staging-db" --env staging
```

Use in workflow:

```yaml
jobs:
  deploy-prod:
    environment: production
    steps:
      - run: deploy.sh
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

### Performance monitoring

```bash
#!/bin/bash
# Track workflow execution times

gh run list --workflow ci.yml --limit 20 --json number,startedAt,updatedAt \
  --jq '.[] | {
    number: .number,
    duration_minutes: (((.updatedAt | fromdateiso8601) - (.startedAt | fromdateiso8601)) / 60 | round)
  }'
```