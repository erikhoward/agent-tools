# Testing Strategy

How to distribute test effort across the pyramid, what each type is for, and the vocabulary of test doubles. Consult when planning test coverage, choosing what to mock, or deciding where a test belongs.

## The Testing Pyramid

```
       /\         E2E (few)      — full system, critical paths only
      /----\      Integration (some) — components together, boundaries
     /--------\   Unit (many)    — single unit, fast, isolated
```

More tests at the bottom, fewer at the top. Inverting the pyramid (many slow,
brittle E2E tests) is the classic failure mode.

## Test Types

| Type | Scope | Speed | What it proves |
|---|---|---|---|
| Unit | One function/module | Milliseconds | Logic is correct |
| Integration | Components together | Seconds | Boundaries work |
| E2E | Whole system, user perspective | Slowest | Critical paths work |

Test at the lowest level that can fail. Push tests down the pyramid whenever
possible.

## Arrange-Act-Assert

Every test, always:

```go
func TestCheckoutAppliesDiscount(t *testing.T) {
    // arrange
    cart := NewCart(PremiumUser())
    cart.Add(Item{Price: 100})

    // act
    total := cart.Total()

    // assert
    if total != 80 {
        t.Errorf("Total() = %d, want 80", total)
    }
}
```

Stuck writing a test? Write it backwards: assert → act → arrange.

## Test Naming

Concrete examples in domain language:

```
Bad:  should_work_correctly / handles_the_edge_case / sets_data_property
Good: calculates_20pct_discount_for_premium_users / returns_error_when_cart_is_empty
```

Formats: `should <behavior>`, `when <action> then <result>`, or
given/when/then nesting for complex scenarios. One behavior per test — a test
that fails for two reasons is two tests.

## Test Doubles

| Double | Purpose | Example use |
|---|---|---|
| **Dummy** | Passed, never used | Filling a required parameter |
| **Stub** | Returns predefined values | "The repo says the user exists" |
| **Spy** | Records how it was called | Asserting an email was sent |
| **Mock** | Verifies expected interactions | Protocol conformance at boundaries |
| **Fake** | Working simplified implementation | In-memory repository |

```go
// Fake — a working, simplified repository
type inMemoryRepo struct{ users map[string]User }

func (r *inMemoryRepo) Save(u User) error { r.users[u.ID] = u; return nil }
func (r *inMemoryRepo) Find(id string) (User, error) { /* ... */ }
```

Prefer fakes over mocks: they verify behavior without coupling the test to
call sequences. Mock only at true external boundaries.

## Strategy by Layer

| Layer | Test with | Focus |
|---|---|---|
| Domain | Plain unit tests, no mocks | Business rules, value objects, invariants |
| Application | Integration with fakes for infrastructure | Use-case orchestration |
| Infrastructure | Integration against real dependencies | Database, API adapters |

## High-Value Integration Tests

Focus integration effort on:

1. **Boundaries** — where systems meet
2. **Critical paths** — money, security, core features
3. **Complex queries** — database operations

**Contract tests** verify every implementation of an interface behaves the
same: write the contract suite once, run it against the fake and the real
adapter alike.

## Test Builders

For complex test objects, build only the fields the test cares about:

```python
def make_order(**overrides):
    defaults = dict(customer_id="cust-1", items=[], status="pending")
    return Order(**{**defaults, **overrides})

# usage: only the interesting part is visible
order = make_order(status="paid")
```

## Common Mistakes

| Mistake | Problem | Fix |
|---|---|---|
| Testing implementation | Breaks on refactor | Test behavior only |
| Too many mocks | Tests prove nothing | Use real/fake objects |
| Shared mutable state | Flaky tests | Isolate every test |
| No meaningful assertion | False confidence | Assert the outcome, not the absence of error |
| Testing trivial code | Wasted effort | Focus on logic and edge cases |
| Slow suites | Feedback abandoned | Push tests down the pyramid |

Adapted from [ramziddin/solid-skills](https://github.com/ramziddin/solid-skills) (MIT).
