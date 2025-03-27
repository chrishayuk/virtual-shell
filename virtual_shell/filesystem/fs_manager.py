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
    
    def __init__(self, provider_name: str = "memory", **provider_args):
        """
        Initialize the virtual filesystem with the specified provider
        
        Args:
            provider_name: Name of the storage provider to use
            **provider_args: Arguments to pass to the provider constructor
        """
        # Create and initialize provider
        self.provider = ProviderManager.create_provider(
            provider_name, 
            **provider_args
        )
        
        # Initialize current directory
        self.current_directory_path = "/"
        
        # Initialize basic filesystem structure
        ProviderManager.initialize_basic_structure(self.provider)
    
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
        
        return True
    
    def resolve_path(self, path: str) -> str:
        """
        Resolve a path to its absolute form
        
        Args:
            path: Path to resolve
        
        Returns:
            Fully resolved absolute path
        """
        return PathResolver.resolve_path(self.current_directory_path, path)
    
    def mkdir(self, path: str) -> bool:
        """
        Create a directory at the specified path
        
        Args:
            path: Path of the directory to create
        
        Returns:
            True if directory was created, False otherwise
        """
        # Normalize and resolve path
        resolved_path = self.resolve_path(path)
        
        # Check if already exists
        if self.provider.get_node_info(resolved_path):
            return False
        
        # Get parent path and directory name
        parent_path, dir_name = PathResolver.split_path(resolved_path)
        
        # Check if parent exists and is a directory
        parent_info = self.provider.get_node_info(parent_path)
        if not parent_info or not parent_info.is_dir:
            return False
        
        # Create directory
        node_info = FSNodeInfo(dir_name, True, parent_path)
        return self.provider.create_node(node_info)
    
    def touch(self, path: str) -> bool:
        """
        Create an empty file at the specified path if it doesn't exist
        
        Args:
            path: Path of the file to create
        
        Returns:
            True if file was created or exists, False otherwise
        """
        # Resolve path
        resolved_path = self.resolve_path(path)
        
        # Check if already exists
        node_info = self.provider.get_node_info(resolved_path)
        if node_info:
            return not node_info.is_dir
        
        # Get parent path and file name
        parent_path, file_name = PathResolver.split_path(resolved_path)
        
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
        """
        Write content to a file
        
        Args:
            path: Path of the file
            content: Content to write
        
        Returns:
            True if write was successful, False otherwise
        """
        # Resolve path
        resolved_path = self.resolve_path(path)
        
        # Check if path exists
        node_info = self.provider.get_node_info(resolved_path)
        
        if node_info:
            # Fail if it's a directory
            if node_info.is_dir:
                return False
            
            # Write to existing file
            return self.provider.write_file(resolved_path, content)
        
        # Create new file
        parent_path, file_name = PathResolver.split_path(resolved_path)
        
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
        """
        Read content from a file
        
        Args:
            path: Path of the file to read
        
        Returns:
            File content or None if file doesn't exist or is a directory
        """
        # Resolve path
        resolved_path = self.resolve_path(path)
        
        # Check if path exists and is a file
        node_info = self.provider.get_node_info(resolved_path)
        if not node_info or node_info.is_dir:
            return None
        
        # Read content
        return self.provider.read_file(resolved_path)
    
    def ls(self, path: str = None) -> List[str]:
        """
        List contents of a directory
        
        Args:
            path: Path of the directory (uses current directory if None)
        
        Returns:
            List of directory contents
        """
        # Resolve path
        resolved_path = self.resolve_path(path) if path is not None else self.current_directory_path
        
        # Check if path exists and is a directory
        node_info = self.provider.get_node_info(resolved_path)
        if not node_info or not node_info.is_dir:
            return []
        
        # List contents
        return self.provider.list_directory(resolved_path)
    
    def cd(self, path: str) -> bool:
        """
        Change current directory
        
        Args:
            path: Path to change to
        
        Returns:
            True if directory change was successful, False otherwise
        """
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
        # Resolve path
        resolved_path = self.resolve_path(path)
        
        # Prevent deleting root
        if resolved_path == "/":
            return False
        
        # Check if path exists
        node_info = self.provider.get_node_info(resolved_path)
        if not node_info:
            return False
        
        # Delete node
        return self.provider.delete_node(resolved_path)
    
    def cp(self, source: str, destination: str) -> bool:
        """
        Copy a file or directory
        
        Args:
            source: Source path
            destination: Destination path
        
        Returns:
            True if copy was successful, False otherwise
        """
        return FileOperations.copy(
            self.provider, 
            PathResolver, 
            source, 
            destination
        )
    
    def mv(self, source: str, destination: str) -> bool:
        """
        Move a file or directory
        
        Args:
            source: Source path
            destination: Destination path
        
        Returns:
            True if move was successful, False otherwise
        """
        return FileOperations.move(
            self.provider, 
            PathResolver, 
            source, 
            destination
        )
    
    """
    Additional methods for VirtualFileSystem in fs_manager.py
    """
    def rmdir(self, path: str) -> bool:
        """
        Remove an empty directory
        
        Args:
            path: Path of the directory to remove
        
        Returns:
            True if directory was removed, False otherwise
        """
        # Resolve path
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

    def cp(self, source: str, destination: str) -> bool:
        """
        Copy a file or directory
        
        Args:
            source: Source path
            destination: Destination path
        
        Returns:
            True if copy was successful, False otherwise
        """
        # Use the FileOperations copy method
        return FileOperations.copy(
            self.provider, 
            PathResolver, 
            source, 
            destination
        )
    
    def find(self, path: str = "/", recursive: bool = True) -> List[str]:
        """
        Find files and directories
        
        Args:
            path: Starting path for search
            recursive: Whether to search subdirectories
        
        Returns:
            List of found paths
        """
        return SearchUtils.find(
            self.provider, 
            path, 
            recursive
        )
    
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
        return SearchUtils.search(
            self.provider, 
            path, 
            pattern, 
            recursive
        )
    
    def get_fs_info(self) -> Dict[str, Any]:
        """
        Get comprehensive filesystem information
        
        Returns:
            Dictionary with filesystem metadata and stats
        """
        return {
            "current_directory": self.current_directory_path,
            "provider_name": self.provider.__class__.__name__,
            "storage_stats": self.provider.get_storage_stats(),
            "total_files": len(self.find("/"))
        }
    
    def get_storage_stats(self) -> Dict:
        """
        Get storage statistics from the provider
        
        Returns:
            Dictionary of storage statistics
        """
        return self.provider.get_storage_stats()
    
    def cleanup(self) -> Dict:
        """
        Perform cleanup operations on the provider
        
        Returns:
            Dictionary of cleanup results
        """
        return self.provider.cleanup()
    
    def get_provider_name(self) -> str:
        """
        Get the name of the current provider
        
        Returns:
            Name of the current storage provider
        """
        return self.provider.__class__.__name__
    
    def get_node_info(self, path: str) -> Optional[FSNodeInfo]:
        """
        Get information about a node at the specified path
        
        Args:
            path: Path to get node information for
        
        Returns:
            FSNodeInfo object or None if node doesn't exist
        """
        resolved_path = self.resolve_path(path)
        return self.provider.get_node_info(resolved_path)
    
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
        return node_info.to_dict()