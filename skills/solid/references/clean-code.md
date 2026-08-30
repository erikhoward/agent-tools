# Clean Code

Naming, function structure, value objects, and comments — the practices that keep code readable and changeable. Consult when writing or reviewing any code, naming things, or deciding how to structure a function.

Clean code is easy to understand, easy to change, and easy to test. Developers read code 10x more than they write it — write for the reader.

## Naming

Priority order — when two rules conflict, the higher one wins:

| Priority | Rule | Bad | Good |
|---|---|---|---|
| 1 | Consistency: one name per concept | `getUserById` / `fetchCustomer` | `getUser` / `getOrder` |
| 2 | Domain language, not jargon | `arr` | `activeCustomers` |
| 3 | Specificity: no `data`, `info`, `manager`, `utils` | `DataManager.processInfo` | `OrderRepository.validatePayment` |
| 4 | Brevity — never at clarity's expense | `usrLst`, `listOfAllActiveUsers` | `activeUsers` |
| 5 | Searchability | `data` | `orderSummary` |

Also: pronounceable (`genymdhms` → `timestamp`); no filler (`userData`, `UserClass`); no abbreviations — if a name is too long to type, the module is doing too much.

## Function Structure

- Early returns and guard clauses over `else` chains
- One level of indentation per function where reasonable — extract instead of nesting
- Small functions; each does one thing at one level of abstraction
- Reads top-to-bottom like a story: public API and high level first, details below

```typescript
// Bad: nested
function process(orders: Order[]) {
  for (const order of orders) {
    if (order.isValid()) {
      for (const item of order.items) {
        if (item.inStock) { /* ... */ }
      }
    }
  }
}

// Good: filter + extract
function process(orders: Order[]) {
  orders.filter(o => o.isValid()).forEach(processOrder);
}
```

Go encodes the same shape — errors are values, handled with early returns:

```go
func Publish(ctx context.Context, order Order) error {
    if err := order.Validate(); err != nil {
        return fmt.Errorf("validate order: %w", err)
    }
    if err := broker.Publish(ctx, order); err != nil {
        return fmt.Errorf("publish order: %w", err)
    }
    return nil
}
```

## Value Objects

Wrap domain primitives (IDs, emails, money) in types instead of passing raw strings and ints across boundaries. Invalid values then cannot exist, and validation happens once at construction.

```typescript
// Bad: raw primitive, validation scattered
function createUser(email: string, age: number) { /* validate where? */ }

// Good: invalid values can't exist
class Email {
  constructor(readonly value: string) {
    if (!value.includes('@')) throw new InvalidEmail(value);
  }
}
function createUser(email: Email, age: Age) { /* already valid */ }
```

Python with a frozen dataclass — immutable and self-validating:

```python
@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        if "@" not in self.value:
            raise InvalidEmail(self.value)
```

## Tell, Don't Ask

Only talk to immediate friends (Law of Demeter) — don't reach through object graphs. Give modules behavior, not getters: callers say what they want, the module decides how.

```typescript
// Bad: train wreck + caller doing the work
const city = order.customer.address.city;
if (account.getBalance() >= amount) {
  account.setBalance(account.getBalance() - amount);
}

// Good: tell, don't ask
const city = order.getShippingCity();
const result = account.withdraw(amount);
```

## Object Calisthenics

Practice rules. Follow them strictly when learning; apply with judgment in production.

| Rule | Point |
|---|---|
| One indent level per function | Extract over nest |
| No `else` | Early returns, guard clauses |
| Wrap primitives | Value objects |
| First-class collections | A collection + its behavior = one type |
| One dot per line | Law of Demeter |
| Don't abbreviate | Long name = too-big module |
| Keep entities small | Functions ~<10 lines, modules ~<50 |
| Two instance variables max | Forces composition |
| No getters/setters | Behavior over data |

Size limits are heuristics. Exceed them deliberately, when cohesion stays high.

## Duplication

Tolerate a little duplication before abstracting — extract shared code at the Rule of Three (third occurrence, not second). A little duplication beats the wrong abstraction.

## Comments

Comments explain WHY — business reasons, non-obvious decisions, warnings. Code already says WHAT and HOW.

```typescript
// Bad: restates the code
counter++; // add 1

// Good: the why
counter++; // legacy API is 0-based; compensate
```

Prefer renaming to commenting: `if (user.canAccessPremiumFeatures())` needs no comment. A comment explaining bad code is a smell — rename or extract instead.

## Formatting

- Related code together; blank lines between concepts
- Public API at top, details below
- ~80-120 character lines; consistent indentation
- Follow the project's formatter — never hand-format around it

---

Adapted from [ramziddin/solid-skills](https://github.com/ramziddin/solid-skills) (MIT).
