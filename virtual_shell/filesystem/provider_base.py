"""
virtual_shell/filesystem/provider_base.py - Abstract base class for storage providers
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from virtual_shell.filesystem.node_info import FSNodeInfo


class StorageProvider(ABC):
    """Abstract base class for filesystem storage providers"""
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the storage provider"""
        pass
        
    @abstractmethod
    def create_node(self, node_info: FSNodeInfo) -> bool:
        """Create a new node (file or directory)"""
        pass
        
    @abstractmethod
    def delete_node(self, path: str) -> bool:
        """Delete a node"""
        pass
        
    @abstractmethod
    def get_node_info(self, path: str) -> Optional[FSNodeInfo]:
        """Get information about a node"""
        pass
        
    @abstractmethod
    def list_directory(self, path: str) -> List[str]:
        """List contents of a directory"""
        pass
        
    @abstractmethod
    def write_file(self, path: str, content: str) -> bool:
        """Write content to a file"""
        pass
        
    @abstractmethod
    def read_file(self, path: str) -> Optional[str]:
        """Read content from a file"""
        pass
        
    @abstractmethod
    def get_storage_stats(self) -> Dict:
        """Get storage statistics"""
        pass
        
    @abstractmethod
    def cleanup(self) -> Dict:
        """Perform cleanup operations"""
        pass