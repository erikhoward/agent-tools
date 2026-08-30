# Go Style — Advanced Patterns

Extended guidance from Google's Go Style Guide: common patterns, package design, and least mechanism. Core conventions live in `../SKILL.md`.

## Common Patterns

### Options Pattern

For optional configuration, prefer a plain `Options` struct; use functional options only when the call sites benefit:

```go
// Good - simple
type Options struct {
	Timeout time.Duration
	Retries int
}

func NewServer(addr string, opts Options) *Server

// Good - functional options when most config is optional
type Option func(*Server)

func WithTimeout(d time.Duration) Option {
	return func(s *Server) {
		s.timeout = d
	}
}

func NewServer(addr string, opts ...Option) *Server
```

### Constructor Pattern

```go
// Good - New for the single type in a package
package widget
func New() *Widget

// Good - NewX when a package has multiple types
package widget
func NewWidget() *Widget
func NewGizmo() *Gizmo
```

### Cleanup Pattern

Document cleanup requirements on the function; use `defer` at the call site:

```go
// Good - document cleanup requirements
// Open opens a file for reading.
// The caller must call Close when done.
func Open(name string) (*File, error)

// Good - defer for cleanup
f, err := os.Open(filename)
if err != nil {
	return err
}
defer f.Close()
```

## Package Design

- Not too large (thousands of lines in one package)
- Not too small (one type per package)
- Group related functionality together
- The standard library is a good example

## Least Mechanism

Prefer simpler constructs, in order:

1. Core language features (channels, slices, maps, loops)
2. Standard library — including the `slices` and `maps` packages (Go 1.21+) and the `min`/`max` builtins
3. External dependencies, only if necessary

```go
// Good - use built-in
users := make(map[string]*User)
first := slices.Min(scores) // Go 1.21+

// Avoid - unless set operations are genuinely complex
import "github.com/deckarep/golang-set"
users := mapset.NewSet()
```
