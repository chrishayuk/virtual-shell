"""
virtual_shell/filesystem/providers/memory.py - In-memory storage provider
"""
import time
import posixpath
from typing import Dict, List, Optional

from virtual_shell.filesystem.provider_base import StorageProvider
from virtual_shell.filesystem.node_info import FSNodeInfo


class MemoryStorageProvider(StorageProvider):
    """In-memory implementation of storage provider"""
    
    def __init__(self, compression_threshold: int = 4096):
        self.nodes = {}  # Dict of path -> FSNodeInfo
        self.content = {}  # Dict of path -> content
        self.compression_threshold = compression_threshold
        self._total_size = 0
        
    def initialize(self) -> bool:
        """Initialize the storage"""
        # Create root directory
        root_info = FSNodeInfo("", True)
        self.nodes["/"] = root_info
        return True
        
    def create_node(self, node_info: FSNodeInfo) -> bool:
        """Create a new node"""
        path = node_info.get_path()
        if path in self.nodes:
            return False
            
        # Ensure parent exists
        parent_path = posixpath.dirname(path)
        if parent_path != path and parent_path not in self.nodes:
            return False
            
        self.nodes[path] = node_info
        if not node_info.is_dir:
            # Initialize empty content for files
            self.content[path] = ""
            
        return True
        
    def delete_node(self, path: str) -> bool:
        """Delete a node"""
        if path not in self.nodes:
            return False
            
        node_info = self.nodes[path]
        
        # Check if directory is empty
        if node_info.is_dir:
            for other_path in list(self.nodes.keys()):
                if other_path.startswith(path + "/"):
                    return False
                    
        # Remove node
        del self.nodes[path]
        
        # Remove content if it's a file
        if path in self.content:
            # Track size change
            self._total_size -= len(self.content[path].encode('utf-8'))
            del self.content[path]
            
        return True
        
    def get_node_info(self, path: str) -> Optional[FSNodeInfo]:
        """Get information about a node"""
        # Normalize path
        if not path:
            path = "/"
        elif path != "/" and path.endswith("/"):
            path = path[:-1]
            
        return self.nodes.get(path)
        
    def list_directory(self, path: str) -> List[str]:
        """List contents of a directory"""
        # Normalize path
        if not path:
            path = "/"
        elif path != "/" and path.endswith("/"):
            path = path[:-1]
            
        if path not in self.nodes or not self.nodes[path].is_dir:
            return []
            
        results = []
        path_prefix = path if path == "/" else path + "/"
        
        # Find direct children
        for other_path, node_info in self.nodes.items():
            # Skip self
            if other_path == path:
                continue
                
            # Check if direct child
            if other_path.startswith(path_prefix):
                rest = other_path[len(path_prefix):]
                if "/" not in rest:
                    results.append(node_info.name)
                    
        return results
        
    def write_file(self, path: str, content: str) -> bool:
        """Write content to a file"""
        # Ensure path exists and is a file
        if path not in self.nodes:
            return False
            
        node_info = self.nodes[path]
        if node_info.is_dir:
            return False
            
        # Update content
        old_size = len(self.content[path].encode('utf-8')) if path in self.content else 0
        new_size = len(content.encode('utf-8'))
        
        self.content[path] = content
        self._total_size = self._total_size - old_size + new_size
        
        # Update modification time
        node_info.modified_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        
        return True
        
    def read_file(self, path: str) -> Optional[str]:
        """Read content from a file"""
        # Ensure path exists and is a file
        if path not in self.nodes or self.nodes[path].is_dir:
            return None
            
        return self.content.get(path, "")
        
    def get_storage_stats(self) -> Dict:
        """Get storage statistics"""
        file_count = sum(1 for info in self.nodes.values() if not info.is_dir)
        dir_count = sum(1 for info in self.nodes.values() if info.is_dir)
        
        return {
            "total_size_bytes": self._total_size,
            "total_size_mb": self._total_size / (1024 * 1024),
            "file_count": file_count,
            "directory_count": dir_count,
            "node_count": len(self.nodes)
        }
        
    def cleanup(self) -> Dict:
        """Perform cleanup operations"""
        # Simple cleanup: remove files in /tmp
        tmp_paths = [p for p in self.nodes.keys() 
                    if p.startswith("/tmp/") and not self.nodes[p].is_dir]
                    
        size_before = self._total_size
        removed = 0
        
        for path in tmp_paths:
            if self.delete_node(path):
                removed += 1
                
        return {
            "bytes_freed": size_before - self._total_size,
            "files_removed": removed
        }