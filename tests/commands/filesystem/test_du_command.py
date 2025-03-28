# tests/chuk_virtual_shell/commands/filesystem/test_du_command.py
import os
import pytest
from chuk_virtual_shell.commands.filesystem.du import DuCommand
from tests.dummy_shell import DummyShell

@pytest.fixture
def dummy_fs_structure():
    """
    Create a dummy filesystem structure:
    
    /              : Contains "file1.txt" and a subdirectory "dir1"
    file1.txt      : A file with 1024 bytes (simulated by a string of 1024 characters)
    dir1           : A directory containing "file2.txt"
    dir1/file2.txt : A file with 2048 bytes (simulated)
    """
    return {
        "/": {
            "file1.txt": "a" * 1024,
            "dir1": {}
        },
        "dir1": {
            "file2.txt": "b" * 2048
        },
        "file1.txt": "a" * 1024,
        "dir1/file2.txt": "b" * 2048
    }

@pytest.fixture
def du_command(dummy_fs_structure):
    """
    Create a DuCommand with a dummy shell using the dummy filesystem.
    Set the current directory to "/" and environment PWD to "/".
    """
    dummy_shell = DummyShell(dummy_fs_structure)
    dummy_shell.fs.current_directory = "/"
    dummy_shell.environ = {"PWD": "/"}
    return DuCommand(shell_context=dummy_shell)

def test_du_no_options(du_command):
    """
    Test du with no options on the current directory ("/").
    The total size should be the sum of file sizes: 1024 (file1.txt) + 2048 (file2.txt) = 3072 bytes.
    Without human-readable flag, du returns size in KB blocks (3072//1024 = 3).
    """
    output = du_command.execute([])
    # Expected output: "3\t." because default path is '.' which resolves to "/" with total size 3072.
    expected = "3\t."
    assert output.strip() == expected

def test_du_human_readable(du_command):
    """
    Test du with the -h flag to get human-readable output.
    For 3072 bytes, the expected human-readable output is "3.0K".
    """
    output = du_command.execute(["-h"])
    # Expected output: "3.0K\t." (using our _human_readable conversion in DuCommand)
    expected = "3.0K\t."
    assert output.strip() == expected

def test_du_summarize(du_command):
    """
    Test du with the -s (summarize) flag.
    In summarize mode, subdirectories are not recursively traversed.
    In our dummy FS, "/" contains "file1.txt" and "dir1".
    For "file1.txt", size is 1024.
    For "dir1", since it's a directory, we assume fs.get_size() returns 0.
    Total should be 1024 bytes. In non-human-readable mode, that is 1024//1024 = 1.
    """
    output = du_command.execute(["-s"])
    expected = "1\t."
    assert output.strip() == expected

def test_du_multiple_paths(du_command):
    """
    Test du with multiple paths.
    For example, run du on both "/" and "dir1".
    For "/" the total size is 3072 bytes => 3 (in KB).
    For "dir1", total size is 2048 bytes => 2048//1024 = 2.
    The output should contain both lines.
    """
    output = du_command.execute(["/", "dir1"])
    # The order of lines might vary, so we'll check for both expected substrings.
    expected_line_root = "3\t/"
    expected_line_dir1 = "2\tdir1"
    assert expected_line_root in output
    assert expected_line_dir1 in output

def test_du_non_existent(du_command):
    """
    Test du with a non-existent path.
    The output should report an error for that path.
    """
    output = du_command.execute(["nonexistent"])
    expected = "du: cannot access 'nonexistent': No such file or directory"
    assert expected in output
