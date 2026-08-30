---
name: typescript
description: Use when writing, refactoring, reviewing, or documenting TypeScript code (.ts, .tsx files, tsconfig.json) — strict mode, type narrowing, discriminated unions, generics with constraints, utility types, `unknown` over `any`, `satisfies` and `as const`, `import type`, error handling with Result types, ESLint enforcement, and React component typing.
license: MIT
compatibility: opencode
metadata:
  language: typescript
  sources:
    - https://www.xjavascript.com/blog/typescript-best-practices/
    - https://dev.to/_d7eb1c1703182e3ce1782/typescript-best-practices-for-production-code-in-2026-lb0
    - https://www.tekvers.com/blog/typescript-best-practices-advanced-patterns
  audience: developers
---

# TypeScript Style

Conventions for idiomatic, type-safe TypeScript, synthesized from community
best-practice guides. Apply when writing and reviewing code; enforce
mechanically with ESLint (see the Enforcement Map). For general design
principles, combine with the `solid` skill.

## When to use

- Writing new TypeScript code or refactoring existing code
- Reviewing TypeScript for type correctness and strict-mode compliance
- Designing types, APIs, generics, or discriminated unions
- Building React components and typing their props and state
- Configuring `tsconfig.json` or ESLint

## Verification

Finish every TypeScript change with:

```bash
npx tsc --noEmit           # type-check (must pass)
npx eslint .               # lint (must pass)
npx prettier --check .     # formatting (must pass)
npx vitest                 # or: npx jest
```

Use `import type` so transpilers (esbuild, SWC) can erase type-only imports —
required when `isolatedModules` is enabled.

## Strict mode

Enable `strict: true` plus the extra strictness flags that catch real bugs:

```jsonc
// Good
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitReturns": true,
    "exactOptionalPropertyTypes": true,
    "isolatedModules": true
  }
}

// Bad - strict: false lets null/undefined and implicit any slip through
{
  "compilerOptions": {
    "strict": false
  }
}
```

`strict: true` is a shorthand that turns on:

| Flag | Effect |
|---|---|
| `strictNullChecks` | `null` and `undefined` are distinct from every other type |
| `noImplicitAny` | error on parameters/vars with no inferable type |
| `strictFunctionTypes` | sound function parameter checking |
| `strictBindCallApply` | correct types for `bind` / `call` / `apply` |
| `strictPropertyInitialization` | class fields must be set in the constructor |
| `noImplicitThis` | error on `this` with an implied `any` |
| `useUnknownInCatchVariables` | `catch` variables are `unknown` |
| `alwaysStrict` | emit `"use strict"` |

## `unknown` over `any`

`any` disables type checking — a typo compiles. `unknown` forces narrowing
before use. Reserve `any` for a genuine escape hatch, and mark it with an
eslint-disable comment that says why.

```typescript
// Good - unknown forces narrowing before any use
function formatValue(value: unknown): string {
  if (typeof value === "string") return value.trim();
  if (typeof value === "number") return value.toFixed(2);
  return String(value);
}

// Bad - any disables all checking; a typo compiles
function formatValue(value: any): string {
  return value.toFiexd(2); // typo, no error
}
```

For data crossing a system boundary (HTTP, JSON, user input), validate at
runtime with Zod — see `references/error-handling.md`.

## Type inference vs explicit annotations

Let TypeScript infer locals; annotate function parameters and public API
return types so the surface stays a contract, not an inference artifact.

```typescript
// Good - infer locals; annotate params and the public return type
function parseConfig(raw: string): Config {
  const parsed = JSON.parse(raw) as unknown;  // narrowed next
  return validateConfig(parsed);
}

// Bad - redundant annotation on a local the compiler already knows, plus any
function parseConfig(raw: string): Config {
  const parsed: any = JSON.parse(raw);
  return parsed;
}
```

## `interface` vs `type`

`interface` for an object shape that will be extended (declaration merging,
`extends`). `type` for unions, intersections, mapped types, and tuples —
things an `interface` cannot express.

```typescript
// Good - interface for an extendable object shape
interface User {
  id: string;
  name: string;
}

// Good - type alias for a union (an interface cannot express this)
type Status = "idle" | "loading" | "success" | "error";

// Bad - interface for a union is not expressible; redefining by hand a shape
// meant to be merged is brittle
```

## Utility types

Before writing a new type, ask: can I derive this from an existing type?

| Utility | Derives |
|---|---|
| `Partial<T>` | all properties optional |
| `Required<T>` | all properties required |
| `Readonly<T>` | all properties readonly |
| `Pick<T, K>` | only the selected keys |
| `Omit<T, K>` | all keys except `K` |
| `Record<K, V>` | a map of `K` to `V` |
| `ReturnType<F>` | the return type of a function |
| `Parameters<F>` | the parameter tuple of a function |
| `Awaited<P>` | the unwrapped type of a `Promise` |

