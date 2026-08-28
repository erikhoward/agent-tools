# Agent Discipline

The AI-agent and correctness guidelines, written for coding agents: designing code the compiler can review, what not to port, and where panics, `unsafe`, and statics are acceptable. Core conventions live in `../SKILL.md`; this file goes deeper.

## Design for AI review

An agent's lack of genuine understanding is counterbalanced by compiler checks — design so the compiler can do the reviewing:

- **Idiomatic APIs**: the more public and internal APIs look like mainstream Rust, the fewer wrong assumptions get imported. Follow the Rust API Guidelines
- **Thorough docs and runnable examples**: agents lean on documentation harder than humans do; document every module and public item
- **Strong types**: avoid primitive obsession — every invariant moved into a type turns a would-be runtime bug into a compile error
- **Testable APIs**: let callers mock I/O, inject clocks, and unit-test their use; coverage of observable behavior is what enables hands-off refactoring

## Write Rust-shaped Rust

When porting from C#, Java, or Python, separate domain logic (translates freely) from language plumbing (does not translate):

| Doesn't translate | Rust-native answer |
|---|---|
| Exceptions, try/catch | `Result` and `?`; panic only for bugs |
| Reflection | generics, traits, (rarely) `Any`, macros |
| Inheritance, interfaces | composition, generics, `dyn Trait` |
| Null checks — `throw_if_null()` | `Option<T>`: the type makes null impossible |

Statics are the deceptive case — familiar syntax, different semantics (below). Any striking technical similarity between your Rust and the source language signals an architecture problem.

## Panic discipline in depth

**Panic means "stop the program now."** Never use panic to communicate errors upstream, and never assume it will be caught — under `panic = "abort"` every panic is fatal.

- Detected programming bugs panic; they don't return errors. A contract violation (`y == 0` in `divide_by`) has no caller who could act on an `Error` variant — don't invent one. Inherently fallible operations (`parse_uri(&str)`) return `Result`
- Panic messages carry data — what broke, plus the values: `assert!(pct <= 100, "invalid percentage {pct}: must be 0..=100")`
- `catch_unwind` is a last resort: per-request isolation in servers so other requests can drain — then promote a restart. Continuing after a caught panic risks observing "impossible" state; invariants were broken mid-update
- **Correct by construction**: before adding a panic path, try to make it unreachable with types — `NonZeroU32` instead of assert-nonzero, an `Even` newtype instead of a runtime check

## Soundness

`unsafe` marks exactly one thing: misuse risks undefined behavior. Dangerous is not unsafe — `unsafe fn delete_database()` is a category error. And unsound — a safe-looking function that can trigger UB in any calling mode, however unlikely — is never acceptable, no exceptions:

```rust
// Unsound: safe signature, UB for misaligned or wrong-sized T
fn unsound_ref<T>(x: &T) -> &u128 {
    unsafe { std::mem::transmute(x) }
}
```

Soundness boundaries are module boundaries. A safe function may rely on invariants established elsewhere in the same module — that is encapsulation, not unsoundness:

```rust
pub struct Device { ptr: *const u8 } // valid after construction

impl Device {
    fn new() -> Self { /* validates and stores ptr */ }
    pub fn get(&self) -> u8 {
        // SAFETY: `new` validated ptr; only this module can invalidate it.
        unsafe { *self.ptr }
    }
}
```

If you cannot safely encapsulate, expose `unsafe` functions and document the contract instead.

## Avoid statics for consistency

Cargo may link several semver-incompatible copies of one crate into a binary — and during a crate's `0.x` lifetime, every minor is a separate major. Each copy gets its own `static`, so a "global" counter can legitimately read 2, 3, or 5 depending on which copy answers:

```rust
static GLOBAL_COUNTER: AtomicUsize = AtomicUsize::new(0);

pub fn increase_counter() -> usize {
    GLOBAL_COUNTER.fetch_add(1, Ordering::Relaxed)
}
```

Statics used only for performance are fine. Statics whose value must be consistent across the program are not — they also fight unit testing and add contention in thread-per-core designs. Pass the state explicitly.

## Tautological tests

Agents generate tests that re-state the implementation — mirroring constants or copying branches. They pass by construction, verify nothing, and raise the noise floor:

