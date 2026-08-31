#!/usr/bin/env bats
#
# agent-tools version-pin.bats — release pinning and stale-release tests
#
# Tests:  VER-01 through VER-07 and STALE-01 through STALE-05
# Scope:  all tests use isolated mktemp -d fake $HOME with temp XDG_CONFIG_HOME.
#

set -uo pipefail

setup() {
  TDIR="$(mktemp -d /tmp/agent-tools-version-test.XXXXXX)"
  _REAL_HOME="$HOME"
  _REAL_XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-}"
  export HOME="$TDIR"
  export XDG_CONFIG_HOME="$TDIR/.config"
  mkdir -p "$XDG_CONFIG_HOME"
  make_remote
  export AGENT_TOOLS_REPO_URL="file://$TDIR/remote"
}

teardown() {
  export HOME="$_REAL_HOME"
  export XDG_CONFIG_HOME="$_REAL_XDG_CONFIG_HOME"
  unset AGENT_TOOLS_REPO_URL
  if [ -n "$TDIR" ] && [ -d "$TDIR" ]; then
    rm -rf "$TDIR" 2>/dev/null || true
  fi
}

make_remote() {
  work="$TDIR/work"
  mkdir -p "$work/agents" "$work/commands" "$work/skills/s"
  git -C "$work" init -q -b main
  git -C "$work" config user.email test@example.com
  git -C "$work" config user.name test
  printf '# agent\n' > "$work/agents/a.md"
  printf '# command\n' > "$work/commands/c.md"
  printf '# skill\n' > "$work/skills/s/SKILL.md"
  printf '# rules\n' > "$work/AGENTS.md"
  git -C "$work" add .
  git -C "$work" commit -qm 'first release'
  git -C "$work" tag v1.0.0
  printf '# second\n' >> "$work/agents/a.md"
  git -C "$work" add .
  git -C "$work" commit -qm 'second release'
  git -C "$work" tag v1.1.0
  git clone -q --bare "$work" "$TDIR/remote"
  rm -rf "$work"
}

@test "VER-01: --version installs the requested release and links agents" {
  cd "$TDIR"
  run bash "$BATS_TEST_DIRNAME/../install.sh" --version v1.1.0
  [ "$status" -eq 0 ]
  [ "$(git -C "$HOME/.local/share/agent-tools" describe --tags --exact-match HEAD)" = "v1.1.0" ]
  [ -L "$XDG_CONFIG_HOME/opencode/agents/a.md" ]
}

@test "VER-02: --version without a tag fails" {
  run bash "$BATS_TEST_DIRNAME/../install.sh" --version
  [ "$status" -eq 1 ]
  [[ "$output" == *"requires a tag"* ]]
}

@test "VER-03: --version with a non-release tag fails" {
  run bash "$BATS_TEST_DIRNAME/../install.sh" --version latest
  [ "$status" -eq 1 ]
  [[ "$output" == *"expects a release tag"* ]]
}

@test "VER-04: --version and --source cannot be combined" {
  run bash "$BATS_TEST_DIRNAME/../install.sh" --version v1.1.0 --source "$TDIR/source"
  [ "$status" -eq 1 ]
  [[ "$output" == *"cannot be combined"* ]]
}

@test "VER-05: a missing release tag fails" {
  cd "$TDIR"
  run bash "$BATS_TEST_DIRNAME/../install.sh" --version v9.9.9
  [ "$status" -eq 1 ]
}

@test "VER-06: a second pinned install moves the clone to the new tag" {
  cd "$TDIR"
  run bash "$BATS_TEST_DIRNAME/../install.sh" --version v1.0.0
  [ "$status" -eq 0 ]
  run bash "$BATS_TEST_DIRNAME/../install.sh" --version v1.1.0
  [ "$status" -eq 0 ]
  [ "$(git -C "$HOME/.local/share/agent-tools" describe --tags --exact-match HEAD)" = "v1.1.0" ]
}

@test "VER-07: --update does not move a pinned clone" {
  cd "$TDIR"
  run bash "$BATS_TEST_DIRNAME/../install.sh" --version v1.0.0
  [ "$status" -eq 0 ]
  run bash "$BATS_TEST_DIRNAME/../install.sh" --update
  [ "$status" -eq 0 ]
  [ "$(git -C "$HOME/.local/share/agent-tools" describe --tags --exact-match HEAD)" = "v1.0.0" ]
  [[ "$output" == *"pinned"* ]]
}

@test "STALE-01: an older pinned clone warns about the latest release" {
  cd "$TDIR"
  run bash "$BATS_TEST_DIRNAME/../install.sh" --version v1.0.0
  [ "$status" -eq 0 ]
  run bash "$BATS_TEST_DIRNAME/../install.sh"
  [ "$status" -eq 0 ]
  [[ "$output" == *"latest release"* ]]
  [[ "$output" == *"--version v1.1.0"* ]]
}

@test "STALE-02: the latest pinned clone does not warn" {
  cd "$TDIR"
  run bash "$BATS_TEST_DIRNAME/../install.sh" --version v1.1.0
  [ "$status" -eq 0 ]
  run bash "$BATS_TEST_DIRNAME/../install.sh"
  [ "$status" -eq 0 ]
  [[ "$output" != *"latest release"* ]]
}

@test "STALE-03: a non-git source skips stale checking" {
  mkdir -p "$TDIR/source/agents" "$TDIR/source/commands" "$TDIR/source/skills/s"
  printf '# agent\n' > "$TDIR/source/agents/a.md"
  printf '# command\n' > "$TDIR/source/commands/c.md"
  printf '# skill\n' > "$TDIR/source/skills/s/SKILL.md"
  printf '# rules\n' > "$TDIR/source/AGENTS.md"
  run env AGENT_TOOLS_REPO_URL="file:///nonexistent" bash "$BATS_TEST_DIRNAME/../install.sh" --source "$TDIR/source"
  [ "$status" -eq 0 ]
}

@test "STALE-04: a fresh clone at the latest main does not warn" {
  cd "$TDIR"
  run bash "$BATS_TEST_DIRNAME/../install.sh"
  [ "$status" -eq 0 ]
  [[ "$output" != *"latest release"* ]]
}

@test "STALE-05: a clone behind a newer release warns with the update command" {
  cd "$TDIR"
  run bash "$BATS_TEST_DIRNAME/../install.sh"
  [ "$status" -eq 0 ]
  git clone -q "$TDIR/remote" "$TDIR/advance"
  git -C "$TDIR/advance" config user.email test@example.com
  git -C "$TDIR/advance" config user.name test
  printf '# third\n' >> "$TDIR/advance/agents/a.md"
  git -C "$TDIR/advance" add .
  git -C "$TDIR/advance" commit -qm 'main update'
  # newer release tag: warns whether or not the shallow clone carried tags (exact/nearest path) or not (head-vs-main fallback)
  git -C "$TDIR/advance" tag v1.2.0
  git -C "$TDIR/advance" push -q origin main v1.2.0
  run bash "$BATS_TEST_DIRNAME/../install.sh"
  [ "$status" -eq 0 ]
  [[ "$output" == *"behind"* ]]
  [[ "$output" == *"--update"* ]]
}
