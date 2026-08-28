# SOLID Principles

The five principles for structuring modules: what each solves, how to apply it, and how to spot violations. Consult when designing a module, deciding where new code belongs, or when coupling makes every change hurt. Ask all five on every module — class, struct, function set, package, or service:

| Principle | Question to ask |
|---|---|
| **S**ingle Responsibility | Does this have ONE reason to change? |
| **O**pen/Closed | Can I extend without modifying? |
| **L**iskov Substitution | Can subtypes replace base types safely? |
| **I**nterface Segregation | Are clients forced to depend on unused methods? |
| **D**ependency Inversion | Do high-level modules depend on abstractions? |

## S — Single Responsibility

> A module should have one, and only one, reason to change.

**Problem**: god modules that do everything — hard to test, change, and understand.

**Detection**: you describe it with "and"; different stakeholders would request changes to different parts.

```typescript
// Bad: three reasons to change — pricing, persistence, reporting
class Order {
  calculateTotal(): number { /* ... */ }
  saveToDatabase(): void { /* ... */ }
  generateInvoice(): string { /* ... */ }
}

// Good: one reason each, collaborating as separate modules
class OrderRepository { save(order: Order): Promise<void> { /* ... */ } }
class InvoiceGenerator { generate(order: Order): Invoice { /* ... */ } }
```

No classes required — plain modules of functions split the same way:

```python
# pricing.py — changes when pricing rules change
def calculate_total(order: Order) -> Money: ...

# repository.py — changes when storage changes
def save(order: Order) -> None: ...
```

## O — Open/Closed

> Open for extension, closed for modification.

**Problem**: every new requirement means editing tested, working code.

**Apply**: create seams where new behavior arrives as new code — a new interface implementation, function value, or module — not a new branch in existing logic.

```typescript
// Bad: every export format edits (and re-tests) this function
function exportReport(format: string, report: Report): string {
  if (format === 'csv') return toCsv(report);
  if (format === 'json') return JSON.stringify(report);
  throw new Error(`Unknown format: ${format}`);
}

// Good: new format = new implementation, nothing existing changes
interface ReportExporter {
  export(report: Report): string;
}
class CsvExporter implements ReportExporter {
  export(report: Report): string { return toCsv(report); }
}
class PdfExporter implements ReportExporter { /* add formats as files, not edits */ }
```

**Architecturally**: new features should be additive — new modules wired in, existing modules untouched.

## L — Liskov Substitution

> Subtypes must be substitutable for their base types without altering correctness.

**Problem**: subtypes that break the parent's contract force type-checks and special cases in callers.

**Apply**: a subtype honors the contract — accepts everything the parent accepts, guarantees everything the parent guarantees. If `getDiscount` returns non-negative numbers, no subtype returns negatives; if the parent never throws, no subtype throws.

**Detection**: `instanceof` or type-checks in calling code; a subtype that rejects input the parent accepted.

Substitutability is why `InMemoryUserRepo` swaps cleanly for `PostgresUserRepo`, and why test doubles are safe. Go gets it without inheritance — any type satisfying the interface is a valid substitute:

```go
type Notifier interface {
    Notify(ctx context.Context, userID, msg string) error
}

type EmailNotifier struct{ /* smtp client */ }
func (e EmailNotifier) Notify(ctx context.Context, userID, msg string) error { /* ... */ }

type LogNotifier struct{}
func (l LogNotifier) Notify(ctx context.Context, userID, msg string) error { /* ... */ }
```

## I — Interface Segregation

> Clients should not be forced to depend on methods they do not use.

**Problem**: fat interfaces force partial implementations — empty bodies, throwing stubs.

**Detection**: any implementation method that is empty, throws, or is never called by a real client.

Split so each client sees only what it calls. Go's idiom: interfaces belong to the consumer and stay tiny — often one or two methods:

```go
// The consumer declares what it needs — nothing more.
type LabelPrinter interface {
    PrintLabel(orderID string) error
}

func dispatch(p LabelPrinter, orderID string) error {
    return p.PrintLabel(orderID) // unaware of scanning, packaging
}
```

In TypeScript, split fat interfaces into small ones; compose with `extends` only when a caller genuinely needs more. Prefer several small consumer-side interfaces over one provider-side god interface.

## D — Dependency Inversion

> High-level modules should not depend on low-level modules. Both depend on abstractions.

**Problem**: business logic locked to a concrete database, provider, or framework — untestable, unswappable.

**Apply**: define the abstraction where the high-level policy lives; low-level details implement it. This is the Dependency Rule: dependencies point inward toward the domain; infrastructure depends on domain, never the reverse.

```typescript
// Bad: locked to a concrete provider
class OrderService {
  private email = new SendGridEmailService();
}

// Good: abstraction, implementation injected
interface EmailService { send(to: string, message: string): void; }

class OrderService {
  constructor(private email: EmailService) {}
  confirm(to: string): void { this.email.send(to, 'Order confirmed'); }
}
```

Same shape in Go — small interface field, wired in the constructor, errors as values:

```go
type EmailSender interface {
    Send(ctx context.Context, to, msg string) error
}

type OrderService struct{ email EmailSender }

func NewOrderService(email EmailSender) *OrderService {
    return &OrderService{email: email}
}

func (s *OrderService) Confirm(ctx context.Context, to string) error {
    return s.email.Send(ctx, to, "Order confirmed") // error returned as a value
}
```

Invert only at boundaries that matter (I/O, third parties, anything slow or external). Inverting pure logic is accidental complexity — the Four Elements of Simple Design rank minimal above flexible.

## SOLID Beyond the Module

The principles scale from types to services and bounded contexts: one responsibility per context (SRP), new features as new modules rather than edits (OCP), substitutable services sharing a contract (LSP), thin interfaces between services (ISP), and domain logic that knows nothing of databases or frameworks (DIP). See architecture.md for the dependency rule.

## Quick Reference

| Principle | One-liner | Red flag |
|---|---|---|
| SRP | One reason to change | "This module handles X and Y and Z" |
| OCP | Add, don't modify | `if/else` chains keyed on type |
| LSP | Subtypes are substitutable | Type-checks in calling code |
| ISP | Small, focused interfaces | Empty or throwing implementations |
| DIP | Depend on abstractions | `new Concrete()` inside business logic |

---

Adapted from [ramziddin/solid-skills](https://github.com/ramziddin/solid-skills) (MIT).
