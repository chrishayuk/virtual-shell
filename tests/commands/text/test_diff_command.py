"""
tests/commands/text/test_diff_command.py - Tests for diff command
"""

import pytest
from tests.dummy_shell import DummyShell
from chuk_virtual_shell.commands.text.diff import DiffCommand


@pytest.fixture
def diff_setup():
    """Set up diff command with test files"""
    shell = DummyShell({})  # Initialize with empty files dict
    cmd = DiffCommand(shell)

    # Create test files
    shell.create_file("file1.txt", "Line 1\nLine 2\nLine 3\nLine 4")
    shell.create_file("file2.txt", "Line 1\nLine 2 modified\nLine 3\nLine 4\nLine 5")
    shell.create_file("same1.txt", "Same content\nOn multiple lines")
    shell.create_file("same2.txt", "Same content\nOn multiple lines")

    return shell, cmd


def test_diff_missing_operand():
    """Test diff with missing operands"""
    shell = DummyShell({})
    cmd = DiffCommand(shell)

    result = cmd.execute([])
    assert "missing operand" in result

    result = cmd.execute(["file1.txt"])
    assert "missing operand" in result


def test_diff_file_not_found(diff_setup):
    """Test diff with non-existent files"""
    shell, cmd = diff_setup

    result = cmd.execute(["nonexistent.txt", "file1.txt"])
    assert "No such file or directory" in result

    result = cmd.execute(["file1.txt", "nonexistent.txt"])
    assert "No such file or directory" in result


def test_diff_identical_files(diff_setup):
    """Test diff with identical files"""
    shell, cmd = diff_setup

    result = cmd.execute(["same1.txt", "same2.txt"])
    assert result == ""  # No output for identical files


def test_diff_unified_format(diff_setup):
    """Test diff with unified format (default)"""
    shell, cmd = diff_setup

    result = cmd.execute(["-u", "file1.txt", "file2.txt"])
    assert "---" in result
    assert "+++" in result
    assert "@@" in result
    assert "-Line 2" in result
    assert "+Line 2 modified" in result
    assert "+Line 5" in result


def test_diff_context_format(diff_setup):
    """Test diff with context format"""
    shell, cmd = diff_setup

    result = cmd.execute(["-c", "file1.txt", "file2.txt"])
    assert "***" in result
    assert "---" in result


def test_diff_normal_format(diff_setup):
    """Test diff with normal format"""
    shell, cmd = diff_setup

    result = cmd.execute(["-n", "file1.txt", "file2.txt"])
    lines = result.splitlines()
    # Should contain change indicators like 2c2 or 4a5
    assert any("c" in line or "a" in line or "d" in line for line in lines)


def test_diff_brief_mode(diff_setup):
    """Test diff in brief mode"""
    shell, cmd = diff_setup

    # Different files
    result = cmd.execute(["-q", "file1.txt", "file2.txt"])
    assert "differ" in result

    # Same files
    result = cmd.execute(["-q", "same1.txt", "same2.txt"])
    assert result == ""


def test_diff_ignore_case(diff_setup):
    """Test diff with ignore case option"""
    shell, cmd = diff_setup

    shell.create_file("upper.txt", "HELLO\nWORLD")
    shell.create_file("lower.txt", "hello\nworld")

    # Without ignore case
    result = cmd.execute(["upper.txt", "lower.txt"])
    assert len(result) > 0  # Should show differences

    # With ignore case
    result = cmd.execute(["-i", "upper.txt", "lower.txt"])
    assert result == ""  # Should be identical when ignoring case


def test_diff_ignore_whitespace(diff_setup):
    """Test diff with whitespace options"""
    shell, cmd = diff_setup

    shell.create_file("spaces1.txt", "hello  world\ntest    line")
    shell.create_file("spaces2.txt", "hello world\ntest line")

    # Without ignore whitespace
    result = cmd.execute(["spaces1.txt", "spaces2.txt"])
    assert len(result) > 0

    # With ignore space change
    result = cmd.execute(["-b", "spaces1.txt", "spaces2.txt"])
    assert result == ""

    # With ignore all space
    shell.create_file("spaces3.txt", "helloworld\ntestline")
    result = cmd.execute(["-w", "spaces1.txt", "spaces3.txt"])
    assert result == ""


def test_diff_ignore_blank_lines(diff_setup):
    """Test diff ignoring blank lines"""
    shell, cmd = diff_setup

    shell.create_file("blank1.txt", "Line 1\n\nLine 2\n\n\nLine 3")
    shell.create_file("blank2.txt", "Line 1\nLine 2\nLine 3")

    # Without ignore blank lines
    result = cmd.execute(["blank1.txt", "blank2.txt"])
    assert len(result) > 0

    # With ignore blank lines
    result = cmd.execute(["-B", "blank1.txt", "blank2.txt"])
    assert result == ""


def test_diff_side_by_side(diff_setup):
    """Test side-by-side diff format"""
    shell, cmd = diff_setup

    result = cmd.execute(["--side-by-side", "file1.txt", "file2.txt"])
    assert "|" in result  # Column separator
    assert "<" in result or ">" in result  # Difference markers


def test_diff_with_additions_only():
    """Test diff when file2 only has additions"""
    shell = DummyShell({})
    cmd = DiffCommand(shell)

    shell.create_file("base.txt", "Line 1\nLine 2")
    shell.create_file("extended.txt", "Line 1\nLine 2\nLine 3\nLine 4")

    result = cmd.execute(["-u", "base.txt", "extended.txt"])
    assert "+Line 3" in result
    assert "+Line 4" in result
    assert "-" not in result or "---" in result  # No deletions except header


def test_diff_with_deletions_only():
    """Test diff when file2 only has deletions"""
    shell = DummyShell({})
    cmd = DiffCommand(shell)

    shell.create_file("full.txt", "Line 1\nLine 2\nLine 3\nLine 4")
    shell.create_file("reduced.txt", "Line 1\nLine 3")

    result = cmd.execute(["-u", "full.txt", "reduced.txt"])
    assert "-Line 2" in result
    assert "-Line 4" in result
