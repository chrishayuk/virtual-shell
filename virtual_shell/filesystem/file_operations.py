"""
virtual_shell/filesystem/file_operations.py - Advanced file and directory operations
"""
import posixpath
from typing import Dict, Optional, Any

from virtual_shell.filesystem.node_info import FSNodeInfo


class FileOperations:
    """
    Advanced file and directory operation utilities
    """
    
    @staticmethod
    def copy(
        fs_provider, 
        path_resolver,
        source: str, 
        destination: str
    ) -> bool:
        """
        Copy a file or directory
        
        Args:
            fs_provider: Filesystem storage provider
            path_resolver: Path resolution utility
            source: Path of the file or directory to copy
            destination: Destination path
        
        Returns:
            True if copy was successful, False otherwise
        """
        # Resolve paths
        source_path = path_resolver.resolve_path(
            fs_provider.current_directory_path if hasattr(fs_provider, 'current_directory_path') else '/', 
            source
        )
        dest_path = path_resolver.resolve_path(
            fs_provider.current_directory_path if hasattr(fs_provider, 'current_directory_path') else '/', 
            destination
        )
        
        # Get source node info
        source_info = fs_provider.get_node_info(source_path)
        if not source_info:
            return False
        
        # Destination parent must exist
        dest_parent = posixpath.dirname(dest_path)
        dest_parent_info = fs_provider.get_node_info(dest_parent)
        if not dest_parent_info or not dest_parent_info.is_dir:
            return False
        
        # Copy file
        if not source_info.is_dir:
            # Read source content
            content = fs_provider.read_file(source_path)
            if content is None:
                return False
            
            # Create destination file node
            dest_name = posixpath.basename(dest_path)
            dest_node_info = FSNodeInfo(
                dest_name, 
                False, 
                posixpath.dirname(dest_path)
            )
            
            # Create the destination node first
            if not fs_provider.create_node(dest_node_info):
                return False
            
            # Write to destination
            return fs_provider.write_file(dest_path, content)
        
        # Copy directory (create directories recursively)
        if source_info.is_dir:
            # Create destination directory
            dest_name = posixpath.basename(dest_path)
            dest_dir_info = FSNodeInfo(
                dest_name, 
                True, 
                posixpath.dirname(dest_path)
            )
            if not fs_provider.create_node(dest_dir_info):
                return False
            
            # Copy contents recursively
            for item in fs_provider.list_directory(source_path):
                src_item = posixpath.join(source_path, item)
                dest_item = posixpath.join(dest_path, item)
                
                # Recursively copy each item
                FileOperations.copy(fs_provider, path_resolver, src_item, dest_item)
            
            return True
        
        return False
    
    @staticmethod
    def move(
        fs_provider, 
        path_resolver,
        source: str, 
        destination: str
    ) -> bool:
        """
        Move a file or directory
        
        Args:
            fs_provider: Filesystem storage provider
            path_resolver: Path resolution utility
            source: Path of the file or directory to move
            destination: Destination path
        
        Returns:
            True if move was successful, False otherwise
        """
        # Copy first
        if not FileOperations.copy(fs_provider, path_resolver, source, destination):
            return False
        
        # Then delete source
        return fs_provider.delete_node(
            path_resolver.resolve_path(
                fs_provider.current_directory_path if hasattr(fs_provider, 'current_directory_path') else '/', 
                source
            )
        )