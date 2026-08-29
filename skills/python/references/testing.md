# Testing

pytest fundamentals, fixtures, parametrization, mocking, async testing, and
test organization. Core conventions live in `../SKILL.md`; for TDD depth
(red-green-refactor discipline) see the `solid` skill.

## TDD cycle (brief)

1. **RED** — write a failing test for the desired behavior
2. **GREEN** — write minimal code to make it pass
3. **REFACTOR** — improve the code while tests stay green

```python
# RED
def test_add_numbers() -> None:
    assert add(2, 3) == 5

# GREEN
def add(a: int, b: int) -> int:
    return a + b
```

## pytest fundamentals

```python
import pytest


def test_addition() -> None:
    assert 2 + 2 == 4


def test_list_append() -> None:
    items = [1, 2, 3]
    items.append(4)
    assert 4 in items
    assert len(items) == 4
```

### Assertions

```python
# Equality and truthiness
assert result == expected
assert result is None
assert result is True
assert not result

# Membership and type
assert item in collection
assert isinstance(result, str)

# Exception testing with message matching
with pytest.raises(ValueError, match="invalid input"):
    raise ValueError("invalid input provided")
```

## Fixtures

### Basic fixture

```python
import pytest


@pytest.fixture
def sample_data() -> dict:
    return {"name": "Alice", "age": 30}


def test_sample_data(sample_data: dict) -> None:
    assert sample_data["name"] == "Alice"
    assert sample_data["age"] == 30
```

### Setup/teardown via yield

Code before `yield` is setup; code after is teardown:

```python
@pytest.fixture
def database():
    db = Database(":memory:")
    db.create_tables()
    db.insert_test_data()
    yield db
    db.close()


def test_database_query(database) -> None:
    result = database.query("SELECT * FROM users")
    assert len(result) > 0
```

### Scopes

```python
# Function scope (default) - runs per test
@pytest.fixture
def temp_file(tmp_path):
    return tmp_path / "test.txt"

# Module scope - once per module
@pytest.fixture(scope="module")
def module_db():
    db = Database(":memory:")
    db.create_tables()
    yield db
    db.close()

# Session scope - once per test session
@pytest.fixture(scope="session")
def shared_resource():
    resource = ExpensiveResource()
    yield resource
    resource.cleanup()
```

### conftest.py for shared fixtures

```python
# tests/conftest.py
import pytest


@pytest.fixture
def client():
    app = create_app(testing=True)
    with app.test_client() as client:
        yield client


@pytest.fixture
def auth_headers(client):
    response = client.post("/api/login", json={"username": "test", "password": "test"})
    token = response.json["token"]
    return {"Authorization": f"Bearer {token}"}
```

## Parametrization

```python
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
    ("PyThOn", "PYTHON"),
])
def test_uppercase(input: str, expected: str) -> None:
    assert input.upper() == expected


@pytest.mark.parametrize("input,expected", [
    ("valid@email.com", True),
    ("invalid", False),
    ("@no-domain.com", False),
], ids=["valid-email", "missing-at", "missing-domain"])
def test_email_validation(input: str, expected: bool) -> None:
    assert is_valid_email(input) is expected
```

## Mocking and patching

```python
from unittest.mock import patch


@patch("mypackage.external_api_call")
def test_with_mock(api_call_mock) -> None:
    api_call_mock.return_value = {"status": "success"}

    result = my_function()

    api_call_mock.assert_called_once()
    assert result["status"] == "success"


@patch("mypackage.api_call")
def test_api_error_handling(api_call_mock) -> None:
    api_call_mock.side_effect = ConnectionError("Network error")

    with pytest.raises(ConnectionError):
        api_call()

    api_call_mock.assert_called_once()
```

## Async testing

pytest-asyncio runs coroutine tests on an event loop:

```python
import pytest


@pytest.mark.asyncio
async def test_async_function() -> None:
    result = await async_add(2, 3)
    assert result == 5


@pytest.mark.asyncio
async def test_async_with_fixture(async_client) -> None:
    response = await async_client.get("/api/users")
    assert response.status_code == 200
```

## Test organization

```
tests/
├── conftest.py          # Shared fixtures
├── unit/                # Unit tests
│   ├── test_models.py
│   ├── test_utils.py
│   └── test_services.py
├── integration/         # Integration tests
│   ├── test_api.py
│   └── test_database.py
└── e2e/                 # End-to-end tests
    └── test_user_flow.py
```

## Running tests

```bash
pytest                              # run all
pytest tests/test_utils.py          # one file
pytest tests/test_utils.py::test_fn # one test
pytest -v                           # verbose
pytest -x                           # stop at first failure
pytest --lf                         # last failed
pytest -k "test_user"               # by name pattern
pytest -m "not slow"                # by marker
pytest --cov=mypackage              # with coverage
pytest --pdb                        # debugger on failure
```

## DO / DON'T

**DO** — follow TDD (red-green-refactor); test one behavior per test; name
tests for the behavior (`test_login_with_invalid_credentials_fails`); use
fixtures to kill duplication; mock external dependencies; cover edge cases
(empty, `None`, boundaries).

**DON'T** — test implementation internals instead of behavior; add complex
conditionals in tests; ignore failures; test third-party code; share state
between tests.

Adapted from [manikosto/claude-code-python-stack](https://github.com/manikosto/claude-code-python-stack)
and [affaan-m/ECC](https://github.com/affaan-m/ECC).
