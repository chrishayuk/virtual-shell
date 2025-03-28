import pytest
from chuk_virtual_shell.commands.system.clear import ClearCommand
from tests.dummy_shell import DummyShell

# Fixture to create a ClearCommand with a dummy shell as the shell_context.
@pytest.fixture
def clear_command():
    # Setup a dummy file system; it won't be used by ClearCommand.
    files = {}
    dummy_shell = DummyShell(files)
    # Optionally, record initial shell state to verify it's unchanged.
    dummy_shell.initial_state = dummy_shell.__dict__.copy()
    # Create ClearCommand with the required shell_context.
    command = ClearCommand(shell_context=dummy_shell)
    return command

# Test that ClearCommand returns the ANSI escape code to clear the screen.
def test_clear_command_returns_ansi(clear_command):
    output = clear_command.execute([])
    expected = "\033[2J\033[H"  # ANSI escape code to clear the screen and reposition the cursor.
    assert output == expected

# Test that extra arguments do not affect the output.
def test_clear_command_with_extra_args(clear_command):
    output = clear_command.execute(["unexpected", "args"])
    expected = "\033[2J\033[H"
    assert output == expected

# Test that the shell context remains unchanged after executing the command.
def test_clear_command_does_not_modify_shell(clear_command):
    # Execute the command.
    _ = clear_command.execute([])
    # Verify that the shell's state remains unchanged (based on our initial snapshot).
    for key, value in clear_command.shell.initial_state.items():
        assert clear_command.shell.__dict__.get(key) == value
