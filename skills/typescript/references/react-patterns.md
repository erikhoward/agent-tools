# React Patterns

Component props, generic components, hook typing, and discriminated unions
for async state in React. Core conventions live in `../SKILL.md`.

## Component props

Type props with an `interface`; model variants and discrete states as string
literal unions, not loose strings.

```typescript
// Good - variant is a literal union; typos are a compile error
interface ButtonProps {
  variant: "primary" | "secondary" | "ghost";
  disabled?: boolean;
  onClick: () => void;
  children: ReactNode;
}

function Button({ variant, disabled, onClick, children }: ButtonProps) {
  // ...
}

// Bad - loose string for a variant; "primay" compiles
interface ButtonProps {
  variant: string;
  disabled?: boolean;
  onClick: () => void;
  children: ReactNode;
}
```

## Generic components

When a component ties an item type to a render prop, make the component
generic so the relationship holds at every call site.

```typescript
// Good - items and renderItem share the type parameter
interface ListProps<T> {
  items: T[];
  renderItem: (item: T) => ReactNode;
  keyOf?: (item: T) => string | number;
}

function List<T>({ items, renderItem, keyOf }: ListProps<T>) {
  return (
    <ul>
      {items.map((item, i) => (
        <li key={keyOf?.(item) ?? i}>{renderItem(item)}</li>
      ))}
    </ul>
  );
}

// Bad - items and renderItem share no type relationship
interface ListProps {
  items: any[];
  renderItem: (item: any) => ReactNode;
}
```

## Typing hooks

Let `useState` infer from the initial value; annotate when it cannot (a
nullable initial value, a union). Type refs for the DOM node. Annotate the
return type of custom hooks — they are a public API.

```typescript
// Good - infer when the initial value is enough; annotate when it is not
const [count, setCount] = useState(0);               // number
const [user, setUser] = useState<User | null>(null); // User | null

// Good - ref typed for the element it attaches to
const inputRef = useRef<HTMLInputElement>(null);

// Good - custom hook annotates its return type
function useDebounced<T>(value: T, delay: number): T {
  // ...
  return value;
}

// Bad - any defeats the point of the hook's state
const [user, setUser] = useState<any>(null);
```

## Discriminated unions for async state

One union, narrowed by a shared `status` literal, replaces a shape full of
optional fields and boolean flags.

```typescript
// Good - each branch narrows cleanly; no optional-field guessing
type AsyncState<T> =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; data: T }
  | { status: "error"; error: string };

function UserList({ state }: { state: AsyncState<User[]> }) {
  switch (state.status) {
    case "idle": return <p>Idle</p>;
    case "loading": return <p>Loading…</p>;
    case "success":
      return <ul>{state.data.map(u => <li key={u.id}>{u.name}</li>)}</ul>;
    case "error": return <p>{state.error}</p>;
  }
}

// Bad - booleans plus optionals; every render branches on guesses
type State = { loading: boolean; data?: User[]; error?: string };
```

## Event handler types

Use React's built-in handler types so `e.target` is narrowed to the right
element.

```typescript
// Good - built-in handler types narrow the element
function onChange(e: ChangeEvent<HTMLInputElement>) {
  setValue(e.target.value);  // e.target is HTMLInputElement
}

function onSubmit(e: FormEvent<HTMLFormElement>) {
  e.preventDefault();
}

// Bad - any loses the element and the target narrowing
function onChange(e: any) {
  setValue(e.target.value);
}
```

## Children typing

`ReactNode` covers strings, numbers, elements, fragments, arrays, and
`null` — the full set React can render. `ReactElement` excludes strings and
fragments, so it rejects valid children.

```typescript
// Good - ReactNode covers everything React can render
interface CardProps {
  children: ReactNode;
}

// Bad - ReactElement rejects strings and fragments
interface CardProps {
  children: ReactElement;
}
```

Adapted from [xjavascript.com](https://www.xjavascript.com/blog/typescript-best-practices/), [dev.to](https://dev.to/_d7eb1c1703182e3ce1782/typescript-best-practices-for-production-code-in-2026-lb0), and [tekvers.com](https://www.tekvers.com/blog/typescript-best-practices-advanced-patterns).
