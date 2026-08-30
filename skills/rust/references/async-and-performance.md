# Async and Performance

Deep dive on tokio runtime tuning, channel selection, cancellation safety, and the allocation discipline behind fast Rust. Consult when writing async code, tuning hot paths, or configuring build profiles; core conventions live in `../SKILL.md`.

## Tokio runtime and blocking work

| Workload | Runtime |
|---|---|
| Many concurrent connections / I/O | `#[tokio::main]` (multi-threaded, default) |
| CLI tools, tests, single connection | `#[tokio::main(flavor = "current_thread")]` |
| Tuned | `Builder::new_multi_thread().worker_threads(n).enable_all().build()?` |

Worker threads multiplex I/O; they do not compute. CPU-bound or blocking work goes to the blocking pool — roughly: under 10µs inline is fine, 10µs–1ms warrants `spawn_blocking`, longer always does. File I/O uses `tokio::fs` (it wraps blocking calls internally); sync-only libraries get wrapped manually:

```rust
// Good - CPU work (or unavoidable sync I/O) off the worker threads
let digest = tokio::task::spawn_blocking(move || sha256(&data))
    .await
    .expect("blocking task panicked");
```

## Graceful shutdown with CancellationToken

Dropping a `JoinHandle` detaches a task; it does not cancel it. Use `tokio_util::sync::CancellationToken` for cooperative shutdown — clone the token into each task and `select!` against `cancelled()`:

```rust
use tokio_util::sync::CancellationToken;

async fn worker(shutdown: CancellationToken) {
    loop {
        tokio::select! {
            _ = shutdown.cancelled() => {
                cleanup().await;
                break;
            }
            _ = do_work() => {}
        }
    }
}

// Children cancel with their parent: one child token per connection
let conn_token = shutdown.child_token();
```

Trigger once at the top (`signal::ctrl_c()` → `token.cancel()`) and wrap the final task drain in `tokio::time::timeout`.

## Choosing a channel

| Primitive | Use for | Semantics to know |
|---|---|---|
| `mpsc::channel(n)` | Work queues | Bounded; `send().await` blocks when full — backpressure by design |
| `mpsc::unbounded_channel` | Almost never | No backpressure; grows until OOM |
| `broadcast::channel(n)` | Pub/sub events | Every subscriber sees every message; laggards get `RecvError::Lagged(n)`; payload must be `Clone` |
| `watch::channel(init)` | Latest value (config, state) | Slow receivers skip intermediates; never hold the `borrow()` `Ref` across `.await` |
| `oneshot::channel()` | Request-response | Single-use; embed the `Sender` in an mpsc request (actor RPC) |
| `JoinSet` | Dynamic task groups | `join_next()` yields results as they complete; drop aborts the rest |

Size bounded channels near the expected burst, erring small — the point is backpressure, not buffering.

## Cancellation safety in select!

When one `select!` branch completes, every other branch's future is dropped — with its partial state. A branch losing mid-read discards progress silently; it compiles and fails only under load.

| Cancel-safe | Not cancel-safe |
|---|---|
| `mpsc`/`broadcast` `recv()`, `watch::changed()` | `read_exact` — partial buffer dies with the future |
| `oneshot::Receiver`, `sleep`, `Mutex::lock` | `read_to_end` — accumulation is internal |
| `AsyncRead::read` — partial reads surfaced | accumulating into a `Vec` inside the future |

```rust
// Bad - if shutdown wins, the half-read buffer's bytes are gone
tokio::select! {
    _ = stream.read_exact(&mut buf) => { /* ... */ }
    _ = shutdown.cancelled() => break,
}

// Good - buffer lives outside; `read` resumes where it stopped
let mut filled = 0;
tokio::select! {
    n = stream.read(&mut buf[filled..]) => filled += n?,
    _ = shutdown.cancelled() => break,
}
```

## Futures are types — keep them small

Locals held across `.await`, and parameters, become fields of the future's state-machine type: large futures mean memcpy on spawn, deep stacks, slow moves. Track the hot ones:

```rust
async fn hot() -> u32 { /* ... */ }

#[test]
fn hot_future_stays_small() {
    let f = hot();
    assert!(std::mem::size_of_val(&f) < 512);
}
```

