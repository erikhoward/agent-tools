---
name: python
description: Use when writing, refactoring, reviewing, or documenting Python code (.py files, pyproject.toml) — idiomatic Python, PEP 8, and type hints; error handling (EAFP), dataclasses, async/await and httpx; testing with pytest; FastAPI and SQLAlchemy patterns; packaging; and the standard toolchain (ruff, black, isort, mypy).
license: MIT
compatibility: opencode
metadata:
  language: python
  sources:
    - https://github.com/affaan-m/ECC/blob/main/skills/python-patterns/SKILL.md
    - https://github.com/manikosto/claude-code-python-stack/blob/main/skills/async-http-patterns/SKILL.md
    - https://github.com/manikosto/claude-code-python-stack/blob/main/skills/fastapi-patterns/SKILL.md
    - https://github.com/manikosto/claude-code-python-stack/blob/main/skills/python-testing/SKILL.md
    - https://github.com/manikosto/claude-code-python-stack/blob/main/skills/sqlalchemy-patterns/SKILL.md
  audience: developers
---

# Python Style

Conventions for idiomatic, readable, and maintainable Python, synthesized from
PEP 8, the Zen of Python, and community pattern collections. Apply when writing
and reviewing code; enforce mechanically with ruff (see the Enforcement Map).
For general design principles, combine with the `solid` skill.

## When to use

- Writing new Python code or refactoring existing code
- Reviewing Python code for style and type correctness
- Designing Python packages, modules, or public APIs
- Building async, FastAPI, or SQLAlchemy applications
- Setting up packaging, testing, or the ruff/mypy toolchain

## Verification

Finish every Python change with:

```bash
ruff check .          # lint (must pass)
ruff format --check . # formatting (or black --check .)
isort --check-only .
mypy .
pytest
```

`ruff format` replaces `black`; pick one, don't mix.

## Formatting & PEP 8

- Line length 88 (black/ruff default) — don't hand-wrap aggressively; let the
  formatter do it
- Indent 4 spaces, never tabs
- One statement per line; no semicolons
- Let the formatter speak for itself; delete comments that restate code

```python
# Good
def get_active_users(users: list[User]) -> list[User]:
    """Return only active users from the provided list."""
    return [user for user in users if user.is_active]


# Bad - terse names, no types, no docstring
def get_active_users(u):
    return [x for x in u if x.a]
```

### Naming

| Item | Convention | Example |
|---|---|---|
| Functions, variables, modules | snake_case | `parse_config` |
| Classes, exceptions, types | UpperCamelCase, acronyms as words | `HttpClient`, not `HTTPClient` |
| Constants | SCREAMING_SNAKE_CASE | `MAX_PACKET_SIZE` |
| Type variables | short: `T`, `T_co` | |
| Internal names | leading underscore | `_helper` |
| Name-mangled private | double leading underscore (class body) | `__internal` |

- Acronyms read as words everywhere: `parse_url`, `HTTPServer`, `user_id`
- Booleans read as predicates: `is_active`, `has_access`, `can_edit`

## Type hints

Annotate public APIs; prefer modern builtins (Python 3.9+) and `X | None`
(3.10+) over `typing` aliases:

```python
# Good - built-in generics, PEP 604 unions
def process(items: list[str]) -> dict[str, int]:
    return {item: len(item) for item in items}


# Bad - obsolete typing aliases in 3.9+ code
from typing import List, Dict, Optional

def process(items: List[str]) -> Dict[str, int]:
    ...

def find(id: str) -> Optional[User]:
    ...
```

```python
# Good
def find(id: str) -> User | None: ...


# Good - modern union syntax
def parse(data: str | bytes) -> JSON: ...
```

Use `Protocol` for structural duck typing — no inheritance required:

```python
from typing import Protocol


class Renderable(Protocol):
    def render(self) -> str: ...


def render_all(items: list[Renderable]) -> str:
    return "\n".join(item.render() for item in items)
```

Use `TypeVar` for generics; bound or constrain when the contract requires it:

```python
from typing import TypeVar

T = TypeVar("T")


def first(items: list[T]) -> T | None:
    return items[0] if items else None
```

- Run `mypy` in strict mode on library code; fix the reported issue, don't
  silence it
- `from __future__ import annotations` lets 3.9 code use `X | None` and
  forward references as strings

## Error handling

**EAFP** — attempt the operation, catch the specific failure. Prefer it over
LBYL when the common case is success:

```python
# Good - EAFP
def get_value(d: dict[str, int], key: str) -> int | None:
    try:
        return d[key]
    except KeyError:
        return None


# Bad - LBYL races and doubles the lookup
def get_value(d: dict[str, int], key: str) -> int | None:
    if key in d:
        return d[key]
    return None
```

Catch specific exceptions — never bare `except:`:

