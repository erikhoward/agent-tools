# Code Smells

A catalog of smells — indicators that design may be wrong — with detection symptoms and fixes. Consult when reviewing code, planning a refactor, or when a change felt harder than it should have been.

Smells are not bugs, and not every smell needs fixing — confirm it's a real problem before refactoring.

## The Five Categories

### Bloaters — code grown too large

| Smell | Symptom | Fix |
|---|---|---|
| Long method | > ~10 lines, multiple jobs | Extract functions |
| Large module | Multiple responsibilities | Split by responsibility |
| Long parameter list | > ~3 parameters | Introduce parameter object |
| Data clumps | Same variables always travel together | Extract a type |
| Primitive obsession | Raw strings/ints for domain concepts | Value objects (see clean-code.md) |

### Misuse of polymorphism

| Smell | Symptom | Fix |
|---|---|---|
| Switch-on-type | Type dispatch, same switch repeated | Polymorphism |
| Refused bequest | Subtype ignores inherited behavior | Replace inheritance with delegation |
| Parallel hierarchies | Adding a subtype forces one elsewhere | Merge or link the hierarchies |

### Change preventers

| Smell | Symptom | Fix |
|---|---|---|
| Divergent change | One module changed for many reasons | Split into focused modules |
| Shotgun surgery | One change touches many modules | Move related code together |

### Dispensables — delete these

| Smell | Symptom | Fix |
|---|---|---|
| Duplicate code | Copy-paste | Extract — after the Rule of Three |
| Dead code | Unreachable, unused | Delete |
| Speculative generality | "Just in case" abstractions | Delete (YAGNI) |
| Comment-annotated code | Comment replaces clarity | Rename, extract |
| Lazy module | Does almost nothing | Inline it |

### Couplers

| Smell | Symptom | Fix |
|---|---|---|
| Feature envy | Function uses another module's data more than its own | Move it there |
| Inappropriate intimacy | Modules poke at each other's internals | Tell, don't ask |
| Message chains | `a.getB().getC().getD()` | Hide delegate |
| Middle man | Module only forwards calls | Inline it |

## Worked Examples

### Long Method

Symptom: multiple jobs, comment headers as section titles, deep nesting.

```typescript
// Bad
function processOrder(order: Order) {
  if (!order.items.length) throw new Error('Empty');
  let total = 0;
  for (const item of order.items) {
    total += item.price * item.quantity - (item.discount ?? 0);
  }
  db.orders.insert({ ...order, total });
  emailService.send(order.customer.email, 'Order confirmed');
}

// Good — the outline is the documentation
function processOrder(order: Order) {
  validate(order);
  const total = calculateTotal(order);
  save(order, total);
  notifyCustomer(order);
}
```

### Feature Envy

Symptom: a function reads another module's data more than its own. Move it to the data it envies.

```python
# Bad: shipping logic lives far from the data it uses
def calculate_shipping(customer: Customer) -> Decimal:
    if customer.country == "US":
        return Decimal("10") if customer.state == "CA" else Decimal("15")
    return Decimal("25")

# Good: moved next to the fields it depends on
class Customer:
    def shipping_cost(self) -> Decimal:
        if self.country == "US":
            return Decimal("10") if self.state == "CA" else Decimal("15")
        return Decimal("25")
```

### Switch-on-Type

Symptom: the same type switch (or `if/else` chain on a type tag) appears in more than one place. Replace with polymorphism so the behavior travels with the type.

```go
// Bad: this switch repeats in Area, Perimeter, Describe...
func Area(s Shape) float64 {
    switch s := s.(type) {
    case Circle:
        return math.Pi * s.Radius * s.Radius
    case Rect:
        return s.W * s.H
    }
    return 0
}

// Good: one behavior, one place
type Shape interface {
    Area() float64
    Perimeter() float64
}

func (c Circle) Area() float64 { return math.Pi * c.Radius * c.Radius }
func (r Rect) Area() float64   { return r.W * r.H }
```

A single switch can be fine (e.g., parsing at the system boundary). Repeated switches are the smell.

### Speculative Generality

Symptom: interfaces with one implementation, "just in case" hooks, parameters no caller uses.

```typescript
// Bad
interface PaymentProcessor {
  process(): void;
  rollback(): void; // never called
  audit(): void;    // never called
}

// Good — add methods when a real caller exists
interface PaymentProcessor {
  process(): void;
}
```

## When You Find a Smell

1. Confirm it's a problem — smells are indicators, not verdicts
2. Ensure tests cover the behavior before touching it
3. Refactor in small steps; run tests after each
4. Stop at "good enough" — the Four Elements of Simple Design define done

---

Adapted from [ramziddin/solid-skills](https://github.com/ramziddin/solid-skills) (MIT).
