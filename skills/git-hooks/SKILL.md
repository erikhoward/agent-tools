---
name: git-hooks
description: Design and diagnose Git hooks that validate the intended snapshot, preserve user state, handle filenames safely, and share enforcement with CI.
license: MIT
compatibility: opencode
---

# Git Hooks

Inspect existing hooks, `core.hooksPath`, repository scripts, and CI before changing anything. Do not install hooks or change Git configuration without explicit authorization.

## Safety Contract

- Client hooks are bypassable. Put required policy in CI or server-side enforcement too.
- A commit hook must validate staged blobs, not unstaged working-tree content. Preserve partial staging and do not modify the index or working tree.
- Handle arbitrary filenames as data. Prefer NUL-delimited Git output and quote every path.
- Include additions, modifications, deletions, and renames when repository-wide references can break.
- Propagate validator failures. Distinguish no relevant files from failed discovery.
- Keep pre-commit checks focused and fast. Put expensive integration work in pre-push or CI.
- Share validation scripts with CI rather than maintaining different rules in hook prose.
- Treat third-party hook code as executable supply-chain input. Pin and review it.
- Keep secrets out of arguments, logs, and generated files.
- Never bypass a hook unless the user explicitly authorizes that action after seeing the failure.

Use one orchestrator with ordered executable checks when several checks are needed. A disabled check must not remain executable in an auto-discovered directory.

Read `references/hook-types.md` for hook parameters and abort behavior. Read `references/server-side-hooks.md` only for server-hosted repositories and bounded receive-hook design.

The retained `examples/modular-pre-commit/` example demonstrates staged-shell validation. Adapt it to the repository. Do not present it as enforcement for every project.
