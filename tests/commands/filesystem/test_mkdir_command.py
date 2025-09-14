"""
tests/chuk_virtual_shell/commands/filesystem/test_mkdir_command.py
"""

import pytest
from chuk_virtual_shell.commands.filesystem.mkdir import MkdirCommand
from tests.dummy_shell import DummyShell


# Fixture to create a MkdirCommand with a dummy shell as the shell_context
@pytest.fixture
def mkdir_command():
    # Setup a dummy file system with no directories initially.
    files = {}
    dummy_shell = DummyShell(files)
    # Create MkdirCommand with the required shell_context
    command = MkdirCommand(shell_context=dummy_shell)
    return command


# Test for missing operand (no directories provided)
def test_mkdir_missing_operand(mkdir_command):
    output = mkdir_command.execute([])
    assert output == "mkdir: missing operand"


# Test for successful directory creation
def test_mkdir_create_directory_success(mkdir_command):
    output = mkdir_command.execute(["new_dir"])
    # Command should return an empty string on success.
    assert output == ""
    # Verify that the directory is created in the dummy file system.
    shell = mkdir_command.shell
    # DummyFileSystem stores absolute paths
    assert "/new_dir" in shell.fs.files
    # Optionally, check that the directory is represented as an empty dict.
    assert shell.fs.files["/new_dir"] == {}


# Test for failure when directory creation is not allowed (e.g. directory already exists)
def test_mkdir_create_directory_failure(mkdir_command):
    # Pre-create the directory to simulate an existing one.
    mkdir_command.shell.fs.mkdir("existing_dir")
    output = mkdir_command.execute(["existing_dir"])
    # Check that the error message contains the directory name
    assert "mkdir: cannot create directory" in output
    assert "existing_dir" in output
