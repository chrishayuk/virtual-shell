"""
tests/chuk_virtual_shell/commands/filesystem/test_rmdir_command.py
"""

import pytest
from chuk_virtual_shell.commands.filesystem.rmdir import RmdirCommand
from tests.dummy_shell import DummyShell


# Fixture to create an RmdirCommand with a dummy shell as the shell_context
@pytest.fixture
def rmdir_command():
    # Setup a dummy file system with some sample directories.
    # "empty_dir" is empty and can be removed.
    # "nonempty_dir" contains a file and should fail removal.
    files = {"empty_dir": {}, "nonempty_dir": {"file.txt": "Content"}}
    dummy_shell = DummyShell(files)
    # Create RmdirCommand with the required shell_context
    command = RmdirCommand(shell_context=dummy_shell)
    return command


# Test for missing operand (no directories provided)
def test_rmdir_missing_operand(rmdir_command):
    output = rmdir_command.execute([])
    assert output == "rmdir: missing operand"


# Test for successful removal of an empty directory
def test_rmdir_remove_empty_directory(rmdir_command):
    output = rmdir_command.execute(["empty_dir"])
    # Command should return an empty string on success.
    assert output == ""
    # Verify that the directory has been removed.
    shell = rmdir_command.shell
    assert "empty_dir" not in shell.fs.files


# Test for failure when attempting to remove a non-existent directory
def test_rmdir_nonexistent_directory(rmdir_command):
    output = rmdir_command.execute(["does_not_exist"])
    expected = "rmdir: cannot remove 'does_not_exist': Directory not empty or not found"
    assert output == expected


# Test for failure when attempting to remove a non-empty directory
def test_rmdir_non_empty_directory(rmdir_command):
    output = rmdir_command.execute(["nonempty_dir"])
    expected = "rmdir: cannot remove 'nonempty_dir': Directory not empty or not found"
    assert output == expected
