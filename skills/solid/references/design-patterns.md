# Design Patterns

Reusable solutions to recurring design problems, with guidance on when they help and when they hurt. Consult when a design problem feels familiar (varying algorithms, incompatible interfaces, construction complexity) or when reviewing pattern-heavy code.

## Don't Force Patterns

Let patterns emerge from refactoring; don't design them in upfront. Use a pattern only when:

1. You recognize the problem — you've seen it before
2. The pattern fits without contortion
3. It simplifies the code, not merely names it
4. The team knows it

A pattern applied to a hypothetical problem is speculative generality.

## Pattern Overview

| Pattern | Kind | Use when | Idiomatic form |
|---|---|---|---|
| Singleton | Creational | Exactly one instance must exist | Prefer DI; Go `sync.Once` |
| Factory | Creational | Creation varies by type or is complex | Constructor switch; Python dict dispatch |
| Builder | Creational | Many optional parameters | Go functional options; Python kwargs |
| Prototype | Creational | Cloning beats rebuilding | Copy method; `copy.deepcopy` |
| Adapter | Structural | Interface mismatch at a boundary | Wrapper implementing the target interface |
| Decorator | Structural | Add behavior without modifying | Python decorator; Go middleware |
| Proxy | Structural | Control access: lazy, cache, auth | Wrapper with the same interface |
| Composite | Structural | Tree of uniform parts (UI, files) | Recursive interface |
| Strategy | Behavioral | Interchangeable algorithms | Interface + implementations |
| Observer | Behavioral | Notify N parties of state changes | Callbacks; Go channels; event bus |
| Template Method | Behavioral | Fixed skeleton, varying steps | Higher-order function beats subclassing |
| Command | Behavioral | Encapsulate a request: undo, queue | Object/closure with `execute`/`undo` |

## Worked Examples

### Strategy — Go

```go
type Pricing interface{ Apply(base Money) Money }

type BlackFriday struct{}

func (BlackFriday) Apply(base Money) Money { return base.Times(0.5) }

type Checkout struct{ pricing Pricing }

func (c Checkout) Total(items []Item) Money {
    return c.pricing.Apply(sumItems(items))
}
```

### Factory — Python

```python
def create_notifier(channel: str) -> Notifier:
    return {
        "email": EmailNotifier,
        "sms": SMSNotifier,
        "push": PushNotifier,
    }[channel]()
```

### Builder — Go functional options

```go
type Option func(*Server)

func WithTimeout(d time.Duration) Option {
    return func(s *Server) { s.timeout = d }
}

func NewServer(host string, port int, opts ...Option) *Server {
    s := &Server{host: host, port: port, timeout: 5 * time.Second}
    for _, opt := range opts {
        opt(s)
    }
    return s
}
```

### Adapter — Go

```go
// OldPaymentAPI.ChargeCents(cents int64) bool — third-party, can't change

type Gateway interface{ Charge(m Money) error }

type OldPaymentAdapter struct{ api *OldPaymentAPI }

func (a OldPaymentAdapter) Charge(m Money) error {
    if a.api.ChargeCents(m.Cents()) {
        return nil
    }
    return ErrChargeFailed
}
```

### Decorator — Python

```python
def timed(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = fn(*args, **kwargs)
        log.info("%s took %.3fs", fn.__name__, time.monotonic() - start)
        return result
    return wrapper
```

### Observer — Go

```go
type Listener interface{ OnOrderPlaced(o Order) }

type OrderService struct{ listeners []Listener }

func (s *OrderService) Place(o Order) error {
    if err := s.process(o); err != nil {
        return err
    }
    for _, l := range s.listeners {
        l.OnOrderPlaced(o)
    }
    return nil
}
```

### Command — TypeScript

```typescript
interface Command {
  execute(): void;
  undo(): void;
}

class AddItemCommand implements Command {
  constructor(private cart: Cart, private item: Item) {}
  execute(): void { this.cart.add(this.item); }
  undo(): void { this.cart.remove(this.item); }
}
```

## Pattern Awareness

When reading unfamiliar code or libraries, locate a pattern on four axes:

1. **Problem** — creational, structural, or behavioral?
2. **Scope** — object, module, or system level?
3. **Timing** — wired at startup/compile time or runtime?
4. **Coupling** — tight or loose?

## Anti-Patterns

| Anti-pattern | Problem | Fix |
|---|---|---|
| God object | One module does everything | Split by responsibility |
| Golden hammer | One pattern for every problem | Match pattern to problem |
| Spaghetti code | Tangled, no structure | Refactor to layers |
| Premature optimization | Speed before correctness | Profile first |
| Copy-paste programming | Duplication spreading | Extract after the Rule of Three |

---

Adapted from [ramziddin/solid-skills](https://github.com/ramziddin/solid-skills) (MIT).
