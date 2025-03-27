"""
virtual_shell/filesystem/__init__.py - Virtual filesystem package initialization
"""

# Import core components
from virtual_shell.filesystem.node_info import FSNodeInfo
from virtual_shell.filesystem.provider_base import StorageProvider
from virtual_shell.filesystem.fs_manager import VirtualFileSystem

# Import provider registry
from virtual_shell.filesystem.providers import get_provider, list_providers, register_provider

# Import security components
from virtual_shell.filesystem.security_wrapper import SecurityWrapper
from virtual_shell.filesystem.security_config import (
    create_secure_provider, 
    create_custom_security_profile,
    get_available_profiles,
    get_profile_settings,
    SECURITY_PROFILES
)

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
    'register_provider',
    
    # Security components
    'SecurityWrapper',
    'create_secure_provider',
    'create_custom_security_profile',
    'get_available_profiles',
    'get_profile_settings',
    'SECURITY_PROFILES',
    
    # Legacy components
    'FSNode',
    'Directory',
    'File'
]