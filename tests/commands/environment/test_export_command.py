"""
tests/chuk_virtual_shell/commands/environment/test_export_command.py
"""
import pytest
from chuk_virtual_shell.commands.environment.export import ExportCommand
from tests.dummy_shell import DummyShell

# Fixture to create an ExportCommand with a dummy shell as the shell_context
@pytest.fixture
def export_command():
    # Create a dummy shell with an empty file system.
    dummy_shell = DummyShell({})
    # Initialize the environment dictionary on the shell.
    dummy_shell.environ = {}
    # Create ExportCommand with the required shell_context.
    command = ExportCommand(shell_context=dummy_shell)
    return command

# Test that calling export with no arguments returns an empty string and makes no changes.
def test_export_no_arguments(export_command):
    output = export_command.execute([])
    assert output == ""
    assert export_command.shell.environ == {}

# Test that export sets environment variables correctly.
def test_export_set_variables(export_command):
    output = export_command.execute(["FOO=bar", "HELLO=world"])
    # Command returns an empty string.
    assert output == ""
    # Check that environment variables have been updated.
    env = export_command.shell.environ
    assert env.get("FOO") == "bar"
    assert env.get("HELLO") == "world"

# Test that export only sets variables for arguments containing "=".
def test_export_invalid_argument(export_command):
    # Pre-populate environment with an existing variable.
    export_command.shell.environ["PRESET"] = "value"
    # Call export with one valid assignment and one invalid argument.
    output = export_command.execute(["NEW=value", "INVALID"])
    # Command returns an empty string.
    assert output == ""
    env = export_command.shell.environ
    # Verify that NEW is added and PRESET remains unchanged.
    assert env.get("NEW") == "value"
    assert env.get("PRESET") == "value"
    # "INVALID" is ignored since it does not contain "=".
    assert "INVALID" not in env
