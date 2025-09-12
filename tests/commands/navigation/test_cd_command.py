import pytest
from chuk_virtual_shell.commands.navigation.cd import CdCommand
from tests.dummy_shell import DummyShell


# Fixture to create a CdCommand with a dummy shell as the shell_context.
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
    # Create CdCommand with the required shell_context.
    command = CdCommand(shell_context=dummy_shell)
    return command


def test_cd_no_argument_home_set(cd_command):
    """
    Test that when no argument is provided and HOME is set,
    cd defaults to HOME.
    """
    output = cd_command.execute([])
    assert output == ""
    env = cd_command.shell.environ
    # Verify that the directory changed to HOME.
    assert env["PWD"] == cd_command.shell.fs.pwd() == "home"


def test_cd_no_argument_home_not_set():
    """
    Test that when no argument is provided and HOME is not set,
    cd defaults to "/" (root).
    """
    files = {"home": {}}
    dummy_shell = DummyShell(files)
    dummy_shell.fs.current_directory = "/"
    dummy_shell.environ = {}  # No HOME defined.
    command = CdCommand(shell_context=dummy_shell)
    output = command.execute([])
    assert output == ""
    env = command.shell.environ
    # Should default to "/" since HOME is not set.
    assert env.get("PWD") == command.shell.fs.pwd() == "/"


def test_cd_valid_directory(cd_command):
    """
    Test that cd to a valid directory (e.g., "projects") changes the PWD.
    """
    output = cd_command.execute(["projects"])
    assert output == ""
    env = cd_command.shell.environ
    assert env["PWD"] == cd_command.shell.fs.pwd() == "projects"


def test_cd_invalid_directory(cd_command):
    """
    Test that attempting to cd to an invalid directory returns an error,
    and that PWD remains unchanged.
    """
    original_pwd = cd_command.shell.environ["PWD"]
    output = cd_command.execute(["nonexistent"])
    assert output == "cd: nonexistent: No such directory"
    # Ensure that the working directory remains unchanged.
    assert cd_command.shell.environ["PWD"] == cd_command.shell.fs.pwd() == original_pwd
