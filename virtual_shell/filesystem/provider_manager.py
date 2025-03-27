"""
virtual_shell/filesystem/provider_manager.py - Filesystem provider management
"""
import posixpath
from typing import Dict, Any, Optional

from virtual_shell.filesystem.providers import get_provider
from virtual_shell.filesystem.node_info import FSNodeInfo


class ProviderManager:
    """
    Manages filesystem providers and their lifecycle
    """
    
    @staticmethod
    def create_provider(
        provider_name: str = "memory", 
        **provider_args
    ):
        """
        Create and initialize a storage provider
        
        Args:
            provider_name: Name of the provider to create
            **provider_args: Arguments for provider initialization
        
        Returns:
            Initialized provider instance
        
        Raises:
            ValueError: If provider cannot be created or initialized
        """
        # Get the provider instance
        provider = get_provider(provider_name, **provider_args)
        if not provider:
            raise ValueError(f"Provider '{provider_name}' not found")
            
        # Initialize the provider
        if not provider.initialize():
            raise ValueError(f"Failed to initialize provider '{provider_name}'")
        
        return provider
    
    @staticmethod
    def change_provider(
        current_provider, 
        new_provider_name: str, 
        **provider_args
    ) -> Optional[Any]:
        """
        Change the current storage provider
        
        Args:
            current_provider: Current provider instance
            new_provider_name: Name of the new provider
            **provider_args: Arguments for new provider
        
        Returns:
            New provider instance or None if change fails
        """
        try:
            # Create new provider
            new_provider = ProviderManager.create_provider(
                new_provider_name, 
                **provider_args
            )
            
            return new_provider
        
        except Exception:
            return None
    
    @staticmethod
    def initialize_basic_structure(provider):
        """
        Initialize basic filesystem structure
        
        Args:
            provider: Storage provider to initialize
        """
        # Check if root exists first
        root_info = provider.get_node_info("/")
        if not root_info:
            # Create root if it doesn't exist
            root_info = FSNodeInfo("", True)
            provider.create_node(root_info)
        
        # Create basic directory structure
        basic_dirs = ["/bin", "/home", "/tmp", "/etc"]
        for directory in basic_dirs:
            provider.create_node(FSNodeInfo(
                directory.split('/')[-1], 
                True, 
                posixpath.dirname(directory)
            ))
        
        # Add some example files
        try:
            provider.create_node(FSNodeInfo("motd", False, "/etc"))
            provider.write_file("/etc/motd", 
                "Welcome to PyodideShell - A Virtual Filesystem with Provider Support!\n")
            
            provider.create_node(FSNodeInfo("passwd", False, "/etc"))
            provider.write_file("/etc/passwd", 
                "root:x:0:0:root:/root:/bin/bash\n"
                "user:x:1000:1000:Default User:/home/user:/bin/bash\n")
        except Exception:
            # Silently fail if file creation doesn't work
            pass