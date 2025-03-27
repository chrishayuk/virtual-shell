"""
tests/virtual_shell/commands/system/test_exit_command.py
"""
import pytest
from virtual_shell.commands.system.exit import ExitCommand
from tests.dummy_shell import DummyShell

# Fixture to create an ExitCommand with a dummy shell as the shell_context
@pytest.fixture
def exit_command():
    # Setup a dummy file system; it won't be used by ExitCommand.
    files = {}
    dummy_shell = DummyShell(files)
    # Set the initial running state to True
    dummy_shell.running = True
    # Create ExitCommand with the required shell_context.
    command = ExitCommand(shell_context=dummy_shell)
    return command

# Test that ExitCommand stops the shell and returns a goodbye message.
def test_exit_command(exit_command):
    output = exit_command.execute([])
    # Verify that the command returns the expected message.
    assert output == "Goodbye!"
    # Verify that the shell's running attribute has been set to False.
    assert exit_command.shell.running is False