```typescript
// Good - derive from an existing type; it tracks User automatically
type UserPatch = Partial<Omit<User, "id">>;

// Bad - redefining the shape by hand; must be kept in sync with User forever
type UserPatch = {
  name?: string;
  email?: string;
};
```

## Discriminated unions

Model mutually exclusive states as a union with a shared literal field.
TypeScript narrows on that field in each `switch` case — no optional-field
guessing.

```typescript
// Good - shared `status` literal narrows in each branch
type RequestState<T> =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; data: T }
  | { status: "error"; error: string };

function render(state: RequestState<User[]>): string {
  switch (state.status) {
    case "idle": return "Waiting";
    case "loading": return "Loading…";
    case "success": return `Got ${state.data.length} users`;
    case "error": return `Failed: ${state.error}`;
  }
}

// Bad - one loose shape with optional fields; every access needs null checks
type RequestState<T> = {
  loading?: boolean;
  data?: T;
  error?: string;
};
```

## Type guards

User-defined `value is T` predicates centralize a narrowing so callers don't
repeat `typeof` / `in` / `instanceof` checks.

```typescript
// Good - predicate narrows the type at every call site
function isError(value: unknown): value is Error {
  return value instanceof Error;
}

if (isError(err)) {
  console.log(err.message);  // narrowed to Error
}

// Bad - inline checks duplicated everywhere; the value stays loosely typed
function handle(value: unknown) {
  if (typeof value === "object" && value && "message" in value) {
    // value is still loosely typed; manual casts follow
  }
}
```

## Generics with constraints

Constrain type parameters with `extends keyof T` so the input and output keep
a real relationship. An unconstrained `<T>` is usually `any` in disguise.

```typescript
// Good - the key is tied to the object; the return type stays precise
function pick<T, K extends keyof T>(obj: T, keys: K[]): Pick<T, K> {
  return keys.reduce((acc, k) => ({ ...acc, [k]: obj[k] }), {} as Pick<T, K>);
}

// Bad - unconstrained T erases the relationship; everything becomes any
function pick<T>(obj: any, keys: string[]): any {
  // ...
}
```

## `as const` and `satisfies`

`as const` keeps literal types instead of widening to the base type.
`satisfies` (TS 4.9+) validates a value against a type without widening it.

```typescript
// Good - as const keeps literal types; typeof [number] yields the union
const directions = ["north", "south", "east", "west"] as const;
type Direction = (typeof directions)[number];  // "north" | "south" | "east" | "west"

// Good - satisfies checks the shape without widening the values
const palette = {
  red: "#f00",
  green: "#0f0",
} satisfies Record<string, string>;
// palette.red is still "#f00", not string

// Bad - widened to string[]; the literal information is gone
const directions = ["north", "south", "east", "west"];
```

## Enums vs union types

Prefer union types or `as const` objects over enums: they tree-shake, have no
runtime cost, and don't emit extra code.

```typescript
// Good - union type, zero runtime cost, tree-shakes
type HttpStatus = 200 | 404 | 500;

// Good - as const object when you need a value/name map at runtime
const HttpStatus = {
  Ok: 200,
  NotFound: 404,
  ServerError: 500,
} as const;
type HttpStatus = (typeof HttpStatus)[keyof typeof HttpStatus];

// Bad - enum emits runtime code and doesn't tree-shake cleanly
enum HttpStatus {
  Ok = 200,
  NotFound = 404,
  ServerError = 500,
}
```

## Null and undefined

Use optional chaining `?.` and nullish coalescing `??`. Avoid the non-null
assertion `!` unless you have just proved the value is non-null.

```typescript
// Good - optional chaining and nullish coalescing
const city = user?.address?.city ?? "Unknown";

// Bad - non-null assertion hides a real null possibility
const city = user!.address!.city;
```

## `import type` and `isolatedModules`

Type-only imports are erased at compile time. Marking them with `import type`
(or the inline `type` modifier) is required when `isolatedModules` is on, so
transpilers like esbuild and SWC can drop types safely.

```typescript
// Good - type-only imports are marked; safe under isolatedModules
import { useState, type ComponentProps, type ReactNode } from "react";
import type { User } from "./types";

// Bad - mixing value and type imports without marking the type ones
import { ComponentProps, ReactNode, useState } from "react";
// a re-export of ComponentProps breaks under isolatedModules
```

## Naming

