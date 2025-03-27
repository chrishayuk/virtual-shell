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

def test_cp_and_mv(vfs):
    # Test copy file
    vfs.write_file("/tmp/source.txt", "Copy content")
    assert vfs.cp("/tmp/source.txt", "/tmp/destination.txt") is True
    assert vfs.read_file("/tmp/destination.txt") == "Copy content"

    # Test move file
    assert vfs.mv("/tmp/source.txt", "/tmp/moved.txt") is True
    assert vfs.read_file("/tmp/moved.txt") == "Copy content"
    assert vfs.get_node_info("/tmp/source.txt") is None

def test_find_and_search(vfs):
    # Prepare test files
    vfs.mkdir("/test_search")
    vfs.write_file("/test_search/file1.txt", "Content 1")
    vfs.write_file("/test_search/file2.txt", "Content 2")
    vfs.write_file("/test_search/file3.log", "Content 3")

    # Test find
    found_files = vfs.find("/test_search")
    assert len(found_files) == 3
    assert set(found_files) == {
        "/test_search/file1.txt", 
        "/test_search/file2.txt", 
        "/test_search/file3.log"
    }

    # Test search with pattern
    txt_files = vfs.search("/test_search", "*.txt")
    assert len(txt_files) == 2
    assert set(txt_files) == {
        "/test_search/file1.txt", 
        "/test_search/file2.txt"
    }

def test_get_fs_info(vfs):
    fs_info = vfs.get_fs_info()
    assert isinstance(fs_info, dict)
    assert "current_directory" in fs_info
    assert "provider_name" in fs_info
    assert "storage_stats" in fs_info
    assert "total_files" in fs_info

def test_change_provider(vfs):
    # Ensure we can change provider
    result = vfs.change_provider("memory")
    assert result is True

    # Verify the current directory is reset
    assert vfs.pwd() == "/"

    # Verify basic structure is maintained
    basic_dirs = {"bin", "home", "tmp", "etc"}
    assert set(vfs.ls("/")) >= basic_dirs