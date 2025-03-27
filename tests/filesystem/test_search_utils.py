"""
tests/virtual_shell/filesystem/test_search_utils.py
Tests for SearchUtils utility class
"""
import posixpath
import pytest
from virtual_shell.filesystem.providers.memory import MemoryStorageProvider
from virtual_shell.filesystem.search_utils import SearchUtils
from virtual_shell.filesystem.node_info import FSNodeInfo


@pytest.fixture
def memory_provider():
    """Create a memory storage provider with test structure"""
    provider = MemoryStorageProvider()
    provider.initialize()
    
    # Create test directory structure
    provider.create_node(FSNodeInfo("test_search", True, "/"))
    
    # Create test files
    test_files = [
        "file1.txt",
        "file2.txt",
        "document.doc",
        "script.py",
        "nested/file3.txt",
        "nested/file4.log"
    ]
    
    for file_path in test_files:
        full_path = f"/test_search/{file_path}"
        # Create parent directories if they don't exist
        if '/' in file_path:
            parent_dir = f"/test_search/{'/'.join(file_path.split('/')[:-1])}"
            provider.create_node(FSNodeInfo(parent_dir.split('/')[-1], True, posixpath.dirname(parent_dir)))
        
        # Create the file
        provider.create_node(FSNodeInfo(file_path.split('/')[-1], False, posixpath.dirname(full_path)))
    
    return provider


def test_find_all_files(memory_provider):
    """Test finding all files in a directory"""
    results = SearchUtils.find(memory_provider, "/test_search")
    
    assert len(results) == 7  # 6 files + 1 nested directory
    assert set(results) == {
        "/test_search/file1.txt",
        "/test_search/file2.txt",
        "/test_search/document.doc",
        "/test_search/script.py",
        "/test_search/nested",
        "/test_search/nested/file3.txt",
        "/test_search/nested/file4.log"
    }


def test_find_non_recursive(memory_provider):
    """Test finding files without recursing into subdirectories"""
    results = SearchUtils.find(memory_provider, "/test_search", recursive=False)
    
    assert len(results) == 5  # 4 files + 1 nested directory
    assert set(results) == {
        "/test_search/file1.txt",
        "/test_search/file2.txt",
        "/test_search/document.doc",
        "/test_search/script.py",
        "/test_search/nested"
    }


def test_search_with_wildcard(memory_provider):
    """Test searching files with wildcard pattern"""
    # Find all text files
    txt_files = SearchUtils.search(memory_provider, "/test_search", "*.txt")
    assert len(txt_files) == 2  # Only top-level txt files
    assert set(txt_files) == {
        "/test_search/file1.txt",
        "/test_search/file2.txt"
    }
    
    # Find all text files recursively
    txt_files_recursive = SearchUtils.search(memory_provider, "/test_search", "*.txt", recursive=True)
    assert len(txt_files_recursive) == 3
    assert set(txt_files_recursive) == {
        "/test_search/file1.txt",
        "/test_search/file2.txt",
        "/test_search/nested/file3.txt"
    }
    
    # Find log files
    log_files = SearchUtils.search(memory_provider, "/test_search", "*.log", recursive=True)
    assert len(log_files) == 1
    assert log_files == ["/test_search/nested/file4.log"]


def test_search_in_subdirectory(memory_provider):
    """Test searching in a specific subdirectory"""
    nested_files = SearchUtils.search(memory_provider, "/test_search/nested", "*.txt")
    assert len(nested_files) == 1
    assert nested_files == ["/test_search/nested/file3.txt"]


def test_search_no_matches(memory_provider):
    """Test searching with a pattern that doesn't match any files"""
    no_matches = SearchUtils.search(memory_provider, "/test_search", "*.xml")
    assert len(no_matches) == 0