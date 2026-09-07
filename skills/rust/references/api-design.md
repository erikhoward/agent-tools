# Rust API Design

- Preserve one intentional public path for an item when compatibility requires it.
- Use validated constructors when not every field combination is valid. Do not expose an invalid intermediate state.
- Accept borrowed forms when the function does not need ownership. Return owned values when the result must outlive inputs.
- Keep concrete APIs until callers need substitution or generic composition.
- Add a builder only when optional construction has become hard to read. Keep required fields required.
- Mark important results `must_use` when silently dropping them is likely a bug.
- Document errors, panic conditions, safety requirements, cancellation, and feature-dependent behavior.
- Treat serialized representations, feature flags, and public trait bounds as compatibility surfaces.

Adapted from leonardomso/rust-skills and Microsoft's Pragmatic Rust Guidelines (MIT).
