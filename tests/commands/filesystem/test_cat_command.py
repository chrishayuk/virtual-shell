"""
tests/chuk_virtual_shell/commands/filesystem/test_cat_command.py
"""

import pytest
from chuk_virtual_shell.commands.filesystem.cat import CatCommand
from tests.dummy_shell import DummyShell


# Fixture to create a CatCommand with a dummy shell as the shell_context
@pytest.fixture
def cat_command():
    # Setup a dummy file system with some sample files
    files = {
        "file1.txt": "Hello, ",
        "file2.txt": "world!",
    }
    dummy_shell = DummyShell(files)
    # Create CatCommand with the required shell_context
    command = CatCommand(shell_context=dummy_shell)
    return command


# Test for missing operand (no files provided)
def test_cat_missing_operand(cat_command):
    output = cat_command.execute([])
    assert output == "cat: missing operand"


# Test for non-existent file
def test_cat_file_not_found(cat_command):
    output = cat_command.execute(["nonexistent.txt"])
    assert output == "cat: nonexistent.txt: No such file"


# Test for a single existing file
def test_cat_single_file(cat_command):
    output = cat_command.execute(["file1.txt"])
    assert output == "Hello, "


# Test for multiple existing files (concatenation)
def test_cat_multiple_files(cat_command):
    output = cat_command.execute(["file1.txt", "file2.txt"])
    assert output == "Hello, world!"
