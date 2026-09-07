# Rust Async And Performance

- A dropped join handle does not guarantee task cancellation. Give each task an owner, shutdown signal, and awaited completion or explicit abort policy.
- Define cancellation safety for futures that can be dropped during partial I/O or state mutation.
- Bound channels, task creation, retries, and work queues. State backpressure behavior.
- Do not hold blocking mutex guards across `.await`. Keep async lock scope short.
- Propagate flush and shutdown errors when callers need durability guarantees.
- Protect maps keyed by untrusted input from collision attacks unless another design bounds the risk.
- Profile before optimizing. Record workload, build profile, warmup, repetitions, environment, and noise. Distinguish measured results from predictions.
- Consider allocation and copying only after locating a relevant cost. Do not replace safe code with `unsafe` for an unmeasured gain.
- Account for panic strategy when isolation or FFI cleanup depends on unwinding.

Adapted from leonardomso/rust-skills and Microsoft's Pragmatic Rust Guidelines (MIT).
