---
name: go
description: Use when writing, refactoring, reviewing, or documenting Go code (.go files) — idiomatic Go and Google Go style guide conventions for naming, imports, error handling, doc comments, table-driven tests, concurrency, generics, and package design.
license: CC-BY-4.0
compatibility: opencode
metadata:
  language: go
  source: https://google.github.io/styleguide/go/
  audience: developers
---

# Go Style

Conventions from Google's Go Style Guide for clear, simple, maintainable Go. Apply these when writing and reviewing code; enforce them mechanically with the `golangci-lint` skill (see its Style Enforcement Map).

## When to use

- Writing new Go code or refactoring existing code
- Reviewing Go code for style compliance
- Documenting Go packages, functions, or types
- Designing APIs, interfaces, or packages

## Principles (in order of importance)

1. **Clarity** — the code's purpose and rationale are clear to the reader
2. **Simplicity** — the code accomplishes its goal the simplest way possible
3. **Concision** — the code has a high signal-to-noise ratio
4. **Maintainability** — the code can be easily maintained
5. **Consistency** — the code is consistent with the broader codebase

## Verification

Finish every Go change with:

```bash
gofmt -l .          # must print nothing
go vet ./...
go build ./...
```

`gofmt` does not manage imports. Use `goimports` for import grouping and ordering:

```bash
go run golang.org/x/tools/cmd/goimports@latest -w .
```

## Formatting

- No fixed line length — prefer refactoring over splitting lines
- `MixedCaps`/`mixedCaps`, never snake_case or underscores
- Let the code speak for itself; delete comments that restate it

## Naming

**Packages** — short, lowercase, no underscores or MixedCaps. Avoid vague utility names (`util`, `common`, `helper`); name packages by what they provide (`cache`, `auth`, `stringutil`):

```go
// Good
package creditcard
package tabwriter
package oauth2

// Bad
package credit_card
package tabWriter
package oAuth2
```

**Functions and methods** — avoid repetition with the package name:

```go
// Good
package yamlconfig
func Parse(input string) (*Config, error)

// Bad - repetitive
func ParseYAMLConfig(input string) (*Config, error)
```

**Variables** — short names in small scopes (`i`, `c`, `db`); longer names in larger scopes. Don't encode the type in the name: `users`, not `userSlice`.

**Constants** — MixedCaps, never SCREAMING_SNAKE or hungarian prefixes. `iota` requires a const block:

```go
// Good
const MaxPacketSize = 512

const (
	ExecuteBit = 1 << iota
	WriteBit
	ReadBit
)

// Bad
const MAX_PACKET_SIZE = 512
const kMaxBufferSize = 1024
```

**Initialisms** — keep the same case throughout (`HTTP`, `API`, `ID`, `URL`):

```go
// Good
func ServeHTTP(w http.ResponseWriter, r *http.Request)
func ProcessXMLAPI() error
var userID string

// Bad
func ServeHttp()
func ProcessXmlApi()
var userId string
```

**Receivers** — short (1-2 letters), an abbreviation of the type, consistent across all methods of the type:

```go
// Good
func (c *Client) Get(url string) (*Response, error)
func (c *Client) Post(url string, body io.Reader) (*Response, error)

// Bad
func (client *Client) Get(url string) (*Response, error)
func (this *Client) Post(url string, body io.Reader) (*Response, error)
```

## Documentation

Doc comments are complete sentences, capitalized and punctuated, starting with the name being described:

```go
// Good
// Join concatenates the elements of its first argument to create a single string.
// The separator string sep is placed between elements in the resulting string.
func Join(elems []string, sep string) string

// Bad
// This function joins strings
func Join(elems []string, sep string) string
```

Package comments sit directly above the package clause, one per package:

```go
// Package math provides basic constants and mathematical functions.
//
// This package does not guarantee bit-identical results across architectures.
package math
```

## Imports

Three groups, separated by blank lines: standard library, external packages, project-local packages:

```go
// Good
package main

import (
	"fmt"
	"hash/adler32"
	"os"

	"github.com/dsnet/compress/flate"
	"golang.org/x/text/encoding"

	"myproj/rpc/protocols/dial"
)
```

- Rename imports only when necessary, and to something descriptive: `foopb "path/to/foo/proto"`
- Side-effect imports (`_ "..."`) go in the final group
- Never use dot imports outside tests

## Error handling

**Return errors, never panic.** Error strings are lowercase with no punctuation:

```go
// Good
return fmt.Errorf("open %s: %w", path, err)

// Bad
return fmt.Errorf("Open %s: %w.", path, err)
```

**Handle every error**:

```go
// Good
if err := doSomething(); err != nil {
	return fmt.Errorf("do something: %w", err)
}

// Bad - ignoring errors
_ = doSomething()
```

**Indent error flow** — no `else` after an error return:

```go
// Good
if err != nil {
	// error handling
	return err
}
// normal code

// Bad
if err != nil {
	// error handling
} else {
	// normal code
}
```

