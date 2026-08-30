# CI/CD Integration with Git Hooks

Integrate Git hooks with continuous integration and deployment pipelines for streamlined automation.

## Overview

Git hooks complement CI/CD systems by providing:
- **Local validation** before pushing (pre-push hooks)
- **Server-side enforcement** when receiving code (pre-receive hooks)
- **CI trigger automation** after successful pushes (post-receive hooks)

## Architecture Patterns

### Pattern 1: Local Pre-flight Checks

Run subset of CI checks locally before pushing.

```bash
#!/bin/bash
# .githooks/pre-push

echo "🚀 Running pre-flight CI checks locally"

# Quick validation that mirrors CI
quick_ci_check() {
    # Lint (fast)
    npm run lint || return 1
    
    # Unit tests only (medium)
    npm run test:unit || return 1
    
    # Build check (validates config)
    npm run build:check || return 1
    
    return 0
}

if ! quick_ci_check; then
    cat <<EOF
❌ Pre-flight checks failed

These checks mirror your CI pipeline. Fix issues before pushing.

Skip with: git push --no-verify (not recommended)
EOF
    exit 1
fi

echo "✅ Pre-flight checks passed"
exit 0
```

### Pattern 2: Server-Side CI Trigger

Automatically trigger CI/CD pipeline on push.

```bash
#!/bin/bash
# hooks/post-receive (on server)

trigger_production_ci() {
    local commit=$1
    
    echo "🚀 Triggering production CI for $commit"
    
    curl -X POST "https://ci.example.com/api/builds" \
        -H "Authorization: Bearer ${CI_TOKEN}" \
        -H "Content-Type: application/json" \
        -d "{
            \"project\": \"myapp\",
            \"branch\": \"main\",
            \"commit\": \"$commit\",
            \"pipeline\": \"production\",
            \"tasks\": [\"test\", \"build\", \"deploy-production\"]
        }"
}

trigger_staging_ci() {
    local commit=$1
    
    echo "🧪 Triggering staging CI for $commit"
    
    curl -X POST "https://ci.example.com/api/builds" \
        -H "Authorization: Bearer ${CI_TOKEN}" \
        -d "{
            \"project\": \"myapp\",
            \"branch\": \"develop\",
            \"commit\": \"$commit\",
            \"pipeline\": \"staging\",
            \"tasks\": [\"test\", \"build\", \"deploy-staging\"]
        }"
}

trigger_feature_ci() {
    local commit=$1
    local branch=$2
    
    echo "🔧 Triggering feature CI for $branch"
    
    # Only run tests for feature branches
    curl -X POST "https://ci.example.com/api/builds" \
        -H "Authorization: Bearer ${CI_TOKEN}" \
        -d "{
            \"project\": \"myapp\",
            \"branch\": \"$branch\",
            \"commit\": \"$commit\",
            \"pipeline\": \"feature\",
            \"tasks\": [\"test\", \"build\"]
        }"
}

while read old_sha new_sha ref_name; do
    branch=$(echo "$ref_name" | sed 's|refs/heads/||')

    case "$branch" in
        main|master)
            trigger_production_ci "$new_sha"
            ;;
        develop)
            trigger_staging_ci "$new_sha"
            ;;
        feature/*)
            trigger_feature_ci "$new_sha" "$branch"
            ;;
    esac
done
```

## Platform-Specific Integrations

### GitHub Actions

Use hooks to complement GitHub Actions workflows.

**Local pre-push hook**:
```bash
#!/bin/bash
# Runs same checks as GitHub Actions locally

echo "🔍 Running GitHub Actions checks locally"

# Run using act (https://github.com/nektos/act)
if command -v act >/dev/null; then
    act pull_request --dry-run || exit 1
else
    # Fallback: run checks manually
    npm run lint && npm test || exit 1
fi

exit 0
```

**GitHub Actions workflow**:
```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npm run lint
  
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npm test
  
  build:
    runs-on: ubuntu-latest
    needs: [lint, test]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npm run build
```

**Post-receive hook for GitHub**:
```bash
#!/bin/bash
# Use webhooks instead of hooks on GitHub

# Configure webhook in repo settings:
# - Payload URL: https://ci.example.com/webhook/github
# - Events: push, pull_request
# - Secret: (set environment variable)

# Webhook receiver handles CI triggering
```

