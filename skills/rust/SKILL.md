---
name: rust
description: Use when writing, refactoring, reviewing, or documenting Rust code (.rs files, Cargo.toml) — idiomatic Rust conventions for ownership and borrowing, error handling and panic discipline, naming, newtypes, API design, async, unsafe, testing, and clippy enforcement.
license: MIT
compatibility: opencode
metadata:
  language: rust
  sources:
    - https://github.com/leonardomso/rust-skills
    - https://microsoft.github.io/rust-guidelines/
  audience: developers
---

# Rust Style

Conventions for idiomatic, fast, and safe Rust, synthesized from the
rust-skills rule collection and Microsoft's Pragmatic Rust Guidelines. Apply
when writing and reviewing code; enforce mechanically with clippy (see the
Enforcement Map). For general design principles, combine with the `solid`
skill.

## When to use

- Writing new Rust functions, structs, modules, or crates
- Implementing error handling, async, concurrency, or `unsafe` code
- Designing public APIs for libraries
- Reviewing or refactoring existing Rust

## Verification

Finish every Rust change with:

```bash
cargo fmt --check                # must pass
cargo clippy --all-targets -- -D warnings
cargo build
cargo test
```

For any crate containing `unsafe`, also run `cargo miri test`.

## Ownership and borrowing

Prefer borrows over clones; accept borrowed slices, not owned containers:

```rust
// Good
fn first_word(s: &str) -> Option<&str> {
    s.split_whitespace().next()
}

// Bad - needless clone, allocation, and panic on empty input
fn first_word(s: &String) -> String {
    s.clone().split_whitespace().next().unwrap().to_string()
}
```

- `&str` not `&String`; `&[T]` not `&Vec<T>` — callers keep their freedom
- `Cow<'a, T>` when a function sometimes needs ownership and sometimes doesn't
- `Arc<T>` for shared ownership across threads; `Rc<T>` single-threaded only
- `mem::take` / `mem::replace` to move a value out of `&mut` without cloning
- Don't reach for `Box<dyn Trait>` when `impl Trait` or generics work — static
  dispatch by default, dynamic by deliberate choice

## Error handling and panic discipline

**Result for recoverable failures; panic only for bugs.** A panic means
"stop the program" — never use it to communicate errors upstream, and never
assume it will be caught.

```rust
// Good - fallible by nature
fn parse_uri(s: &str) -> Result<Uri, ParseError>

// Good - contract violation is a bug: panic with a useful message
fn divide_by(x: u32, y: u32) -> u32 // panics on y == 0
```

- Propagate with `?`; implement `From<E>` so `?` converts automatically
- `thiserror` for library error types; `anyhow` (or `eyre`) for applications —
  never mix multiple application-level error types
- No `unwrap()` in production code. `expect("invariant message")` only for
  bugs — and the message must state what went wrong with actual values
- Panic messages carry data: `assert!(buf.len() >= HEADER, "buffer too small: got {} bytes, need {HEADER}", buf.len())`
- Error messages start lowercase, no trailing punctuation
- `catch_unwind` is a last resort (per-request isolation in servers), not a
  recovery mechanism — promote a restart after a panic
- Document fallibility: `# Errors` section in doc comments; `# Panics` when
  the function can panic

## Types

Make invalid states unrepresentable — the compiler is the reviewer that never
gets tired:

```rust
// Good - invariants enforced at construction
pub struct UserId(u64);
pub struct Email(String); // validated in constructor

// Bad - primitives mixed freely at every call site
fn transfer(from: u64, to: u64, amount: i64)
```

