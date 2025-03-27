"""
tests/virtual_shell/filesystem/test_path_resolver.py
Tests for PathResolver utility class
"""
import pytest
from virtual_shell.filesystem.path_resolver import PathResolver


def test_resolve_path_absolute():
    """Test resolving absolute paths"""
    # Absolute path should remain unchanged
    assert PathResolver.resolve_path("/home/user", "/etc") == "/etc"
    assert PathResolver.resolve_path("/home/user", "/home/documents") == "/home/documents"


def test_resolve_path_relative():
    """Test resolving relative paths"""
    # Relative path should be joined with current directory
    assert PathResolver.resolve_path("/home/user", "documents") == "/home/user/documents"
    assert PathResolver.resolve_path("/", "home") == "/home"


def test_resolve_path_parent_directory():
    """Test resolving paths with parent directory reference"""
    assert PathResolver.resolve_path("/home/user", "./../bin") == "/home/bin"
    assert PathResolver.resolve_path("/home/user/documents", "..") == "/home/user"
    assert PathResolver.resolve_path("/home/user", "./../../etc") == "/etc"


def test_resolve_path_edge_cases():
    """Test edge cases in path resolution"""
    # Empty current directory
    assert PathResolver.resolve_path("", "documents") == "/documents"
    
    # Empty path
    assert PathResolver.resolve_path("/home/user", "") == "/home/user"
    
    # Root directory
    assert PathResolver.resolve_path("/", "home") == "/home"
    assert PathResolver.resolve_path("/home/user", "/") == "/"


def test_split_path():
    """Test path splitting"""
    # Basic path splitting
    parent, basename = PathResolver.split_path("/home/user/documents/file.txt")
    assert parent == "/home/user/documents"
    assert basename == "file.txt"
    
    # Root directory edge case
    parent, basename = PathResolver.split_path("/")
    assert parent == "/"
    assert basename == ""
    
    # Single level path
    parent, basename = PathResolver.split_path("/home")
    assert parent == "/"
    assert basename == "home"


def test_normalize_path():
    """Test path normalization"""
    # Remove trailing slashes
    assert PathResolver.normalize_path("/home/user/") == "/home/user"
    assert PathResolver.normalize_path("/") == "/"
    
    # Handle empty path
    assert PathResolver.normalize_path("") == "/"
    
    # Ensure no change to well-formed paths
    assert PathResolver.normalize_path("/home/user") == "/home/user"