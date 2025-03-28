# tests/chuk_virtual_shell/commands/navigation/test_ls_command.py
import pytest
from chuk_virtual_shell.commands.navigation.ls import LsCommand
from tests.dummy_shell import DummyShell

# Fixture to create an LsCommand with a dummy shell as the shell_context
@pytest.fixture
def ls_command():
    # Setup a dummy file system with a basic structure:
    # The root directory ("/") contains two files and one subdirectory "folder".
    # "folder" contains two files.
    files = {
        "/": {"a.txt": "content", "b.txt": "content", "folder": {}},
        "folder": {"c.txt": "content", "d.txt": "content"},
        "a.txt": "content"
    }
    dummy_shell = DummyShell(files)
    # Set the current directory to "/"
    dummy_shell.fs.current_directory = "/"
    # Create LsCommand with the required shell_context
    command = LsCommand(shell_context=dummy_shell)
    return command

# Test ls with no arguments (lists current directory)
def test_ls_no_argument(ls_command):
    output = ls_command.execute([])
    # Expect sorted keys from "/" directory: "a.txt", "b.txt", "folder"
    expected = "a.txt b.txt folder"
    assert output == expected

# Test ls with a directory argument (lists contents of the specified directory)
def test_ls_directory_argument(ls_command):
    output = ls_command.execute(["folder"])
    # Expect sorted keys from "folder": "c.txt", "d.txt"
    expected = "c.txt d.txt"
    assert output == expected

# Test ls with a file argument (returns the file itself)
def test_ls_file_argument(ls_command):
    output = ls_command.execute(["a.txt"])
    expected = "a.txt"
    assert output == expected

# Test ls with a non-existent path (returns empty string)
def test_ls_non_existent(ls_command):
    output = ls_command.execute(["nonexistent"])
    expected = ""
    assert output == expected
