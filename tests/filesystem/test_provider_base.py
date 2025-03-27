"""
tests/virtual_shell/filesystem/test_provider_base.py
"""
import pytest
from typing import Dict, List, Optional
from virtual_shell.filesystem.node_info import FSNodeInfo
from virtual_shell.filesystem.provider_base import StorageProvider

# DummyProvider implements StorageProvider for testing purposes.
class DummyProvider(StorageProvider):
    def initialize(self) -> bool:
        return True
        
    def create_node(self, node_info: FSNodeInfo) -> bool:
        self.last_created = node_info
        return True
        
    def delete_node(self, path: str) -> bool:
        self.deleted_path = path
        return True
        
    def get_node_info(self, path: str) -> Optional[FSNodeInfo]:
        # For testing, create a dummy FSNodeInfo based on the path.
        # Assume the name is the last component and parent is the rest.
        parts = path.rstrip('/').split('/')
        name = parts[-1] if parts[-1] else ""
        parent = "/".join(parts[:-1]) or ""
        return FSNodeInfo(name=name, is_dir=False, parent_path=parent)
        
    def list_directory(self, path: str) -> List[str]:
        return ["file1.txt", "file2.txt"]
        
    def write_file(self, path: str, content: str) -> bool:
        self.last_written = (path, content)
        return True
        
    def read_file(self, path: str) -> Optional[str]:
        return "dummy content"
        
    def get_storage_stats(self) -> Dict:
        return {"used": 1024, "free": 2048}
        
    def cleanup(self) -> Dict:
        return {"cleaned": True}

@pytest.fixture
def dummy_provider():
    return DummyProvider()

def test_initialize(dummy_provider):
    assert dummy_provider.initialize() is True

def test_create_node(dummy_provider):
    node_info = FSNodeInfo(name="test.txt", is_dir=False, parent_path="/home")
    result = dummy_provider.create_node(node_info)
    assert result is True
    # Verify that the provider stored the node info.
    assert dummy_provider.last_created == node_info

def test_delete_node(dummy_provider):
    path = "/home/test.txt"
    result = dummy_provider.delete_node(path)
    assert result is True
    # Verify that the deleted path is stored.
    assert dummy_provider.deleted_path == path

def test_get_node_info(dummy_provider):
    path = "/etc/config.json"
    node_info = dummy_provider.get_node_info(path)
    # Verify that node_info is an instance of FSNodeInfo and has the expected properties.
    assert isinstance(node_info, FSNodeInfo)
    expected_name = "config.json"
    expected_parent = "/etc"
    assert node_info.name == expected_name
    assert node_info.parent_path == expected_parent
    # Also, get_path() should return the correct full path.
    assert node_info.get_path() == f"/{expected_name}" if expected_parent == "" else f"{expected_parent}/{expected_name}"

def test_list_directory(dummy_provider):
    listing = dummy_provider.list_directory("/any/path")
    assert isinstance(listing, list)
    assert listing == ["file1.txt", "file2.txt"]

def test_write_file(dummy_provider):
    path = "/tmp/log.txt"
    content = "log entry"
    result = dummy_provider.write_file(path, content)
    assert result is True
    # Verify that the provider stored the write details.
    assert dummy_provider.last_written == (path, content)

def test_read_file(dummy_provider):
    path = "/tmp/log.txt"
    content = dummy_provider.read_file(path)
    assert content == "dummy content"

def test_get_storage_stats(dummy_provider):
    stats = dummy_provider.get_storage_stats()
    assert isinstance(stats, dict)
    assert "used" in stats and "free" in stats
    assert stats["used"] == 1024
    assert stats["free"] == 2048

def test_cleanup(dummy_provider):
    result = dummy_provider.cleanup()
    assert isinstance(result, dict)
    assert result.get("cleaned") is True
