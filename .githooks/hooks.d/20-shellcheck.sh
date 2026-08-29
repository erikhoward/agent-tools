#!/usr/bin/env bash
set -euo pipefail

# Pre-commit hook: Run shellcheck on staged .sh files
# Skips gracefully if shellcheck is not installed

STAGED=$(git diff --cached --name-only --diff-filter=ACM | grep '\.sh$' || true)
[ -n "$STAGED" ] || exit 0

if ! command -v shellcheck &>/dev/null; then
    echo "  shellcheck not found — skipping shell linting"
    exit 0
fi

echo "$STAGED" | while IFS= read -r f; do
    shellcheck "$f"
done