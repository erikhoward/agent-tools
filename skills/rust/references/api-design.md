# API Design

Builders, newtype guards, trait design, module structure, and documentation
conventions for public APIs. Consult when designing a crate's surface or
reviewing API ergonomics.

## Builder Pattern

For construction with more than ~2 optional parameters:

```rust
pub struct Server {
    addr: SocketAddr,
    workers: usize,
    timeout: Duration,
}

#[derive(Default)]
pub struct ServerBuilder {
    workers: Option<usize>,
    timeout: Option<Duration>,
}

impl Server {
    pub fn builder(addr: SocketAddr) -> ServerBuilder {
        ServerBuilder { addr, ..Default::default() }
    }
}

impl ServerBuilder {
    #[must_use]
    pub fn workers(mut self, n: usize) -> Self { self.workers = Some(n); self }

    #[must_use]
    pub fn timeout(mut self, d: Duration) -> Self { self.timeout = Some(d); self }

    /// All validation — including cross-field checks — happens here.
    pub fn build(self) -> Result<Server, ConfigError> {
        let workers = self.workers.unwrap_or_else(num_cpus::get);
        if workers == 0 { return Err(ConfigError::ZeroWorkers); }
        Ok(Server { addr: self.addr, workers, timeout: self.timeout.unwrap_or(DEFAULT_TIMEOUT) })
    }
}
```

Rules:

- Setters named `x()`, not `set_x()`; they consume and return `Self`
- Setters are infallible — every check, including cross-field, lives in
  `Result`-returning `.build()`
- `#[must_use]` on setters so a dropped builder is a warning, not a silent bug
- Required parameters go in `Foo::builder(required...)` — not as builder
  setters
- Constructors with 4+ parameters should be restructured into grouped
  newtypes (`Deposit::new(account: Account, amount: Currency)`) instead

## Newtype Guards

A newtype that encodes an invariant must enforce it at the boundary:

```rust
pub struct Email(String);

impl Email {
    pub fn parse(s: &str) -> Result<Self, InvalidEmail> {
        if s.contains('@') { Ok(Self(s.to_owned())) } else { Err(InvalidEmail) }
    }
}

impl FromStr for Email { type Err = InvalidEmail; /* ... */ }
impl TryFrom<&str> for Email { type Error = InvalidEmail; /* ... */ }
```

- Fallible constructor + `TryFrom`/`FromStr`; **no** infallible `From<String>`
  — that reintroduces the invalid state you built the type to forbid
- Self-validating types are preferred over builder cross-checks: a field that
  cannot be wrong needs no `build()` validation

## Trait Design

- **Sealed traits** — usable by downstream code, implementable only in your
  crate (prevents breakage when you evolve internals):

```rust
mod sealed { pub trait Sealed {} }
pub trait Extension: sealed::Sealed { /* ... */ }
impl sealed::Sealed for String {}
```

- **Extension traits** to add methods to foreign types (`impl MyExt for
  Foreign`)
- Associated type when each impl has exactly one output; generic parameter
  when a type can implement the trait for many inputs
- Blanket impls (`impl<T: Bound> Trait for T`) give behavior to everything
  satisfying the bound — do it deliberately
- Orphan rule: can't implement a foreign trait for a foreign type — wrap the
  type in a newtype instead

## Boundary Flexibility

```rust
// Accept flexible input; store concrete types
fn load(path: impl AsRef<Path>) -> Result<Data, LoadError>
fn tag(label: impl Into<String>) -> Label
fn slice(range: impl RangeBounds<usize>) -> Section
fn read_all(r: impl Read) -> Result<Vec<u8>, IoError>   // sans-IO: any reader
```

- `impl Into<T>` / `AsRef<T>` on parameters — but struct fields stay concrete
  (`String`, `PathBuf`), never `T: AsRef<str>`
- `impl Read`/`impl Write` for one-shot I/O functions — callers bring their
  own source
- `#[non_exhaustive]` on public enums/structs you expect to extend; features
  must be strictly additive; serde stays behind a feature flag in libraries

## Module Structure

- Essential types at the crate root (`foo::Client`), the rest grouped
  semantically (`foo::account`, `foo::network`) — never junk-drawer
  `traits`/`errors`/`utils` modules
- No prelude, no glob re-exports (`pub use foo::*`) — explicit, deliberate
  surface
- Every public item reachable through exactly one path; `#[doc(inline)]` on
  `pub use` so re-exports read as siblings
- `pub(crate)` / `pub(super)` for internals — soundness boundaries equal
  module boundaries, so visibility is also your encapsulation tool
- Parameter order consistent everywhere: call-specific first, ubiquitous
  (loggers) last, closures last and at most one

## Dependency Escalation Ladder

Prefer, in order: **concrete type > generic parameter > `dyn Trait`**.

- Start concrete; add generics when a second implementation actually arrives
- Nesting generics visibly (`Service<Backend<Store>>`) is a design smell —
  wrap in a named concrete type
- Heavyweight shared services implement `Clone` via the `Arc<Inner>` pattern
  so consumers share one instance cheaply

## Documentation Conventions

Canonical sections, present when applicable:

```rust
/// Copies a file from `src` to `dst`.
///
/// Extended documentation in free form.
///
/// # Examples
/// One or more runnable examples. Use `?`, not `.unwrap()`.
///
/// # Errors
/// Every known error condition.
///
/// # Panics
/// When and why the function panics.
///
/// # Safety
/// (unsafe fns) Every condition the caller must uphold.
pub fn copy(src: File, dst: File) -> Result<(), CopyError>
```

- Summary sentence under ~15 words — it is what module listings show
- `//!` module docs: what it contains, when to use it, interaction guarantees
- Intra-doc links (`[`Config`][crate::Config]`) instead of URLs
- Parameters explained in prose — no `# Parameters` tables
- No design-journey narratives or compliance self-reports — document the
  end-state, not the process

Adapted from [leonardomso/rust-skills](https://github.com/leonardomso/rust-skills) and [Microsoft's Pragmatic Rust Guidelines](https://microsoft.github.io/rust-guidelines/) (both MIT).
