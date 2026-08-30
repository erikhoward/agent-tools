# Advanced Types

Conditional types, mapped types, template literal types, branded types, and
function overloads for expressing precise contracts. Core conventions live
in `../SKILL.md`.

## Conditional types

`T extends U ? X : Y` selects a type based on a relationship; the `infer`
keyword extracts a type from a pattern.

```typescript
// Good - branch on a type relationship
type IsString<T> = T extends string ? true : false;
type A = IsString<"hi">;  // true
type B = IsString<42>;    // false

// Good - infer pulls the element type out of an array pattern
type ArrayElement<T> = T extends (infer U)[] ? U : never;
type Item = ArrayElement<string[]>;  // string

// Good - recursively unwrap nested Promises
type Unwrap<T> = T extends Promise<infer U> ? Unwrap<U> : T;
type R = Unwrap<Promise<Promise<number>>>;  // number

// Bad - hardcoding every combination; loses generality and must be kept in sync
type UnwrapString = string;
type UnwrapNumberPromise = number;
// ...
```

## Mapped types

Map over an object's keys to transform each property's type.

```typescript
type Nullable<T> = { [K in keyof T]: T[K] | null };

type DeepReadonly<T> = {
  readonly [K in keyof T]: T[K] extends object ? DeepReadonly<T[K]> : T[K];
};

type Async<T> = {
  [K in keyof T]: Promise<T[K]>;
};

type FormErrors<T> = {
  [K in keyof T]?: string;
};

type Stringify<T> = {
  [K in keyof T]: string;
};

// Good - derive once; every field follows
type AsyncUser = Async<User>;  // { id: Promise<string>; name: Promise<string> }

// Bad - rewriting the async shape by hand for each model
type AsyncUser = {
  id: Promise<string>;
  name: Promise<string>;
};
```

## Template literal types

Compose string literal types from unions — event names, API routes, CSS
properties, env keys.

```typescript
// Good - event handler names derived from an event union
type EventName = "click" | "focus" | "blur";
type Handler = `on${Capitalize<EventName>}`;  // "onClick" | "onFocus" | "onBlur"

// Good - typed API route strings
type HttpMethod = "GET" | "POST";
type ApiRoute = `${HttpMethod} /api/${string}`;  // "GET /api/users" | "POST /api/users" | ...

// Good - CSS margin property names
type MarginKey = `margin${"" | "Top" | "Right" | "Bottom" | "Left"}`;

// Good - uppercased env config keys
type EnvKey<K extends string> = Uppercase<K>;

// Bad - a loose string for routes; "/api/" typos compile
type ApiRoute = string;
```

## Branded types (nominal typing)

TypeScript is structurally typed, so two `string` aliases are assignable to
each other. A brand field makes distinct IDs incompatible at compile time.

```typescript
// Good - the brand field makes UserId and ProductId incompatible
interface Brand<T extends string> {
  readonly __brand: T;
}
type UserId = string & Brand<"UserId">;
type ProductId = string & Brand<"ProductId">;

function fetchUser(id: UserId): Promise<User> { /* ... */ }

declare const uid: UserId;
declare const pid: ProductId;
fetchUser(pid);  // error: ProductId is not assignable to UserId

// Bad - both are just string; the wrong ID type compiles
function fetchUser(id: string): Promise<User> { /* ... */ }
fetchUser(productId);  // no error
```

Construct branded values through a smart constructor that validates the
input, not by casting raw strings at every call site.

## Function overloads

Overloads give callers a precise return type per input shape, while a single
implementation signature handles the runtime.

```typescript
// Good - each overload promises a specific return type
function parse(input: string): unknown;
function parse<T>(input: string, reviver: (value: unknown) => T): T;
function parse<T>(input: string, reviver?: (value: unknown) => T): unknown {
  return JSON.parse(input, reviver as JSONReviver);
}

const obj = parse(raw);        // unknown
const typed = parse(raw, r => r as User);  // User

// Bad - one broad signature forces callers to cast at every use
function parse(input: string, reviver?: Function): any;
```

- The implementation signature is not visible to callers; keep it permissive
- Order overloads from most specific to least specific
- Prefer a generic signature when the overloads are just `T` variants of the
  same shape; reach for overloads when the return type changes by argument
  count or literal value

## `satisfies` in depth

`satisfies` validates a value against a type without widening it, so the
original literal types survive for later narrowing.

```typescript
// Good - validates the shape but keeps the literal value types
const config = {
  port: 8080,
  host: "localhost",
} satisfies Config;
// config.port is still `8080`, not `number`

// Good - catches missing keys and wrong shapes at the definition site
const routes = {
  home: "/",
  about: "/about",
} satisfies Record<string, `/${string}`>;

// Bad - annotating the variable widens the literals away
const config: Config = { port: 8080, host: "localhost" };
// config.port is now `number`; the literal `8080` is lost
```

Use `satisfies` whenever you want "this value must conform to a shape, but I
still want its narrowest type downstream."

Adapted from [xjavascript.com](https://www.xjavascript.com/blog/typescript-best-practices/), [dev.to](https://dev.to/_d7eb1c1703182e3ce1782/typescript-best-practices-for-production-code-in-2026-lb0), and [tekvers.com](https://www.tekvers.com/blog/typescript-best-practices-advanced-patterns).
