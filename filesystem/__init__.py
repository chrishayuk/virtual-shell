"""
filesystem/__init__.py - Virtual filesystem package initialization
"""

from filesystem.node_base import FSNode
from filesystem.directory import Directory
from filesystem.file import File
from filesystem.fs_manager import VirtualFileSystem

# Export main classes
__all__ = [
    'FSNode',
    'Directory',
    'File',
    'VirtualFileSystem'
]