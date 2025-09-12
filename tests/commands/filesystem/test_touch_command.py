"""
tests/chuk_virtual_shell/commands/filesystem/test_touch_command.py
"""

import pytest
from chuk_virtual_shell.commands.filesystem.touch import TouchCommand
from tests.dummy_shell import DummyShell


# Fixture to create a TouchCommand with a dummy shell as the shell_context
@pytest.fixture
def touch_command():
    # Setup a dummy file system with no initial files.
    files = {}
    dummy_shell = DummyShell(files)
    # Create TouchCommand with the required shell_context
    command = TouchCommand(shell_context=dummy_shell)
    return command


# Test for missing operand (no files provided)
def test_touch_missing_operand(touch_command):
    output = touch_command.execute([])
    assert output == "touch: missing operand"


# Test for successful creation of an empty file
def test_touch_create_file_success(touch_command):
    output = touch_command.execute(["newfile.txt"])
    # Command should return an empty string on success.
    assert output == ""
    # Verify that newfile.txt exists in the dummy file system and is empty.
    shell = touch_command.shell
    assert "newfile.txt" in shell.fs.files
    assert shell.fs.files["newfile.txt"] == ""


# Test for failure when touch returns False (simulate failure)
def test_touch_failure(touch_command):
    # Override the touch method to simulate a failure.
    def fail_touch(path):
        return False

    touch_command.shell.fs.touch = fail_touch
    output = touch_command.execute(["failfile.txt"])
    # Expect an error message indicating the file could not be touched.
    assert output == "touch: cannot touch 'failfile.txt'"
