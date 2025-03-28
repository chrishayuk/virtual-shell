# tests/chuk_virtual_shell/commands/filesystem/test_mv_command.py
import pytest
from chuk_virtual_shell.commands.filesystem.mv import MvCommand
from tests.dummy_shell import DummyShell
import os

@pytest.fixture
def mv_command():
    # Setup a dummy file system with a basic structure:
    # The root directory ("/") contains a file "file1" and a directory "dir".
    files = {
        "/": {"file1": "Hello World", "dir": {}},
        "file1": "Hello World"
    }
    dummy_shell = DummyShell(files)
    dummy_shell.fs.current_directory = "/"
    command = MvCommand(shell_context=dummy_shell)
    return command

def test_mv_single_file(mv_command):
    # Test moving (renaming) a single file.
    output = mv_command.execute(["file1", "file2"])
    assert output == ""
    # Verify that file2 exists with the original content.
    assert mv_command.shell.fs.read_file("file2") == "Hello World"
    # Verify that file1 no longer exists.
    assert mv_command.shell.fs.read_file("file1") is None

def test_mv_multiple_files(mv_command):
    # Add an extra file for testing moving multiple files.
    mv_command.shell.fs.write_file("file3", "Another file")
    # Move file1 and file3 into directory "dir".
    output = mv_command.execute(["file1", "file3", "dir"])
    assert output == ""
    # Verify that the files are now in "dir".
    file1_dest = os.path.join("dir", "file1")
    file3_dest = os.path.join("dir", "file3")
    assert mv_command.shell.fs.read_file(file1_dest) == "Hello World"
    assert mv_command.shell.fs.read_file(file3_dest) == "Another file"
    # Verify that the original files have been removed.
    assert mv_command.shell.fs.read_file("file1") is None
    assert mv_command.shell.fs.read_file("file3") is None

def test_mv_non_existent(mv_command):
    # Attempt to move a non-existent file.
    output = mv_command.execute(["nonexistent", "dest"])
    expected = "mv: nonexistent: No such file"
    assert output == expected
