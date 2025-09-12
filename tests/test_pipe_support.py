"""Tests for pipe support in shell interpreter"""

import pytest
from chuk_virtual_shell.shell_interpreter import ShellInterpreter


@pytest.fixture
def shell():
    """Create a shell with test data"""
    shell = ShellInterpreter()
    shell.execute("mkdir /tmp")
    return shell


def test_simple_pipe(shell):
    """Test a simple pipe between two commands"""
    shell.execute("echo 'hello world' > /tmp/test.txt")
    result = shell.execute("cat /tmp/test.txt | wc -w")
    assert result.strip() == "2"


def test_multi_pipe(shell):
    """Test multiple pipes chained together"""
    # Create test data
    shell.execute("echo 'apple' > /tmp/fruits.txt")
    shell.execute("echo 'banana' >> /tmp/fruits.txt")
    shell.execute("echo 'apple' >> /tmp/fruits.txt")
    shell.execute("echo 'cherry' >> /tmp/fruits.txt")

    # Test three-command pipeline
    result = shell.execute("cat /tmp/fruits.txt | sort | uniq")
    lines = result.strip().split("\n")
    assert lines == ["apple", "banana", "cherry"]


def test_pipe_with_grep(shell):
    """Test pipe with grep command"""
    shell.execute("echo 'line with foo' > /tmp/test.txt")
    shell.execute("echo 'line without' >> /tmp/test.txt")
    shell.execute("echo 'another foo line' >> /tmp/test.txt")

    result = shell.execute("cat /tmp/test.txt | grep foo")
    lines = result.strip().split("\n")
    assert len(lines) == 2
    assert "foo" in lines[0]
    assert "foo" in lines[1]


def test_pipe_with_awk(shell):
    """Test pipe with awk command"""
    shell.execute("echo 'Alice,30' > /tmp/data.csv")
    shell.execute("echo 'Bob,25' >> /tmp/data.csv")
    shell.execute("echo 'Charlie,35' >> /tmp/data.csv")

    # Pipe to awk to extract names
    result = shell.execute("cat /tmp/data.csv | awk -F, '{print $1}'")
    assert "Alice" in result
    assert "Bob" in result
    assert "Charlie" in result


def test_pipe_with_head_tail(shell):
    """Test pipe with head and tail commands"""
    # Create numbered lines
    for i in range(1, 11):
        if i == 1:
            shell.execute(f"echo 'line{i}' > /tmp/lines.txt")
        else:
            shell.execute(f"echo 'line{i}' >> /tmp/lines.txt")

    # Get first 5 lines then last 2 of those
    result = shell.execute("cat /tmp/lines.txt | head -n 5 | tail -n 2")
    lines = result.strip().split("\n")
    assert lines == ["line4", "line5"]


def test_pipe_with_sed(shell):
    """Test pipe with sed command"""
    shell.execute("echo 'hello world' > /tmp/test.txt")
    shell.execute("echo 'goodbye world' >> /tmp/test.txt")

    result = shell.execute("cat /tmp/test.txt | sed 's/world/universe/g'")
    assert "hello universe" in result
    assert "goodbye universe" in result


def test_pipe_preserves_newlines(shell):
    """Test that pipes preserve newlines between commands"""
    shell.execute("echo 'line1' > /tmp/test.txt")
    shell.execute("echo 'line2' >> /tmp/test.txt")
    shell.execute("echo 'line3' >> /tmp/test.txt")

    result = shell.execute("cat /tmp/test.txt | grep line")
    lines = result.strip().split("\n")
    assert len(lines) == 3
    assert lines == ["line1", "line2", "line3"]


def test_pipe_error_handling(shell):
    """Test error handling in pipes"""
    # Non-existent command in pipeline
    result = shell.execute("echo hello | nonexistent | wc")
    assert "command not found" in result

    # File not found in first command
    result = shell.execute("cat /nonexistent.txt | wc")
    assert "No such file" in result or "No such file or directory" in result


def test_empty_pipe_segments(shell):
    """Test handling of empty segments in pipe"""
    # Empty segment should be ignored
    result = shell.execute("echo hello | | wc -w")
    assert result.strip() == "1"
