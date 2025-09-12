import pytest
from chuk_virtual_shell.commands.system.exit import ExitCommand
from tests.dummy_shell import DummyShell


# Fixture to create an ExitCommand with a dummy shell as the shell_context.
@pytest.fixture
def exit_command():
    # Setup a dummy file system; it won't be used by ExitCommand.
    files = {}
    dummy_shell = DummyShell(files)
    # Ensure the shell is initially running.
    dummy_shell.running = True
    # Optionally, snapshot the initial shell state (excluding running).
    dummy_shell.initial_state = dummy_shell.__dict__.copy()
    # Create ExitCommand with the required shell_context.
    command = ExitCommand(shell_context=dummy_shell)
    return command


def test_exit_command_basic(exit_command):
    """
    Test that executing the exit command returns the expected goodbye message and stops the shell.
    """
    output = exit_command.execute([])
    assert output == "Goodbye!"
    assert exit_command.shell.running is False


def test_exit_command_with_extra_args(exit_command):
    """
    Test that providing extra arguments to the exit command does not affect the outcome.
    """
    # Reset running state for testing.
    exit_command.shell.running = True
    output = exit_command.execute(["extra", "arguments"])
    assert output == "Goodbye!"
    assert exit_command.shell.running is False


def test_exit_command_no_side_effects(exit_command):
    """
    Verify that aside from stopping the shell, no other shell attributes are unexpectedly modified.
    """
    # Capture a snapshot of the shell's state before executing the command.
    initial_state = exit_command.shell.initial_state.copy()
    # Execute the exit command.
    _ = exit_command.execute([])
    # Remove the 'running' attribute and any extra keys (like 'initial_state') from the comparison.
    for key in ["running", "initial_state"]:
        initial_state.pop(key, None)
    current_state = exit_command.shell.__dict__.copy()
    for key in ["running", "initial_state"]:
        current_state.pop(key, None)
    assert current_state == initial_state
