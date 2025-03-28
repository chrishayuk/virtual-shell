# tests/chuk_virtual_shell/commands/navigation/test_ls_command.py
import pytest
import time
from chuk_virtual_shell.commands.navigation.ls import LsCommand
from tests.dummy_shell import DummyShell

@pytest.fixture
def ls_command():
    # Setup a dummy file system with a structured directory:
    # Root ("/") contains:
    #   - "a.txt", "b.txt": normal files
    #   - ".hidden": hidden file
    #   - "folder": subdirectory containing:
    #         "c.txt": normal file
    #         ".hidden_folder": a hidden subdirectory (could be empty)
    files = {
        "/": {"a.txt": "content", "b.txt": "content", ".hidden": "secret", "folder": {}},
        "folder": {"c.txt": "content", ".hidden_folder": {}},
        "a.txt": "content"
    }
    dummy_shell = DummyShell(files)
    dummy_shell.fs.current_directory = "/"
    dummy_shell.environ = {"PWD": "/"}
    # Ensure that dummy_shell.fs.get_node_info() returns an object with 'is_dir'
    # For our tests, we assume that directories are represented by dicts.
    # For example, DummyShell.fs.get_node_info("folder", base_path="/") should return an object with is_dir == True.
    return LsCommand(shell_context=dummy_shell)

def test_ls_no_flags(ls_command):
    """
    When no flags are provided, ls should list only non-hidden files in the current directory.
    Expected output (sorted): "a.txt b.txt folder"
    """
    output = ls_command.execute([])
    expected = "a.txt b.txt folder"
    assert output == expected

def test_ls_all_flag(ls_command):
    """
    With the -a flag, ls should include hidden files.
    Expected output (sorted): ".hidden a.txt b.txt folder"
    """
    output = ls_command.execute(["-a"])
    expected = ".hidden a.txt b.txt folder"
    assert output == expected

def test_ls_long_flag(ls_command):
    """
    With the -l flag, ls should return a long-format listing.
    We check that each output line starts with a permission string (either directory or file)
    and includes the filename.
    """
    output = ls_command.execute(["-l"])
    lines = output.split("\n")
    # Expected sorted order for current directory: "a.txt", "b.txt", "folder"
    # We'll check for a dummy permission string (e.g. "-rw-r--r--" for files and "drwxr-xr-x" for directories)
    for filename in ["a.txt", "b.txt", "folder"]:
        matching = [line for line in lines if filename in line]
        assert matching, f"Expected a line for {filename} in long listing format"
        # Check that the line starts with either a file or directory permission pattern.
        # (These are dummy values; adjust based on your _is_directory implementation.)
        assert matching[0].startswith("-rw") or matching[0].startswith("drwx"), (
            f"Line for {filename} does not have expected permission string: {matching[0]}"
        )

def test_ls_long_all_flags(ls_command):
    """
    With both -l and -a flags, ls should list all files (including hidden) in long format.
    We check that at least one line contains the hidden file entry.
    """
    output = ls_command.execute(["-la"])
    lines = output.split("\n")
    found_hidden = any(".hidden" in line for line in lines)
    assert found_hidden, "Expected hidden file '.hidden' to appear in long listing with -a flag"

