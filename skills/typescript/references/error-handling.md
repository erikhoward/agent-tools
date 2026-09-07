# TypeScript Error Boundaries

Choose the repository's existing exception or Result convention. Do not add a second error model for one feature.

- Catch values as `unknown`. Narrow before reading fields or messages.
- Treat `response.json()` and all other external data as `unknown`. Validate it with the project's runtime validator or an explicit type guard before returning a domain type.
- A generic function such as `fetchJson<T>()` cannot prove the runtime response is `T`. Accept a decoder when a generic boundary is needed:

```typescript
async function fetchJson<T>(url: string, decode: (value: unknown) => T): Promise<T> {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`request failed: ${response.status}`);
  return decode(await response.json());
}
```

- Translate errors at ownership boundaries. Preserve the cause when supported. Do not expose credentials, tokens, or unbounded response bodies.
- Define which failures callers can recover from. Avoid catching an error only to log and rethrow it at every layer.
- Observe every promise. Preserve cancellation and cleanup when an operation is aborted.
- Test malformed payloads, transport failures, timeouts, cancellation, and redaction.

Adapted from xjavascript.com, dev.to, and tekvers.com.
