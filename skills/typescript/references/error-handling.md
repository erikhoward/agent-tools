# Error Handling

Typed catch blocks, the Result type pattern, runtime validation with Zod, and
typed fetch wrappers. Core conventions live in `../SKILL.md`.

## catch blocks are `unknown`

Under strict mode (`useUnknownInCatchVariables`), a caught value is `unknown`,
not `Error` — anything can be thrown. Narrow before reading its properties.

```typescript
// Good - narrow to Error, then fall back for everything else
try {
  const data = JSON.parse(raw);
} catch (e) {
  if (e instanceof Error) {
    log(e.message);
  } else {
    log(String(e));
  }
}

// Bad - assuming e is an Error; .message may not exist
try {
  const data = JSON.parse(raw);
} catch (e) {
  log(e.message);  // error: e is unknown
}
```

## Result type pattern

Encode success and failure in the return type so callers must handle both.
Use it for expected, recoverable failures a caller will branch on.

```typescript
// Good - the type forces callers to handle both branches
type Ok<T> = { ok: true; value: T };
type Err<E> = { ok: false; error: E };
type Result<T, E = Error> = Ok<T> | Err<E>;

function divide(n: number, d: number): Result<number, string> {
  if (d === 0) return { ok: false, error: "divide by zero" };
  return { ok: true, value: n / d };
}

const r = divide(10, 0);
if (r.ok) {
  console.log(r.value);  // number
} else {
  console.log(r.error);  // string
}

// Bad - throw and hope; the return type hides the failure path
function divide(n: number, d: number): number {
  if (d === 0) throw new Error("divide by zero");
  return n / d;
}
```

## Typed fetch wrappers

`fetch` does not type its response body. A typed wrapper gives every call
site a real return type instead of a cast.

```typescript
// Good - a typed wrapper makes fetchJson<T> a real contract
async function fetchJson<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, init);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json() as Promise<T>;
}

const users = await fetchJson<User[]>("/api/users");

// Bad - fetch returns untyped JSON; the cast lives at every call site
const users = (await (await fetch("/api/users")).json()) as User[];
```

Even better, validate the response at the boundary with Zod (below) so the
type is not just an assertion but a checked guarantee.

## Runtime validation with Zod

A single Zod schema is both the runtime check and the source of the type,
so `as` assertions and hand-written interfaces stay in sync for free.

```typescript
// Good - one schema drives both the runtime check and the type
import { z } from "zod";

const UserSchema = z.object({
  id: z.string(),
  name: z.string(),
  email: z.string().email(),
});
type User = z.infer<typeof UserSchema>;

async function fetchUser(url: string): Promise<User> {
  const res = await fetch(url);
  return UserSchema.parse(await res.json());  // throws on mismatch
}

// Good - safeParse returns a Result-like value when you handle errors locally
const parsed = UserSchema.safeParse(raw);
if (parsed.success) {
  console.log(parsed.data);   // User
} else {
  console.log(parsed.error);  // ZodError
}

// Bad - trust the JSON shape; a missing field is undefined at runtime
const user = (await res.json()) as User;
```

## Custom error classes with a discriminated `_tag`

A `_tag` literal field lets a `switch` narrow a union of error classes without
brittle `instanceof` chains.

```typescript
// Good - a _tag discriminator narrows the error in each branch
class ValidationError extends Error {
  readonly _tag = "ValidationError" as const;
  constructor(public field: string, message: string) {
    super(message);
  }
}

class NotFoundError extends Error {
  readonly _tag = "NotFoundError" as const;
  constructor(public id: string) {
    super(`not found: ${id}`);
  }
}

function report(e: ValidationError | NotFoundError): string {
  switch (e._tag) {
    case "ValidationError": return `${e.field}: ${e.message}`;
    case "NotFoundError": return `missing ${e.id}`;
  }
}

// Bad - instanceof across a wide hierarchy is brittle and order-dependent
function report(e: unknown): string {
  if (e instanceof ValidationError) return (e as ValidationError).field;
  if (e instanceof NotFoundError) return (e as NotFoundError).id;
  return "unknown error";
}
```

## When to use Result vs exceptions

- Use **Result** for expected, recoverable failures a caller will branch on —
  parsing, validation, lookups, optional values
- Use **exceptions** for genuinely exceptional conditions and programmer
  errors — invariant violations, unreachable code, broken assumptions
- At system boundaries (HTTP, JSON parse, user input), **validate with Zod**
  and convert the outcome to a Result or a typed error

Adapted from [xjavascript.com](https://www.xjavascript.com/blog/typescript-best-practices/), [dev.to](https://dev.to/_d7eb1c1703182e3ce1782/typescript-best-practices-for-production-code-in-2026-lb0), and [tekvers.com](https://www.tekvers.com/blog/typescript-best-practices-advanced-patterns).
