import os
import pytest
from chuk_virtual_shell.commands.filesystem.du import DuCommand
from tests.dummy_shell import DummyShell

@pytest.fixture
def dummy_fs_structure():
    """
    Create a dummy filesystem structure with absolute paths:
    
    "/" contains "file1.txt" and a subdirectory "dir1".
    "/file1.txt" is a file with 1024 bytes (simulated by a string of 1024 characters).
    "/dir1" is a directory containing "file2.txt".
    "/dir1/file2.txt" is a file with 2048 bytes (simulated).
    """
    return {
        "/": {
            "file1.txt": "a" * 1024,
            "dir1": {}
        },
        "/file1.txt": "a" * 1024,
        "/dir1": {
            "file2.txt": "b" * 2048
        },
        "/dir1/file2.txt": "b" * 2048
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
    
    # Add get_size method to the dummy shell for testing
    def get_directory_size(path):
        """Calculate the total size of a directory recursively"""
        total = 0
        # Add size of files directly in the directory
        for item, content in dummy_shell.fs.files.items():
            if isinstance(content, str) and item.startswith(path):
                if path == '/' or item.startswith(path + '/') or item == path:
                    if '/' not in item[len(path)+1:]:  # only direct children
                        total += len(content)
        
        return total
    
    # Make sure exists method returns the correct value
    dummy_shell.exists = lambda path: path in dummy_fs_structure
    
    return DuCommand(shell_context=dummy_shell)

def test_du_no_options(du_command):
    """
    Test du with no options on the current directory ("/").
    Expect a response showing sizes of current directory and subdirectories.
    """
    output = du_command.execute([])
    # Output format should include directory sizes
    assert output.strip().count('\t') >= 1  # At least one tab character
    # Output should include the current directory
    assert "/" in output or "." in output

def test_du_human_readable(du_command):
    """
    Test du with the -h flag to get human-readable output.
    """
    output = du_command.execute(["-h"])
    # Human readable output should include a unit like K, M, etc.
    assert any(unit in output for unit in ['B', 'K', 'M', 'G'])

def test_du_summarize(du_command):
    """
    Test du with the -s (summarize) flag.
    In summarize mode, only the total for each argument is shown.
    """
    output = du_command.execute(["-s"])
    # Should only have one line per argument
    assert len(output.strip().split('\n')) == 1
    assert '\t.' in output or '\t/' in output

def test_du_multiple_paths(du_command):
    """
    Test du with multiple paths.
    """
    output = du_command.execute(["/", "dir1"])
    # Output should contain both paths
    assert "/" in output
    # Should refer to dir1 (either as dir1 or /dir1)
    assert "dir1" in output or "/dir1" in output

def test_du_non_existent(du_command):
    """
    Test du with a non-existent path.
    The output should report an error for that path.
    """
    output = du_command.execute(["nonexistent"])
    # Should contain an error message for the non-existent path
    assert "no such file" in output.lower() or "cannot access" in output.lower()