- Newtypes for IDs and domain primitives; guard invariants in a fallible
  constructor (`parse`, don't validate)
- Enums for mutually exclusive states; match exhaustively — avoid catch-all
  `_` that hides new variants
- `Option<T>` / `Result<T, E>`, never sentinel values (`-1`, empty string)
- `PathBuf` not `String` for anything touching the filesystem
- Implement `Debug` for all public types (manual + redacted when secrets are
  involved); `Display` for user-facing output — never swap them
- Avoid stringly-typed APIs — enums and newtypes instead

## Naming

| Item | Convention | Example |
|---|---|---|
| Types, traits, enums, variants | UpperCamelCase, acronyms as words | `HttpClient`, not `HTTPClient` |
| Functions, variables, modules | snake_case | `parse_config` |
| Constants, statics | SCREAMING_SNAKE_CASE | `MAX_PACKET_SIZE` |
| Lifetimes / type params | short: `'a`, `T`, `E` | |

- Conversion prefixes: `as_` cheap reference cast, `to_` expensive copy,
  `into_` consumes ownership
- Predicates: `is_`, `has_`, `can_` return `bool`
- No `get_` prefix on simple getters; iterator trio: `iter` / `iter_mut` /
  `into_iter`
- Short names (`foo::Id`, not `foo::FooId`); no weasel words — `Manager`,
  `Service`, `Factory` name nothing. Name the behavior (`Bookings`,
  `BookingDispatcher`)

## API design

- **Builder** for construction with more than ~2 optional parameters:
  `Foo::builder()`, chainable setters named `x()` (not `set_x()`), all
  validation in a `Result`-returning `.build()`
- Implement `From<T>`, never `Into<U>` — `From` gives `Into` for free;
  `TryFrom` for fallible conversions, `FromStr` to enable `"x".parse()`
- Accept `impl Into<T>` / `impl AsRef<T>` at boundaries for caller
  flexibility — but store concrete types internally
- `#[must_use]` when ignoring the result is likely a bug; `#[non_exhaustive]`
  on public enums/structs for forward compatibility
- Don't expose `Rc`/`Arc`/`Box`/`RefCell` in public APIs — take `&T`, `&mut
  T`, or `T`; wrappers stay internal
- Derive the common traits (`Debug`, `Clone`, `PartialEq`) on public types;
  `Default` whenever `new()` takes no arguments
- Every public item reachable through exactly one path — no duplicate
  re-exports

## Async

- **Never hold a `Mutex`/`RwLock` guard across `.await`** — use
  `tokio::sync::Mutex` or restructure; deadlocks await
- CPU-intensive work goes to `spawn_blocking`; async code uses `tokio::fs`,
  not `std::fs`
- `join!`/`try_join!` for concurrent independent futures; `select!` only with
  cancellation-safe branches
- Bounded channels (`mpsc`) for backpressure; `watch` for latest-value,
  `broadcast` for pub/sub, `oneshot` for request-response
- Native `async fn` in traits (stable); `AsyncFn` bounds over manual
  `Fn() -> Fut` plumbing
- Long CPU-bound async tasks yield: `tokio::task::yield_now().await` every
  ~10–100µs of work

## Unsafe

`unsafe` requires a reason, and there are only three: novel abstractions,
measured performance, FFI. Never to "simplify" safe code, bypass `Send`
bounds, or transmute lifetimes.

```rust
// SAFETY: `ptr` is valid for reads and points to a UTF-8 string
// initialized by `init()` above.
unsafe fn print_string(ptr: *const String) {}
```

- `// SAFETY:` comment above every `unsafe` block; `# Safety` section in
  every `unsafe fn`
- Keep blocks minimal — mark the operation, not the surrounding function
- Unsound code is never acceptable — safe-looking functions that can trigger
  UB are broken regardless of how unlikely the trigger
- Run `cargo miri test` in CI for any crate with `unsafe`

## Testing

- Unit tests live in `#[cfg(test)] mod tests { use super::*; ... }` within
  the module; public-API tests go in `tests/`
- Descriptive names that state the behavior: `returns_error_when_cart_is_empty`
- Arrange-Act-Assert structure; `#[tokio::test]` for async; `#[should_panic]`
  where panics are the contract
- **No tautological tests** — assert a property (`checkpoints are evenly
  spaced`), never a mirrored constant (`assert_eq!(CHECKPOINTS, [0, 90, 180, 270])`)
- Keep doc examples as runnable doctests — they are tests
- `criterion` for benchmarks, `proptest` for properties, `insta` for
  snapshots, `loom` for lock-free code

## Documentation

```rust
/// Copies a file from `src` to `dst`.          <- summary, < 15 words
///
/// Extended documentation in free form.
///
/// # Errors
/// Returns an error if `src` cannot be read or `dst` cannot be written.
///
/// # Panics
/// Panics if `src` and `dst` are the same file.
pub fn copy(src: File, dst: File) -> Result<(), CopyError>
```

- `///` on every public item; `//!` for module docs
- Summary sentence under ~15 words — it renders in module listings
- Examples use `?`, not `.unwrap()`; hide setup with `# ` lines
- Explain parameters in prose — no `# Parameters` tables
- No meta-design narratives ("why we chose X over Y") in user-facing docs

## Agent discipline

Rules that specifically counter common agent failure modes:

- **Write Rust-shaped Rust.** Don't port C#/Java/Python patterns 1:1 — a
  `throw_if_null()` never makes sense; error handling, ownership, and
  component lifetimes have Rust-native answers
- **One path per item.** When refactoring, don't re-export under new paths to
  "simplify" — redesign the module structure
- **Strong types are your guardrails.** The more invariants live in types,
  the more agent mistakes become compile errors instead of runtime bugs
- **Macros must not lie** — no macro that alters signatures, converts structs
  to enums, or changes async-ness. Prefer functions; macros are a last
  resort
- **Avoid statics** for state that must be consistent — multiple semver
  copies of a crate may be linked in one binary, each with its own static

## Enforcement map

Many of these conventions map to clippy lints — enforce mechanically where
possible:

| Convention | Clippy lint |
|---|---|
| `&String` / `&Vec<T>` parameters | `clippy::ptr_arg` |
| Needless clone/borrow | `clippy::redundant_clone`, `clippy::needless_borrow` |
| `unwrap()` in production | `clippy::unwrap_used` (restriction group — enable) |
| `expect()` without message | `clippy::expect_used` (restriction group) |
| `println!` in libraries | `clippy::print_stdout` |
| `new()` with no args, no `Default` | `clippy::new_without_default` |
| Casing violations | `non_camel_case_types`, `non_snake_case`, `non_upper_case_globals` |
| `Box<dyn Trait>` where `impl Trait` fits | `clippy::redundant_allocation`, `clippy::trait_duplication_in_bounds` |
| Unneeded `return` / `else` | `clippy::needless_return`, `clippy::collapsible_else_if` |

Baseline lint setup (workspace `Cargo.toml`):

```toml
[workspace.lints.rust]
unsafe_code = "warn"
missing_docs = "warn"

[workspace.lints.clippy]
all = { level = "warn", priority = -1 }
correctness = { level = "deny", priority = -1 }
unwrap_used = "warn"
```

Use `#[expect(lint, reason = "...")]` (not `#[allow]`) for local overrides —
stale suppressions then warn on their own.

## Extended guidance

- **`references/idiomatic-patterns.md`** — ownership deep dive (Cow, Arc/Rc,
  mem::take), collections choice, pattern matching, closures, conversions,
  serde
- **`references/api-design.md`** — builders, newtype guards, sealed traits,
  module structure, doc conventions in depth
- **`references/async-and-performance.md`** — tokio patterns, channels,
  cancellation safety, allocation discipline, hot-path profiling, release
  profiles
- **`references/agent-discipline.md`** — the full AI-agent guidelines:
  soundness boundaries, statics, mockable I/O, static verification setup

## References

- **Rust API Guidelines**: https://rust-lang.github.io/api-guidelines/
- **Pragmatic Rust Guidelines (Microsoft)**: https://microsoft.github.io/rust-guidelines/
- **rust-skills rule collection**: https://github.com/leonardomso/rust-skills
- **The Rustonomicon**: https://doc.rust-lang.org/nomicon/
- **The Rust Performance Book**: https://nnethercote.github.io/perf-book/
- **Effective Rust**: https://effective-rust.com/

Adapted from [leonardomso/rust-skills](https://github.com/leonardomso/rust-skills)
and [Microsoft's Pragmatic Rust Guidelines](https://microsoft.github.io/rust-guidelines/)
(both MIT).
