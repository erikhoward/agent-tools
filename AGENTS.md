# Agent Guidelines

Behavioural guidelines to reduce common LLM coding mistakes, derived from
[Andrej Karpathy's observations](https://x.com/karpathy/status/2015883857489522876).
Bias toward caution over speed; for trivial tasks, use judgment. The skills
and agents in this repo reinforce these principles — defer to them instead of
restating.

## 1. Think Before Coding

Don't assume, don't hide confusion, surface tradeoffs. State assumptions
explicitly; if multiple interpretations exist, present them; if unclear, stop
and ask. For anything blocked, risky, or beyond scope, escalate to a
consultant agent (see roster) rather than guess. `flow-plan` owns the
clarify-first workflow.

## 2. Simplicity First

Minimum code that solves the problem — no features, abstractions,
flexibility, or error handling beyond what was asked. If 200 lines could be
50, rewrite. The `solid` skill encodes this as the Four Elements of Simple
Design and YAGNI; load it for any coding or review task.

## 3. Surgical Changes

Touch only what you must. Don't refactor adjacent code, match existing style,
and remove only the orphans your own changes create. Every changed line
should trace to the request. `developer-fast` enforces minimal-context,
minimal-change discipline; `solid` covers clean-code structure.

## 4. Goal-Driven Execution

Define success criteria and loop until verified: "add validation" → write
failing tests, then make them pass. For multi-step work, `flow-implement`
owns the decompose → delegate → per-task verify (tests, type-check, lint) →
TodoWrite loop; `flow-plan` fixes acceptance criteria up front.

## Communication Style

Use the `bare-bones` skill for all documentation and user-facing communication.
Write in Simplified Technical English: short sentences, active voice, simple
tenses, one word per meaning. This is on by default.

To turn it off, the user can say "turn off bare-bones", "disable STE", or "stop
using simplified English". To turn it back on, the user can say "turn on
bare-bones" or "enable STE". When off, write in your default style.

## Repo Assets

Load and follow the relevant skill, agent, or command instead of improvising.

### Skills (`skills/`)

| Skill | Use for |
|---|---|
| `solid` | Any coding/review — SOLID, TDD, clean code, code smells |
| `bare-bones` | Technical writing in ASD-STE100 Simplified Technical English |
| `git-commit` | Writing conventional commit messages |
| `go`, `python`, `rust`, `typescript`, `golangci-lint` | Language-specific conventions + verification |
| `github`, `git-hooks` | GitHub workflows, hooks |
| `flow-ideate`, `flow-plan`, `flow-implement` | Ideation → planning → parallel build |

### Agents (`agents/`)

| Agent | Role |
|---|---|
| `build` | Orchestrator — runs `/flow-implement`, `/flow-ideate`; decomposes, delegates, verifies |
| `plan` | Orchestrator — runs `/flow-plan`; clarifies, consults, produces the plan |
| `developer-prime` | Complex, multi-file, long-context, frontend implementation |
| `developer-fast` | Scoped, single-file, boilerplate, high-volume implementation |
| `principal-architect` | Tier 2 — system strategy, cross-service architecture |
| `solution-architect` | Tier 2 — concrete service designs, cross-component interfaces |
| `database-architect` | Tier 2 — data modelling, schema, migrations |
| `security-expert` | Tier 2 — threat modelling, auth, secure coding |
| `code-analyst`, `performance-engineer`, `ui-ux-designer` | Tier 1 analysts — read-only, blueprints |
| `devops-engineer`, `test-engineer` | Tier 1 analysts during planning; implementers during execution |
| `@explore` | Built-in opencode subagent — not a custom agent from this repo |

`build` and `plan` are the workflow orchestrators. Tier 2 consultants operate
**Think → Advise → Review**; Tier 1 analysts produce blueprints in parallel.
See `flow-plan` for the full tier model.

## Model Strategy

Agents without an explicit `model:` field inherit the session default / invoker's model. This is intentional — Tier 1 analysts benefit from context-adaptive model inheritance.

Tier 2 consultants have explicit models to ensure a reasoning step above the orchestrator.

Commands may override the agent's model for workflow-specific optimization.

| Tier | Model | Rationale |
|---|---|---|
| Orchestrators (build, plan) | Explicit (glm-5.1 / glm-5.2) | Workflow owners, fixed reasoning level |
| Tier 2 consultants | Explicit (glm-5.2) | Reasoning step above orchestrator for deeper analysis |
| Implementation agents | Explicit (gpt-5.6-luna / deepseek-v4-flash) | Complex implementer uses reasoning-tier model; fast implementer uses lightweight model for speed |
| Tier 1 analysts | Inherited (no explicit model) | Context-adaptive — benefits from invoker's model |
| Commands | May override agent model | Workflow-specific optimization (e.g., /flow-plan → claude-opus-5) |

### Commands (`commands/`)

| Command | Action |
|---|---|
| `/flow-ideate`, `/flow-plan`, `/flow-implement` | Ideation, planning, parallel build |
| `/git-commit`, `/git-push`, `/git-commit-push` | Conventional commit, push, both |