```python
# Good
try:
    with open(path) as f:
        return Config.from_json(f.read())
except FileNotFoundError as e:
    raise ConfigError(f"config not found: {path}") from e
except json.JSONDecodeError as e:
    raise ConfigError(f"invalid JSON in config: {path}") from e


# Bad - swallows everything, including KeyboardInterrupt
try:
    ...
except:
    pass
```

Chain with `raise ... from e` to preserve the traceback:

```python
try:
    parsed = json.loads(data)
except json.JSONDecodeError as e:
    raise ValueError(f"failed to parse data: {data}") from e
```

Define a custom exception hierarchy so callers can catch at the right level:

```python
class AppError(Exception):
    """Base exception for all application errors."""


class ValidationError(AppError):
    """Raised when input validation fails."""


class NotFoundError(AppError):
    """Raised when a requested resource is not found."""
```

## Context managers

Use `with` for every resource with cleanup (files, locks, sessions, DB
transactions):

```python
# Good
def read_config(path: str) -> str:
    with open(path) as f:
        return f.read()


# Bad - manual close, leaks on exception
def read_config(path: str) -> str:
    f = open(path)
    return f.read()
```

`contextlib.contextmanager` for simple cases; a class with
`__enter__`/`__exit__` when state is complex:

```python
from contextlib import contextmanager


@contextmanager
def timer(name: str):
    start = time.perf_counter()
    yield
    print(f"{name} took {time.perf_counter() - start:.4f}s")


with timer("data processing"):
    process_large_dataset()
```

```python
class DatabaseTransaction:
    def __init__(self, connection):
        self.connection = connection

    def __enter__(self):
        self.connection.begin_transaction()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.connection.commit()
        else:
            self.connection.rollback()
        return False  # don't suppress exceptions
```

## Comprehensions & generators

List comprehensions for simple transforms; generator expressions for lazy or
large data; expand complex logic into a named function:

```python
# Good - comprehension for a simple transform
names = [user.name for user in users if user.is_active]


# Bad - manual loop for a trivial transform
names = []
for user in users:
    if user.is_active:
        names.append(user.name)
```

```python
# Good - generator expression, lazy, no intermediate list
total = sum(x * x for x in range(1_000_000))


# Bad - materializes a million-element list first
total = sum([x * x for x in range(1_000_000)])
```

```python
# Bad - too dense to read
result = [x * 2 for x in items if x > 0 if x % 2 == 0]


# Good - readable when logic is non-trivial
def doubled_evens(items: Iterable[int]) -> list[int]:
    return [x * 2 for x in items if x > 0 and x % 2 == 0]
```

Generator functions stream large files without loading them whole:

```python
def read_lines(path: str) -> Iterator[str]:
    with open(path) as f:
        for line in f:
            yield line.strip()
```

## Data classes & named tuples

`@dataclass` for mutable/immutable records with auto-generated `__init__`,
`__repr__`, `__eq__`; `__post_init__` for validation; `slots=True` (3.10+) to
shrink memory:

```python
from dataclasses import dataclass, field


@dataclass
class User:
    id: str
    name: str
    email: str
    is_active: bool = True

    def __post_init__(self) -> None:
        if "@" not in self.email:
            raise ValueError(f"invalid email: {self.email}")
```

`NamedTuple` for lightweight immutable records with field names:

```python
from typing import NamedTuple


class Point(NamedTuple):
    x: float
    y: float
```

`__slots__` on plain classes cuts memory and blocks accidental attribute
creation:

```python
# Good
class Point:
    __slots__ = ("x", "y")

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y


# Bad - per-instance __dict__ bloats memory
class Point:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
```

## Decorators

Always use `@functools.wraps` so the wrapper keeps the original name, doc, and
signature:

```python
import functools


def log_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
```

Parameterized decorators add one wrapping layer that takes the arguments:

```python
def repeat(times: int):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return [func(*args, **kwargs) for _ in range(times)]
        return wrapper
    return decorator
```

## Concurrency

Pick the model by the workload:

- **Threads** — I/O-bound work (network, disk); the GIL releases on I/O
- **Processes** — CPU-bound work; bypasses the GIL via separate interpreters
- **asyncio** — many concurrent I/O streams in one thread; highest throughput
  for fan-out HTTP

```python
# Threads - I/O-bound fan-out
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
    results = list(pool.map(fetch_url, urls))

# Processes - CPU-bound
with concurrent.futures.ProcessPoolExecutor() as pool:
    results = list(pool.map(compute, datasets))

# asyncio - concurrent I/O
results = await asyncio.gather(*(fetch_async(url) for url in urls))
```

For depth — httpx/aiohttp, retry/backoff, streaming, rate limiting, and
respx testing — see `references/async-and-concurrency.md`.

## Packaging & imports

src layout keeps the package importable only when installed, matching the
test environment:

```
myproject/
├── src/
│   └── mypackage/
│       ├── __init__.py
│       ├── api/
│       │   └── __init__.py
│       └── models.py
├── tests/
│   ├── conftest.py
│   └── test_models.py
└── pyproject.toml
```

