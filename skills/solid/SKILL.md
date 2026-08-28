---
name: solid
description: Use when writing or reviewing any code — applies SOLID principles, TDD (red-green-refactor), clean code practices, code-smell detection, and the Four Elements of Simple Design to produce senior-engineer quality software. Triggers include "implement a feature", "refactor", "review code quality", "design a module", "write tests", or any coding task where maintainability matters.
license: MIT
compatibility: opencode
metadata:
  source: https://github.com/ramziddin/solid-skills
  audience: developers
---

# Solid — Professional Software Engineering

Write code as a senior engineer would: testable, flexible, and maintainable.
The goal of software is to let developers **discover, understand, add, change,
remove, test, debug, deploy, and monitor** features cost-effectively.

Tool-agnostic. For language-specific conventions, combine with the matching
language skill (e.g. `go`).

## TDD — The Working Method

When implementing behavior, default to the red-green-refactor loop:

```
RED        write a failing test that describes the behavior you want
GREEN      write the simplest code that makes it pass
REFACTOR   clean up — this is where design happens
```

The Three Laws:

1. No production code without a failing test
2. No more test code than sufficient to fail
3. No more production code than sufficient to pass

Test **behavior, not implementation**, with concrete examples in domain
language ("recognizes `racecar` as a palindrome", not "handles edge case").
When the plan's testing strategy or the task prompt assigns tests after
implementation instead, follow that — but never skip verification.

Details: [references/tdd.md](references/tdd.md), [references/testing.md](references/testing.md)

## The Four Elements of Simple Design

The decision rubric, in priority order — when two principles conflict, the
higher one wins:

1. **Runs all the tests** — it works
2. **Expresses intent** — readable, reveals purpose
3. **No duplication** — after the Rule of Three, not before
4. **Minimal** — fewest abstractions that satisfy the requirement

## SOLID — Ask on Every Module

| Principle | Question to ask |
|---|---|
| **S**ingle Responsibility | Does this have ONE reason to change? |
| **O**pen/Closed | Can I extend without modifying? |
| **L**iskov Substitution | Can subtypes replace base types safely? |
| **I**nterface Segregation | Are clients forced to depend on unused methods? |
| **D**ependency Inversion | Do high-level modules depend on abstractions? |

Details and worked examples: [references/solid-principles.md](references/solid-principles.md)

## Clean Code Essentials

**Naming priority**: consistency > understandability (domain language) >
specificity (avoid `data`, `info`, `manager`) > brevity > searchability.

**Structure**:
- Early returns over `else` chains
- One level of indentation per function where reasonable
- Wrap domain primitives (IDs, emails, money) in value objects instead of
  passing raw strings/ints across boundaries
- Keep functions small; keep modules cohesive
- Law of Demeter: only talk to immediate friends

Details: [references/clean-code.md](references/clean-code.md)

## Code Smells — Stop and Refactor

| Smell | Fix |
|---|---|
| Long method | Extract functions |
| Large class/module | Split by responsibility |
| Long parameter list | Introduce parameter object |
| Divergent change | Split into focused modules |
| Shotgun surgery | Move related code together |
| Feature envy | Move the function to the data it envies |
| Data clumps | Extract a type for grouped data |
| Primitive obsession | Wrap in value objects |
| Switch-on-type | Replace with polymorphism |
| Speculative generality | YAGNI — delete unused abstractions |

Full catalog: [references/code-smells.md](references/code-smells.md)

## Manage Complexity

- **Essential** complexity is inherent to the problem; **accidental**
  complexity is introduced by the solution — only the second is your fault
- Detect it via change amplification (small change, many files), cognitive
  load, and unknown unknowns
- Fight it with YAGNI, KISS, and DRY-after-three

## Design with Responsibility in Mind

For every module ask: what is its stereotype — data holder, service
provider, coordinator, controller, or interfacer? If it's two stereotypes,
it's two modules. Details: [references/object-design.md](references/object-design.md)

## Patterns

Creational (Factory, Builder), structural (Adapter, Decorator), behavioral
(Strategy, Observer, Command). **Don't force patterns — let them emerge from
refactoring.** Details: [references/design-patterns.md](references/design-patterns.md)

## Architecture

- **Vertical slices**: features as end-to-end, self-contained units
- **The dependency rule**: dependencies point inward, toward the domain;
  infrastructure depends on domain, never the reverse

Details: [references/architecture.md](references/architecture.md)

## Checklists

**Before coding**:
1. Do I understand the requirement? (acceptance criteria first)
2. What is the simplest solution?
3. What patterns might apply? (don't force them)
4. Am I solving a real problem or a hypothetical one?

**While coding**:
1. Is this the simplest thing that could work?
2. Does this module have a single responsibility?
3. Am I depending on abstractions or concretions at boundaries?
4. Can I name this more clearly?
5. Is there duplication worth extracting? (Rule of Three)

**After it works**:
1. Do all tests pass?
2. Is there dead code to remove?
3. Are names still accurate after the changes?
4. Would a new team member understand this in six months?

## Red Flags — Stop and Rethink

- Writing production code without a failing test (when TDD applies)
- Functions doing two jobs "while I'm here"
- Abstractions created before the third duplication
- Features added "just in case"
- Hardcoded values that should be configuration
- God modules that know everything
- Tests that break on refactor without any behavior change

## Remember

> A little duplication is 10x better than the wrong abstraction.

> Focus on WHAT needs to happen, not HOW.

## References

- **`references/tdd.md`** — red-green-refactor mechanics, the Three Laws, triangulation
- **`references/testing.md`** — test pyramid, doubles, naming, strategy by layer
- **`references/solid-principles.md`** — the five principles in depth
- **`references/clean-code.md`** — naming, structure, value objects
- **`references/code-smells.md`** — detection and fixes
- **`references/object-design.md`** — object stereotypes and responsibilities
- **`references/design-patterns.md`** — when patterns help, when they hurt
- **`references/architecture.md`** — vertical slicing and the dependency rule

Adapted from [ramziddin/solid-skills](https://github.com/ramziddin/solid-skills) (MIT).
