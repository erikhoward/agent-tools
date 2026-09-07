# Server-Side Git Hooks

Use this reference only when the Git host permits custom receive hooks.

- `pre-receive` evaluates the full push and can reject it.
- `update` evaluates one ref at a time and can reject that ref.
- `post-receive` runs after acceptance and cannot reject the push.
- Read every ref record. Handle creation and deletion SHAs explicitly.
- Validate committed objects and complete introduced history, not a working tree or only the endpoint diff.
- Bound object traversal, process time, memory, and output. Fail according to the repository's documented availability policy.
- Keep authorization and protected-ref policy on the server even when client hooks provide faster feedback.
- Do not put deployment, unbounded network calls, or secret values in a blocking receive hook. Queue authorized post-receive work with controlled credentials and observable failure handling.
- Test hooks against a disposable bare repository before deployment. Document recovery if a bad hook blocks all pushes.

Managed Git hosting often does not allow custom server hooks. Use supported branch protection, required checks, or policy APIs instead.