### GitLab CI

Integrate with GitLab pipelines.

**Pre-push validation**:
```bash
#!/bin/bash

echo "🦊 Validating GitLab CI configuration"

# Validate .gitlab-ci.yml syntax (GitLab CLI)
if command -v glab >/dev/null; then
    glab ci lint .gitlab-ci.yml || exit 1
fi

exit 0
```

**GitLab CI configuration**:
```yaml
# .gitlab-ci.yml
stages:
  - lint
  - test
  - build
  - deploy

lint:
  stage: lint
  script:
    - npm run lint

test:
  stage: test
  script:
    - npm test
  coverage: '/Statements\s*:\s*(\d+\.?\d*)%/'

build:
  stage: build
  script:
    - npm run build
  artifacts:
    paths:
      - dist/

deploy:staging:
  stage: deploy
  script:
    - ./deploy-staging.sh
  only:
    - develop

deploy:production:
  stage: deploy
  script:
    - ./deploy-production.sh
  only:
    - main
  when: manual
```

### Other CI Systems

Any CI system (Jenkins, CircleCI, etc.) can be triggered from hooks the same way as GitHub Actions/GitLab above: call its trigger API from a post-receive hook, and keep validations in sync via the shared-script pattern below.

## Hook-CI Synchronization

Keep hook validations in sync with CI pipeline.

### Pattern: Shared Validation Scripts

**Project structure**:
```
project/
├── .githooks/
│   ├── pre-commit
│   └── pre-push
├── .github/workflows/
│   └── ci.yml
└── scripts/
    ├── lint.sh          # Shared
    ├── test.sh          # Shared
    └── build.sh         # Shared
```

**Shared script**:
```bash
#!/bin/bash
# scripts/lint.sh

set -e

echo "🔍 Running linters"

# ESLint
npm run lint:js

# Stylelint
npm run lint:css

# Prettier
npm run lint:format

echo "✅ Linting passed"
```

**Hook usage**:
```bash
#!/bin/bash
# .githooks/pre-push

./scripts/lint.sh || exit 1
./scripts/test.sh || exit 1
```

**CI usage**:
```yaml
# .github/workflows/ci.yml
- name: Lint
  run: ./scripts/lint.sh
  
- name: Test
  run: ./scripts/test.sh
```

### Pattern: CI Configuration Validation

```bash
#!/bin/bash
# pre-commit hook

validate_ci_config() {
    # GitHub Actions
    if [ -f ".github/workflows/ci.yml" ]; then
        if command -v actionlint >/dev/null; then
            actionlint .github/workflows/*.yml || return 1
        fi
    fi
    
    # GitLab CI
    if [ -f ".gitlab-ci.yml" ]; then
        if command -v glab >/dev/null; then
            glab ci lint .gitlab-ci.yml || return 1
        fi
    fi
    
    # CircleCI
    if [ -f ".circleci/config.yml" ]; then
        if command -v circleci >/dev/null; then
            circleci config validate || return 1
        fi
    fi
    
    return 0
}

# Only validate if CI config changed
if git diff --cached --name-only | grep -qE '(\.github/workflows/|\.gitlab-ci\.yml|\.circleci/)'; then
    echo "🔍 Validating CI configuration"
    validate_ci_config || exit 1
fi
```

## Deployment Automation

### Pattern: Tagged Release Deployment

```bash
#!/bin/bash
# hooks/post-receive

while read old_sha new_sha ref_name; do
    # Check if it's a tag
    if echo "$ref_name" | grep -q '^refs/tags/'; then
        tag=$(echo "$ref_name" | sed 's|refs/tags/||')
        
        # Only deploy semantic version tags
        if echo "$tag" | grep -qE '^v[0-9]+\.[0-9]+\.[0-9]+$'; then
            deploy_tagged_release "$tag" "$new_sha"
        fi
    fi
done

deploy_tagged_release() {
    local tag=$1
    local commit=$2
    
    echo "🚀 Deploying release $tag"
    
    # Trigger deployment pipeline
    curl -X POST "https://ci.example.com/api/deploy" \
        -H "Authorization: Bearer ${CI_TOKEN}" \
        -d "{
            \"version\": \"$tag\",
            \"commit\": \"$commit\",
            \"environment\": \"production\"
        }"
    
    # Send notification
    curl -X POST "$SLACK_WEBHOOK" \
        -d "{\"text\":\"🎉 Deployed $tag to production\"}"
}
```

