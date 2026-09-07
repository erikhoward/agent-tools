---
name: go
description: Apply repository-aware Go conventions for APIs, errors, context, concurrency, ownership, tests, and verification. Use when writing, reviewing, or changing Go code.
license: CC-BY-4.0
compatibility: opencode
metadata:
  source: https://google.github.io/styleguide/go/
---

# Go

Follow the repository's Go version, formatter, linter, package layout, and CI commands. Do not install tools, change configuration, or format unrelated files unless requested.

## Contracts

- Use standard Go naming. Preserve conventional initialisms such as `ID`, `URL`, and `HTTP`. Keep package names short and avoid package-name stutter.
- Put `context.Context` first. Pass it through call chains. Do not store it in structs unless an API contract requires that design.
- Return errors as values. Add useful operation context with `%w` when callers need the cause. Use lowercase error text without trailing punctuation. Do not both log and return the same error at one layer.
- Define small interfaces at the consumer. Start with concrete types. Add abstraction only for an observed boundary or substitution need.
- Treat ownership as part of the API. Document whether callers can retain or mutate slices, maps, buffers, channels, and returned resources.
- Never start a goroutine without an owner, stop condition, and cleanup path. Bound queues and fan-out. Avoid holding locks during I/O or callbacks.
- Preserve `nil` versus empty collections when it affects serialization or API behavior.
- Keep exported comments useful and accurate. Do not restate signatures.

## Tests

Test observable behavior with repository conventions. Use table tests when several inputs share one contract, not as ceremony. Ensure concurrent tests terminate and do not depend on timing when synchronization is available.

## Verification

Run the repository's focused checks first. Common fallbacks are:

```text
gofmt -w <changed-files>
go test ./...
go vet ./...
```

Run `go build ./...` when build coverage adds evidence. Report unavailable checks. Do not download `latest` tooling as part of verification.

Adapted from the Google Go Style Guide (CC BY 4.0).
