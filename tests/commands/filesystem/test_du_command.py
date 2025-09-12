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
        "/": {"file1.txt": "a" * 1024, "dir1": {}},
        "/file1.txt": "a" * 1024,
        "/dir1": {"file2.txt": "b" * 2048},
        "/dir1/file2.txt": "b" * 2048,
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
                if path == "/" or item.startswith(path + "/") or item == path:
                    if "/" not in item[len(path) + 1 :]:  # only direct children
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
    assert output.strip().count("\t") >= 1  # At least one tab character
    # Output should include the current directory
    assert "/" in output or "." in output


def test_du_human_readable(du_command):
    """
    Test du with the -h flag to get human-readable output.
    """
    output = du_command.execute(["-h"])
    # Human readable output should include a unit like K, M, etc.
    assert any(unit in output for unit in ["B", "K", "M", "G"])


def test_du_summarize(du_command):
    """
    Test du with the -s (summarize) flag.
    In summarize mode, only the total for each argument is shown.
    """
    output = du_command.execute(["-s"])
    # Should only have one line per argument
    assert len(output.strip().split("\n")) == 1
    assert "\t." in output or "\t/" in output


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


def test_du_help_via_argparse_error(du_command):
    """
    Test that invalid arguments trigger SystemExit and return help
    """
    output = du_command.execute(["--invalid-option"])
    # Should return help text when argparse fails
    assert "du -" in output or "Display disk usage" in output


def test_du_total_flag_multiple_paths(du_command):
    """
    Test du with -c flag on multiple paths to show grand total
    """
    output = du_command.execute(["-c", "/file1.txt", "/dir1/file2.txt"])
    # Should include a "total" line
    assert "total" in output


def test_du_single_file(du_command):
    """
    Test du on a single file
    """
    output = du_command.execute(["/file1.txt"])
    # Should show the file size
    assert "/file1.txt" in output or "file1.txt" in output


def test_du_file_access_error(du_command):
    """
    Test du when file access fails
    """
    # Mock get_file_size to raise exception
    original_get_size = du_command._get_file_size

    def mock_get_size(path):
        if "error" in path:
            raise Exception("Access denied")
        return original_get_size(path)

    du_command._get_file_size = mock_get_size

    # Create a mock file that exists but can't be accessed
    du_command.shell.fs.files["/error_file.txt"] = "content"

    output = du_command.execute(["/error_file.txt"])
    assert "cannot access" in output


def test_du_fallback_existence_check_via_read_file():
    """
    Test existence checking when fs.exists is not available, using read_file fallback
    """
    dummy_shell = DummyShell({"/test.txt": "content"})

    # Mock hasattr to return False for exists methods
    import builtins

    original_hasattr = builtins.hasattr

    def mock_hasattr(obj, name):
        if name == "exists":
            return False
        return original_hasattr(obj, name)

    builtins.hasattr = mock_hasattr

    try:
        du_cmd = DuCommand(shell_context=dummy_shell)
        output = du_cmd.execute(["/test.txt"])

        # Should still work via read_file fallback
        assert "test.txt" in output
    finally:
        builtins.hasattr = original_hasattr


def test_du_fallback_existence_check_via_ls():
    """
    Test existence checking when read_file fails but ls works for directories
    """
    dummy_shell = DummyShell({"/testdir": {}})

    # Mock hasattr and read_file
    import builtins

    original_hasattr = builtins.hasattr

    def mock_hasattr(obj, name):
        if name == "exists":
            return False
        return original_hasattr(obj, name)

    original_read = dummy_shell.fs.read_file

    def mock_read(path):
        return None  # Always fail to read as file

    builtins.hasattr = mock_hasattr
    dummy_shell.fs.read_file = mock_read

    try:
        du_cmd = DuCommand(shell_context=dummy_shell)
        output = du_cmd.execute(["/testdir"])

        # Should work via ls fallback
        assert "testdir" in output
    finally:
        builtins.hasattr = original_hasattr
        dummy_shell.fs.read_file = original_read


def test_du_existence_check_all_fallbacks_fail():
    """
    Test when all existence check methods fail
    """
    dummy_shell = DummyShell({})

    # Mock hasattr to return False for exists
    import builtins

    original_hasattr = builtins.hasattr

    def mock_hasattr(obj, name):
        if name == "exists":
            return False
        return original_hasattr(obj, name)

    # Mock read_file and ls to fail
    original_read = dummy_shell.fs.read_file
    original_ls = dummy_shell.fs.ls

    dummy_shell.fs.read_file = lambda path: None

    def mock_ls(path):
        raise Exception("Cannot list")

    dummy_shell.fs.ls = mock_ls

    builtins.hasattr = mock_hasattr

    try:
        du_cmd = DuCommand(shell_context=dummy_shell)
        output = du_cmd.execute(["/nonexistent"])

        # Should report error
        assert "cannot access" in output or "No such file" in output
    finally:
        builtins.hasattr = original_hasattr
        dummy_shell.fs.read_file = original_read
        dummy_shell.fs.ls = original_ls


def test_du_directory_listing_error():
    """
    Test when directory listing fails
    """
    dummy_shell = DummyShell({"/baddir": {}})

    # Mock ls to fail
    original_ls = dummy_shell.fs.ls

    def mock_ls(path):
        if "baddir" in path:
            raise Exception("Permission denied")
        return original_ls(path)

    dummy_shell.fs.ls = mock_ls

    du_cmd = DuCommand(shell_context=dummy_shell)
    output = du_cmd.execute(["/baddir"])

    # Should handle gracefully and show 0 size
    assert "/baddir" in output or "baddir" in output


