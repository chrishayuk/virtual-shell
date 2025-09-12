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
    assert output == "rm: cannot remove 'nonexistent.txt'"
