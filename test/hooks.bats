#!/usr/bin/env bats

setup() {
  TDIR="$(mktemp -d)"
  REPO="$TDIR/repo"
  mkdir -p "$REPO/.githooks/hooks.d" "$REPO/scripts"
  git -C "$REPO" init -q
  git -C "$REPO" config user.email test@example.com
  git -C "$REPO" config user.name test
  cp "$BATS_TEST_DIRNAME/../.githooks/hooks.d/10-validate-config.sh" "$REPO/.githooks/hooks.d/"
  cp "$BATS_TEST_DIRNAME/../.githooks/hooks.d/20-shellcheck.sh" "$REPO/.githooks/hooks.d/"
  chmod +x "$REPO/.githooks/hooks.d/"*.sh
  cat >"$REPO/scripts/validate.py" <<'PY'
from pathlib import Path
raise SystemExit(0 if Path("policy.md").read_text() == "valid\n" else 1)
PY
  printf 'valid\n' >"$REPO/policy.md"
  printf '#!/usr/bin/env bash\nprintf "ok\\n"\n' >"$REPO/check.sh"
  git -C "$REPO" add .
  git -C "$REPO" commit -qm initial
}

teardown() {
  rm -rf "$TDIR"
}

@test "config hook validates staged content, not the working tree" {
  printf 'invalid\n' >"$REPO/policy.md"
  git -C "$REPO" add policy.md
  printf 'valid\n' >"$REPO/policy.md"

  run bash -c 'cd "$1" && .githooks/hooks.d/10-validate-config.sh' _ "$REPO"
  [ "$status" -ne 0 ]
  [ "$(git -C "$REPO" show :policy.md)" = invalid ]
  [ "$(cat "$REPO/policy.md")" = valid ]
}

@test "config hook accepts a valid index despite invalid working content" {
  printf 'invalid\n' >"$REPO/policy.md"

  run bash -c 'cd "$1" && .githooks/hooks.d/10-validate-config.sh' _ "$REPO"
  [ "$status" -eq 0 ]
  [ "$(git -C "$REPO" show :policy.md)" = valid ]
  [ "$(cat "$REPO/policy.md")" = invalid ]
}

@test "config hook validates staged deletions" {
  git -C "$REPO" rm -q policy.md

  run bash -c 'cd "$1" && .githooks/hooks.d/10-validate-config.sh' _ "$REPO"
  [ "$status" -ne 0 ]
  [ ! -e "$REPO/policy.md" ]
  [ "$(git -C "$REPO" diff --cached --name-status -- policy.md)" = $'D\tpolicy.md' ]
}

@test "shell hook reads staged bytes and handles a leading-dash path" {
  mkdir -p "$TDIR/bin"
  cat >"$TDIR/bin/shellcheck" <<'SH'
#!/usr/bin/env bash
bash -n "${@: -1}"
SH
  chmod +x "$TDIR/bin/shellcheck"
  printf '#!/usr/bin/env bash\nif then\n' >"$REPO/- odd.sh"
  git -C "$REPO" add -- '- odd.sh'
  printf '#!/usr/bin/env bash\nprintf "fixed\\n"\n' >"$REPO/- odd.sh"

  # shellcheck disable=SC2016
  run env PATH="$TDIR/bin:$PATH" bash -c 'cd "$1" && .githooks/hooks.d/20-shellcheck.sh' _ "$REPO"
  [ "$status" -ne 0 ]
  [ "$(git -C "$REPO" show ':- odd.sh')" != "$(cat "$REPO/- odd.sh")" ]
}

@test "shell hook handles a newline in a staged filename" {
  mkdir -p "$TDIR/bin"
  cat >"$TDIR/bin/shellcheck" <<'SH'
#!/usr/bin/env bash
bash -n "${@: -1}"
SH
  chmod +x "$TDIR/bin/shellcheck"
  name=$'line\nbreak.sh'
  printf '#!/usr/bin/env bash\nif then\n' >"$REPO/$name"
  git -C "$REPO" add -- "$name"
  printf '#!/usr/bin/env bash\nprintf "fixed\\n"\n' >"$REPO/$name"

  # shellcheck disable=SC2016
  run env PATH="$TDIR/bin:$PATH" bash -c 'cd "$1" && .githooks/hooks.d/20-shellcheck.sh' _ "$REPO"
  [ "$status" -ne 0 ]
}

@test "example shell hook validates staged bytes for unusual paths" {
  name=$'- example\ncheck.sh'
  printf '#!/usr/bin/env bash\nif then\n' >"$REPO/$name"
  git -C "$REPO" add -- "$name"
  printf '#!/usr/bin/env bash\nprintf "fixed\\n"\n' >"$REPO/$name"

  example="$BATS_TEST_DIRNAME/../skills/git-hooks/examples/modular-pre-commit/hooks.d/10-validate-bash.sh"
  run bash -c 'cd "$1" && "$2"' _ "$REPO" "$example"
  [ "$status" -ne 0 ]
  [ "$(git -C "$REPO" show ":$name")" != "$(cat "$REPO/$name")" ]
}
