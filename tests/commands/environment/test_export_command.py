"""
tests/chuk_virtual_shell/commands/environment/test_export_command.py
"""

import pytest
from chuk_virtual_shell.commands.environment.export import ExportCommand
from tests.dummy_shell import DummyShell


# Fixture to create an ExportCommand with a dummy shell as the shell_context.
@pytest.fixture
def export_command():
    dummy_shell = DummyShell({})
    dummy_shell.environ = {}
    command = ExportCommand(shell_context=dummy_shell)
    return command


# Test valid assignments
def test_export_valid(export_command):
    result = export_command.execute(["FOO=bar", "BAZ=qux"])
    # No errors should be returned, and the environment should be updated.
    assert result == ""
    assert export_command.shell.environ["FOO"] == "bar"
    assert export_command.shell.environ["BAZ"] == "qux"


# Test a mix of valid and invalid assignments
def test_export_invalid_assignment(export_command):
    result = export_command.execute(["FOO", "BAR=baz"])
    # "FOO" is invalid and should produce an error message.
    assert "invalid assignment" in result
    # The valid assignment "BAR=baz" should still be set.
    assert export_command.shell.environ["BAR"] == "baz"


# Test assignment with missing key
def test_export_missing_key(export_command):
    result = export_command.execute(["=value"])
    assert "missing variable name" in result
    # Ensure that no key is set when the key is missing.
    assert "=value" not in export_command.shell.environ
