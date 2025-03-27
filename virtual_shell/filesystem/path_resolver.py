"""
virtual_shell/filesystem/path_resolver.py - Path resolution utilities
"""
import posixpath
from typing import List


class PathResolver:
    """
    Utility class for resolving and manipulating filesystem paths
    """
    
    @staticmethod
    def resolve_path(current_directory: str, path: str) -> str:
        """
        Resolve a path to its absolute form
        
        Args:
            current_directory: Current working directory
            path: Path to resolve
        
        Returns:
            Fully resolved absolute path
        """
        if not path:
            return current_directory
            
        # Handle absolute vs relative paths
        if path.startswith('/'):
            resolved = path
        else:
            if current_directory == '/':
                resolved = '/' + path
            else:
                resolved = current_directory + '/' + path
                
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
    
    @staticmethod
    def split_path(path: str) -> tuple:
        """
        Split a path into its parent directory and basename
        
        Args:
            path: Full path to split
        
        Returns:
            Tuple of (parent_path, basename)
        """
        parent_path = posixpath.dirname(path)
        basename = posixpath.basename(path)
        return parent_path, basename
    
    @staticmethod
    def normalize_path(path: str) -> str:
        """
        Normalize a path by removing trailing slashes and handling edge cases
        
        Args:
            path: Path to normalize
        
        Returns:
            Normalized path
        """
        if not path:
            return '/'
        
        # Remove trailing slashes, except for root
        if path != '/' and path.endswith('/'):
            path = path[:-1]
        
        return path