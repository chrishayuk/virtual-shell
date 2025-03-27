"""
tests/virtual_shell/filesystem/test_file_operations.py
Tests for FileOperations utility class
"""
import pytest
import posixpath
from virtual_shell.filesystem.file_operations import FileOperations
from virtual_shell.filesystem.providers.memory import MemoryStorageProvider
from virtual_shell.filesystem.path_resolver import PathResolver
from virtual_shell.filesystem.node_info import FSNodeInfo


@pytest.fixture
def memory_provider():
    """Create a memory storage provider for testing"""
    provider = MemoryStorageProvider()
    provider.initialize()
    
    # Create some basic structure
    provider.create_node(FSNodeInfo("tmp", True, "/"))
    provider.create_node(FSNodeInfo("source", True, "/tmp"))
    
    return provider


def test_copy_file(memory_provider):
    """Test copying a single file"""
    # Create source file
    memory_provider.create_node(FSNodeInfo("test.txt", False, "/tmp/source"))
    memory_provider.write_file("/tmp/source/test.txt", "Hello, World!")
    
    # Attempt to copy
    result = FileOperations.copy(
        memory_provider, 
        PathResolver, 
        "/tmp/source/test.txt", 
        "/tmp/destination.txt"
    )
    
    # Verify copy was successful
    assert result is True
    assert memory_provider.read_file("/tmp/destination.txt") == "Hello, World!"


def test_copy_directory(memory_provider):
    """Test copying a directory with multiple files"""
    # Create source directory with files
    memory_provider.create_node(FSNodeInfo("source_dir", True, "/tmp"))
    memory_provider.create_node(FSNodeInfo("file1.txt", False, "/tmp/source_dir"))
    memory_provider.create_node(FSNodeInfo("file2.txt", False, "/tmp/source_dir"))
    memory_provider.write_file("/tmp/source_dir/file1.txt", "Content 1")
    memory_provider.write_file("/tmp/source_dir/file2.txt", "Content 2")
    
    # Attempt to copy directory
    result = FileOperations.copy(
        memory_provider, 
        PathResolver, 
        "/tmp/source_dir", 
        "/tmp/destination_dir"
    )
    
    # Verify copy was successful
    assert result is True
    assert memory_provider.get_node_info("/tmp/destination_dir") is not None
    assert memory_provider.read_file("/tmp/destination_dir/file1.txt") == "Content 1"
    assert memory_provider.read_file("/tmp/destination_dir/file2.txt") == "Content 2"


def test_copy_nonexistent_source(memory_provider):
    """Test copying a non-existent source"""
    result = FileOperations.copy(
        memory_provider, 
        PathResolver, 
        "/tmp/nonexistent.txt", 
        "/tmp/destination.txt"
    )
    
    assert result is False


def test_copy_to_invalid_destination(memory_provider):
    """Test copying to an invalid destination"""
    # Create source file
    memory_provider.create_node(FSNodeInfo("test.txt", False, "/tmp"))
    memory_provider.write_file("/tmp/test.txt", "Hello, World!")
    
    # Attempt to copy to a non-directory destination
    result = FileOperations.copy(
        memory_provider, 
        PathResolver, 
        "/tmp/test.txt", 
        "/nonexistent/destination.txt"
    )
    
    assert result is False


def test_move_file(memory_provider):
    """Test moving a file"""
    # Create source file
    memory_provider.create_node(FSNodeInfo("test.txt", False, "/tmp"))
    memory_provider.write_file("/tmp/test.txt", "Move content")
    
    # Attempt to move
    result = FileOperations.move(
        memory_provider, 
        PathResolver, 
        "/tmp/test.txt", 
        "/tmp/destination.txt"
    )
    
    # Verify move was successful
    assert result is True
    assert memory_provider.read_file("/tmp/destination.txt") == "Move content"
    assert memory_provider.get_node_info("/tmp/test.txt") is None