**Wrap with `%w`** when callers should inspect the error with `errors.Is`/`errors.As`; use `%v` when you deliberately don't want wrapping.

## Functions

- Keep signatures on one line where possible
- Use named results only when they aid documentation; never naked returns in long functions
- Avoid stutter: `WriteTo`, not `WriteConfigTo`

```go
// Good
func (r *Reader) Read(p []byte) (n int, err error)
func WithTimeout(parent context.Context, d time.Duration) (context.Context, cancel func())

// Bad - naked return far from the signature
func Process() (result int, err error) {
	// ... many lines ...
	result = 42
	return // unclear what's being returned
}
```

## Nil slices

Return and use nil slices; they behave like empty slices in `len`, `range`, and `append`:

```go
// Good
var s []int

if len(s) == 0 { // works for both nil and empty
	// ...
}

// Bad - usually not what you want
if s == nil {
	// ...
}
```

## Interfaces

Keep interfaces small. Define them where they are consumed. Accept interfaces, return concrete types:

```go
// Good - single method, composed
type Reader interface {
	Read(p []byte) (n int, err error)
}

type ReadWriter interface {
	Reader
	Writer
}

// Good
func Process(r io.Reader) (*Result, error)

// Avoid unless necessary
func Process(r *os.File) (*Result, error)
```

## Generics

Start without generics — slices, maps, channels, and interfaces often work just as well with less complexity (least mechanism). Reach for type parameters only when they earn their keep:

- **One instantiation in practice?** Write the code for that concrete type. Adding polymorphism later is easy; removing unneeded abstraction is hard.
- **Types share a unifying interface?** Model the solution with that interface; generics may not be needed.
- **Reaching for `any` + type switches?** That's the case where generics are the better tool:

```go
// Bad - any + type switch loses type safety
func Max(values []any) any

// Good - type parameter preserves it
func Max[T cmp.Ordered](values []T) T
```

- Don't use generics to build DSLs — especially error-handling frameworks and test assertion libraries
- Prefer `any` over `interface{}` in new code (Go 1.18+)
- Document exported generic APIs with motivating runnable examples

## Concurrency

Document concurrency safety on types:

```go
// Cache stores expensive computation results.
//
// Methods are not safe for concurrent use.
type Cache struct{ /* ... */ }

// Client is safe for concurrent use by multiple goroutines.
type Client struct{ /* ... */ }
```

- Never launch a goroutine without a defined exit path and a lifecycle owner
- Use `golang.org/x/sync/errgroup` for fan-out with error propagation
- Guard simple shared state with `sync.Mutex`; use channels for ownership transfer and signaling
- `context.Context` is the first parameter; document non-default context behavior

```go
// Run executes the worker's run loop.
//
// If the context is cancelled, Run returns a nil error.
func (w *Worker) Run(ctx context.Context) error {
	for {
		select {
		case <-ctx.Done():
			return nil
		case ev := <-w.events:
			w.handle(ev)
		}
	}
}
```

## Testing

Table-driven tests with subtests:

```go
func TestParse(t *testing.T) {
	tests := []struct {
		name    string
		input   string
		want    int
		wantErr bool
	}{
		{name: "valid", input: "123", want: 123},
		{name: "invalid", input: "abc", wantErr: true},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := Parse(tt.input)
			if (err != nil) != tt.wantErr {
				t.Errorf("Parse() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if got != tt.want {
				t.Errorf("Parse() = %v, want %v", got, tt.want)
			}
		})
	}
}
```

Test names describe the function and case without stutter:

```go
// Good
func TestParse(t *testing.T)
func TestParse_InvalidInput(t *testing.T)
func TestClient_Get_Success(t *testing.T)

// Bad
func TestParseFunction(t *testing.T)
func Test_Parse(t *testing.T)
```

## Composite literals

Field names for external types; matching braces for block literals:

```go
// Good - field names for external types
r := csv.Reader{
	Comma:           ',',
	Comment:         '#',
	FieldsPerRecord: 4,
}

// Good - field names optional for package-local types
okay := LocalType{42, "hello"}

// Good
items := []*Item{
	{Name: "foo"},
	{Name: "bar"},
}

// Bad - closing brace not aligned with opening
items := []*Item{
	{Name: "foo"},
	{Name: "bar"}}
```

## Extended guidance

- **`references/advanced-patterns.md`** — options/constructor/cleanup patterns, package design, least mechanism

## References

- **Style Guide**: https://google.github.io/styleguide/go/guide
- **Style Decisions**: https://google.github.io/styleguide/go/decisions
- **Best Practices**: https://google.github.io/styleguide/go/best-practices
- **Effective Go**: https://go.dev/doc/effective_go
- **Generics tutorial**: https://go.dev/doc/tutorial/generics
- **Code Review Comments**: https://github.com/golang/go/wiki/CodeReviewComments
- **Go Proverbs**: https://go-proverbs.github.io/
