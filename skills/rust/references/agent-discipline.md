# Rust Boundary Discipline

- Do not weaken a safe API to silence borrow or lifetime errors. Recheck ownership and invariants.
- Keep unsafe operations behind a small safe boundary. Document what callers and implementers must guarantee.
- Treat FFI data, raw pointers, lengths, alignment, ownership transfer, unwinding, and thread rules as explicit contracts.
- Avoid global mutable state. Multiple crate versions can create separate statics that appear to be one process-wide instance.
- Isolate test helpers from production APIs with existing test modules or an intentionally controlled feature. A feature name alone does not prevent production use.
- Test behavior and invariants. Do not copy the implementation algorithm into the assertion.
- Preserve public compatibility unless a break and migration are approved.

Adapted from leonardomso/rust-skills and Microsoft's Pragmatic Rust Guidelines (MIT).
