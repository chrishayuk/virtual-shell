"""
tests/chuk_virtual_shell/commands/text/test_grep_command.py
"""

import pytest
from chuk_virtual_shell.commands.text.grep import GrepCommand
from tests.dummy_shell import DummyShell


@pytest.fixture
def grep_command():
    # Setup a dummy file system with sample files
    files = {
        "file1.txt": "Hello world\nThis is a test\nHello again",
        "file2.txt": "HELLO WORLD\nAnother test\nGoodbye world",
        "numbers.txt": "Line 1\nLine 2\nLine 3\nLine 4",
        "words.txt": "The quick brown fox\njumps over the\nlazy dog",
        "dir/nested.txt": "Nested file content\nWith pattern inside",
    }
    dummy_shell = DummyShell(files)
    command = GrepCommand(shell_context=dummy_shell)
    return command


def test_grep_missing_pattern(grep_command):
    output = grep_command.execute([])
    assert output == "grep: missing pattern"


def test_grep_no_files(grep_command):
    output = grep_command.execute(["pattern"])
    assert output == "grep: no input files"


def test_grep_basic_search(grep_command):
    output = grep_command.execute(["Hello", "file1.txt"])
    assert output == "Hello world\nHello again"


def test_grep_case_insensitive(grep_command):
    output = grep_command.execute(["-i", "hello", "file2.txt"])
    assert output == "HELLO WORLD"


def test_grep_invert_match(grep_command):
    output = grep_command.execute(["-v", "Hello", "file1.txt"])
    assert output == "This is a test"


def test_grep_line_numbers(grep_command):
    output = grep_command.execute(["-n", "Line", "numbers.txt"])
    assert "1:Line 1" in output
    assert "2:Line 2" in output
    assert "3:Line 3" in output
    assert "4:Line 4" in output


def test_grep_count_only(grep_command):
    output = grep_command.execute(["-c", "Line", "numbers.txt"])
    assert output == "4"


def test_grep_multiple_files(grep_command):
    output = grep_command.execute(["world", "file1.txt", "file2.txt"])
    assert "file1.txt:Hello world" in output
    assert "file2.txt:Goodbye world" in output


def test_grep_whole_word(grep_command):
    output = grep_command.execute(["-w", "the", "words.txt"])
    assert output == "jumps over the"


def test_grep_list_files_only(grep_command):
    output = grep_command.execute(["-l", "world", "file1.txt", "file2.txt"])
    lines = output.split("\n")
    assert "file1.txt" in lines
    assert "file2.txt" in lines


def test_grep_no_filename(grep_command):
    output = grep_command.execute(["-h", "world", "file1.txt", "file2.txt"])
    assert "file1.txt:" not in output
    assert "file2.txt:" not in output
    assert "Hello world" in output


def test_grep_combined_options(grep_command):
    output = grep_command.execute(["-in", "hello", "file1.txt"])
    assert "1:Hello world" in output
    assert "3:Hello again" in output


def test_grep_file_not_found(grep_command):
    output = grep_command.execute(["pattern", "nonexistent.txt"])
    assert "No such file or directory" in output


def test_grep_extended_regex(grep_command):
    output = grep_command.execute(["-E", "H.*o", "file1.txt"])
    assert "Hello world" in output
    assert "Hello again" in output


def test_grep_stdin_simulation(grep_command):
    # Simulate stdin by setting the stdin buffer
    grep_command.shell._stdin_buffer = "Test line 1\nMatching line\nTest line 2"
    output = grep_command.execute(["Matching"])
    assert output == "Matching line"
