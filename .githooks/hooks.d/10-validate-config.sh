#!/usr/bin/env bash
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"

if git diff --cached --quiet --diff-filter=ACMRTD -- '*.md' '*.sh' 'scripts/**' 'agents/**' 'commands/**' 'skills/**'; then
    exit 0
fi

tmp_dir="$(mktemp -d "${TMPDIR:-/tmp}/agent-tools-index.XXXXXX")"
trap 'rm -rf "$tmp_dir"' EXIT

git -C "$repo_root" checkout-index --all --prefix="$tmp_dir/"

if [ ! -f "$tmp_dir/scripts/validate.py" ]; then
    printf 'error: staged scripts/validate.py is missing\n' >&2
    exit 1
fi

(
    cd "$tmp_dir"
    python3 scripts/validate.py
)
