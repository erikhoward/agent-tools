#!/usr/bin/env bash
set -euo pipefail

command -v shellcheck >/dev/null 2>&1 || {
    printf 'shellcheck not found; skipping shell lint\n' >&2
    exit 0
}

tmp_dir="$(mktemp -d "${TMPDIR:-/tmp}/agent-tools-shellcheck.XXXXXX")"
trap 'rm -rf "$tmp_dir"' EXIT

count=0
while IFS= read -r -d '' path; do
    case "$path" in
        *.sh|.githooks/pre-commit|skills/git-hooks/examples/modular-pre-commit/pre-commit) ;;
        *) continue ;;
    esac
    count=$((count + 1))
    staged="$tmp_dir/$count.sh"
    git show ":$path" >"$staged"
    shellcheck -S style "$staged"
done < <(git diff --cached --name-only --diff-filter=ACMRT -z)