Import order — stdlib, third-party, local — separated by blank lines:

```python
# Good
import os
from pathlib import Path

import httpx
from fastapi import FastAPI

from mypackage.models import User
```

`__init__.py` exports the public surface; `__all__` makes it explicit:

```python
"""mypackage - a sample Python package."""

__version__ = "1.0.0"

from mypackage.models import User, Post

__all__ = ["User", "Post", "__version__"]
```

## Performance & memory

`__slots__` and `dataclass(slots=True)` cut per-instance memory; generators
stream instead of materializing; `"".join()` beats `+=` in loops:

```python
# Good - O(n)
result = "".join(str(item) for item in items)


# Bad - O(n^2); strings are immutable, each += copies
result = ""
for item in items:
    result += str(item)
```

```python
# Good - yields one line at a time, constant memory
def read_lines(path: str) -> Iterator[str]:
    with open(path) as f:
        for line in f:
            yield line.strip()


# Bad - loads the whole file into a list
def read_lines(path: str) -> list[str]:
    with open(path) as f:
        return [line.strip() for line in f]
```

## Anti-patterns

```python
# Bad - mutable default argument is shared across calls
def append_to(item, items=[]):
    items.append(item)
    return items


# Good - None sentinel, fresh list per call
def append_to(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

```python
# Bad - type() misses subclasses and is brittle
if type(obj) == list:
    process(obj)


# Good - isinstance respects the type hierarchy
if isinstance(obj, list):
    process(obj)
```

```python
# Bad - == None can call user-defined __eq__
if value == None:
    ...


# Good - identity comparison
if value is None:
    ...
```

```python
# Bad - pollutes the namespace, hides origins
from os.path import *


# Good - explicit names
from os.path import join, exists
```

## Enforcement map

Many of these conventions map to ruff rules — enforce mechanically where
possible:

| Convention | Ruff rule |
|---|---|
| Mutable default argument | `B006` |
| Bare `except:` | `E722` |
| `== None` / `!= None` | `E711` |
| `== True` / `== False` | `E712` |
| `from module import *` | `F403` |
| Unused import | `F401` |
| Line too long | `E501` |
| f-string without placeholders | `F541` |

Baseline `pyproject.toml`:

```toml
[tool.ruff]
line-length = 88
select = ["E", "F", "I", "B", "N", "W", "UP"]

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
```

Use `# noqa: <CODE>` only with a specific rule code, and only when the
suppression is justified — never to hide a real issue.

## Agent discipline

Rules that specifically counter common agent failure modes:

- **Write Python-shaped Python.** Don't port Java/Rust patterns 1:1 — no
  boilerplate getters/setters, no over-engineered ABCs when a `Protocol` or a
  plain function does, no `this`/`self`-style ceremony that Python doesn't need
- **Prefer the stdlib and small deps.** `pathlib`, `dataclasses`,
  `contextlib`, `functools`, `concurrent.futures` cover most needs; don't pull
  a library for something the language already does
- **Don't silence — fix.** No `# noqa` or `# type: ignore` to mask a problem;
  fix the issue, or document the specific rule code and the reason
- **Never swallow exceptions.** `except: pass` and `except Exception: pass`
  hide bugs; catch specific exceptions and either handle or re-raise
- **Annotate public APIs, not every local.** Type hints are for the reader and
  mypy; over-annotating trivia adds noise without value

## Extended guidance

- **`references/async-and-concurrency.md`** — async/await, httpx & aiohttp,
  retry/backoff, streaming, rate limiting, respx testing,
  threads-vs-processes-vs-async
- **`references/fastapi.md`** — app factory, Pydantic settings, dependency
  injection, routers, schemas, middleware, WebSockets, background tasks,
  security
- **`references/testing.md`** — pytest, TDD red-green-refactor, fixtures,
  parametrization, mocking, async testing, test organization
- **`references/sqlalchemy.md`** — SQLAlchemy 2.0 async sessions, models,
  relationships, 2.0-style queries, eager loading, repository pattern, Alembic

## References

- **PEP 8 — Style Guide**: https://peps.python.org/pep-0008/
- **PEP 20 — The Zen of Python**: https://peps.python.org/pep-0020/
- **PEP 484 — Type Hints**: https://peps.python.org/pep-0484/
- **The Hitchhiker's Guide to Python**: https://docs.python-guide.org/
- **ruff**: https://docs.astral.sh/ruff/
- **mypy**: https://mypy.readthedocs.io/
- **pytest**: https://docs.pytest.org/
- **FastAPI**: https://fastapi.tiangolo.com/
- **SQLAlchemy 2.0**: https://docs.sqlalchemy.org/en/20/

Adapted from [affaan-m/ECC](https://github.com/affaan-m/ECC) and
[manikosto/claude-code-python-stack](https://github.com/manikosto/claude-code-python-stack).
