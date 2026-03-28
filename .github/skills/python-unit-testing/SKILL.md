---
name: python-unit-testing
description: >
  Clean unit test writing guidelines for Python with pytest.
  Use this when asked to write, create, or refactor Python unit tests.
---

# Python Unit Testing

Tests are written with **pytest**. Every test in this skill is a **unit test** — one class or function under test, all dependencies mocked or replaced.

## Folder Structure

The `tests/` folder mirrors the production code structure exactly. Production files can have short names — test files must use the full verbose name to avoid conflicts across modules:

```
src/
  user/
    adapters/
      postgres.py        ← short is fine here
    domain/
      service.py         ← short is fine here
tests/
  user/
    adapters/
      test_postgres_user_adapter.py   ← verbose: module + layer + concept
    domain/
      test_user_domain_service.py     ← verbose: module + layer + concept
```

After writing a test, always verify it passes before moving on:

```bash
uv run pytest tests/path/to/test_file.py::TestClass::test_name -v
```

For the full iterative fixing workflow, see the `python-test-fixing` skill.

## Type Hints

Always use complete type hints for fixtures and test functions:

```python
@pytest.fixture
def executor(registry: ToolRegistry) -> ToolExecutor:
    return ToolExecutor(registry)

@pytest.mark.asyncio
async def test_feature(self, executor: ToolExecutor) -> None:
    result = await executor.execute("action", {})
    assert result == "expected"
```

## Test Organization

Group related tests in classes with a `Test` prefix:

```python
class TestPydanticConversion:
    async def test_simple_model(self): ...
    async def test_nested_model(self): ...

class TestEnumConversion:
    async def test_standalone_enum(self): ...
    async def test_invalid_value(self): ...
```

## Naming

Test names describe what is being tested — no comments or docstrings needed:

```python
# Good
async def test_pydantic_with_nested_optional(self): ...
async def test_invalid_enum_value(self): ...

# Bad
async def test_case_1(self): ...
async def test_model(self): ...
```

## Test Data

Define test models and fixtures at module level:

```python
class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"

class Task(BaseModel):
    title: str
    priority: Priority = Priority.MEDIUM
```

## Assertions

Be specific — assert concrete values, not just truthiness:

```python
# Good
assert "Berlin" in result
assert len(results) == 2

# Bad
assert result
assert True
```

## Exception Testing

Use `pytest.raises` with a `match` pattern:

```python
with pytest.raises(ValueError, match="not found"):
    await executor.execute("nonexistent", {})
```

## Async Tests

Always use `@pytest.mark.asyncio` for async tests:

```python
@pytest.mark.asyncio
async def test_async_operation(self, executor: ToolExecutor) -> None:
    result = await executor.execute("action", {})
    assert isinstance(result, str)
```
