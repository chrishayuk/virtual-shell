"""
tests/virtual_shell/filesystem/test_directory.py
"""
import pytest
from virtual_shell.filesystem.directory import Directory
from virtual_shell.filesystem.file import File

def test_directory_initialization():
    dir_node = Directory("mydir")
    assert dir_node.name == "mydir"
    assert dir_node.parent is None
    assert dir_node.children == {}
    # Check initial timestamps (using the fixed timestamp)
    assert dir_node.created_at == "2025-03-27T12:00:00Z"
    assert dir_node.modified_at == "2025-03-27T12:00:00Z"

def test_add_child():
    parent = Directory("parent")
    child = File("child.txt", content="data")
    parent.add_child(child)
    # Verify that the child's parent is set to the parent directory.
    assert child.parent == parent
    # Verify that the child is in the parent's children dictionary.
    assert "child.txt" in parent.children
    # Verify that modified_at has been updated (in this example, the same fixed timestamp).
    assert parent.modified_at == "2025-03-27T12:00:00Z"

def test_remove_child_success():
    parent = Directory("parent")
    child = File("child.txt", content="data")
    parent.add_child(child)
    removed = parent.remove_child("child.txt")
    # The removed node should be the same as the child we added.
    assert removed == child
    # After removal, the child should no longer be in the children dict.
    assert "child.txt" not in parent.children
    # Verify that modified_at has been updated.
    assert parent.modified_at == "2025-03-27T12:00:00Z"

def test_remove_child_failure():
    parent = Directory("parent")
    # Removing a non-existent child should return None.
    removed = parent.remove_child("nonexistent")
    assert removed is None

def test_get_child():
    parent = Directory("parent")
    child = File("child.txt", content="data")
    parent.add_child(child)
    retrieved = parent.get_child("child.txt")
    assert retrieved == child

def test_list_children():
    parent = Directory("parent")
    child1 = File("child1.txt", content="data1")
    child2 = File("child2.txt", content="data2")
    parent.add_child(child1)
    parent.add_child(child2)
    children = parent.list_children()
    assert isinstance(children, dict)
    # Check that the keys in the children dictionary match the names of the added files.
    assert set(children.keys()) == {"child1.txt", "child2.txt"}
