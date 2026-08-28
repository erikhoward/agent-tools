# Architecture

Structuring a codebase so features can be added, changed, removed, tested, and deployed with minimal friction: vertical slices, the dependency rule, and boundary contracts. Consult when starting a project, adding a new feature area, or when changes routinely touch many unrelated directories.

## The Goal

Architecture exists so the team can:

1. **Add** features with minimal friction
2. **Change** existing features safely
3. **Remove** features cleanly
4. **Test** features in isolation
5. **Deploy** independently where possible

## Vertical Slices

Organize by **feature**, not by technical layer. A slice is a self-contained, end-to-end unit: entry point, logic, storage.

```
Bad: layer-first            Good: feature-first
src/                        src/
  controllers/                users/
    UserController              handler
    OrderController             service
  services/                     storage
    UserService               orders/
    OrderService                handler
  repositories/                 service
    UserRepository              storage
    OrderRepository
```

Why: a change to "users" stays inside `users/`. Layer-first scatters one feature across the tree — shotgun surgery by layout.

## The Dependency Rule

Dependencies point **inward**, toward the domain:

```
Infrastructure → Application → Domain
   (outer)         (middle)     (inner)
```

- Inner layers know nothing about outer layers
- The domain has zero imports of infrastructure or frameworks
- Invert boundaries with interfaces that the domain itself defines

```go
// domain/order.go — inner: defines the port
type OrderRepository interface {
    Save(ctx context.Context, o Order) error
}

// infra/postgres/order_repo.go — outer: implements it
type OrderRepo struct{ db *sql.DB }

func (r *OrderRepo) Save(ctx context.Context, o domain.Order) error {
    // SQL here
}
```

Infrastructure imports the domain; the domain imports nothing. The same rule holds in any language — Python protocols, TypeScript interfaces, Rust traits.

## Contracts at Boundaries

Interfaces owned by the inner layer define what outer layers must provide. Multiple implementations coexist:

```
PaymentGateway (domain)
  ├─ StripeGateway   (infra)
  ├─ PayPalGateway   (infra)
  └─ FakeGateway     (tests)
```

## Cross-Cutting Concerns

Logging, auth, validation, and error handling span all slices. Handle them with middleware, interceptors, or decorators at the boundary — not by scattering them through domain logic.

## Conway's Law

Organizations design systems that mirror their communication structure. Align team boundaries and architecture intentionally, or the architecture will drift toward the org chart anyway.

## Architectural Styles

| Style | Shape | Tradeoff |
|---|---|---|
| Layered | Presentation → business → persistence | Simple, familiar; rots into a ball of mud without the dependency rule |
| Hexagonal (ports & adapters) | Domain at center, adapters at edges | Domain stays pure; more wiring at the edges |
| Clean | Entities → use cases → adapters → frameworks | Explicit; heaviest ceremony |

All three enforce the same idea: the dependency rule. Pick the lightest one that keeps the domain isolated.

## Walking Skeleton

Start with a minimal end-to-end slice: the thinnest feature that touches every layer and is deployable from day one. It proves the architecture works before you invest in it.

Example e-commerce skeleton: view one product (hardcoded) → add to cart → "checkout" (logs only). Then flesh out slices.

## Testing by Layer

```
E2E / acceptance   few, slow, critical paths only
Integration        some, real dependencies at the edges
Unit               many, fast, mostly domain
```

Test the domain with plain unit tests, adapters with integration tests against real dependencies, and reserve E2E for critical paths.

## Architecture Decision Records

Record significant decisions while the context is fresh:

```markdown
ADR 001: PostgreSQL for persistence

Status: Accepted
Context: need a database; options PostgreSQL, MongoDB, MySQL.
Decision: PostgreSQL — ACID, team familiarity, JSON support.
Consequences: migrations required; need ops expertise; strong queries.
```

## Red Flags

- Circular dependencies between modules
- Domain importing infrastructure
- Framework code inside business logic
- No clear boundaries between features
- Shared mutable state across modules
- "util"/"common" packages that grow forever
- Database schema driving the domain model

---

Adapted from [ramziddin/solid-skills](https://github.com/ramziddin/solid-skills) (MIT).
