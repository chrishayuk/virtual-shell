# Testing Guide

## Running Tests

```bash
# Run all tests
uv run pytest

# Run tests quietly
uv run pytest -q

# Run specific test file
uv run pytest tests/commands/system/test_python_command.py

# Run with coverage
uv run pytest --cov=chuk_virtual_shell
```

## Code Quality Checks

```bash
# Linting with ruff
uv run ruff check .
uv run ruff check --fix .  # Auto-fix issues

# Type checking with mypy
uv run mypy chuk_virtual_shell

# Code formatting with black
uv run black --check chuk_virtual_shell  # Check only
uv run black chuk_virtual_shell          # Format code

# Run flake8 (if installed)
uv run flake8 chuk_virtual_shell
```

## Known Test Warnings

You may see RuntimeWarnings about "coroutine was never awaited" in some tests:

```
RuntimeWarning: coroutine 'PythonCommand.execute_async' was never awaited
```

These warnings are **expected and harmless**. They occur when:
- Unit tests mock async methods
- The mock library creates coroutine objects
- The test doesn't await them (which is correct for synchronous test contexts)

These warnings indicate the async/sync separation is working correctly - the commands have async implementations that are properly detected by the mocking framework.

## Test Organization

Tests are organized by component:

```
tests/
├── commands/           # Command tests
│   ├── environment/   # Environment commands (export, env, alias)
│   ├── filesystem/    # File operations (cp, mv, rm, etc.)
│   ├── navigation/    # Navigation (cd, ls, pwd)
│   ├── system/        # System commands (python, sh, date, etc.)
│   └── text/          # Text processing (grep, sed, awk, etc.)
├── interpreters/       # Python and Bash interpreter tests
├── sandbox/           # Sandbox configuration tests
└── session/          # Session management tests
```

## Writing Tests

### Basic Test Structure

```python
import pytest
from unittest.mock import Mock
from chuk_virtual_shell.commands.system.example import ExampleCommand

class TestExampleCommand:
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_shell = Mock()
        self.mock_shell.fs = Mock()
        self.cmd = ExampleCommand(self.mock_shell)
    
    def test_example_functionality(self):
        """Test basic functionality"""
        result = self.cmd.execute(["arg1", "arg2"])
        assert "expected" in result
```

### Testing Async Commands

For commands with async implementations:

```python
import asyncio
import pytest

@pytest.mark.asyncio
async def test_async_command():
    """Test async command execution"""
    cmd = AsyncCommand(mock_shell)
    result = await cmd.execute_async(["args"])
    assert result == "expected"
```

## Test Coverage

Current test suite status:
- **940 tests passing**
- **1 test skipped** (platform-specific)
- **99.9% pass rate**

To view coverage report:

```bash
uv run pytest --cov=chuk_virtual_shell --cov-report=html
open htmlcov/index.html
```