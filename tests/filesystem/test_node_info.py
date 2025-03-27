"""
tests/virtual_shell/filesystem/test_node_info.py
"""
import time
import uuid
import pytest
from virtual_shell.filesystem.node_info import FSNodeInfo

def test_get_path_no_parent():
    # When parent_path is empty and name is provided, path should be "/<name>"
    node = FSNodeInfo(name="file.txt", is_dir=False, parent_path="")
    assert node.get_path() == "/file.txt"

def test_get_path_root():
    # When name is empty, it is considered root
    node = FSNodeInfo(name="", is_dir=True, parent_path="")
    assert node.get_path() == "/"

def test_get_path_with_root_parent():
    # When parent_path is "/" the result should be "/<name>"
    node = FSNodeInfo(name="folder", is_dir=True, parent_path="/")
    assert node.get_path() == "/folder"

def test_get_path_nested():
    # When parent_path is non-root, the path should be "parent_path/name"
    node = FSNodeInfo(name="document.txt", is_dir=False, parent_path="/home/user")
    assert node.get_path() == "/home/user/document.txt"

def test_to_dict():
    # Create a node and convert to dictionary.
    node = FSNodeInfo(name="data", is_dir=True, parent_path="/var")
    info_dict = node.to_dict()
    
    # Check all keys exist
    expected_keys = {"id", "name", "is_dir", "parent_path", "full_path", "modified_at", "metadata"}
    assert expected_keys <= set(info_dict.keys())
    
    # Validate values are correctly mapped
    assert info_dict["name"] == "data"
    assert info_dict["is_dir"] is True
    assert info_dict["parent_path"] == "/var"
    assert info_dict["full_path"] == "/var/data"
    assert info_dict["metadata"] == {}
    # Check that modified_at is a non-empty string
    assert isinstance(info_dict["modified_at"], str) and info_dict["modified_at"]

def test_from_dict():
    # Create a node, convert it to a dict, then create a new node from that dict.
    original = FSNodeInfo(name="config.json", is_dir=False, parent_path="/etc", metadata={"size": 1024})
    data = original.to_dict()
    # Simulate a time delay to ensure the new node's modified_at isn't accidentally updated
    time.sleep(0.01)
    recreated = FSNodeInfo.from_dict(data)
    
    # Check that all attributes match
    assert recreated.id == original.id
    assert recreated.name == original.name
    assert recreated.is_dir == original.is_dir
    assert recreated.parent_path == original.parent_path
    assert recreated.get_path() == original.get_path()
    assert recreated.modified_at == original.modified_at
    assert recreated.metadata == original.metadata

def test_unique_id():
    # Ensure that multiple instances have unique IDs.
    node1 = FSNodeInfo(name="a", is_dir=False)
    node2 = FSNodeInfo(name="b", is_dir=False)
    assert node1.id != node2.id
    # Also check that the ID looks like a UUID (version 4 is random)
    uuid_obj = uuid.UUID(node1.id)
    assert uuid_obj.version in {1, 4}
