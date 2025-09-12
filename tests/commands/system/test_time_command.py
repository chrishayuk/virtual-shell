import re
import time
import pytest
from chuk_virtual_shell.commands.system.time import TimeCommand
from tests.dummy_shell import DummyShell


@pytest.fixture
def time_command():
    dummy_shell = DummyShell({})
    dummy_shell.start_time = time.time()
    # Simulate a slight delay (e.g., 0.001 sec) in command execution.
    dummy_shell.execute = lambda cmd: (time.sleep(0.001), "dummy output")[1]
    return TimeCommand(shell_context=dummy_shell)


def test_time_command_no_subcommand(time_command):
    """
    When no subcommand is provided, the time command should display the current time.
    """
    output = time_command.execute([])
    # Expect the output to start with "Current time:" and include a valid time string.
    assert output.startswith("Current time:")
    # Optionally, check for a date/time pattern (YYYY-MM-DD HH:MM:SS).
    pattern = r"Current time:\s*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
    assert re.match(pattern, output)


def test_time_command_with_subcommand(time_command):
    """
    When a subcommand is provided, the time command should execute it, return its output,
    and report the execution time.
    """
    output = time_command.execute(["echo", "hello"])
    # Check that the dummy output is present.
    assert "dummy output" in output
    # Check that execution time is reported.
    pattern = r"Execution time:\s*([\d.]+) seconds"
    match = re.search(pattern, output)
    assert match is not None, "Execution time not reported"
    # Optionally ensure that the reported time is a positive float.
    elapsed = float(match.group(1))
    assert elapsed > 0
