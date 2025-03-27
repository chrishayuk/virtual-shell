"""
tests/virtual_shell/commands/environment/test_env_command.py
"""
import pytest
from virtual_shell.commands.environment.env import EnvCommand
from tests.dummy_shell import DummyShell

# Fixture to create an EnvCommand with a dummy shell as the shell_context
@pytest.fixture
def env_command():
    # Create a dummy shell with an empty file system
    dummy_shell = DummyShell({})
    # Add an environment dictionary to the shell.
    dummy_shell.environ = {"VAR1": "value1", "VAR2": "value2"}
    # Create EnvCommand with the required shell_context
    command = EnvCommand(shell_context=dummy_shell)
    return command

# Test for proper environment variable output formatting
def test_env_command_output(env_command):
    output = env_command.execute([])
    # Split output lines; order is not guaranteed so we use set comparison.
    lines = output.split("\n")
    expected_lines = {"VAR1=value1", "VAR2=value2"}
    assert set(lines) == expected_lines
