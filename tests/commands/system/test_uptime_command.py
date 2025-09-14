import re
import time
import pytest
from chuk_virtual_shell.commands.system.uptime import UptimeCommand
from tests.dummy_shell import DummyShell


@pytest.fixture
def uptime_command():
    # Setup a dummy shell.
    dummy_shell = DummyShell({})
    # Simulate that the shell started 2 hours (7200 seconds) ago.
    dummy_shell.start_time = time.time() - 7200
    return UptimeCommand(shell_context=dummy_shell)


def test_uptime_command_format(uptime_command):
    """
    The uptime command should return a string in the format:
    'Uptime: Xh Ym Zs'
    """
    output = uptime_command.execute([])
    # Check that the output starts with "Uptime:".
    assert output.startswith("Uptime:")
    # Validate the overall format using regex.
    pattern = r"Uptime:\s+(\d+)h\s+(\d+)m\s+(\d+)s"
    match = re.match(pattern, output)
    assert match is not None, "Uptime output format is incorrect"
    # Verify that the hours are at least 2 (since we set a 2-hour offset).
    hours = int(match.group(1))
    assert hours >= 2


def test_uptime_command_with_extra_args(uptime_command):
    """
    Passing extra arguments should trigger the help message.
    """
    output = uptime_command.execute(["unexpected"])
    # Assuming help_text is returned when args are provided.
    assert uptime_command.get_help() in output or output == ""