```rust
// Bad - asserts the definition against itself
assert_eq!(CHECKPOINTS, [0, 90, 180, 270]);

// Good - asserts a property the value must satisfy
assert!(CHECKPOINTS.windows(2).all(|w| w[1] - w[0] == 90));
```

If a tautological test exists only to satisfy mutation coverage, skip the mutation instead.

## No meta-design documentation

User-facing docs record end state, never the design journey. Cut on sight:

- self-report tables ("Rule | Applied | Where") summarizing which guidelines were followed, and "why we chose X over Y" essays — they describe process, not behavior
- design journals and process narratives that go stale immediately

A short Design Principles section in the README describing enduring, user-relevant goals (allocation-free, `#[no_std]`) is fine.

## Macros: last resort

"Macros are for when you run out of language." Rust gives you a lot of language — use it first.

- Prefer `macro_rules!` over proc macros when it can do the job: inspectable expansion, faster builds, no syn/quote machinery
- Macros must not lie about signatures — no added parameters, no changed async-ness, no structs-become-enums. What is written must match what happens
- Third-party items a macro needs come from a hidden module in the host crate, so callers never depend on them directly:

```rust
#[doc(hidden)]
pub mod _private {
    pub use ::bar::Bar;
}
// macro emits: impl ::foo::_private::Bar for MyType { ... }
```

- Proc macros: a thin `foo_proc` facade (`proc-macro = true`) delegating to a regular `foo_proc_impl` crate holding the logic, snapshot tests (insta), and trybuild UI tests

## Mockable I/O

Anything non-deterministic, external, or environment-dependent — files, network, clocks, entropy — must be mockable. Libraries don't do ad-hoc `read("foo.txt")`; they accept an injected I/O core, or build mocking in behind a non-public enum:

```rust
pub struct Library {
    core: LibraryCore, // not public
}

enum LibraryCore {
    Native,
    #[cfg(feature = "test-util")]
    Mocked(mock::MockCtrl),
}

impl Library {
    #[cfg(feature = "test-util")]
    pub fn new_mocked() -> (Self, mock::MockCtrl) { /* ... */ }
}
```

Gate every test affordance behind one feature named `test-util` — mocking, sensitive-data inspection, safety-check overrides, fake data — so production builds cannot enable them by accident.

## Static verification setup

Workspace `Cargo.toml`; member crates opt in with `[lints] workspace = true`:

```toml
[workspace.lints.rust]
missing_docs = "warn"
missing_debug_implementations = "warn"
trivial_numeric_casts = "warn"
unsafe_op_in_unsafe_fn = "warn"

[workspace.lints.clippy]
all = { level = "warn", priority = -1 }
correctness = { level = "deny", priority = -1 }
pedantic = { level = "warn", priority = -1 }
clone_on_ref_ptr = "warn" # restriction lints that pay for themselves
map_err_ignore = "warn"
undocumented_unsafe_blocks = "warn"
unused_result_ok = "warn"
```

CI gates beyond fmt and clippy: `cargo-audit` (vulnerable dependencies), `cargo-hack --each-feature` (feature combinations), `cargo-udeps` (unused dependencies), and `cargo miri test` for any crate containing `unsafe`.

## FFI essentials

- `-sys` crates import bindings to an existing C library; `-ffi` crates export C-style APIs from Rust. The suffix tells readers which way the boundary faces
- Core logic lives in a plain Rust crate as idiomatic, safe, testable code; the FFI crate only translates — never let `#[repr(C)]` shapes or ownership-by-pointer leak into the core crate:

```rust
// foo-ffi: translation only; logic stays in `foo`
#[unsafe(no_mangle)]
pub unsafe extern "C" fn transmit_message(
    destination: *const [u8; 8],
    data: *const u8,
    data_len: usize,
) -> u8 {
    // SAFETY: caller guarantees both pointers for the call's duration.
    let (destination, data) = unsafe {
        (*destination, std::slice::from_raw_parts(data, data_len).to_vec())
    };
    match foo::Message::new(destination, data).transmit() {
        Ok(()) => 0,
        Err(_) => 1,
    }
}
```

Adapted from [leonardomso/rust-skills](https://github.com/leonardomso/rust-skills) and [Microsoft's Pragmatic Rust Guidelines](https://microsoft.github.io/rust-guidelines/) (both MIT).
