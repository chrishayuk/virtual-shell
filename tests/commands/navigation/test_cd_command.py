"""
tests/virtual_shell/commands/navigation/test_cd_command.py
"""
import pytest
from virtual_shell.commands.navigation.cd import CdCommand
from tests.dummy_shell import DummyShell

# Fixture to create a CdCommand with a dummy shell as the shell_context
@pytest.fixture
def cd_command():
    # Setup a dummy file system with some directories.
    # For example, a "home" directory and a "projects" directory.
    files = {
        "home": {},
        "projects": {},
    }
    dummy_shell = DummyShell(files)
    # Set default current directory to root.
    dummy_shell.fs.current_directory = "/"
    # Set environment variables (e.g., HOME and initial PWD)
    dummy_shell.environ = {"HOME": "home", "PWD": "/"}
    # Create CdCommand with the required shell_context
    command = CdCommand(shell_context=dummy_shell)
    return command

# Test cd with no arguments uses HOME from environment.
def test_cd_no_argument_home_set(cd_command):
    # No argument should default to HOME ("home").
    output = cd_command.execute([])
    assert output == ""
    # Verify that the directory changed to HOME.
    env = cd_command.shell.environ
    assert env["PWD"] == cd_command.shell.fs.pwd() == "home"

# Test cd with no arguments when HOME is not set: defaults to "/"
def test_cd_no_argument_home_not_set():
    # Setup a dummy shell without HOME defined.
    files = {"home": {}}
    dummy_shell = DummyShell(files)
    dummy_shell.fs.current_directory = "/"
    dummy_shell.environ = {}  # No HOME defined.
    command = CdCommand(shell_context=dummy_shell)
    output = command.execute([])
    assert output == ""
    # Should default to "/" since HOME is not set.
    env = command.shell.environ
    assert env.get("PWD") == command.shell.fs.pwd() == "/"

# Test cd to a valid directory.
def test_cd_valid_directory(cd_command):
    # Change to "projects" directory.
    output = cd_command.execute(["projects"])
    assert output == ""
    env = cd_command.shell.environ
    assert env["PWD"] == cd_command.shell.fs.pwd() == "projects"

# Test cd to an invalid directory.
def test_cd_invalid_directory(cd_command):
    output = cd_command.execute(["nonexistent"])
    assert output == "cd: nonexistent: No such directory"
    # Ensure that PWD remains unchanged.
    assert cd_command.shell.environ["PWD"] == cd_command.shell.fs.pwd()
