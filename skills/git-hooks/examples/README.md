# Modular Pre-Commit Example

This example runs executable checks from `hooks.d/` in filename order. The shell check reads staged blobs, so unstaged edits do not change the result.

Review and adapt the scripts before use. Git hooks are executable code. Do not install them or set `core.hooksPath` without user authorization. Required policy must also run in CI because client hooks can be bypassed.
