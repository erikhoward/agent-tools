# Idiomatic Patterns

Ownership deep dive, collections choice, pattern matching, closures,
conversions, const, and serde. Consult when deciding how to structure data
access, or when a construct feels like a fight with the compiler.

## Smart Pointer Decision Table

| Need | Single-threaded | Across threads |
|---|---|---|
| Shared ownership | `Rc<T>` | `Arc<T>` |
| Interior mutability | `RefCell<T>` | `Mutex<T>` / `RwLock<T>` |
| Read-heavy interior mutability | `RefCell<T>` | `RwLock<T>` (reads ≫ writes) |
| Conditional ownership | `Cow<'a, T>` | — |

`Cow<'a, T>` borrows when it can, owns when it must:

```rust
// Good - zero-copy when the input is already valid
fn normalize(name: &str) -> Cow<'_, str> {
    if name.chars().any(|c| c.is_uppercase()) {
        Cow::Owned(name.to_lowercase())
    } else {
        Cow::Borrowed(name)
    }
}
```

## Moving Out of `&mut` Without Cloning

```rust
// Good - takes the value, leaves a default behind
let old = std::mem::take(&mut self.pending);
let prev = std::mem::replace(&mut self.state, State::Idle);
```

**Drop order**: struct fields drop top-to-bottom (declaration order); locals
drop in reverse. When guards and dependencies matter, declare in the order
they should be released in reverse.

## Collections Choice

| Need | Use |
|---|---|
| General sequence | `Vec<T>` (default) |
| Queue / deque | `VecDeque<T>` |
| Key-value, fast unordered | `HashMap<K, V>` |
| Sorted keys, range queries | `BTreeMap<K, V>` |
| Insertion order preserved | `IndexMap<K, V>` |
| Priority / repeated max | `BinaryHeap<T>` |
| Membership / dedup | `HashSet<T>` — never `Vec::contains` in loops |

Never `LinkedList` — it is worse than `Vec` on every axis Rust programs care
about.

## Pattern Matching

```rust
// let-else: early-return extraction
let Some(config) = self.config.as_ref() else {
    return Ok(());
};

// matches! for boolean tests
if matches!(msg, Msg::Error { code: 404, .. }) { /* ... */ }

// @ binding: capture while matching
match event {
    KeyEvent { code @ 65..=90, mods: KeyMods::SHIFT } => upper(code),
    KeyEvent { code, .. } => lower(code),
}
```

- Match enums exhaustively — a catch-all `_` arm silently swallows every
  variant added later
- Prefer `if let` chains (stable 2024) over nested `if let` pyramids

## Closures

Require the least restrictive bound the callback needs —
`Fn` ⊂ `FnMut` ⊂ `FnOnce`, accept the widest:

```rust
// Good - accepts any closure, zero boxing
fn retry<F: FnMut() -> Result<T, E>, T, E>(mut op: F) -> Result<T, E> { /* ... */ }

// Good - return closures as impl, not Box<dyn Fn>
fn tagger(prefix: &'static str) -> impl Fn(String) -> String + 'static {
    move |s| format!("{prefix}:{s}")
}
```

- `move` for closures that outlive the scope; clone what you need *before*
  the `move` to keep the original
- Edition 2021+ captures are disjoint — a closure using only `user.name`
  borrows `user.name`, not all of `user`

## Conversions

| Trait | Direction | Use |
|---|---|---|
| `From<T>` | infallible | implement `From`, get `Into` free — never implement `Into` yourself |
| `TryFrom<T>` | fallible | narrowing casts, validated construction |
| `FromStr` | `&str` → T | enables `"42".parse()` |
| `AsRef<T>` / `AsMut<T>` | cheap borrow | flexible parameters |

`From` also enables `?` — the conversion happens in the operator.

## Const and Compile-Time

- `const fn` for functions that can run at compile time — don't contort code
  for it, mark it when it already qualifies
- `const` for inlined values; `static` for a single addressed instance (and
  see the agent-discipline reference before adding statics)
- `const {}` blocks for compile-time evaluation and assertions inside
  functions
- Const generics `<const N: usize>` for fixed-size abstractions without macros

## Serde Quick Hits

```rust
#[derive(Serialize, Deserialize)]
#[serde(rename_all = "snake_case", deny_unknown_fields)]
struct Config {
    #[serde(default)]
    retries: u32,
    #[serde(skip_serializing_if = "Option::is_none")]
    note: Option<String>,
    #[serde(flatten)]
    extra: BTreeMap<String, Value>,
}
```

- Enum tagging is a deliberate choice: externally (default), internally,
  adjacently, untagged — each changes the wire format
- Validate while deserializing with `#[serde(try_from = "RawConfig")]` —
  parse, don't validate afterward
- Custom field handling: `#[serde(with = "...")]` or
  `serialize_with`/`deserialize_with`

Adapted from [leonardomso/rust-skills](https://github.com/leonardomso/rust-skills) and [Microsoft's Pragmatic Rust Guidelines](https://microsoft.github.io/rust-guidelines/) (both MIT).
