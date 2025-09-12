import pytest
from chuk_virtual_shell.commands.system.whoami import WhoamiCommand
from tests.dummy_shell import DummyShell


@pytest.fixture
def whoami_command():
    # Setup a dummy shell.
    dummy_shell = DummyShell({})
    # Set the USER environment variable.
    dummy_shell.environ = {"USER": "testuser"}
    return WhoamiCommand(shell_context=dummy_shell)


def test_whoami_command_basic(whoami_command):
    """
    The whoami command should return the username from the shell environment.
    """
    output = whoami_command.execute([])
    assert output == "testuser"


def test_whoami_command_with_extra_args(whoami_command):
    """
    If extra arguments are provided, whoami should return its help text.
    """
    output = whoami_command.execute(["unexpected"])
    assert whoami_command.get_help() in output or output == ""
