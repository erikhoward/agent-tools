#!/usr/bin/env bash
set -euo pipefail

# Pre-commit hook: Validate repo configuration
# Runs the repo's validate.py on staged .md and agent/command/skill files

REPO_ROOT="$(git rev-parse --show-toplevel)"

# Only run if .md or agent/command/skill files are staged
STAGED=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(md|sh)$|(^|/)scripts/' || true)
[ -n "$STAGED" ] || exit 0

# Run validate.py from the repo root
if [ -f "$REPO_ROOT/scripts/validate.py" ]; then
    python3 "$REPO_ROOT/scripts/validate.py"
else
    echo "⚠️  Warning: validate.py not found at $REPO_ROOT/scripts/validate.py — skipping"
    exit 0
fi