- Scope borrows and temporaries so they end before the `.await`; Box large values that must cross one
- Clone `Arc`s (cheap) before `.await` instead of holding borrows of their contents — borrows across `.await` are the classic `!Send` future cause
- Yield cooperatively: `tokio::task::yield_now().await` every 10–100µs of CPU work. Task switches cost hundreds of ns; that interval keeps switching overhead under ~1% while peers still get scheduled

## Allocation discipline

- `with_capacity` when size is known; `collect()` beats push loops (uses `size_hint`)
- Reuse in loops: `.clear()` keeps capacity; `drain(..)` clears while yielding; `x.clone_from(&y)` reuses `x`'s allocation where `x = y.clone()` drops it; `mem::take(&mut buf)` moves a scratch buffer out without cloning
- Box enum variants >128 bytes with small siblings — an enum's size is its largest variant (`clippy::large_enum_variant`)
- Built-once immutable sequences: `Box<[T]>` / `Arc<str>` drop the capacity word and shrink to fit; `Vec<Box<str>>` beats `Vec<String>` for many small entries
- `shrink_to_fit()` long-lived collections grown without reservation

```rust
use std::fmt::Write;

// Good - one allocation, reused across all items
let mut line = String::with_capacity(128);
for item in items {
    line.clear();
    write!(&mut line, "{}: {}", item.name, item.value).unwrap();
    consume(&line);
}
```

## Hot-path idioms

- Iterators over indexing — they eliminate bounds checks; collect once at the end, not per stage
- `entry()` for insert-or-update: one hash and one lookup, not `contains_key` + `insert`
- `write!` into a reused buffer over `format!`, which allocates per call
- Fast hashers (`foldhash`, `FxHash`) for trusted keys; keep the DoS-resistant default for untrusted input
- `BufReader`/`BufWriter` around file and socket streams (8 KiB default; 32–512 KiB for large sequential scans); flush `BufWriter` explicitly — `drop` swallows flush errors

## Release profile, allocator, target

```toml
[profile.release]
lto = "fat"           # "thin": most of the win, much faster builds
codegen-units = 1     # better codegen, slower compile
panic = "abort"       # smaller binary; forfeits catch_unwind isolation
strip = true          # smaller binary; keep symbols in a profiling profile

[profile.bench]
debug = 1             # symbols for profilers and flamegraphs
```

- `panic = "abort"` removes unwinding but makes every panic fatal — don't combine it with per-request `catch_unwind` isolation
- Applications (never libraries): mimalloc as global allocator — cheap throughput on allocation-heavy paths, up to ~25% in Microsoft's benchmarks

```rust
#[global_allocator]
static GLOBAL: mimalloc::MiMalloc = mimalloc::MiMalloc;
```

- Compile for the deployment floor in `.cargo/config.toml` — apps only, since target settings are ignored for libraries:

```toml
[target.x86_64-unknown-linux-gnu]
rustflags = ["-C", "target-cpu=x86-64-v3"]
```

## Profile before optimizing

No optimizing on intuition. Benchmark the hot path (`criterion` or `divan`, `black_box` the inputs), profile (flamegraph, VTune, Superluminal), then fix what the data names. The usual suspects once measured: per-call `format!` and clone allocations, the default hasher on trusted keys, unbuffered I/O, oversized futures.

## Numeric safety

Integer overflow panics in debug and wraps silently in release — choose the behavior explicitly:

| Family | Returns | Use when |
|---|---|---|
| `checked_add` | `Option<T>` | Overflow is an error the caller must handle |
| `saturating_add` | `T` | Clamping at the bound is correct behavior |
| `wrapping_add` | `T` | Modular arithmetic is intended (checksums, ring buffers) |
| `overflowing_add` | `(T, bool)` | Result plus the carry flag |

- No `as` for narrowing casts: `300u32 as u8 == 44`, silently. Widen with `u32::from(x)` (won't compile if lossy), narrow with `u8::try_from(x)?`
- Never compare floats with `==` — rounding, and `NaN != NaN`. Compare within a tolerance; sort with `f64::total_cmp`, which orders `NaN` instead of panicking like `partial_cmp(...).unwrap()`
- `NonZeroU32` forbids zero at the type level and makes `Option<NonZeroU32>` exactly `u32`-sized (niche optimization): the zero check happens once, at construction

Adapted from [leonardomso/rust-skills](https://github.com/leonardomso/rust-skills) and [Microsoft's Pragmatic Rust Guidelines](https://microsoft.github.io/rust-guidelines/) (both MIT).
