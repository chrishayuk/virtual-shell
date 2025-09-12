"""
tests/test_sed_command.py - Tests for sed command functionality
"""

import pytest
from chuk_virtual_shell.shell_interpreter import ShellInterpreter


@pytest.fixture
def shell():
    """Create a shell instance for testing"""
    shell = ShellInterpreter()
    shell.execute("mkdir -p /tmp")
    return shell


def test_sed_in_place_editing(shell):
    """Test sed -i flag for in-place file editing"""
    # Create test file
    shell.fs.write_file("/tmp/test.txt", "hello world\ngoodbye world")

    # Edit in place
    result = shell.execute('sed -i "s/world/universe/g" /tmp/test.txt')
    assert result == ""  # No output for in-place editing

    # Check file was modified
    content = shell.fs.read_file("/tmp/test.txt")
    assert content == "hello universe\ngoodbye universe"


def test_sed_in_place_with_multiple_files(shell):
    """Test sed -i with multiple files"""
    # Create test files
    shell.fs.write_file("/tmp/file1.txt", "foo bar")
    shell.fs.write_file("/tmp/file2.txt", "foo baz")

    # Edit both files in place
    shell.execute('sed -i "s/foo/FOO/g" /tmp/file1.txt /tmp/file2.txt')

    assert shell.fs.read_file("/tmp/file1.txt") == "FOO bar"
    assert shell.fs.read_file("/tmp/file2.txt") == "FOO baz"


def test_sed_combined_flags(shell):
    """Test sed with combined flags like -in"""
    # Create test file
    shell.fs.write_file("/tmp/test.txt", "Line 1\nLine 2\nLine 3")

    # Use -in (in-place + quiet)
    shell.execute('sed -in "2d" /tmp/test.txt')

    content = shell.fs.read_file("/tmp/test.txt")
    assert content == "Line 1\nLine 3"


def test_sed_extended_regex(shell):
    """Test sed -E flag for extended regex"""
    # Create test file
    shell.fs.write_file("/tmp/test.txt", "123 abc\n456 def")

    # Use extended regex
    result = shell.execute('sed -E "s/[0-9]+/NUM/g" /tmp/test.txt')
    assert "NUM abc" in result
    assert "NUM def" in result


def test_sed_quiet_mode(shell):
    """Test sed -n flag for quiet mode"""
    # Create test file
    shell.fs.write_file("/tmp/test.txt", "Line 1\nLine 2\nLine 3")

    # Print only specific line
    result = shell.execute('sed -n "2p" /tmp/test.txt')
    assert result == "Line 2"


def test_sed_delete_pattern(shell):
    """Test sed pattern deletion"""
    # Create test file
    shell.fs.write_file("/tmp/test.txt", "keep this\ndelete me\nkeep this too")

    # Delete lines containing pattern
    result = shell.execute('sed "/delete/d" /tmp/test.txt')
    assert "keep this" in result
    assert "keep this too" in result
    assert "delete" not in result


def test_sed_range_operations(shell):
    """Test sed with line ranges"""
    # Create test file
    content = "\n".join([f"Line {i}" for i in range(1, 11)])
    shell.fs.write_file("/tmp/test.txt", content)

    # Delete lines 3-5
    result = shell.execute('sed "3,5d" /tmp/test.txt')
    lines = result.strip().split("\n")
    assert len(lines) == 7
    assert "Line 3" not in result
    assert "Line 4" not in result
    assert "Line 5" not in result


def test_sed_multiple_scripts(shell):
    """Test sed with multiple -e scripts"""
    # Create test file
    shell.fs.write_file("/tmp/test.txt", "foo bar baz")

    # Apply multiple transformations
    result = shell.execute('sed -e "s/foo/FOO/" -e "s/baz/BAZ/" /tmp/test.txt')
    assert result == "FOO bar BAZ"


def test_sed_with_input_redirection(shell):
    """Test sed with input redirection"""
    # Create test file
    shell.fs.write_file("/tmp/input.txt", "hello world")

    # Use sed with input redirection
    result = shell.execute('sed "s/hello/hi/" < /tmp/input.txt')
    assert result == "hi world"


def test_sed_in_pipeline(shell):
    """Test sed in a pipeline"""
    # Create test file
    shell.fs.write_file("/tmp/data.txt", "apple\nbanana\napricot")

    # Use sed in pipeline
    result = shell.execute('cat /tmp/data.txt | sed "s/^a/A/" | grep "^A"')
    assert "Apple" in result
    assert "Apricot" in result
    assert "banana" not in result


def test_sed_case_insensitive(shell):
    """Test sed with case-insensitive flag"""
    # Create test file
    shell.fs.write_file("/tmp/test.txt", "Hello HELLO hello")

    # Case-insensitive replacement
    result = shell.execute('sed "s/hello/hi/gi" /tmp/test.txt')
    assert result == "hi hi hi"


def test_sed_first_occurrence_only(shell):
    """Test sed replacing only first occurrence"""
    # Create test file
    shell.fs.write_file("/tmp/test.txt", "foo foo foo")

    # Replace only first occurrence
    result = shell.execute('sed "s/foo/bar/" /tmp/test.txt')
    assert result == "bar foo foo"


def test_sed_last_line_operations(shell):
    """Test sed operations on last line"""
    # Create test file
    shell.fs.write_file("/tmp/test.txt", "Line 1\nLine 2\nLine 3")

    # Delete last line
    result = shell.execute('sed "$d" /tmp/test.txt')
    assert result == "Line 1\nLine 2"

    # Modify last line
    result = shell.execute('sed "$s/3/THREE/" /tmp/test.txt')
    assert "Line THREE" in result
