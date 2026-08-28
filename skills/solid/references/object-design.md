# Object Design

How to assign responsibilities to modules and types: stereotypes, tell-don't-ask, contracts, composition, polymorphism, value objects, and aggregates. Consult when designing a new module, splitting a god module, or deciding where a piece of behavior belongs.

## Responsibility-Driven Design

Modules and objects are defined by their **responsibilities, not their data**.

Find candidates from the requirements:
- **Nouns** → candidate modules/types
- **Verbs** → candidate behaviors
- **Domain concepts** → value objects

Every module should answer: what does it **know**, what does it **do**, what does it **decide**?

## Object Stereotypes

Every module fits one — maybe two — stereotypes:

| Stereotype | Purpose | Example |
|---|---|---|
| Information holder | Knows things, holds data | `User`, `Product` |
| Structurer | Maintains relationships | `OrderItems`, `UserGroup` |
| Service provider | Performs work | `PaymentProcessor`, `EmailSender` |
| Coordinator | Orchestrates workflow | `OrderFulfillment` |
| Controller | Makes decisions, delegates | `CheckoutHandler` |
| Interfacer | Translates between systems | `UserAPIAdapter`, DB mapper |

For every module ask: (1) **What stereotype is this?** (2) **Is it doing too much?** If you can't answer cleanly, refactor. Two stereotypes means two modules.

## Tell, Don't Ask

Command; don't interrogate and do the work yourself. The module that has the data should have the behavior.

```typescript
// Bad: asking, then doing
if (account.balance >= amount) account.balance -= amount;

// Good: telling
const result = account.withdraw(amount);
```

## Design by Contract

Every method has:
- **Preconditions** — what must be true before calling
- **Postconditions** — what will be true after
- **Invariants** — what is always true about the module

```go
// Invariant: balance is never negative.
// Precondition: amount > 0.
// Postcondition: balance decreased, or an error explains why not.
func (a *Account) Withdraw(amount Money) (Money, error) {
    if !amount.IsPositive() {
        return a.balance, ErrInvalidAmount
    }
    if a.balance.LessThan(amount) {
        return a.balance, ErrInsufficientFunds
    }
    a.balance = a.balance.Minus(amount)
    return a.balance, nil
}
```

Go and Rust push postconditions into the type system (`error`, `Result`); Python and TypeScript rely on validation plus tests.

## Composition Over Inheritance

Inheritance couples parent to child (fragile base class). Reserve it for a true "is-a" relationship or an intentional template method. Otherwise compose.

```go
type DiscountPolicy interface{ Calculate() Percent }

type User struct{ discount DiscountPolicy } // pluggable behavior

func (u User) Discount() Percent { return u.discount.Calculate() }
```

Go omits implementation inheritance entirely — if a design only works via inheritance, that's a signal to reconsider the design, not the language.

## Law of Demeter

Only talk to immediate friends: `this`/self, parameters, objects you create, direct components.

```typescript
// Bad: reaching through objects
order.getCustomer().getAddress().getCity();

// Good: ask the immediate friend
order.shippingCity();
```

Changes to `Address` no longer ripple through every caller.

## Encapsulation

Hide internals; expose behavior. Levels: **data** (private fields), **implementation** (how it works), **type** (concrete behind an interface), **design** (architecture hidden from clients).

```python
# Bad: clients can corrupt state
order.items.append(item)   # bypasses validation
order.total = -999

# Good: state changes only through behavior
order.add_item(item)       # recalculates and validates
```

## Polymorphism

Replace conditionals with types — switch-on-type becomes dispatch.

```go
type ShippingMethod interface{ Cost(orderValue Money) Money }

func shippingCost(m ShippingMethod, orderValue Money) Money {
    return m.Cost(orderValue) // no branch on method name
}
```

## Value Objects vs Entities

| | Value object | Entity |
|---|---|---|
| Identity | Attributes only | Explicit ID, survives changes |
| Mutability | Immutable | Mutable via methods |
| Equality | By value | By identity |
| Examples | `Money`, `Email`, `DateRange` | `User`, `Order` |

```go
type Money struct {
    amount   int64 // minor units
    currency string
}

func (m Money) Add(other Money) (Money, error) {
    if m.currency != other.currency {
        return Money{}, ErrCurrencyMismatch
    }
    return Money{m.amount + other.amount, m.currency}, nil
}
```

## Aggregates

A cluster of objects changed as a single unit. One object is the **aggregate root**; external code references only the root, and the root enforces invariants for the whole cluster.

```typescript
// Bad: bypasses validation
order.items.push(new OrderItem(product, 2));

// Good: through the root — invariant checked
order.addItem(product, 2);
```

---

Adapted from [ramziddin/solid-skills](https://github.com/ramziddin/solid-skills) (MIT).
