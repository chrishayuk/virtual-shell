"""
tests/virtual_shell/commands/navigation/test_pwd_command.py
"""
import pytest
from virtual_shell.commands.navigation.pwd import PwdCommand
from tests.dummy_shell import DummyShell

# Fixture to create a PwdCommand with a dummy shell as the shell_context
@pytest.fixture
def pwd_command():
    # Setup a dummy file system (files are not needed for pwd).
    files = {}
    dummy_shell = DummyShell(files)
    # Set the current directory in the dummy file system.
    dummy_shell.fs.current_directory = "/my/test/directory"
    # Create PwdCommand with the required shell_context.
    command = PwdCommand(shell_context=dummy_shell)
    return command

# Test that PwdCommand returns the correct current directory.
def test_pwd_command(pwd_command):
    output = pwd_command.execute([])
    assert output == "/my/test/directory"
