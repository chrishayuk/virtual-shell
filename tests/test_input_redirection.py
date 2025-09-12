"""
tests/test_input_redirection.py - Tests for shell input redirection
"""

import pytest
from chuk_virtual_shell.shell_interpreter import ShellInterpreter


@pytest.fixture
def shell():
    """Create a shell instance for testing"""
    shell = ShellInterpreter()
    shell.execute("mkdir /tmp")
    return shell


def test_basic_input_redirection(shell):
    """Test basic input redirection with <"""
    # Create a file with content
    shell.fs.write_file("/tmp/input.txt", "Hello World\nLine 2\nLine 3")

    # Use wc with input redirection
    result = shell.execute("wc < /tmp/input.txt")
    # Should show 3 lines, 6 words, and byte count
    assert "3" in result
    assert "6" in result


def test_input_redirection_with_grep(shell):
    """Test input redirection with grep"""
    # Create a file with content
    shell.fs.write_file("/tmp/data.txt", "apple\nbanana\napricot\ncherry")

    # Use grep with input redirection (simple pattern)
    result = shell.execute("grep ap < /tmp/data.txt")
    assert "apple" in result
    assert "apricot" in result
    assert "banana" not in result
    assert "cherry" not in result


def test_input_redirection_with_sort(shell):
    """Test input redirection with sort"""
    # Create unsorted file
    shell.fs.write_file("/tmp/unsorted.txt", "zebra\napple\nbanana\ncherry")

    # Sort with input redirection
    result = shell.execute("sort < /tmp/unsorted.txt")
    lines = result.strip().split("\n")
    assert lines == ["apple", "banana", "cherry", "zebra"]


def test_input_redirection_with_head(shell):
    """Test input redirection with head"""
    # Create file with many lines
    content = "\n".join([f"Line {i}" for i in range(1, 21)])
    shell.fs.write_file("/tmp/many_lines.txt", content)

    # Use head with input redirection
    result = shell.execute("head -n 5 < /tmp/many_lines.txt")
    lines = result.strip().split("\n")
    assert len(lines) == 5
    assert lines[0] == "Line 1"
    assert lines[4] == "Line 5"


def test_input_redirection_with_tail(shell):
    """Test input redirection with tail"""
    # Create file
    content = "\n".join([f"Line {i}" for i in range(1, 11)])
    shell.fs.write_file("/tmp/lines.txt", content)

    # Use tail with input redirection
    result = shell.execute("tail -n 3 < /tmp/lines.txt")
    lines = result.strip().split("\n")
    assert len(lines) == 3
    assert lines[0] == "Line 8"
    assert lines[2] == "Line 10"


def test_input_redirection_with_sed(shell):
    """Test input redirection with sed"""
    # Create file
    shell.fs.write_file("/tmp/sed_input.txt", "foo bar\nbaz foo\nqux")

    # Use sed with input redirection
    result = shell.execute("sed s/foo/FOO/g < /tmp/sed_input.txt")
    assert "FOO bar" in result
    assert "baz FOO" in result


def test_input_redirection_with_awk(shell):
    """Test input redirection with awk"""
    # Create CSV file
    shell.fs.write_file(
        "/tmp/data.csv", "Alice,30,Engineer\nBob,25,Designer\nCharlie,35,Manager"
    )

    # Use awk with input redirection
    result = shell.execute("awk -F, '{print $1}' < /tmp/data.csv")
    assert "Alice" in result
    assert "Bob" in result
    assert "Charlie" in result


def test_input_and_output_redirection(shell):
    """Test combined input and output redirection"""
    # Create input file
    shell.fs.write_file("/tmp/input.txt", "zebra\napple\nbanana")

    # Sort with both input and output redirection
    result = shell.execute("sort < /tmp/input.txt > /tmp/sorted.txt")
    assert result == ""  # No terminal output

    # Check output file
    content = shell.fs.read_file("/tmp/sorted.txt")
    assert content == "apple\nbanana\nzebra"


def test_input_redirection_with_patch(shell):
    """Test input redirection with patch command"""
    # Create original file
    shell.fs.write_file("/tmp/original.txt", "Line 1\nLine 2\nLine 3")

    # Create patch file
    patch_content = """--- /tmp/original.txt
+++ /tmp/modified.txt
@@ -1,3 +1,3 @@
 Line 1
-Line 2
+Line 2 modified
 Line 3"""
    shell.fs.write_file("/tmp/changes.patch", patch_content)

    # Apply patch with input redirection
    result = shell.execute("patch /tmp/original.txt < /tmp/changes.patch")
    assert "patching file" in result

    # Verify the file was patched
    content = shell.fs.read_file("/tmp/original.txt")
    assert "Line 2 modified" in content


def test_input_redirection_nonexistent_file(shell):
    """Test input redirection with non-existent file"""
    result = shell.execute("wc < /tmp/nonexistent.txt")
    assert "No such file" in result


def test_input_redirection_with_uniq(shell):
    """Test input redirection with uniq"""
    # Create file with duplicates
    shell.fs.write_file(
        "/tmp/duplicates.txt", "apple\napple\nbanana\nbanana\nbanana\ncherry"
    )

    # Use uniq with input redirection
    result = shell.execute("uniq < /tmp/duplicates.txt")
    lines = result.strip().split("\n")
    assert lines == ["apple", "banana", "cherry"]


def test_input_redirection_with_cat(shell):
    """Test input redirection with cat (which normally doesn't need it)"""
    # Create file
    shell.fs.write_file("/tmp/cat_input.txt", "Content from file")

    # Cat with input redirection (redundant but should work)
    result = shell.execute("cat < /tmp/cat_input.txt")
    assert result == "Content from file"


def test_multiple_redirections(shell):
    """Test complex command with input and output redirection"""
    # Create input file
    shell.fs.write_file("/tmp/numbers.txt", "5\n2\n8\n1\n9\n3")

    # Sort numbers and save top 3
    shell.execute("sort -n < /tmp/numbers.txt > /tmp/temp.txt")
    shell.execute("head -n 3 < /tmp/temp.txt > /tmp/top3.txt")

    content = shell.fs.read_file("/tmp/top3.txt")
    assert content == "1\n2\n3"


def test_input_redirection_preserves_stdin(shell):
    """Test that stdin is properly set and cleared"""
    # Create two files
    shell.fs.write_file("/tmp/file1.txt", "Content 1")
    shell.fs.write_file("/tmp/file2.txt", "Content 2")

    # Use input redirection twice
    result1 = shell.execute("cat < /tmp/file1.txt")
    result2 = shell.execute("cat < /tmp/file2.txt")

    assert result1 == "Content 1"
    assert result2 == "Content 2"


def test_input_redirection_with_quoted_filename(shell):
    """Test input redirection with quoted filename containing spaces"""
    # Create file with spaces in name
    shell.fs.write_file("/tmp/file with spaces.txt", "Test content")

    # Use input redirection with quoted filename
    result = shell.execute('cat < "/tmp/file with spaces.txt"')
    assert result == "Test content"
