"""
tests/chuk_virtual_shell/commands/filesystem/test_rm_command.py
"""

import pytest
from chuk_virtual_shell.commands.filesystem.rm import RmCommand
from tests.dummy_shell import DummyShell


# Fixture to create an RmCommand with a dummy shell as the shell_context
@pytest.fixture
def rm_command():
    # Setup a dummy file system with some sample files.
    files = {"file1.txt": "Content", "file2.txt": "Another Content"}
    dummy_shell = DummyShell(files)
    # Create RmCommand with the required shell_context
    command = RmCommand(shell_context=dummy_shell)
    return command


# Fixture with directory structure
@pytest.fixture
def rm_command_with_dirs():
    files = {
        "/file1.txt": "Content",
        "/dir1": {},
        "/dir1/file2.txt": "Nested file",
        "/dir1/subdir": {},
        "/dir1/subdir/deep.txt": "Deep file",
        "/dir2": {},
        "/emptydir": {}
    }
    dummy_shell = DummyShell(files)
    command = RmCommand(shell_context=dummy_shell)
    return command


# Test for missing operand (no files provided)
def test_rm_missing_operand(rm_command):
    output = rm_command.execute([])
    assert output == "rm: missing operand"


# Test for successful removal of an existing file
def test_rm_remove_existing_file(rm_command):
    output = rm_command.execute(["file1.txt"])
    # Command should return an empty string on success.
    assert output == ""
    # Verify that file1.txt has been removed from the dummy file system.
    assert "file1.txt" not in rm_command.shell.fs.files


# Test for failure when trying to remove a non-existent file
def test_rm_remove_non_existent_file(rm_command):
    output = rm_command.execute(["nonexistent.txt"])
    # Expect an error message indicating the file cannot be removed.
    assert "cannot remove" in output and "nonexistent.txt" in output


# Test force flag with non-existent file
def test_rm_force_nonexistent(rm_command):
    output = rm_command.execute(["-f", "nonexistent.txt"])
    # With -f, should not report error for non-existent files
    assert output == ""


# Test removing directory without recursive flag
def test_rm_directory_without_recursive(rm_command_with_dirs):
    output = rm_command_with_dirs.execute(["/dir1"])
    # Should fail when trying to remove directory without -r
    assert "Is a directory" in output


# Test recursive removal
def test_rm_recursive(rm_command_with_dirs):
    output = rm_command_with_dirs.execute(["-r", "/dir1"])
    # Should succeed
    assert output == ""
    # Verify directory and contents are removed
    assert "/dir1" not in rm_command_with_dirs.shell.fs.files
    assert "/dir1/file2.txt" not in rm_command_with_dirs.shell.fs.files
    assert "/dir1/subdir/deep.txt" not in rm_command_with_dirs.shell.fs.files


# Test verbose flag
def test_rm_verbose(rm_command):
    output = rm_command.execute(["-v", "file1.txt"])
    # Should show what was removed
    assert "removed" in output
    assert "file1.txt" in output


# Test combined flags
def test_rm_combined_flags(rm_command_with_dirs):
    output = rm_command_with_dirs.execute(["-rf", "/dir1"])
    # Should succeed silently
    assert output == ""
    assert "/dir1" not in rm_command_with_dirs.shell.fs.files


# Test verbose recursive
def test_rm_verbose_recursive(rm_command_with_dirs):
    output = rm_command_with_dirs.execute(["-rv", "/dir1"])
    # Should show each file/dir removed
    assert "removed" in output
    # Should mention multiple items
    lines = output.strip().split('\n')
    assert len(lines) > 1  # Multiple items removed


# Test help flag
def test_rm_help(rm_command):
    output = rm_command.execute(["--help"])
    assert "Usage:" in output
    assert "-r" in output
    assert "-f" in output
