"""
tests/virtual_shell/filesystem/providers/test_sqlite_storage_provider.py
"""
import os
import posixpath
import json
import time
import pytest
from virtual_shell.filesystem.providers.sqlite import SqliteStorageProvider
from virtual_shell.filesystem.node_info import FSNodeInfo

@pytest.fixture
def provider():
    prov = SqliteStorageProvider(db_path=":memory:")
    assert prov.initialize() is True
    return prov

def test_initialize(provider):
    # The root node ("/") should exist after initialization.
    root_info = provider.get_node_info("/")
    assert root_info is not None
    # Root node's name is expected to be empty.
    assert root_info.name == ""
    # Verify that the root node is marked as a directory.
    assert root_info.is_dir is True

def test_create_node_file(provider):
    # First, create a parent directory /home.
    home_info = FSNodeInfo(name="home", is_dir=True, parent_path="/")
    assert provider.create_node(home_info) is True
    # Create a file under /home.
    file_info = FSNodeInfo(name="test.txt", is_dir=False, parent_path="/home")
    result = provider.create_node(file_info)
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
    # Create a directory /docs and two files inside.
    docs_info = FSNodeInfo(name="docs", is_dir=True, parent_path="/")
    assert provider.create_node(docs_info) is True
    
    file1 = FSNodeInfo(name="a.txt", is_dir=False, parent_path="/docs")
    file2 = FSNodeInfo(name="b.txt", is_dir=False, parent_path="/docs")
    assert provider.create_node(file1) is True
    assert provider.create_node(file2) is True
    
    listing = provider.list_directory("/docs")
    # The listing should contain "a.txt" and "b.txt"
    assert set(listing) == {"a.txt", "b.txt"}

def test_write_and_read_file(provider):
    # Create a parent directory /logs.
    logs_info = FSNodeInfo(name="logs", is_dir=True, parent_path="/")
    assert provider.create_node(logs_info) is True
    # Create file /logs/log.txt.
    file_info = FSNodeInfo(name="log.txt", is_dir=False, parent_path="/logs")
    assert provider.create_node(file_info) is True
    
    content = "This is a test log."
    result = provider.write_file("/logs/log.txt", content)
    assert result is True
    
    # Read back the file content.
    read_content = provider.read_file("/logs/log.txt")
    assert read_content == content

def test_delete_node_file(provider):
    # Create directory /temp and a file in it.
    temp_info = FSNodeInfo(name="temp", is_dir=True, parent_path="/")
    assert provider.create_node(temp_info) is True
    file_info = FSNodeInfo(name="delete_me.txt", is_dir=False, parent_path="/temp")
    assert provider.create_node(file_info) is True
    # Verify the file exists.
    assert provider.get_node_info("/temp/delete_me.txt") is not None
    # Delete the file.
    result = provider.delete_node("/temp/delete_me.txt")
    assert result is True
    # File should no longer exist.
    assert provider.get_node_info("/temp/delete_me.txt") is None

def test_delete_node_directory_nonempty(provider):
    # Create directory /nonempty and add a file inside.
    dir_info = FSNodeInfo(name="nonempty", is_dir=True, parent_path="/")
    assert provider.create_node(dir_info) is True
    file_info = FSNodeInfo(name="child.txt", is_dir=False, parent_path="/nonempty")
    assert provider.create_node(file_info) is True
    # Attempt to delete the non-empty directory should fail.
    result = provider.delete_node("/nonempty")
    assert result is False

def test_get_storage_stats(provider):
    # Create a directory and file to contribute to storage stats.
    dir_info = FSNodeInfo(name="data", is_dir=True, parent_path="/")
    assert provider.create_node(dir_info) is True
    file_info = FSNodeInfo(name="file1.txt", is_dir=False, parent_path="/")
    assert provider.create_node(file_info) is True
    text = "Hello World"
    assert provider.write_file("/file1.txt", text) is True
    
    stats = provider.get_storage_stats()
    assert isinstance(stats, dict)
    # At least one file and one directory should be present.
    assert stats["file_count"] >= 1
    assert stats["directory_count"] >= 1
    # Total size should reflect the size of "Hello World".
    expected_size = len(text.encode('utf-8'))
    assert stats["total_size_bytes"] == expected_size

def test_cleanup(provider):
    # Create /tmp directory and add a temporary file.
    tmp_info = FSNodeInfo(name="tmp", is_dir=True, parent_path="/")
    assert provider.create_node(tmp_info) is True
    file_info = FSNodeInfo(name="junk.txt", is_dir=False, parent_path="/tmp")
    assert provider.create_node(file_info) is True
    content = "temporary data"
    assert provider.write_file("/tmp/junk.txt", content) is True
    
    # Get storage size before cleanup.
    stats_before = provider.get_storage_stats()
    size_before = stats_before["total_size_bytes"]
    
    # Run cleanup (which should remove files in /tmp).
    result = provider.cleanup()
    assert "files_removed" in result
    assert result["files_removed"] >= 1
    assert result["bytes_freed"] > 0
    
    # Verify that the temporary file no longer exists.
    assert provider.get_node_info("/tmp/junk.txt") is None
