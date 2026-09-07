# Python Async And Concurrency

Use this reference for lifecycle and correctness decisions, not as a framework template.

- Use async only when the surrounding stack is async and the work can yield. Move blocking CPU or file work to an appropriate executor when measurement justifies it.
- Create long-lived HTTP clients at an owned application boundary. Close them during shutdown. Do not create a client for each request.
- Bound fan-out with a semaphore, worker pool, or bounded queue. Define cancellation and partial-failure behavior.
- Set connect, read, write, pool, and total timeouts as the client and operation require.
- Retry only transient failures and operations safe to repeat. Bound attempts and elapsed time. Honor server retry guidance. Add jitter when synchronized retries are a risk.
- Preserve cancellation. Do not catch cancellation under a broad exception handler or leave child tasks running after the owner exits.
- Stream large responses when the API permits it. Enforce size limits for untrusted input.
- In tests, use the repository's async plugin and HTTP mocking conventions. Test timeout, cancellation, retry exhaustion, and cleanup behavior without real network access.

Record client ownership, concurrency limits, retry conditions, and shutdown behavior in the public boundary or nearby documentation.

Adapted from affaan-m/ECC and manikosto/claude-code-python-stack.
