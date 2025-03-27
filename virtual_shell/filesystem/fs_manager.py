"""
virtual_shell/filesystem/fs_manager.py - Virtual filesystem manager with provider support
"""
import posixpath
from typing import Dict, List, Optional, Any

from virtual_shell.filesystem.node_info import FSNodeInfo
from virtual_shell.filesystem.path_resolver import PathResolver
from virtual_shell.filesystem.search_utils import SearchUtils
from virtual_shell.filesystem.file_operations import FileOperations
from virtual_shell.filesystem.provider_manager import ProviderManager


class VirtualFileSystem:
    """
    Modular virtual filesystem manager with pluggable storage providers
    """
    
    def __init__(self, provider_name: Any = "memory", security_profile: str = None, **provider_args):
        """
        Initialize the virtual filesystem with the specified provider

        Args:
            provider_name: Either the name of the storage provider (str) or an already-created provider instance.
            security_profile: Optional security profile to apply ("default", "strict", "readonly", etc.)
            **provider_args: Arguments to pass to the provider constructor
        """
        # Extract security settings from provider_args if provided
        security_args = {}
        for key in list(provider_args.keys()):
            if key.startswith('security_'):
                security_args[key[9:]] = provider_args.pop(key)
        
        # If provider_name is a string, look it up; otherwise, use the provided instance
        if isinstance(provider_name, str):
            self.provider = ProviderManager.create_provider(provider_name, **provider_args)
        else:
            self.provider = provider_name

        # Initialize current directory
        self.current_directory_path = "/"
        
        # Initialize basic filesystem structure
        ProviderManager.initialize_basic_structure(self.provider)
        
        # Apply security wrapper if profile specified
        if security_profile:
            from virtual_shell.filesystem.security_config import create_secure_provider
            self.provider = create_secure_provider(self.provider, security_profile, **security_args)
            
            # Make sure current_directory_path is accessible to the wrapper
            if hasattr(self.provider, 'current_directory_path'):
                self.provider.current_directory_path = self.current_directory_path

    
    def change_provider(self, provider_name: str, **provider_args) -> bool:
        """
        Change the storage provider
        
        Args:
            provider_name: Name of the new provider
            **provider_args: Arguments for the new provider
            
        Returns:
            True if provider was changed successfully, False otherwise
        """
        new_provider = ProviderManager.change_provider(
            self.provider, 
            provider_name, 
            **provider_args
        )
        
        if not new_provider:
            return False
        
        # Update provider and reinitialize
        self.provider = new_provider
        ProviderManager.initialize_basic_structure(self.provider)
        
        # Reset current directory
        self.current_directory_path = "/"
        
        # success
        return True
    
    def apply_security(self, profile: str = "default", **settings) -> bool:
        """
        Apply security restrictions to the filesystem
        
        Args:
            profile: Security profile name ("default", "strict", "readonly", etc.)
            **settings: Override specific security settings
            
        Returns:
            True if security was applied successfully
        """
        try:
            from virtual_shell.filesystem.security_config import create_secure_provider
            self.provider = create_secure_provider(self.provider, profile, **settings)
            
            # Make sure current_directory_path is accessible to the wrapper
            if hasattr(self.provider, 'current_directory_path'):
                self.provider.current_directory_path = self.current_directory_path
                
            return True
        except Exception as e:
            print(f"Error applying security: {e}")
            return False
            
    def get_security_violations(self) -> List[Dict]:
        """
        Get the security violation log
        
        Returns:
            List of security violation events
        """
        if hasattr(self.provider, 'get_violation_log'):
            return self.provider.get_violation_log()
        return []
        
    def is_read_only(self) -> bool:
        """
        Check if the filesystem is in read-only mode
        
        Returns:
            True if filesystem is read-only
        """
        if hasattr(self.provider, 'read_only'):
            return self.provider.read_only
        return False
        
    def set_read_only(self, read_only: bool = True) -> None:
        """
        Set the read-only mode for the filesystem
        
        Args:
            read_only: Whether to set the filesystem to read-only
        """
        if hasattr(self.provider, 'read_only'):
            self.provider.read_only = read_only
    
    def resolve_path(self, path: str) -> str:
        """
        Resolve a path to its absolute form
        
        Args:
            path: Path to resolve
        
        Returns:
            Fully resolved absolute path
        """
        # resolve the path
        resolved = PathResolver.resolve_path(self.current_directory_path, path)
        # path resolved
        return resolved
    
    def mkdir(self, path: str) -> bool:
        """
        Create a directory at the specified path
        
        Args:
            path: Path of the directory to create
        
        Returns:
            True if directory was created, False otherwise
        """
        resolved_path = self.resolve_path(path)
        if self.provider.get_node_info(resolved_path):
            return False
        
        parent_path, dir_name = PathResolver.split_path(resolved_path)
        parent_info = self.provider.get_node_info(parent_path)
        if not parent_info or not parent_info.is_dir:
            return False
        
        node_info = FSNodeInfo(dir_name, True, parent_path)
        result = self.provider.create_node(node_info)
        return result
    
    def rmdir(self, path: str) -> bool:
        """
        Remove an empty directory
        
        Args:
            path: Path of the directory to remove
        
        Returns:
            True if directory was removed, False otherwise
        """
        resolved_path = self.resolve_path(path)
        # Check if path exists and is a directory
        node_info = self.provider.get_node_info(resolved_path)
        if not node_info or not node_info.is_dir:
            return False
        # Prevent deleting root
        if resolved_path == "/":
            return False
        # Ensure directory is empty
        contents = self.provider.list_directory(resolved_path)
        if contents:
            return False
        # Delete directory
        return self.provider.delete_node(resolved_path)
    
    def touch(self, path: str) -> bool:
        """
        Create an empty file at the specified path if it doesn't exist
        
        Args:
            path: Path of the file to create
        
        Returns:
            True if file was created or exists, False otherwise
        """
        resolved_path = self.resolve_path(path)
        node_info = self.provider.get_node_info(resolved_path)
        if node_info:
            return not node_info.is_dir
        
        parent_path, file_name = PathResolver.split_path(resolved_path)
        parent_info = self.provider.get_node_info(parent_path)
        if not parent_info or not parent_info.is_dir:
            return False
        
        node_info = FSNodeInfo(file_name, False, parent_path)
        if not self.provider.create_node(node_info):
            return False
        
        result = self.provider.write_file(resolved_path, "")
        return result
    
    def write_file(self, path: str, content: str) -> bool:
        """
        Write content to a file
        
        Args:
            path: Path of the file
            content: Content to write
        
        Returns:
            True if write was successful, False otherwise
        """
        resolved_path = self.resolve_path(path)
        node_info = self.provider.get_node_info(resolved_path)
        
        if node_info:
            if node_info.is_dir:
                return False
            result = self.provider.write_file(resolved_path, content)
            return result
        
        parent_path, file_name = PathResolver.split_path(resolved_path)
        parent_info = self.provider.get_node_info(parent_path)
        if not parent_info or not parent_info.is_dir:
            return False
        
        node_info = FSNodeInfo(file_name, False, parent_path)
        if not self.provider.create_node(node_info):
            return False
        
        result = self.provider.write_file(resolved_path, content)
        return result
    
    def read_file(self, path: str) -> Optional[str]:
        """
        Read content from a file
        
        Args:
            path: Path of the file to read
        
        Returns:
            File content or None if file doesn't exist or is a directory
        """
        resolved_path = self.resolve_path(path)
        node_info = self.provider.get_node_info(resolved_path)
        if not node_info or node_info.is_dir:
            return None
        content = self.provider.read_file(resolved_path)
        return content
    
    def ls(self, path: str = None) -> List[str]:
        """
        List contents of a directory
        
        Args:
            path: Path of the directory (uses current directory if None)
        
        Returns:
            List of directory contents
        """
        resolved_path = self.resolve_path(path) if path is not None else self.current_directory_path
        node_info = self.provider.get_node_info(resolved_path)
        if not node_info or not node_info.is_dir:
            return []
        contents = self.provider.list_directory(resolved_path)
        return contents
    
    def cd(self, path: str) -> bool:
        """
        Change current directory
        
        Args:
            path: Path to change to
        
        Returns:
            True if directory change was successful, False otherwise
        """
        resolved_path = self.resolve_path(path)
        node_info = self.provider.get_node_info(resolved_path)
        if not node_info or not node_info.is_dir:
            return False
        
        self.current_directory_path = resolved_path
        
        # Update current directory in security wrapper if present
        if hasattr(self.provider, 'current_directory_path'):
            self.provider.current_directory_path = resolved_path
            
        return True
    
    def pwd(self) -> str:
        """
        Get current working directory
        
        Returns:
            Current working directory path
        """
        return self.current_directory_path
    
    def rm(self, path: str) -> bool:
        """
        Remove a file or empty directory
        
        Args:
            path: Path to remove
        
        Returns:
            True if removal was successful, False otherwise
        """
        resolved_path = self.resolve_path(path)
        if resolved_path == "/":
            return False
        
        node_info = self.provider.get_node_info(resolved_path)
        if not node_info:
            return False
        
        result = self.provider.delete_node(resolved_path)
        return result
    
    def cp(self, source: str, destination: str) -> bool:
        """
        Copy a file or directory
        
        Args:
            source: Source path
            destination: Destination path
        
        Returns:
            True if copy was successful, False otherwise
        """
        result = FileOperations.copy(
            self.provider, 
            PathResolver, 
            source, 
            destination
        )
        return result
    
    def mv(self, source: str, destination: str) -> bool:
        """
        Move a file or directory
        
        Args:
            source: Source path
            destination: Destination path
        
        Returns:
            True if move was successful, False otherwise
        """
        result = FileOperations.move(
            self.provider, 
            PathResolver, 
            source, 
            destination
        )
        return result
    
    def find(self, path: str = "/", recursive: bool = True) -> List[str]:
        """
        Find files and directories
        
        Args:
            path: Starting path for search
            recursive: Whether to search subdirectories
        
        Returns:
            List of found paths
        """
        results = SearchUtils.find(
            self.provider, 
            path, 
            recursive
        )
        return results
    
    def search(self, path: str = "/", pattern: str = "*", recursive: bool = True) -> List[str]:
        """
        Search for files matching a pattern
        
        Args:
            path: Starting path for search
            pattern: Wildcard pattern to match
            recursive: Whether to search subdirectories
        
        Returns:
            List of matching file paths
        """
        results = SearchUtils.search(
            self.provider, 
            path, 
            pattern, 
            recursive
        )
        return results
    
    def get_fs_info(self) -> Dict[str, Any]:
        """
        Get comprehensive filesystem information
        
        Returns:
            Dictionary with filesystem metadata and stats
        """
        info = {
            "current_directory": self.current_directory_path,
            "provider_name": self.provider.__class__.__name__,
            "storage_stats": self.provider.get_storage_stats(),
            "total_files": len(self.find("/"))
        }
        
        # Add security info if applicable
        if hasattr(self.provider, 'read_only'):
            info["security"] = {
                "read_only": self.provider.read_only,
                "violations": len(self.get_security_violations()) if hasattr(self.provider, 'get_violation_log') else 0
            }
            
        return info
    
    def get_storage_stats(self) -> Dict:
        """
        Get storage statistics from the provider
        
        Returns:
            Dictionary of storage statistics
        """
        stats = self.provider.get_storage_stats()
        return stats
    
    def cleanup(self) -> Dict:
        """
        Perform cleanup operations on the provider
        
        Returns:
            Dictionary of cleanup results
        """
        result = self.provider.cleanup()
        return result
    
    def get_provider_name(self) -> str:
        """
        Get the name of the current provider
        
        Returns:
            Name of the current storage provider
        """
        provider_name = self.provider.__class__.__name__
        return provider_name
    
    def get_node_info(self, path: str) -> Optional[FSNodeInfo]:
        """
        Get information about a node at the specified path
        
        Args:
            path: Path to get node information for
        
        Returns:
            FSNodeInfo object or None if node doesn't exist
        """
        resolved_path = self.resolve_path(path)
        info = self.provider.get_node_info(resolved_path)
        return info
    
    def get_node(self, path: str) -> Optional[Dict]:
        """
        Get node information as a dictionary
        
        Args:
            path: Path to get node information for
        
        Returns:
            Dictionary representation of node info or None
        """
        node_info = self.get_node_info(path)
        if not node_info:
            return None
        node_dict = node_info.to_dict()
        return node_dict