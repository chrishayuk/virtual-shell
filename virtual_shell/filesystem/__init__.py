"""
virtual_shell/filesystem/__init__.py - Virtual filesystem package initialization
"""

# Import core components
from virtual_shell.filesystem.node_info import FSNodeInfo
from virtual_shell.filesystem.provider_base import StorageProvider
from virtual_shell.filesystem.fs_manager import VirtualFileSystem

# Import provider registry
from virtual_shell.filesystem.providers import get_provider, list_providers

# Keep original classes for backward compatibility
from virtual_shell.filesystem.node_base import FSNode
from virtual_shell.filesystem.directory import Directory
from virtual_shell.filesystem.file import File

# Export main classes
__all__ = [
    # Core components
    'VirtualFileSystem',
    'FSNodeInfo',
    'StorageProvider',
    'get_provider',
    'list_providers',
    
    # Legacy components
    'FSNode',
    'Directory',
    'File'
]