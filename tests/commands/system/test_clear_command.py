"""
tests/chuk_virtual_shell/commands/system/test_clear_command.py
"""
import pytest
from chuk_virtual_shell.commands.system.clear import ClearCommand
from tests.dummy_shell import DummyShell

# Fixture to create a ClearCommand with a dummy shell as the shell_context
@pytest.fixture
def clear_command():
    # Setup a dummy file system; it won't be used by ClearCommand.
    files = {}
    dummy_shell = DummyShell(files)
    # Create ClearCommand with the required shell_context.
    command = ClearCommand(shell_context=dummy_shell)
    return command

# Test that ClearCommand returns the ANSI escape code to clear the screen.
def test_clear_command(clear_command):
    output = clear_command.execute([])
    # ANSI escape code to clear the screen and reposition the cursor.
    expected = "\033[2J\033[H"
    assert output == expected
