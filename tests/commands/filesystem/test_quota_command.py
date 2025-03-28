# tests/chuk_virtual_shell/commands/filesystem/test_quota_command.py
import os
import pytest
from chuk_virtual_shell.commands.filesystem.quota import QuotaCommand
from tests.dummy_shell import DummyShell

# Fixture: Create a dummy filesystem structure for quota testing.
@pytest.fixture
def dummy_fs_structure():
    """
    Simulate a filesystem with user directories.
    For example:
      /home/testuser contains two files:
          file1.txt (2048 bytes)
          file2.txt (1024 bytes)
    """
    return {
        "/": {"home": {}},
        "home": {"testuser": {}},
        "home/testuser": {
            "file1.txt": "a" * 2048,
            "file2.txt": "b" * 1024,
        },
        "file1.txt": "a" * 2048,
        "home/testuser/file1.txt": "a" * 2048,
        "home/testuser/file2.txt": "b" * 1024,
    }

# Fixture: Create a QuotaCommand with a dummy shell configured for a user.
@pytest.fixture
def quota_command(dummy_fs_structure):
    dummy_shell = DummyShell(dummy_fs_structure)
    dummy_shell.fs.current_directory = "/home/testuser"
    # Set environment variables; current_user is used when no target is provided.
    dummy_shell.environ = {"PWD": "/home/testuser", "MAX_TOTAL_SIZE": "6000000"}
    dummy_shell.current_user = "testuser"
    
    # Simulate user_exists: return True only for "testuser"
    dummy_shell.user_exists = lambda target: target == "testuser"
    # Simulate group_exists: return True only for "staff"
    dummy_shell.group_exists = lambda target: target == "staff"
    
    # For quota calculation, simulate a simple walk and get_size.
    def walk(path):
        # Very simple walk: if path is /home/testuser, yield one tuple.
        if path == "/home/testuser":
            yield ("/home/testuser", [], ["file1.txt", "file2.txt"])
        else:
            yield (path, [], [])
    dummy_shell.fs.walk = walk

    # Simulate get_size: return length of file content.
    dummy_shell.fs.get_size = lambda path: len(dummy_shell.fs.read_file(path) or "")
    # Simulate exists and is_dir based on dummy structure:
    dummy_shell.fs.exists = lambda path: path in ["/home/testuser", "/home/testuser/file1.txt", "/home/testuser/file2.txt"]
    dummy_shell.fs.is_dir = lambda path: path == "/home/testuser"
    
    return QuotaCommand(shell_context=dummy_shell)

def test_quota_default_user(quota_command):
    """
    Test that when no target is provided, the quota command defaults to the current user.
    Expected output should contain the header for user quotas and simulated quota info.
    """
    output = quota_command.execute([])
    assert "Disk quotas for users:" in output
    assert "Filesystem" in output
    # Check that output line for the user quota is present.
    # For testuser, simulated _get_quota_info should return values.
    assert "/dev/sda1" in output

def test_quota_nonexistent_user(quota_command, monkeypatch):
    """
    Test that if a target user does not exist, the quota command reports no quotas.
    """
    # Force user_exists to return False.
    monkeypatch.setattr(quota_command.shell, "user_exists", lambda target: False)
    output = quota_command.execute(["nonexistent"])
    assert "quota: no user quotas for nonexistent" in output

def test_quota_group_mode(quota_command, monkeypatch):
    """
    Test that when the -g flag is used, the quota command reports group quotas.
    For a non-existent group, an error message should be returned.
    """
    # By default, group_exists returns True only for "staff". Test with a valid group.
    output = quota_command.execute(["-g", "staff"])
    assert "Disk quotas for groups:" in output
    # Now test for a group that doesn't exist.
    monkeypatch.setattr(quota_command.shell, "group_exists", lambda target: False)
    output2 = quota_command.execute(["-g", "nonexistent_group"])
    assert "quota: no group quotas for nonexistent_group" in output2

def test_quota_human_readable(quota_command):
    """
    Test that when the -h flag is used, quota outputs sizes in a human-readable format.
    """
    output = quota_command.execute(["-h"])
    # Look for a size formatted with a unit (e.g., 'K' or 'M'); in our simulated case, sizes are in KB.
    # Since the simulation uses blocks calculated from file sizes in /home/testuser,
    # we expect that the output includes a human-readable size.
    # The exact string might vary; check for the unit.
    assert "K" in output or "M" in output
