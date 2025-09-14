import pytest
from chuk_virtual_shell.commands.environment.env import EnvCommand
from tests.dummy_shell import DummyShell


# Fixture to create an EnvCommand with a dummy shell as the shell_context.
@pytest.fixture
def env_command():
    # Create a dummy shell with an empty file system.
    dummy_shell = DummyShell({})
    # Add an environment dictionary with multiple variables.
    dummy_shell.environ = {"VAR1": "value1", "VAR2": "value2", "OTHER": "oops"}
    # Create the EnvCommand instance.
    command = EnvCommand(shell_context=dummy_shell)
    return command


# Test for proper output when no filter is applied.
def test_env_command_output(env_command):
    output = env_command.execute([])
    lines = set(output.split("\n"))
    expected_lines = {"VAR1=value1", "VAR2=value2", "OTHER=oops"}
    assert lines == expected_lines


# Test filtering: only variables that contain "VAR" should be shown.
def test_env_command_filter(env_command):
    output = env_command.execute(["VAR"])
    lines = set(output.split("\n"))
    expected_lines = {"VAR1=value1", "VAR2=value2"}
    assert lines == expected_lines


# Test filtering when no variable matches the filter.
def test_env_command_no_match(env_command):
    output = env_command.execute(["NONEXISTENT"])
    # Expect an empty output when the filter does not match any environment variable.
    assert output == ""
