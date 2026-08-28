# Advanced Git Hooks Patterns

Complex validation patterns, techniques, and architectural approaches for sophisticated Git hooks implementations.

## Table of Contents

- [Multi-Stage Validation](#multi-stage-validation)
- [Incremental Checking](#incremental-checking)
- [Caching Strategies](#caching-strategies)
- [Parallel Execution](#parallel-execution)
- [Conditional Logic Patterns](#conditional-logic-patterns)
- [Language-Specific Validation](#language-specific-validation)
- [Integration Patterns](#integration-patterns)
- [Performance Optimization](#performance-optimization)

## Multi-Stage Validation

Organize complex validation into stages with increasing cost.

### Pattern: Fast-Fail Pipeline

Run cheap validations first, expensive ones only if needed:

```bash
#!/bin/bash
set -e

echo "🔍 Stage 1: Syntax Validation (fast)"
# Quick syntax checks
for file in $(git diff --cached --name-only --diff-filter=ACM | grep '\.sh$'); do
    bash -n "$file" || exit 1
done
echo "✅ Syntax valid"

echo "🔍 Stage 2: Linting (medium)"
# Linting (slower)
shellcheck $(git diff --cached --name-only --diff-filter=ACM | grep '\.sh$') || exit 1
echo "✅ Linting passed"

echo "🔍 Stage 3: Security Scan (slow)"
# Security scanning (expensive)
bandit -r $(git diff --cached --name-only --diff-filter=ACM | grep '\.py$') || exit 1
echo "✅ Security scan clean"

exit 0
```

## Incremental Checking

Only validate changed files or affected code sections.

### Pattern: Delta-Based Validation

```bash
#!/bin/bash

# Process each changed Python file
# Process substitution avoids the pipeline subshell, so a failure reaches exit 1
while read -r file; do
    echo "🔍 Validating $file"
    # flake8 has no line-range option; validate the whole file
    # (for delta-only linting, use `flake8 --diff` or diff-quality)
    flake8 --select=E,W "$file" || exit 1
done < <(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')

exit 0
```

### Pattern: Affected Test Selection

Run only tests affected by changes:

```bash
#!/bin/bash

# Map source files to test files
get_affected_tests() {
    local changed_files=$1
    local test_files=""
    
    for file in $changed_files; do
        # Pattern: src/module.py → tests/test_module_test.py
        test_file=$(echo "$file" | sed 's|^src/|tests/test_|; s|\.py$|_test.py|')
        
        if [ -f "$test_file" ]; then
            test_files="$test_files $test_file"
        fi
        
        # Also include integration tests if controllers changed
        if echo "$file" | grep -q 'controllers/'; then
            test_files="$test_files tests/integration/"
        fi
    done
    
    echo "$test_files"
}

CHANGED=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')
TESTS=$(get_affected_tests "$CHANGED")

if [ -n "$TESTS" ]; then
    echo "Running affected tests: $TESTS"
    pytest $TESTS || exit 1
else
    echo "No affected tests found"
fi

exit 0
```

## Caching Strategies

Cache validation results to speed up repeated checks.

### Pattern: Content-Based Caching

```bash
#!/bin/bash

CACHE_DIR=".git/hooks-cache"
mkdir -p "$CACHE_DIR"

# Generate cache key from file content
get_cache_key() {
    local file=$1
    git hash-object "$file"
}

# Check if validation cached
is_cached() {
    local file=$1
    local cache_key=$(get_cache_key "$file")
    local cache_file="$CACHE_DIR/$cache_key"
    
    if [ -f "$cache_file" ]; then
        # Check if cache is still valid
        local cached_result=$(cat "$cache_file")
        if [ "$cached_result" = "pass" ]; then
            return 0
        fi
    fi
    return 1
}

# Store validation result
cache_result() {
    local file=$1
    local result=$2
    local cache_key=$(get_cache_key "$file")
    echo "$result" > "$CACHE_DIR/$cache_key"
}

# Validate with caching
validate_file() {
    local file=$1
    
    if is_cached "$file"; then
        echo "✅ $file (cached)"
        return 0
    fi
    
    echo "🔍 $file (validating)"
    if eslint "$file"; then
        cache_result "$file" "pass"
        return 0
    else
        cache_result "$file" "fail"
        return 1
    fi
}

# Process files
for file in $(git diff --cached --name-only --diff-filter=ACM | grep '\.js$'); do
    validate_file "$file" || exit 1
done

exit 0
```

### Pattern: Cache Invalidation

```bash
#!/bin/bash

CACHE_DIR=".git/hooks-cache"

# Clear cache older than 1 day
clean_old_cache() {
    find "$CACHE_DIR" -type f -mtime +1 -delete
}

# Clear cache when dependencies change
invalidate_on_deps() {
    local deps_hash=$(cat package.json package-lock.json 2>/dev/null | git hash-object --stdin)
    local last_deps="$CACHE_DIR/deps-hash"
    
    if [ -f "$last_deps" ]; then
        if [ "$(cat "$last_deps")" != "$deps_hash" ]; then
            echo "Dependencies changed, clearing cache"
            rm -rf "$CACHE_DIR"/*
        fi
    fi
    
    mkdir -p "$CACHE_DIR"
    echo "$deps_hash" > "$last_deps"
}

clean_old_cache
invalidate_on_deps

# Continue with validation...
```

## Parallel Execution

Speed up validation by running checks in parallel.

### Pattern: Background Jobs

```bash
#!/bin/bash

# Run validation in background
validate_python() {
    flake8 $(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')
}

validate_javascript() {
    eslint $(git diff --cached --name-only --diff-filter=ACM | grep '\.js$')
}

validate_css() {
    stylelint $(git diff --cached --name-only --diff-filter=ACM | grep '\.css$')
}

# Start background jobs
validate_python &
PY_PID=$!

validate_javascript &
JS_PID=$!

validate_css &
CSS_PID=$!

# Wait for all jobs
EXIT_CODE=0

wait $PY_PID || EXIT_CODE=1
wait $JS_PID || EXIT_CODE=1
wait $CSS_PID || EXIT_CODE=1

exit $EXIT_CODE
```

### Pattern: GNU Parallel

```bash
#!/bin/bash

# Install: apt-get install parallel

validate_file() {
    local file=$1
    case "$file" in
        *.py)  python -m py_compile "$file" ;;
        *.js)  eslint "$file" ;;
        *.sh)  shellcheck "$file" ;;
        *)     return 0 ;;
    esac
}

# Export function for parallel
export -f validate_file

# Validate files in parallel
git diff --cached --name-only --diff-filter=ACM | \
    parallel --halt soon,fail=1 validate_file {}

exit $?
```

## Conditional Logic Patterns

Smart decisions about when to run validations.

### Pattern: Change Detection

```bash
#!/bin/bash

has_python_changes() {
    git diff --cached --name-only --diff-filter=ACM | grep -q '\.py$'
}

has_frontend_changes() {
    git diff --cached --name-only --diff-filter=ACM | grep -qE '\.(js|jsx|ts|tsx|css)$'
}

has_backend_changes() {
    git diff --cached --name-only --diff-filter=ACM | grep -qE '^(src|api)/'
}

# Conditional validation
if has_python_changes; then
    echo "🐍 Running Python validations"
    flake8 && mypy . || exit 1
fi

if has_frontend_changes; then
    echo "🎨 Running frontend validations"
    npm run lint && npm run type-check || exit 1
fi

if has_backend_changes; then
    echo "⚙️  Running backend tests"
    pytest tests/unit/ || exit 1
fi

exit 0
```

### Pattern: Branch-Based Rules

```bash
#!/bin/bash

BRANCH=$(git symbolic-ref --short HEAD)

# Strict rules for main branch
if [ "$BRANCH" = "main" ]; then
    echo "📋 Main branch: Running full validation"
    npm test && npm run build || exit 1
    
# Relaxed rules for feature branches
elif echo "$BRANCH" | grep -q '^feature/'; then
    echo "🚀 Feature branch: Quick validation"
    npm run lint || exit 1
    
# Development branches
elif [ "$BRANCH" = "develop" ]; then
    echo "🔧 Develop branch: Medium validation"
    npm run lint && npm run test:unit || exit 1
fi

exit 0
```

### Pattern: File Count Thresholds

```bash
#!/bin/bash

FILE_COUNT=$(git diff --cached --name-only --diff-filter=ACM | wc -l)

# Skip expensive checks for small changes
if [ "$FILE_COUNT" -lt 5 ]; then
    echo "Small change ($FILE_COUNT files), running quick checks"
    npm run lint:quick || exit 1
    
# Run moderate checks for medium changes
elif [ "$FILE_COUNT" -lt 20 ]; then
    echo "Medium change ($FILE_COUNT files), running standard checks"
    npm run lint && npm run test:changed
    
# Full validation for large changes
else
    echo "Large change ($FILE_COUNT files), running full validation"
    npm test && npm run build
fi
```

## Language-Specific Validation

Patterns for common programming languages.

### Python

```bash
#!/bin/bash

validate_python() {
    local files=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')
    [ -z "$files" ] && return 0
    
    echo "🐍 Python validation"
    
    # Syntax check
    echo "$files" | xargs -n1 python -m py_compile || return 1
    
    # Linting
    flake8 $files || return 1
    
    # Type checking
    if command -v mypy >/dev/null; then
        mypy $files || return 1
    fi
    
    # Import sorting
    if command -v isort >/dev/null; then
        isort --check-only $files || {
            echo "Run: isort $files"
            return 1
        }
    fi
    
    # Formatting
    if command -v black >/dev/null; then
        black --check $files || {
            echo "Run: black $files"
            return 1
        }
    fi
    
    return 0
}
```

### JavaScript/TypeScript

```bash
#!/bin/bash

validate_javascript() {
    local files=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(js|jsx|ts|tsx)$')
    [ -z "$files" ] && return 0
    
    echo "📜 JavaScript/TypeScript validation"
    
    # Linting
    eslint $files || return 1
    
    # Type checking
    if [ -f "tsconfig.json" ]; then
        tsc --noEmit || return 1
    fi
    
    # Formatting
    if command -v prettier >/dev/null; then
        prettier --check $files || {
            echo "Run: prettier --write $files"
            return 1
        }
    fi
    
    return 0
}
```

### Go

```bash
#!/bin/bash

validate_go() {
    local files=$(git diff --cached --name-only --diff-filter=ACM | grep '\.go$')
    [ -z "$files" ] && return 0
    
    echo "🐹 Go validation"
    
    # Formatting
    gofmt -l $files | grep . && {
        echo "Run: gofmt -w $files"
        return 1
    }
    
    # Linting
    golangci-lint run $files || return 1
    
    # Vet
    go vet ./... || return 1
    
    # Tests for affected packages
    local packages=$(echo "$files" | xargs -n1 dirname | sort -u | sed 's|^|./|')
    go test $packages || return 1
    
    return 0
}
```

## Integration Patterns

Integrate hooks with external systems.

### Pattern: Ticket Validation

```bash
#!/bin/bash

require_ticket_reference() {
    local commit_sha=$1
    local branch=$(git symbolic-ref --short HEAD)
    local commit_msg=$(git show -s --format=%B "$commit_sha")
    
    # Extract ticket from branch or commit
    local ticket=$(echo "$branch $commit_msg" | grep -oE '(JIRA|TICKET)-[0-9]+' | head -n1)
    
    if [ -z "$ticket" ]; then
        echo "❌ No ticket reference found"
        echo "Include ticket in branch name or commit message"
        echo "Example: feature/JIRA-123-new-feature"
        echo "Example: fix(api): resolve timeout issue [JIRA-456]"
        return 1
    fi
    
    # Validate ticket exists (optional)
    if command -v curl >/dev/null && [ -n "$JIRA_API_TOKEN" ]; then
        local response=$(curl -s -u "$JIRA_USER:$JIRA_API_TOKEN" \
            "https://jira.example.com/rest/api/2/issue/$ticket")
        
        if echo "$response" | grep -q '"errorMessages"'; then
            echo "❌ Ticket $ticket not found in JIRA"
            return 1
        fi
        
        echo "✅ Validated ticket: $ticket"
    fi
    
    return 0
}

# pre-push: stdin provides "local_ref local_sha remote_ref remote_sha" lines
while read -r local_ref local_sha remote_ref remote_sha; do
    # Skip deleted refs
    [ "$local_sha" = "0000000000000000000000000000000000000000" ] && continue
    require_ticket_reference "$local_sha" || exit 1
done
```

### Pattern: Continuous Integration

See references/ci-cd-integration.md → Local Pre-Flight Checks.

### Pattern: Security Scanning

```bash
#!/bin/bash

security_scan() {
    echo "🔒 Security scanning"
    
    # Check for secrets
    if command -v gitleaks >/dev/null; then
        gitleaks detect --no-git --staged || return 1
    fi
    
    # Check dependencies
    if [ -f "package.json" ]; then
        npm audit --audit-level=high || return 1
    fi
    
    if [ -f "requirements.txt" ]; then
        safety check -r requirements.txt || return 1
    fi
    
    # Check for hardcoded credentials
    if git diff --cached | grep -iE "(password|api[_-]?key|secret|token)\s*=\s*[\"'][^\"']+"; then
        echo "❌ Possible hardcoded credentials detected"
        return 1
    fi
    
    return 0
}
```

## Performance Optimization

### Pattern: Early Exit

```bash
#!/bin/bash

# Exit immediately if no relevant files changed
CHANGED=$(git diff --cached --name-only --diff-filter=ACM)

if ! echo "$CHANGED" | grep -qE '\.(js|py|go|rs)$'; then
    echo "No source files changed, skipping validation"
    exit 0
fi

# Continue with validation...
```

### Pattern: Resource Limits

```bash
#!/bin/bash

# Set timeout
timeout 60s npm test || {
    echo "❌ Tests timed out after 60s"
    echo "Consider running: git commit --no-verify"
    exit 1
}

# Note: there is no portable RSS limit (ulimit -m / RLIMIT_RSS is a no-op on modern Linux)
npm run lint
```