"""
tests/virtual_shell/filesystem/test_fs_manager.py
"""
import os
import pytest
from virtual_shell.filesystem.fs_manager import VirtualFileSystem
from virtual_shell.filesystem.directory import Directory
from virtual_shell.filesystem.file import File

def test_initialization():
    fs = VirtualFileSystem()
    # Check that basic directories exist
    for d in ["/bin", "/home", "/tmp", "/etc"]:
        node = fs.get_node(d)
        assert node is not None, f"Directory {d} should exist"
        assert isinstance(node, Directory)
    # Check that example files exist with expected content
    motd = fs.read_file("/etc/motd")
    assert "Welcome to PyodideShell" in motd
    passwd = fs.read_file("/etc/passwd")
    assert "root:x:" in passwd

def test_mkdir():
    fs = VirtualFileSystem()
    # Create a new directory
    result = fs.mkdir("/newdir")
    assert result is True
    newdir = fs.get_node("/newdir")
    assert isinstance(newdir, Directory)
    # Attempt to create the same directory again should fail
    result2 = fs.mkdir("/newdir")
    assert result2 is False
    # Creating a directory when the parent doesn't exist should fail
    result3 = fs.mkdir("/nonexistent/newdir")
    assert result3 is False

def test_touch():
    fs = VirtualFileSystem()
    # Create a new file using touch
    result = fs.touch("/home/test.txt")
    assert result is True
    file_node = fs.get_node("/home/test.txt")
    assert isinstance(file_node, File)
    assert file_node.read() == ""
    # Touching an existing file should update its modified timestamp
    old_modified = file_node.modified_at
    result2 = fs.touch("/home/test.txt")
    assert result2 is True
    # In our example, modified_at is always updated to the fixed timestamp.
    assert file_node.modified_at == "2025-03-27T12:00:00Z"

def test_write_and_read_file():
    fs = VirtualFileSystem()
    # Write a new file and read its content
    result = fs.write_file("/home/welcome.txt", "Hello World")
    assert result is True
    content = fs.read_file("/home/welcome.txt")
    assert content == "Hello World"
    # Overwrite file content
    result2 = fs.write_file("/home/welcome.txt", "New Content")
    assert result2 is True
    content2 = fs.read_file("/home/welcome.txt")
    assert content2 == "New Content"
    # Reading a non-existent file should return None
    assert fs.read_file("/home/nonexistent.txt") is None

def test_rm_file():
    fs = VirtualFileSystem()
    # Create a file then remove it
    fs.touch("/tmp/remove.txt")
    assert fs.get_node("/tmp/remove.txt") is not None
    result = fs.rm("/tmp/remove.txt")
    assert result is True
    assert fs.get_node("/tmp/remove.txt") is None

def test_rm_directory_nonempty():
    fs = VirtualFileSystem()
    # Create a directory and add a file so it becomes non-empty
    fs.mkdir("/tmp/testdir")
    fs.touch("/tmp/testdir/file.txt")
    # rm should fail on a non-empty directory
    result = fs.rm("/tmp/testdir")
    assert result is False

def test_rmdir():
    fs = VirtualFileSystem()
    # Create a new empty directory
    fs.mkdir("/tmp/emptydir")
    # Removing an empty directory using rmdir should succeed
    result = fs.rmdir("/tmp/emptydir")
    assert result is True
    # Trying to remove it again should fail
    result2 = fs.rmdir("/tmp/emptydir")
    assert result2 is False
    # Creating a directory with contents and then using rmdir should fail
    fs.mkdir("/tmp/dirwithfile")
    fs.touch("/tmp/dirwithfile/file.txt")
    result3 = fs.rmdir("/tmp/dirwithfile")
    assert result3 is False

def test_ls():
    fs = VirtualFileSystem()
    # List contents of root; expect to see basic directories.
    listing = fs.ls("/")
    expected = {"bin", "home", "tmp", "etc"}
    # The listing may include additional entries; check for expected ones.
    assert set(listing) >= expected
    # Listing a file should return an empty list.
    listing_file = fs.ls("/etc/motd")
    assert listing_file == []

def test_cd_and_pwd():
    fs = VirtualFileSystem()
    # Change directory to /home
    result = fs.cd("/home")
    assert result is True
    assert fs.pwd() == "/home"
    # Create a subdirectory and change to it using a relative path.
    fs.mkdir("/home/user")
    result2 = fs.cd("user")
    assert result2 is True
    assert fs.pwd() == "/home/user"
    # Attempting to cd into a file should fail.
    result3 = fs.cd("/etc/motd")
    assert result3 is False

def test_resolve_path():
    fs = VirtualFileSystem()
    # Create additional directories for testing
    fs.mkdir("/home/test")
    # Test resolving an absolute path
    node, remaining = fs.resolve_path("/home/test")
    assert isinstance(node, Directory)
    assert remaining is None
    # Test relative path resolution from /home
    fs.current_directory = fs.get_node("/home")
    node2, remaining2 = fs.resolve_path("test")
    assert isinstance(node2, Directory)
    assert remaining2 is None
    # Test resolving a path that doesn't fully exist
    node3, remaining3 = fs.resolve_path("/home/test/nonexistent")
    # node3 should be the /home/test directory, and remaining3 should be "nonexistent"
    assert node3.get_path() == "/home/test"
    assert remaining3 == "nonexistent"
