"""
virtual_shell/filesystem/search_utils.py - Filesystem search and discovery utilities
"""
import posixpath
import fnmatch
from typing import List, Callable, Optional


class SearchUtils:
    """
    Utility class for searching and discovering filesystem contents
    """
    
    @staticmethod
    def find(
        fs_provider, 
        path: str = "/", 
        recursive: bool = True, 
        filter_func: Optional[Callable] = None
    ) -> List[str]:
        """
        Find files and directories under a given path
        
        Args:
            fs_provider: Filesystem storage provider
            path: Starting path for search (default: root)
            recursive: Whether to search subdirectories (default: True)
            filter_func: Optional function to filter results
        
        Returns:
            List of full paths of files and directories
        """
        def _recursive_find(current_path):
            results = []
            try:
                contents = fs_provider.list_directory(current_path)
                for item in contents:
                    full_item_path = (current_path + '/' + item).replace('//', '/')
                    
                    # Get node info
                    full_path_info = fs_provider.get_node_info(full_item_path)
                    
                    # Apply filter if provided
                    if (not filter_func) or (filter_func and filter_func(full_item_path)):
                        results.append(full_item_path)
                    
                    # Recursively search subdirectories
                    if recursive and full_path_info and full_path_info.is_dir:
                        results.extend(_recursive_find(full_item_path))
            except Exception:
                pass
            return results
        
        return _recursive_find(path)
    
    @staticmethod
    def search(
        fs_provider, 
        path: str = "/", 
        pattern: str = "*", 
        recursive: bool = False
    ) -> List[str]:
        """
        Search for files matching a pattern
        
        Args:
            fs_provider: Filesystem storage provider
            path: Starting path for search
            pattern: Wildcard pattern to match (simple * supported)
            recursive: Whether to search subdirectories
        
        Returns:
            List of matching file paths
        """
        def _match_pattern(filename: str) -> bool:
            return fnmatch.fnmatch(posixpath.basename(filename), pattern)
        
        return SearchUtils.find(
            fs_provider, 
            path, 
            recursive, 
            filter_func=lambda x: (
                # Store node info in a variable to prevent redundant calls
                (lambda info: info and not info.is_dir and _match_pattern(x))
                (fs_provider.get_node_info(x))
            )
        )
