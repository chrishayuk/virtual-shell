"""
tests/test_shell_redirection.py - Tests for shell output redirection
"""

import pytest
from chuk_virtual_shell.shell_interpreter import ShellInterpreter


@pytest.fixture
def shell():
    """Create a shell instance for testing"""
    shell = ShellInterpreter()
    shell.execute("mkdir /tmp")
    return shell


def test_basic_output_redirection(shell):
    """Test basic output redirection with >"""
    # Redirect echo output to file
    result = shell.execute('echo "Hello World" > /tmp/output.txt')
    assert result == ""  # No output to terminal when redirecting

    # Check file contents
    content = shell.fs.read_file("/tmp/output.txt")
    assert content == "Hello World"


def test_append_redirection(shell):
    """Test append redirection with >>"""
    # Create initial file
    shell.execute('echo "Line 1" > /tmp/append.txt')

    # Append more lines
    shell.execute('echo "Line 2" >> /tmp/append.txt')
    shell.execute('echo "Line 3" >> /tmp/append.txt')

    # Check file contents
    content = shell.fs.read_file("/tmp/append.txt")
    assert content == "Line 1\nLine 2\nLine 3"


def test_overwrite_redirection(shell):
    """Test that > overwrites existing files"""
    # Create initial file
    shell.execute('echo "Original content" > /tmp/overwrite.txt')

    # Overwrite with new content
    shell.execute('echo "New content" > /tmp/overwrite.txt')

    # Check file contents
    content = shell.fs.read_file("/tmp/overwrite.txt")
    assert content == "New content"
    assert "Original" not in content


def test_redirection_with_commands(shell):
    """Test redirection with various commands"""
    # Create test data
    shell.fs.write_file("/tmp/data.txt", "Line 1\nLine 2\nLine 3\nLine 4\nLine 5")

    # Test with head
    shell.execute("head -n 3 /tmp/data.txt > /tmp/head_output.txt")
    content = shell.fs.read_file("/tmp/head_output.txt")
    assert content == "Line 1\nLine 2\nLine 3"

    # Test with grep
    shell.execute('grep "3" /tmp/data.txt > /tmp/grep_output.txt')
    content = shell.fs.read_file("/tmp/grep_output.txt")
    assert content == "Line 3"

    # Test with sort
    shell.fs.write_file("/tmp/unsorted.txt", "zebra\napple\nbanana")
    shell.execute("sort /tmp/unsorted.txt > /tmp/sorted.txt")
    content = shell.fs.read_file("/tmp/sorted.txt")
    assert content == "apple\nbanana\nzebra"


def test_redirection_with_pipes(shell):
    """Test redirection at the end of a pipeline"""
    # Create test data
    shell.fs.write_file("/tmp/numbers.txt", "5\n2\n8\n1\n9\n3")

    # Pipeline with redirection
    shell.execute("cat /tmp/numbers.txt | sort -n | head -n 3 > /tmp/result.txt")

    content = shell.fs.read_file("/tmp/result.txt")
    assert content == "1\n2\n3"


def test_redirection_with_quoted_filename(shell):
    """Test redirection with quoted filenames containing spaces"""
    # Redirect to filename with spaces
    shell.execute('echo "Test content" > "/tmp/file with spaces.txt"')

    content = shell.fs.read_file("/tmp/file with spaces.txt")
    assert content == "Test content"


def test_redirection_preserves_quotes_in_content(shell):
    """Test that quotes in command output are preserved"""
    # Echo with quotes
    shell.execute("echo 'He said \"Hello\"' > /tmp/quotes.txt")

    content = shell.fs.read_file("/tmp/quotes.txt")
    assert content == 'He said "Hello"'


def test_redirection_with_diff(shell):
    """Test redirection with diff command"""
    # Create two files to diff
    shell.fs.write_file("/tmp/file1.txt", "Line 1\nLine 2\nLine 3")
    shell.fs.write_file("/tmp/file2.txt", "Line 1\nLine 2 modified\nLine 3")

    # Redirect diff output
    shell.execute("diff -u /tmp/file1.txt /tmp/file2.txt > /tmp/diff.patch")

    content = shell.fs.read_file("/tmp/diff.patch")
    assert "---" in content
    assert "+++" in content
    assert "-Line 2" in content
    assert "+Line 2 modified" in content


def test_redirection_with_awk(shell):
    """Test redirection with awk command"""
    # Create CSV data
    shell.fs.write_file("/tmp/data.csv", "Alice,30\nBob,25\nCharlie,35")

    # Use awk with redirection
    shell.execute("awk -F, '{print $1}' /tmp/data.csv > /tmp/names.txt")

    content = shell.fs.read_file("/tmp/names.txt")
    assert content == "Alice\nBob\nCharlie"


def test_redirection_with_sed(shell):
    """Test redirection with sed command"""
    # Create test file
    shell.fs.write_file("/tmp/input.txt", "foo bar\nbaz foo\nqux")

    # Use sed with redirection
    shell.execute("sed s/foo/FOO/g /tmp/input.txt > /tmp/sed_output.txt")

    content = shell.fs.read_file("/tmp/sed_output.txt")
    assert content == "FOO bar\nbaz FOO\nqux"


def test_empty_output_redirection(shell):
    """Test redirecting empty output"""
    # Create an empty file and cat it (produces empty output)
    shell.execute("touch /tmp/source_empty.txt")
    shell.execute("cat /tmp/source_empty.txt > /tmp/empty.txt")

    content = shell.fs.read_file("/tmp/empty.txt")
    assert content == ""


def test_redirection_error_handling(shell):
    """Test error handling with redirection"""
    # Try to redirect output from non-existent command
    result = shell.execute("nonexistent > /tmp/error.txt")
    assert "command not found" in result

    # File should not be created for failed commands
    content = shell.fs.read_file("/tmp/error.txt")
    assert content is None


def test_multiple_redirections_in_pipeline(shell):
    """Test that only the last redirection in a pipeline works"""
    # Create test data
    shell.fs.write_file("/tmp/input.txt", "apple\nbanana\ncherry")

    # This should redirect the final output, not intermediate
    shell.execute("cat /tmp/input.txt | sort > /tmp/sorted.txt")

    content = shell.fs.read_file("/tmp/sorted.txt")
    assert content == "apple\nbanana\ncherry"


def test_redirection_with_ls(shell):
    """Test redirection with ls command"""
    # Create some files
    shell.execute("mkdir /tmp/testdir")
    shell.execute("touch /tmp/testdir/file1.txt")
    shell.execute("touch /tmp/testdir/file2.txt")
    shell.execute("mkdir /tmp/testdir/subdir")

    # Redirect ls output
    shell.execute("ls /tmp/testdir > /tmp/ls_output.txt")

    content = shell.fs.read_file("/tmp/ls_output.txt")
    assert "file1.txt" in content
    assert "file2.txt" in content
    assert "subdir" in content


def test_redirection_with_wc(shell):
    """Test redirection with wc command"""
    # Create test file
    shell.fs.write_file("/tmp/count.txt", "One\nTwo\nThree\nFour Five")

    # Redirect wc output
    shell.execute("wc /tmp/count.txt > /tmp/wc_output.txt")

    content = shell.fs.read_file("/tmp/wc_output.txt")
    # Should show lines, words, bytes
    assert "4" in content  # 4 lines
    assert "5" in content  # 5 words