| Item | Convention | Example |
|---|---|---|
| Variables, functions | camelCase | `parseConfig` |
| Types, interfaces, classes | PascalCase, acronyms as words | `HttpClient`, not `HTTPClient` |
| Constants | SCREAMING_SNAKE_CASE | `MAX_PACKET_SIZE` |
| Type parameters | single letter: `T`, `K`, `V` | |

- Acronyms read as words everywhere: `parseUrl`, `userId`, `HTTPServer`
- Booleans read as predicates: `isActive`, `hasAccess`, `canEdit`

## Never use `as` to lie to the compiler

A type assertion tells the compiler "trust me" and skips the check. Use a
type guard or runtime validation instead. The one legitimate use is when
TypeScript's inference cannot keep up — for example after `.filter(Boolean)`.

```typescript
// Good - a type predicate narrows without any assertion
const names = input.filter((x): x is string => typeof x === "string");

// Good - legitimate `as`: TS cannot narrow filter(Boolean) on its own
const values = input.filter(Boolean) as string[];

// Bad - asserting an empty object is a full User; the field is undefined
const user = {} as User;
user.name;  // typed as string, but undefined at runtime
```

## Enforcement map

Many of these conventions map to typescript-eslint rules — enforce
mechanically where possible. The full rule IDs (prefixed with the
typescript-eslint scope) appear in the config below:

| Convention | Rule |
|---|---|
| `any` usage | `no-explicit-any` |
| Unused variables | `no-unused-vars` |
| Non-null assertion `!` | `no-non-null-assertion` |
| Floating promises | `no-floating-promises` |
| Consistent type imports | `consistent-type-imports` |
| Explicit return types | `explicit-function-return-type` |
| Strict boolean expressions | `strict-boolean-expressions` |

Baseline flat config enabling `recommended` plus the type-checked `strict`
rules:

```js
// eslint.config.js
import tseslint from "typescript-eslint";

export default tseslint.config(
  ...tseslint.configs.recommended,
  ...tseslint.configs.strict,
  {
    rules: {
      "@typescript-eslint/no-explicit-any": "error",
      "@typescript-eslint/no-non-null-assertion": "error",
      "@typescript-eslint/no-floating-promises": "error",
      "@typescript-eslint/consistent-type-imports": "error",
    },
  },
);
```

The `strict` config is type-checked — it needs
`parserOptions.projectService` (or `parserOptions.project`) pointing at your
`tsconfig.json`. Use an inline `// eslint-disable-next-line ...` with a
reason only for a genuine escape hatch, never to hide a real issue.

## Agent discipline

Rules that specifically counter common agent failure modes:

- **Write TypeScript-shaped TypeScript.** Don't port Java/C# patterns 1:1 —
  no boilerplate abstract classes when an interface or type alias does, no
  unnecessary decorators, no getter/setter ceremony a plain field covers
- **Don't use `as` to silence type errors.** Fix the type, or add a type
  guard / runtime validation. The only valid `as` is where inference cannot
  keep up (e.g. after `.filter(Boolean)`)
- **Avoid `any`.** Prefer `unknown` and narrow; for boundary data, validate
  with Zod. Reserve `any` for a true escape hatch, marked with an
  eslint-disable comment that states the reason
- **Don't over-annotate.** Let inference work for locals; annotate public
  APIs (parameters and return types) so the surface is a contract
- **Prefer union types over enums.** They tree-shake and carry no runtime
  cost; reserve enums for the rare case you need a value/name map

## Extended guidance

- **`references/advanced-types.md`** — conditional types, mapped types,
  template literal types, branded types, function overloads, `DeepReadonly`,
  `Async` type transforms, `satisfies` in depth
- **`references/react-patterns.md`** — component props, generic components,
  hooks typing, discriminated unions in React state, event handler types,
  children typing
- **`references/error-handling.md`** — Result type pattern, typed catch
  blocks, runtime validation with Zod, typed fetch wrappers, custom error
  classes with a discriminated `_tag`

## References

- **TypeScript Handbook**: https://www.typescriptlang.org/docs/
- **TSConfig Reference**: https://www.typescriptlang.org/tsconfig
- **Effective TypeScript**: https://effectivetypescript.com/
- **typescript-eslint**: https://typescript-eslint.io/
- **Zod**: https://zod.dev
- **Total TypeScript**: https://www.totaltypescript.com/

Adapted from [xjavascript.com](https://www.xjavascript.com/blog/typescript-best-practices/), [dev.to](https://dev.to/_d7eb1c1703182e3ce1782/typescript-best-practices-for-production-code-in-2026-lb0), and [tekvers.com](https://www.tekvers.com/blog/typescript-best-practices-advanced-patterns).
