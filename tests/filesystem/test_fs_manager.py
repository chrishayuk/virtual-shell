"""
tests/virtual_shell/filesystem/test_fs_manager_provider.py
"""
import posixpath
import pytest
from virtual_shell.filesystem.fs_manager import VirtualFileSystem
from virtual_shell.filesystem.node_info import FSNodeInfo

# Fixture that creates a VirtualFileSystem using the memory provider.
@pytest.fixture
def vfs():
    # IMPORTANT: Ensure that VirtualFileSystem calls provider.initialize()
    # If not, update VirtualFileSystem.__init__ accordingly.
    fs = VirtualFileSystem(provider_name="memory")
    return fs

def test_resolve_path(vfs):
    # Test absolute path remains unchanged.
    assert vfs.resolve_path("/etc") == "/etc"
    vfs.current_directory_path = "/home/user"
    assert vfs.resolve_path("docs") == "/home/user/docs"
    vfs.current_directory_path = "/home/user"
    resolved = vfs.resolve_path("./../bin")
    assert resolved == "/home/bin"
    assert vfs.resolve_path("") == "/home/user"

def test_mkdir(vfs):
    result = vfs.mkdir("/projects")
    assert result is True
    result_dup = vfs.mkdir("/projects")
    assert result_dup is False
    node = vfs.get_node_info("/projects")
    assert node is not None and node.is_dir

def test_touch(vfs):
    result = vfs.touch("/home/test.txt")
    assert result is True
    result_dup = vfs.touch("/home/test.txt")
    assert result_dup is True
    node = vfs.get_node_info("/home/test.txt")
    assert node is not None and not node.is_dir

def test_write_and_read_file(vfs):
    text = "Hello Virtual FS!"
    result = vfs.write_file("/etc/welcome.txt", text)
    assert result is True
    content = vfs.read_file("/etc/welcome.txt")
    assert content == text

def test_rm_file(vfs):
    vfs.touch("/tmp/remove_me.txt")
    assert vfs.get_node_info("/tmp/remove_me.txt") is not None
    result = vfs.rm("/tmp/remove_me.txt")
    assert result is True
    assert vfs.get_node_info("/tmp/remove_me.txt") is None

def test_rmdir(vfs):
    result = vfs.mkdir("/tmp/emptydir")
    assert result is True
    rm_result = vfs.rmdir("/tmp/emptydir")
    assert rm_result is True
    rm_nonexistent = vfs.rmdir("/tmp/emptydir")
    assert rm_nonexistent is False

def test_ls(vfs):
    listing = vfs.ls("/")
    expected = {"bin", "home", "tmp", "etc"}
    # Ensure the expected basic structure is present.
    assert set(listing) >= expected

def test_cd_and_pwd(vfs):
    result = vfs.cd("/home")
    assert result is True
    assert vfs.pwd() == "/home"
    assert vfs.mkdir("/home/user") is True
    result2 = vfs.cd("user")
    assert result2 is True
    assert vfs.pwd() == "/home/user"
    vfs.touch("/home/user/file.txt")
    result_fail = vfs.cd("file.txt")
    assert result_fail is False

def test_get_storage_stats(vfs):
    stats = vfs.get_storage_stats()
    assert isinstance(stats, dict)
    assert stats["directory_count"] >= 4
    assert stats["file_count"] >= 0

def test_cleanup(vfs):
    assert vfs.touch("/tmp/tempfile.txt") is True
    text = "Temporary data"
    assert vfs.write_file("/tmp/tempfile.txt", text) is True
    stats_before = vfs.get_storage_stats()
    size_before = stats_before["total_size_bytes"]
    result = vfs.cleanup()
    assert result["files_removed"] >= 1
    assert result["bytes_freed"] > 0
    assert vfs.get_node_info("/tmp/tempfile.txt") is None

def test_get_node_info(vfs):
    node_info = vfs.get_node_info("/etc/motd")
    assert node_info is not None
    assert isinstance(node_info, FSNodeInfo)
