"""
tests/virtual_shell/filesystem/providers/test_memory_storage_provider.py
"""
import os
import time
import posixpath
import pytest
from virtual_shell.filesystem.providers.memory import MemoryStorageProvider
from virtual_shell.filesystem.node_info import FSNodeInfo

@pytest.fixture
def provider():
    prov = MemoryStorageProvider()
    prov.initialize()
    return prov

def test_initialize(provider):
    # After initialization, root ("/") should exist.
    root = provider.get_node_info("/")
    assert root is not None
    assert root.name == ""  # Root node was created with an empty name.
    # Also, check that the root is marked as a directory.
    assert root.is_dir is True

def test_create_node_file(provider):
    # Create a file node under an existing directory.
    node_info = FSNodeInfo(name="test.txt", is_dir=False, parent_path="/home")
    # First, create the parent directory.
    parent_info = FSNodeInfo(name="home", is_dir=True, parent_path="/")
    provider.create_node(parent_info)
    result = provider.create_node(node_info)
    assert result is True
    # Verify that the node exists.
    created = provider.get_node_info("/home/test.txt")
    assert created is not None
    assert created.name == "test.txt"

def test_create_node_directory_failure(provider):
    # Attempt to create a node where parent does not exist.
    node_info = FSNodeInfo(name="orphan", is_dir=False, parent_path="/nonexistent")
    result = provider.create_node(node_info)
    assert result is False

def test_list_directory(provider):
    # Create a directory with children.
    dir_info = FSNodeInfo(name="docs", is_dir=True, parent_path="/")
    provider.create_node(dir_info)
    
    # Create two files in /docs.
    file1 = FSNodeInfo(name="a.txt", is_dir=False, parent_path="/docs")
    file2 = FSNodeInfo(name="b.txt", is_dir=False, parent_path="/docs")
    provider.create_node(file1)
    provider.create_node(file2)
    
    # List /docs directory.
    listing = provider.list_directory("/docs")
    # The listing should contain "a.txt" and "b.txt".
    assert set(listing) == {"a.txt", "b.txt"}

def test_write_and_read_file(provider):
    # Create parent directory for file.
    dir_info = FSNodeInfo(name="logs", is_dir=True, parent_path="/")
    provider.create_node(dir_info)
    
    # Create file node.
    file_info = FSNodeInfo(name="log.txt", is_dir=False, parent_path="/logs")
    provider.create_node(file_info)
    
    # Write content to the file.
    content = "This is a test log."
    result = provider.write_file("/logs/log.txt", content)
    assert result is True
    # Read back the content.
    read_content = provider.read_file("/logs/log.txt")
    assert read_content == content

def test_delete_node_file(provider):
    # Create a file and then delete it.
    dir_info = FSNodeInfo(name="temp", is_dir=True, parent_path="/")
    provider.create_node(dir_info)
    
    file_info = FSNodeInfo(name="delete_me.txt", is_dir=False, parent_path="/temp")
    provider.create_node(file_info)
    
    # Verify file exists.
    assert provider.get_node_info("/temp/delete_me.txt") is not None
    result = provider.delete_node("/temp/delete_me.txt")
    assert result is True
    # File should no longer exist.
    assert provider.get_node_info("/temp/delete_me.txt") is None

def test_delete_node_directory_nonempty(provider):
    # Create a directory with a child, then try to delete it.
    dir_info = FSNodeInfo(name="nonempty", is_dir=True, parent_path="/")
    provider.create_node(dir_info)
    
    file_info = FSNodeInfo(name="child.txt", is_dir=False, parent_path="/nonempty")
    provider.create_node(file_info)
    
    # Attempt to delete the non-empty directory should fail.
    result = provider.delete_node("/nonempty")
    assert result is False

def test_get_storage_stats(provider):
    # Create a few files and directories.
    provider.create_node(FSNodeInfo(name="data", is_dir=True, parent_path="/"))
    provider.create_node(FSNodeInfo(name="file1.txt", is_dir=False, parent_path="/"))
    provider.write_file("/file1.txt", "Hello World")
    
    stats = provider.get_storage_stats()
    # Check that stats include file and directory counts.
    assert "file_count" in stats
    assert "directory_count" in stats
    assert stats["file_count"] >= 1
    assert stats["directory_count"] >= 1
    assert "total_size_bytes" in stats
    # Total size should reflect the size of "Hello World"
    assert stats["total_size_bytes"] == len("Hello World".encode('utf-8'))

def test_cleanup(provider):
    # Create a temporary file in /tmp.
    tmp_dir_info = FSNodeInfo(name="tmp", is_dir=True, parent_path="/")
    provider.create_node(tmp_dir_info)
    file_info = FSNodeInfo(name="junk.txt", is_dir=False, parent_path="/tmp")
    provider.create_node(file_info)
    content = "temporary data"
    provider.write_file("/tmp/junk.txt", content)
    size_before = provider.get_storage_stats()["total_size_bytes"]
    
    # Run cleanup (which removes files in /tmp).
    result = provider.cleanup()
    # Ensure that some bytes were freed and one file was removed.
    assert result["files_removed"] >= 1
    assert result["bytes_freed"] > 0
    # Verify that the file no longer exists.
    assert provider.get_node_info("/tmp/junk.txt") is None
