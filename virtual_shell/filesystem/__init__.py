"""
virtual_shell/filesystem/__init__.py - Virtual filesystem package initialization
"""

from virtual_shell.filesystem.node_base import FSNode
from virtual_shell.filesystem.directory import Directory
from virtual_shell.filesystem.file import File
from virtual_shell.filesystem.fs_manager import VirtualFileSystem

# Export main classes
__all__ = [
    'FSNode',
    'Directory',
    'File',
    'VirtualFileSystem'
]