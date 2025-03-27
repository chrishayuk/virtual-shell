"""
virtual_shell/filesystem/fs_manager.py - Virtual filesystem manager with provider support
"""
import posixpath
from typing import Dict, List, Optional, Union

from virtual_shell.filesystem.node_info import FSNodeInfo
from virtual_shell.filesystem.provider_base import StorageProvider
from virtual_shell.filesystem.providers import get_provider


class VirtualFileSystem:
    """
    Manager for the virtual filesystem that provides methods for 
    file and directory manipulation using pluggable storage providers
    """
    
    def __init__(self, provider_name: str = "memory", **provider_args):
        """
        Initialize the virtual filesystem with the specified provider
        
        Args:
            provider_name: Name of the storage provider to use
            **provider_args: Arguments to pass to the provider constructor
            
        Raises:
            ValueError: If provider could not be found or initialized
        """
        # Get the provider instance
        self.provider = get_provider(provider_name, **provider_args)
        if not self.provider:
            raise ValueError(f"Provider '{provider_name}' not found")
            
        # Initialize the provider
        if not self.provider.initialize():
            raise ValueError(f"Failed to initialize provider '{provider_name}'")
            
        self.current_directory_path = "/"
        
        # Initialize basic structure
        self._init_basic_structure()
        
    def _init_basic_structure(self):
        """Initialize the basic filesystem structure"""
        # Check if root exists first
        root_info = self.provider.get_node_info("/")
        if not root_info:
            # Create root if it doesn't exist (shouldn't happen if provider.initialize() worked)
            root_info = FSNodeInfo("", True)
            self.provider.create_node(root_info)
        
        # Create basic directory structure
        self.mkdir("/bin")
        self.mkdir("/home")
        self.mkdir("/tmp")
        self.mkdir("/etc")
        
        # Add some example files
        self.write_file("/etc/motd", "Welcome to PyodideShell - A Virtual Filesystem with Provider Support!\n")
        self.write_file("/etc/passwd", "root:x:0:0:root:/root:/bin/bash\nuser:x:1000:1000:Default User:/home/user:/bin/bash\n")
    
    def change_provider(self, provider_name: str, **provider_args) -> bool:
        """
        Change the storage provider
        
        Args:
            provider_name: Name of the new provider
            **provider_args: Arguments for the new provider
            
        Returns:
            True if provider was changed successfully, False otherwise
        """
        new_provider = get_provider(provider_name, **provider_args)
        if not new_provider:
            return False
            
        # Initialize the new provider
        if not new_provider.initialize():
            return False
            
        self.provider = new_provider
        self._init_basic_structure()
        return True
    
    def get_provider_name(self) -> str:
        """Get the name of the current provider"""
        return self.provider.__class__.__name__
    
    def resolve_path(self, path: str) -> str:
        """Resolve a path to its absolute form"""
        if not path:
            return self.current_directory_path
            
        # Handle absolute vs relative paths
        if path.startswith('/'):
            resolved = path
        else:
            if self.current_directory_path == '/':
                resolved = '/' + path
            else:
                resolved = self.current_directory_path + '/' + path
                
        # Normalize path (handle .. and .)
        components = []
        for part in resolved.split('/'):
            if part == '' or part == '.':
                continue
            elif part == '..':
                if components:
                    components.pop()
            else:
                components.append(part)
                
        return '/' + '/'.join(components)
    
    def mkdir(self, path: str) -> bool:
        """Create a directory at the specified path"""
        if not path:
            return False
            
        if path.endswith('/'):
            path = path[:-1]
            
        # Handle root directory case
        if path == '/':
            return True  # Root already exists
            
        # Resolve path
        resolved_path = self.resolve_path(path)
        
        # Check if already exists
        if self.provider.get_node_info(resolved_path):
            return False
            
        # Get parent path
        parent_path = posixpath.dirname(resolved_path)
        dir_name = posixpath.basename(resolved_path)
        
        if not dir_name:
            return False
            
        # Check if parent exists and is a directory
        parent_info = self.provider.get_node_info(parent_path)
        if not parent_info or not parent_info.is_dir:
            return False
            
        # Create directory
        node_info = FSNodeInfo(dir_name, True, parent_path)
        return self.provider.create_node(node_info)
    
    def touch(self, path: str) -> bool:
        """Create an empty file at the specified path if it doesn't exist"""
        # Resolve path
        resolved_path = self.resolve_path(path)
        
        # Check if already exists
        node_info = self.provider.get_node_info(resolved_path)
        if node_info:
            if node_info.is_dir:
                return False
            return True  # File exists, just touch it (updating timestamp handled by provider)
                
        # Get parent path
        parent_path = posixpath.dirname(resolved_path)
        file_name = posixpath.basename(resolved_path)
        
        if not file_name:
            return False
            
        # Check if parent exists and is a directory
        parent_info = self.provider.get_node_info(parent_path)
        if not parent_info or not parent_info.is_dir:
            return False
            
        # Create file
        node_info = FSNodeInfo(file_name, False, parent_path)
        if not self.provider.create_node(node_info):
            return False
            
        # Write empty content
        return self.provider.write_file(resolved_path, "")
    
    def write_file(self, path: str, content: str) -> bool:
        """Write content to a file at the specified path"""
        # Resolve path
        resolved_path = self.resolve_path(path)
        
        # Check if path exists
        node_info = self.provider.get_node_info(resolved_path)
        
        if node_info:
            if node_info.is_dir:
                return False
                
            # Write to existing file
            return self.provider.write_file(resolved_path, content)
            
        # Create new file
        parent_path = posixpath.dirname(resolved_path)
        file_name = posixpath.basename(resolved_path)
        
        if not file_name:
            return False
            
        # Check if parent exists and is a directory
        parent_info = self.provider.get_node_info(parent_path)
        if not parent_info or not parent_info.is_dir:
            return False
            
        # Create file
        node_info = FSNodeInfo(file_name, False, parent_path)
        if not self.provider.create_node(node_info):
            return False
            
        # Write content
        return self.provider.write_file(resolved_path, content)
    
    def read_file(self, path: str) -> Optional[str]:
        """Read content from a file at the specified path"""
        # Resolve path
        resolved_path = self.resolve_path(path)
        
        # Check if path exists and is a file
        node_info = self.provider.get_node_info(resolved_path)
        if not node_info or node_info.is_dir:
            return None
            
        # Read content
        return self.provider.read_file(resolved_path)
    
    def rm(self, path: str) -> bool:
        """Remove a file or empty directory"""
        # Resolve path
        resolved_path = self.resolve_path(path)
        
        # Check if path exists
        node_info = self.provider.get_node_info(resolved_path)
        if not node_info:
            return False
            
        # Prevent deleting root
        if resolved_path == "/":
            return False
            
        # Delete node
        return self.provider.delete_node(resolved_path)
    
    def rmdir(self, path: str) -> bool:
        """Remove an empty directory"""
        # This is just an alias for rm since the provider already checks if directory is empty
        resolved_path = self.resolve_path(path)
        
        # Check if path exists and is a directory
        node_info = self.provider.get_node_info(resolved_path)
        if not node_info or not node_info.is_dir:
            return False
            
        # Delete directory
        return self.provider.delete_node(resolved_path)
    
    def ls(self, path: str = None) -> List[str]:
        """List contents of a directory"""
        if path is None:
            resolved_path = self.current_directory_path
        else:
            resolved_path = self.resolve_path(path)
            
        # Check if path exists and is a directory
        node_info = self.provider.get_node_info(resolved_path)
        if not node_info or not node_info.is_dir:
            return []
            
        # List contents
        return self.provider.list_directory(resolved_path)
    
    def cd(self, path: str) -> bool:
        """Change current directory"""
        # Resolve path
        resolved_path = self.resolve_path(path)
        
        # Check if path exists and is a directory
        node_info = self.provider.get_node_info(resolved_path)
        if not node_info or not node_info.is_dir:
            return False
            
        # Change directory
        self.current_directory_path = resolved_path
        return True
    
    def pwd(self) -> str:
        """Get current working directory path"""
        return self.current_directory_path
    
    def get_storage_stats(self) -> Dict:
        """Get storage statistics from the provider"""
        return self.provider.get_storage_stats()
    
    def cleanup(self) -> Dict:
        """Perform cleanup operations on the provider"""
        return self.provider.cleanup()
        
    def get_node_info(self, path: str) -> Optional[FSNodeInfo]:
        """Get information about a node at the specified path"""
        resolved_path = self.resolve_path(path)
        return self.provider.get_node_info(resolved_path)
        
    # Compatibility methods for old code that uses the node-based interface
    
    def get_node(self, path: str) -> Optional[Dict]:
        """
        Get node information as a dictionary
        
        This is a compatibility method for old code that expects a node object.
        It returns a dictionary representation of the node info.
        """
        node_info = self.get_node_info(path)
        if not node_info:
            return None
        return node_info.to_dict()