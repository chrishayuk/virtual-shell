"""
tests/virtual_shell/filesystem/test_node_base.py
"""
import pytest
from virtual_shell.filesystem.node_base import FSNode

def test_root_node_get_path():
    # A node with no parent is considered root.
    # According to the implementation, get_path() always returns "/" for a root node.
    root = FSNode("root", parent=None)
    assert root.get_path() == "/"

def test_child_node_get_path():
    # Create a root node (its get_path() returns "/")
    root = FSNode("root", parent=None)
    # Create a child node with the root as its parent.
    # Since root.get_path() returns "/", the child's path should be "/child".
    child = FSNode("child", parent=root)
    assert child.get_path() == "/child"

def test_grandchild_node_get_path():
    # Create a chain: root -> child -> grandchild.
    # The root node's get_path() returns "/"
    # Therefore, child's get_path() returns "/child"
    # And grandchild's get_path() returns "/child/grandchild"
    root = FSNode("root", parent=None)
    child = FSNode("child", parent=root)
    grandchild = FSNode("grandchild", parent=child)
    assert grandchild.get_path() == "/child/grandchild"

def test_multiple_levels_get_path():
    # Test a deeper hierarchy.
    root = FSNode("root", parent=None)
    folder1 = FSNode("folder1", parent=root)
    folder2 = FSNode("folder2", parent=folder1)
    file_node = FSNode("file.txt", parent=folder2)
    # Expected path: "/folder1/folder2/file.txt"
    assert file_node.get_path() == "/folder1/folder2/file.txt"
