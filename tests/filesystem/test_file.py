"""
tests/virtual_shell/filesystem/test_file.py
"""
import pytest
from virtual_shell.filesystem.file import File

def test_file_initialization():
    file_node = File("test.txt", content="Hello")
    assert file_node.name == "test.txt"
    assert file_node.content == "Hello"
    assert file_node.size == len("Hello")
    # Check that timestamps are set (using the example fixed timestamp)
    assert file_node.created_at == "2025-03-27T12:00:00Z"
    assert file_node.modified_at == "2025-03-27T12:00:00Z"

def test_file_write():
    file_node = File("test.txt", content="Initial")
    file_node.write("New Content")
    assert file_node.content == "New Content"
    assert file_node.size == len("New Content")
    # Verify modified_at is updated (fixed timestamp in this example)
    assert file_node.modified_at == "2025-03-27T12:00:00Z"

def test_file_append():
    file_node = File("test.txt", content="Hello")
    file_node.append(" World")
    assert file_node.content == "Hello World"
    assert file_node.size == len("Hello World")
    # Verify modified_at is updated (fixed timestamp in this example)
    assert file_node.modified_at == "2025-03-27T12:00:00Z"

def test_file_read():
    file_node = File("test.txt", content="Some content")
    assert file_node.read() == "Some content"
