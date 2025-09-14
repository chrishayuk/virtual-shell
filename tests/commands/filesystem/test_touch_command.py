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


# Fixture with existing files
@pytest.fixture
def touch_command_with_files():
    files = {
        "/existing.txt": "Old content",
        "/dir1": {}
    }
    dummy_shell = DummyShell(files)
    command = TouchCommand(shell_context=dummy_shell)
    return command


# Test for missing operand (no files provided)
def test_touch_missing_operand(touch_command):
    output = touch_command.execute([])
    assert "missing" in output and "operand" in output


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
    # Override both touch and write_file methods to simulate a failure.
    def fail_touch(path):
        return False
    
    def fail_write(path, content):
        return False

    touch_command.shell.fs.touch = fail_touch
    touch_command.shell.fs.write_file = fail_write
    output = touch_command.execute(["failfile.txt"])
    # Expect an error message indicating the file could not be touched.
    assert "cannot touch" in output and "failfile.txt" in output


# Test -c flag (no create)
def test_touch_no_create_flag(touch_command):
    output = touch_command.execute(["-c", "nonexistent.txt"])
    # Should not create the file
    assert output == ""
    assert "nonexistent.txt" not in touch_command.shell.fs.files


# Test touching existing file
def test_touch_existing_file(touch_command_with_files):
    output = touch_command_with_files.execute(["/existing.txt"])
    # Should succeed without error
    assert output == ""
    # Content should remain unchanged
    assert touch_command_with_files.shell.fs.files["/existing.txt"] == "Old content"


# Test multiple files
def test_touch_multiple_files(touch_command):
    output = touch_command.execute(["file1.txt", "file2.txt", "file3.txt"])
    assert output == ""
    assert "file1.txt" in touch_command.shell.fs.files
    assert "file2.txt" in touch_command.shell.fs.files
    assert "file3.txt" in touch_command.shell.fs.files


# Test combined flags
def test_touch_combined_flags(touch_command_with_files):
    output = touch_command_with_files.execute(["-cm", "/existing.txt"])
    # -c and -m together: don't create new files, modify time of existing
    assert output == ""


# Test help flag
def test_touch_help(touch_command):
    output = touch_command.execute(["--help"])
    assert "Usage:" in output
    assert "-c" in output
    assert "-a" in output
    assert "-m" in output


# Test -t flag without argument
def test_touch_t_flag_missing_arg(touch_command):
    output = touch_command.execute(["-t"])
    assert "option requires an argument" in output


# Test -t flag with time argument
def test_touch_t_flag_with_time(touch_command):
    output = touch_command.execute(["-t", "202401011200", "file.txt"])
    # Should create the file (time handling is simulated in virtual fs)
    assert output == ""
    assert "file.txt" in touch_command.shell.fs.files
