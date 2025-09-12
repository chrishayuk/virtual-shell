"""
tests/chuk_virtual_shell/commands/filesystem/test_echo_command.py
"""

import pytest
from chuk_virtual_shell.commands.filesystem.echo import EchoCommand
from tests.dummy_shell import DummyShell


# Fixture to create an EchoCommand with a dummy shell as the shell_context
@pytest.fixture
def echo_command():
    # Setup a dummy file system with an existing file to test append redirection.
    files = {
        "existing.txt": "Existing content. ",
    }
    dummy_shell = DummyShell(files)
    # Create EchoCommand with the required shell_context
    command = EchoCommand(shell_context=dummy_shell)
    return command


# Test that echo with no arguments returns an empty string.
def test_echo_no_arguments(echo_command):
    output = echo_command.execute([])
    assert output == ""


# Test that echo simply returns the concatenated arguments when no redirection is provided.
def test_echo_simple(echo_command):
    output = echo_command.execute(["Hello", "World"])
    assert output == "Hello World"


# Test echo with redirection overwrite using ">"
def test_echo_redirection_overwrite(echo_command):
    output = echo_command.execute(["Hello", "World", ">", "file1.txt"])
    # Command should return an empty string as the redirection output is not printed.
    assert output == ""
    # Check that the file content has been overwritten.
    shell = echo_command.shell
    assert shell.fs.read_file("file1.txt") == "Hello World"


# Test echo with redirection append using ">>"
def test_echo_redirection_append(echo_command):
    # Append text to an existing file.
    output = echo_command.execute(["Appended", "text", ">>", "existing.txt"])
    assert output == ""
    shell = echo_command.shell
    # The file should now have the original content plus the appended text.
    assert shell.fs.read_file("existing.txt") == "Existing content. Appended text"


# Test echo redirection error when write_file fails.
def test_echo_redirection_write_error(echo_command):
    # Override the write_file method to simulate a write failure.
    def fail_write_file(path, content):
        return False

    echo_command.shell.fs.write_file = fail_write_file
    output = echo_command.execute(["Error", ">", "fail.txt"])
    # Expect an error message indicating the file could not be written.
    assert output == "echo: cannot write to 'fail.txt'"
