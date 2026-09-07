# Commit Message Edge Cases

- Reverts should identify the reverted commit and explain why. Follow the repository's existing revert format.
- In a monorepo, use stable product or package scopes only when they help readers and release automation.
- Use trailers for machine-readable metadata. Preserve exact tokens required by Git or repository tooling, such as `Co-authored-by` and `Signed-off-by`.
- A breaking-change trailer is `BREAKING CHANGE: <description>`. State migration impact. The `!` marker can also flag the breaking change in the subject.
- Dependency update type and scope are repository policy. Infer them from recent history instead of applying a universal `build` or `chore` rule.
- Generated commits and release automation must follow the same subject limit and trailer contract when the repository requires it.

Do not add commitlint, release tooling, or hooks merely to format one message.
