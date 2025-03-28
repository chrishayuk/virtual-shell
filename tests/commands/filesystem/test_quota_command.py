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
        "/home": {"testuser": {}, "groups": {"staff": {}}},
        "/home/testuser": {
            "file1.txt": "a" * 2048,
            "file2.txt": "b" * 1024,
        },
        "/home/groups": {"staff": {}},
        "/home/groups/staff": {
            "groupfile.txt": "c" * 1024
        },
        "/home/testuser/file1.txt": "a" * 2048,
        "/home/testuser/file2.txt": "b" * 1024,
        "/home/groups/staff/groupfile.txt": "c" * 1024
    }

# Fixture: Create a QuotaCommand with a dummy shell configured for a user.
@pytest.fixture
def quota_command(dummy_fs_structure):
    dummy_shell = DummyShell(dummy_fs_structure)
    dummy_shell.fs.current_directory = "/home/testuser"
    # Set environment variables; current_user is used when no target is provided.
    dummy_shell.environ = {"PWD": "/home/testuser", "HOME": "/home/testuser", "MAX_TOTAL_SIZE": "6000000"}
    dummy_shell.current_user = "testuser"
    
    # Create a get_user_home method for the shell
    dummy_shell.get_user_home = lambda user: f"/home/{user}" if user == "testuser" else None
    
    # Create a get_storage_stats method for the shell.fs
    # This is needed by the quota command to get quota information
    dummy_shell.fs.get_storage_stats = lambda: {
        'filesystem': '/dev/sda1', 
        'max_total_size': 5000000,
        'max_file_size': 1000000,
        'max_files': 500000,
        'total_size_bytes': 3072,
        'file_count': 2
    }
    
    return QuotaCommand(shell_context=dummy_shell)

def test_quota_default_user(quota_command):
    """
    Test that when no target is provided, the quota command defaults to the current user.
    Expected output should contain the header for user quotas and filesystem info.
    """
    output = quota_command.execute([])
    assert "Disk quotas for users:" in output
    assert "Filesystem" in output
    # Check that output has some filesystem name - now we're using what the storage_stats provides
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
    # For the staff group that exists, ensure it can be found in the filesystem
    # We don't need to add a get_group_directory method, just ensure the calculations work
    output = quota_command.execute(["-g", "staff"])
    assert "Disk quotas for groups:" in output
    
    # Now test for a group that doesn't exist
    monkeypatch.setattr(quota_command.shell, "group_exists", lambda target: False)
    output2 = quota_command.execute(["-g", "nonexistent_group"])
    assert "quota: no group quotas for nonexistent_group" in output2

def test_quota_human_readable(quota_command):
    """
    Test that when the -h flag is used, quota outputs sizes in a human-readable format.
    """
    output = quota_command.execute(["-h"])
    # Check for general headers
    assert "Disk quotas for users:" in output  
    assert "Filesystem" in output
    # Check that output has a filesystem name
    assert "/dev/sda1" in output
    # Look for a size formatted with a unit (e.g., 'K' or 'M')
    assert "K" in output or "M" in output