### Pattern: Branch-Based Deployment

```bash
#!/bin/bash
# hooks/post-receive

while read old_sha new_sha ref_name; do
    branch=$(echo "$ref_name" | sed 's|refs/heads/||')
    
    case "$branch" in
        main)
            deploy_production "$new_sha"
            ;;
        staging)
            deploy_staging "$new_sha"
            ;;
        develop)
            deploy_dev "$new_sha"
            ;;
    esac
done

deploy_production() {
    echo "🌐 Deploying to production"
    ssh deploy@prod.example.com "cd /app && git pull && ./deploy.sh"
}

deploy_staging() {
    echo "🧪 Deploying to staging"
    ssh deploy@staging.example.com "cd /app && git pull && ./deploy.sh"
}

deploy_dev() {
    echo "🔧 Deploying to development"
    ssh deploy@dev.example.com "cd /app && git pull && ./deploy.sh"
}
```

## Monitoring and Notifications

### Pattern: Build Status Reporting

```bash
#!/bin/bash
# hooks/post-receive

send_build_notification() {
    local status=$1
    local branch=$2
    local commit=$3
    local message=$4
    
    if [ "$status" = "success" ]; then
        color="good"
        emoji="✅"
    else
        color="danger"
        emoji="❌"
    fi
    
    curl -X POST "$SLACK_WEBHOOK" \
        -H "Content-Type: application/json" \
        -d "{
            \"attachments\": [{
                \"color\": \"$color\",
                \"title\": \"$emoji Build $status\",
                \"fields\": [
                    {\"title\": \"Branch\", \"value\": \"$branch\", \"short\": true},
                    {\"title\": \"Commit\", \"value\": \"$commit\", \"short\": true},
                    {\"title\": \"Message\", \"value\": \"$message\"}
                ]
            }]
        }"
}

trigger_ci() {
    local branch=$1
    local commit=$2

    # Delegate to the trigger_*_ci functions defined in Pattern 2
    case "$branch" in
        main|master) trigger_production_ci "$commit" ;;
        develop)     trigger_staging_ci "$commit" ;;
        *)           trigger_feature_ci "$commit" "$branch" ;;
    esac
}

while read old_sha new_sha ref_name; do
    branch=$(echo "$ref_name" | sed 's|refs/heads/||')
    message=$(git log -1 --pretty=%s "$new_sha")
    
    # Trigger CI and report status
    if trigger_ci "$branch" "$new_sha"; then
        send_build_notification "success" "$branch" "${new_sha:0:7}" "$message"
    else
        send_build_notification "failed" "$branch" "${new_sha:0:7}" "$message"
    fi
done
```

## Best Practices

**Keep hooks fast**:
```bash
# Run full test suite in CI, quick checks in hooks
# Hook (30 seconds)
npm run lint && npm run test:unit

# CI (5 minutes)
npm run lint && npm test && npm run build && npm run test:e2e
```

**Make hooks optional for developers**:
```bash
# Allow bypass with flag
if [ "$SKIP_HOOKS" = "1" ]; then
    echo "⚠️  Skipping hooks (SKIP_HOOKS=1)"
    exit 0
fi

# Usage: SKIP_HOOKS=1 git push
```

**Log hook executions**:
```bash
#!/bin/bash

# Hooks typically lack write permission to /var/log; log somewhere writable
LOG_FILE=".git/hooks.log"

log_execution() {
    echo "[$(date)] $1" >> "$LOG_FILE"
}

while read -r old_sha new_sha ref_name; do
    log_execution "pre-receive started for $ref_name"
    # ... hook logic ...
    log_execution "pre-receive completed for $ref_name"
done
```

**Handle failures gracefully**:
```bash
#!/bin/bash

if ! trigger_ci "$commit"; then
    # Log error but don't block push
    echo "⚠️  Warning: Failed to trigger CI" >&2
    echo "Build may need to be triggered manually" >&2
    # Continue (exit 0) - push already succeeded
fi
```