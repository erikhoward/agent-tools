# Test-Driven Development

The red-green-refactor loop, the Three Laws, and the techniques that make TDD produce better design. Consult when implementing behavior — any function or module with logic worth verifying. TDD is a *design* technique that happens to leave tests behind, not a testing technique.

## The Core Loop

```
RED → GREEN → REFACTOR → RED → ...
```

### RED — write a failing test

The test should:

- Use domain language, not technical jargon
- Describe WHAT, not HOW
- Be a concrete example, not an abstract statement

```go
// Bad: abstract
func TestAdd(t *testing.T) { /* ... */ }

// Good: concrete behavior
func TestAddReturnsSum(t *testing.T) {
    if got := Add(2, 3); got != 5 {
        t.Errorf("Add(2, 3) = %d, want 5", got)
    }
}
```

### GREEN — simplest code that passes

Two strategies:

1. **Fake it** — return a hardcoded value; let more tests drive the real implementation
2. **Obvious implementation** — when the solution is truly obvious, write it

Prefer fake-it when unsure. Generalization comes from the next test, not from foresight.

### REFACTOR — where design happens

With the test green, clean up:

- Duplication (but wait for the Rule of Three)
- Long functions to extract
- Poor names to improve
- Complex conditions to simplify

## The Three Laws

1. **No production code** without a failing test
2. **No more test code** than sufficient to fail (compile errors count)
3. **No more production code** than sufficient to pass the one failing test

## The Rule of Three

Only extract duplication when you see it **three times**. Wrong abstractions are worse than duplication — wait for the pattern to emerge.

```
Duplication #1 — leave it
Duplication #2 — note it, leave it
Duplication #3 — now extract it
```

## Triangulation

Each new test sculpts the solution toward a general implementation. Think in
**degrees of freedom**: each test carves out one more case until the
implementation handles all of them.

```go
// Test 1 pins the simple case
Add(2, 3) = 5        // fake: return 5

// Test 2 forces generalization
Add(2, 0) = 2        // now the constant must become real logic

// Test 3 pins the edge
Add(-1, 1) = 0
```

## Transformation Priority Premise

Going from RED to GREEN, prefer simpler transformations:

| Priority | Transformation |
|---|---|
| 1 | `{}` → nil |
| 2 | nil → constant |
| 3 | constant → variable |
| 4 | unconditional → conditional |
| 5 | scalar → collection |
| 6 | statement → recursion |

Higher priority = simpler. Avoid jumping to complex transformations early.

## Arrange-Act-Assert

Structure every test:

```python
def test_premium_discount():
    # arrange — set up the world
    cart = Cart(user=premium_user())
    cart.add(item(price=100))

    # act — execute the behavior
    total = cart.total()

    # assert — verify the outcome
    assert total == 80
```

**Writing tests backwards** sometimes helps: assert first (what do I want to
verify?), then act (what produces it?), then arrange (what setup does it need?).

## Test Naming

- Behavior-driven names in domain language
- Concrete examples, not abstract statements
- One behavior per test
- No implementation details leaking into names

```
Bad:  test_set_data_property / handles_edge_case
Good: test_returns_error_when_cart_is_empty / recognizes "racecar" as a palindrome
```

## Classic vs Mockist

| | Classic (Detroit) | Mockist (London) |
|---|---|---|
| Dependencies | Real objects where practical | Mocked at boundaries |
| Confidence | Higher, slower | Faster, more isolated |
| Best for | Pure logic, domain code | Infrastructure-adjacent code |

Start classic; mock only at true boundaries (database, network, clock).

## Common Mistakes

1. Writing code before tests — violates the fundamental principle
2. Writing too much test — just enough to fail
3. Writing too much code — just enough to pass
4. Skipping refactor — this is where design lives
5. Testing implementation — test behavior, not how it's done
6. Abstract test names — use concrete examples
7. Extracting too early — wait for the Rule of Three

Adapted from [ramziddin/solid-skills](https://github.com/ramziddin/solid-skills) (MIT).
