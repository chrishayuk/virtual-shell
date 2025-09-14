"""
tests/chuk_virtual_shell/commands/text/test_head_tail_commands.py
"""

import pytest
from chuk_virtual_shell.commands.text.head import HeadCommand
from chuk_virtual_shell.commands.text.tail import TailCommand
from tests.dummy_shell import DummyShell


@pytest.fixture
def commands():
    # Create content with 20 lines
    lines = [f"Line {i}" for i in range(1, 21)]
    content = "\n".join(lines)

    files = {
        "test.txt": content,
        "short.txt": "Line 1\nLine 2\nLine 3",
        "bytes.txt": "Hello World!",  # 12 bytes
    }
    dummy_shell = DummyShell(files)

    head_command = HeadCommand(shell_context=dummy_shell)
    tail_command = TailCommand(shell_context=dummy_shell)
    return head_command, tail_command, dummy_shell


# HEAD COMMAND TESTS


def test_head_default(commands):
    head_command, _, _ = commands
    output = head_command.execute(["test.txt"])
    lines = output.splitlines()
    assert len(lines) == 10
    assert lines[0] == "Line 1"
    assert lines[9] == "Line 10"


def test_head_specific_lines(commands):
    head_command, _, _ = commands
    output = head_command.execute(["-n", "5", "test.txt"])
    lines = output.splitlines()
    assert len(lines) == 5
    assert lines[0] == "Line 1"
    assert lines[4] == "Line 5"


def test_head_legacy_format(commands):
    head_command, _, _ = commands
    output = head_command.execute(["-5", "test.txt"])
    lines = output.splitlines()
    assert len(lines) == 5


def test_head_combined_format(commands):
    head_command, _, _ = commands
    output = head_command.execute(["-n5", "test.txt"])
    lines = output.splitlines()
    assert len(lines) == 5


def test_head_bytes(commands):
    head_command, _, _ = commands
    output = head_command.execute(["-c", "5", "bytes.txt"])
    assert output == "Hello"


def test_head_multiple_files(commands):
    head_command, _, _ = commands
    output = head_command.execute(["-n", "2", "test.txt", "short.txt"])
    assert "==> test.txt <==" in output
    assert "==> short.txt <==" in output
    assert "Line 1" in output
    assert "Line 2" in output


def test_head_quiet_mode(commands):
    head_command, _, _ = commands
    output = head_command.execute(["-q", "-n", "2", "test.txt", "short.txt"])
    assert "==>" not in output
    assert "Line 1" in output


def test_head_verbose_mode(commands):
    head_command, _, _ = commands
    output = head_command.execute(["-v", "-n", "2", "test.txt"])
    assert "==> test.txt <==" in output


def test_head_stdin(commands):
    head_command, _, dummy_shell = commands
    dummy_shell._stdin_buffer = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"
    output = head_command.execute(["-n", "3"])
    lines = output.splitlines()
    assert len(lines) == 3
    assert lines[2] == "Line 3"


def test_head_file_not_found(commands):
    head_command, _, _ = commands
    output = head_command.execute(["nonexistent.txt"])
    assert "No such file or directory" in output


# TAIL COMMAND TESTS


def test_tail_default(commands):
    _, tail_command, _ = commands
    output = tail_command.execute(["test.txt"])
    lines = output.splitlines()
    assert len(lines) == 10
    assert lines[0] == "Line 11"
    assert lines[9] == "Line 20"


def test_tail_specific_lines(commands):
    _, tail_command, _ = commands
    output = tail_command.execute(["-n", "5", "test.txt"])
    lines = output.splitlines()
    assert len(lines) == 5
    assert lines[0] == "Line 16"
    assert lines[4] == "Line 20"


def test_tail_legacy_format(commands):
    _, tail_command, _ = commands
    output = tail_command.execute(["-5", "test.txt"])
    lines = output.splitlines()
    assert len(lines) == 5
    assert lines[0] == "Line 16"


def test_tail_combined_format(commands):
    _, tail_command, _ = commands
    output = tail_command.execute(["-n5", "test.txt"])
    lines = output.splitlines()
    assert len(lines) == 5


def test_tail_bytes(commands):
    _, tail_command, _ = commands
    output = tail_command.execute(["-c", "6", "bytes.txt"])
    assert output == "World!"


def test_tail_from_line(commands):
    _, tail_command, _ = commands
    output = tail_command.execute(["-n", "+15", "test.txt"])
    lines = output.splitlines()
    assert len(lines) == 6  # Lines 15-20
    assert lines[0] == "Line 15"
    assert lines[5] == "Line 20"


def test_tail_multiple_files(commands):
    _, tail_command, _ = commands
    output = tail_command.execute(["-n", "2", "test.txt", "short.txt"])
    assert "==> test.txt <==" in output
    assert "==> short.txt <==" in output
    assert "Line 19" in output
    assert "Line 20" in output
    assert "Line 3" in output


def test_tail_quiet_mode(commands):
    _, tail_command, _ = commands
    output = tail_command.execute(["-q", "-n", "2", "test.txt", "short.txt"])
    assert "==>" not in output


def test_tail_verbose_mode(commands):
    _, tail_command, _ = commands
    output = tail_command.execute(["-v", "-n", "2", "test.txt"])
    assert "==> test.txt <==" in output


def test_tail_stdin(commands):
    _, tail_command, dummy_shell = commands
    dummy_shell._stdin_buffer = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"
    output = tail_command.execute(["-n", "3"])
    lines = output.splitlines()
    assert len(lines) == 3
    assert lines[0] == "Line 3"
    assert lines[2] == "Line 5"


def test_tail_follow_warning(commands):
    _, tail_command, _ = commands
    output = tail_command.execute(["-f", "test.txt"])
    assert "follow mode not fully supported" in output


def test_tail_file_not_found(commands):
    _, tail_command, _ = commands
    output = tail_command.execute(["nonexistent.txt"])
    assert "No such file or directory" in output
