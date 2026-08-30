# Async and Concurrency

When to choose threads, processes, or asyncio, and async HTTP client patterns
with httpx and aiohttp. Core conventions live in `../SKILL.md`.

## Choosing a concurrency model

| Workload | Model | Why |
|---|---|---|
| I/O-bound (network, disk, DB) | `ThreadPoolExecutor` | GIL releases on I/O; threads cheap |
| CPU-bound (math, hashing, image) | `ProcessPoolExecutor` | Separate interpreters bypass the GIL |
| Many concurrent I/O streams | `asyncio` | One thread, highest fan-out throughput |

## concurrent.futures

```python
import concurrent.futures


def fetch_url(url: str) -> str:
    with urllib.request.urlopen(url) as response:
        return response.read().decode()


# Threads - I/O-bound
def fetch_all_urls(urls: list[str]) -> dict[str, str]:
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(fetch_url, url): url for url in urls}
        results: dict[str, str] = {}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                results[url] = future.result()
            except Exception as e:
                results[url] = f"Error: {e}"
    return results


# Processes - CPU-bound
def compute(data: list[int]) -> int:
    return sum(x ** 2 for x in data)


def process_all(datasets: list[list[int]]) -> list[int]:
    with concurrent.futures.ProcessPoolExecutor() as executor:
        return list(executor.map(compute, datasets))
```

## async/await basics

```python
import asyncio


async def fetch_async(url: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text


async def fetch_all(urls: list[str]) -> dict[str, str]:
    tasks = [fetch_async(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return dict(zip(urls, results))
```

## httpx (recommended)

Sync and async from one library, HTTP/2 support, built-in connection pooling:

```python
import httpx

# Sync
response = httpx.get("https://api.example.com/users")
response.raise_for_status()
data = response.json()

# Async
async with httpx.AsyncClient() as client:
    response = await client.get("https://api.example.com/users")
    response.raise_for_status()
    data = response.json()
```

### Reusable client with connection pooling

Create one client, reuse it — connection pools live on the client, not the
request:

```python
import httpx


class APIClient:
    def __init__(self, base_url: str, api_key: str) -> None:
        self.client = httpx.AsyncClient(
            base_url=base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=httpx.Timeout(30.0, connect=5.0),
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
        )

    async def get_user(self, user_id: int) -> dict:
        response = await self.client.get(f"/users/{user_id}")
        response.raise_for_status()
        return response.json()

    async def close(self) -> None:
        await self.client.aclose()
```

### Retry with exponential backoff

Retry on 5xx and transient connection errors; give up after `max_retries`:

```python
import asyncio
import httpx


async def retry_request(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    max_retries: int = 3,
    base_delay: float = 1.0,
    **kwargs,
) -> httpx.Response:
    last_exc: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            response = await client.request(method, url, **kwargs)
            if response.status_code < 500:
                return response
            last_exc = httpx.HTTPStatusError(
                f"server error: {response.status_code}",
                request=response.request,
                response=response,
            )
        except (httpx.ConnectError, httpx.ReadTimeout) as exc:
            last_exc = exc

        if attempt < max_retries:
            await asyncio.sleep(base_delay * (2 ** attempt))

    raise last_exc
```

### Streaming large responses

Stream to disk chunk-by-chunk; never hold the whole body in memory:

```python
async def download_file(url: str, output_path: str) -> None:
    async with httpx.AsyncClient() as client:
        async with client.stream("GET", url) as response:
            response.raise_for_status()
            with open(output_path, "wb") as f:
                async for chunk in response.aiter_bytes(chunk_size=8192):
                    f.write(chunk)
```

### Concurrent requests

```python
import asyncio
import httpx


async def fetch_all(urls: list[str]) -> list[dict]:
    async with httpx.AsyncClient() as client:
        tasks = [client.get(url) for url in urls]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        results: list[dict] = []
        for url, response in zip(urls, responses):
            if isinstance(response, Exception):
                results.append({"url": url, "error": str(response)})
            else:
                results.append({"url": url, "data": response.json()})
        return results
```

### Rate-limited client

A semaphore caps in-flight requests; a delay spaces them out:

```python
import asyncio
import httpx


class RateLimitedClient:
    def __init__(self, client: httpx.AsyncClient, requests_per_second: float = 10) -> None:
        self.client = client
        self.semaphore = asyncio.Semaphore(int(requests_per_second))
        self.delay = 1.0 / requests_per_second

    async def get(self, url: str, **kwargs) -> httpx.Response:
        async with self.semaphore:
            response = await self.client.get(url, **kwargs)
            await asyncio.sleep(self.delay)
            return response
```

## aiohttp

Async-only; useful where httpx is unavailable or for legacy stacks:

```python
import aiohttp


async def fetch_with_aiohttp(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()


# With connection pooling
connector = aiohttp.TCPConnector(limit=100, limit_per_host=20)
session = aiohttp.ClientSession(connector=connector)
```

## Testing with respx

respx mocks httpx transports so tests run without network access:

```python
import respx
import httpx
import pytest


@respx.mock
@pytest.mark.asyncio
async def test_get_user() -> None:
    respx.get("https://api.example.com/users/1").mock(
        return_value=httpx.Response(200, json={"id": 1, "name": "Alice"})
    )

    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/users/1")
        assert response.json()["name"] == "Alice"


@respx.mock
@pytest.mark.asyncio
async def test_api_error() -> None:
    respx.get("https://api.example.com/users/999").mock(
        return_value=httpx.Response(404, json={"error": "Not found"})
    )

    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/users/999")
        assert response.status_code == 404
```

## httpx vs aiohttp

| Feature | httpx | aiohttp |
|---|---|---|
| Sync + Async | Yes | Async only |
| HTTP/2 | Yes | No |
| Connection pooling | Built-in | Built-in |
| Streaming | `aiter_bytes()` | `content.read()` |
| Testing | respx | aioresponses |
| FastAPI testing | AsyncClient + ASGITransport | N/A |

Adapted from [affaan-m/ECC](https://github.com/affaan-m/ECC) and
[manikosto/claude-code-python-stack](https://github.com/manikosto/claude-code-python-stack).
