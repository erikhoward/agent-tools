#!/usr/bin/env bash
set -euo pipefail

tmp_dir="$(mktemp -d "${TMPDIR:-/tmp}/staged-shell.XXXXXX")"
trap 'rm -rf "$tmp_dir"' EXIT

count=0
while IFS= read -r -d '' path; do
    case "$path" in *.sh) ;; *) continue ;; esac
    count=$((count + 1))
    staged="$tmp_dir/$count.sh"
    git show ":$path" >"$staged"
    bash -n "$staged"
done < <(git diff --cached --name-only --diff-filter=ACMRT -z)