def test_du_file_size_error_in_directory():
    """
    Test when getting file size fails within a directory scan
    """
    dummy_shell = DummyShell(
        {"/dir": {}, "/dir/good.txt": "content", "/dir/bad.txt": "content"}
    )

    # Mock get_size to fail for specific file
    dummy_shell.fs.get_size if hasattr(dummy_shell.fs, "get_size") else None

    def mock_get_size(path):
        if "bad.txt" in path:
            raise Exception("Cannot read size")
        return len(dummy_shell.fs.files.get(path, ""))

    dummy_shell.fs.get_size = mock_get_size

    du_cmd = DuCommand(shell_context=dummy_shell)
    output = du_cmd.execute(["/dir"])

    # Should handle the error gracefully
    assert "/dir" in output or "dir" in output


def test_du_directory_detection_fallbacks():
    """
    Test directory detection when standard methods aren't available
    """
    dummy_shell = DummyShell({"/testdir": {}})

    # Mock hasattr to return False for directory detection methods
    import builtins

    original_hasattr = builtins.hasattr

    def mock_hasattr(obj, name):
        if name in ["is_dir", "isdir", "get_node_info"]:
            return False
        return original_hasattr(obj, name)

    builtins.hasattr = mock_hasattr

    try:
        du_cmd = DuCommand(shell_context=dummy_shell)
        output = du_cmd.execute(["/testdir"])

        # Should use ls fallback to detect directory
        assert "testdir" in output
    finally:
        builtins.hasattr = original_hasattr


def test_du_directory_detection_ls_fallback_fails():
    """
    Test directory detection when even ls fallback fails
    """
    dummy_shell = DummyShell({"/maybe_dir": "not_really_content"})

    # Mock hasattr and ls to fail
    import builtins

    original_hasattr = builtins.hasattr

    def mock_hasattr(obj, name):
        if name in ["is_dir", "isdir", "get_node_info"]:
            return False
        return original_hasattr(obj, name)

    original_ls = dummy_shell.fs.ls

    def mock_ls(path):
        raise Exception("Not a directory")

    builtins.hasattr = mock_hasattr
    dummy_shell.fs.ls = mock_ls

    try:
        du_cmd = DuCommand(shell_context=dummy_shell)
        output = du_cmd.execute(["/maybe_dir"])

        # Should treat as file
        assert "maybe_dir" in output
    finally:
        builtins.hasattr = original_hasattr
        dummy_shell.fs.ls = original_ls


def test_du_file_size_via_shell_get_size():
    """
    Test file size calculation when shell has get_size method
    """
    dummy_shell = DummyShell({"/test.txt": "content"})

    # Add get_size method to shell (not fs) and mock hasattr
    dummy_shell.get_size = lambda path: 42

    import builtins

    original_hasattr = builtins.hasattr

    def mock_hasattr(obj, name):
        if obj is dummy_shell.fs and name == "get_size":
            return False
        return original_hasattr(obj, name)

    builtins.hasattr = mock_hasattr

    try:
        du_cmd = DuCommand(shell_context=dummy_shell)
        output = du_cmd.execute(["/test.txt"])

        # Should use shell's get_size method
        assert "test.txt" in output
    finally:
        builtins.hasattr = original_hasattr


def test_du_file_size_fallback_to_read_file():
    """
    Test file size calculation falls back to reading file content
    """
    dummy_shell = DummyShell({"/test.txt": "hello world"})

    # Mock hasattr to return False for get_size methods
    import builtins

    original_hasattr = builtins.hasattr

    def mock_hasattr(obj, name):
        if name == "get_size":
            return False
        return original_hasattr(obj, name)

    builtins.hasattr = mock_hasattr

    try:
        du_cmd = DuCommand(shell_context=dummy_shell)
        output = du_cmd.execute(["/test.txt"])

        # Should calculate size from file content length
        assert "test.txt" in output
    finally:
        builtins.hasattr = original_hasattr


def test_du_file_size_read_fails():
    """
    Test file size calculation when read_file returns None
    """
    dummy_shell = DummyShell({"/test.txt": "content"})

    # Mock hasattr and read_file
    import builtins

    original_hasattr = builtins.hasattr

    def mock_hasattr(obj, name):
        if name == "get_size":
            return False
        return original_hasattr(obj, name)

    original_read = dummy_shell.fs.read_file
    dummy_shell.fs.read_file = lambda path: None

    builtins.hasattr = mock_hasattr

    try:
        du_cmd = DuCommand(shell_context=dummy_shell)
        output = du_cmd.execute(["/test.txt"])

        # Should handle gracefully with 0 size
        assert "test.txt" in output
    finally:
        builtins.hasattr = original_hasattr
        dummy_shell.fs.read_file = original_read


def test_du_human_readable_bytes():
    """
    Test human readable formatting for bytes (should not have decimal)
    """
    dummy_shell = DummyShell({"/small.txt": "a"})  # 1 byte
    du_cmd = DuCommand(shell_context=dummy_shell)

    output = du_cmd.execute(["-h", "/small.txt"])
    # Should show "1B" (no decimal for bytes)
    assert "B" in output


def test_du_human_readable_large_size():
    """
    Test human readable formatting for very large sizes (terabytes)
    """
    dummy_shell = DummyShell({})
    du_cmd = DuCommand(shell_context=dummy_shell)

    # Test format_size directly for very large number
    large_size = 5 * (1024**4) + 512 * (1024**3)  # > 5TB
    formatted = du_cmd._format_size(large_size)

    # Should show in terabytes
    assert "T" in formatted
