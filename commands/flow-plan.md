---
description: Gather requirements, consult specialist agents in parallel, and create a comprehensive implementation plan
agent: plan
model: opencode/claude-opus-5
---

Feature name: $1

Use `flow-plan` skill and plan the task.

After saving the plan file, present the user with the exact plan file path (`.opencode/plans/<feature-name>.md`).

Then tell the user to run `/flow-implement <feature-name>` to start the implementation.
