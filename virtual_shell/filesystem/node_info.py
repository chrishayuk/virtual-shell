"""
virtual_shell/filesystem/node_info.py - Node info for storage providers
"""
import time
import uuid
from typing import Dict, Optional

class FSNodeInfo:
    """
    Information about a filesystem node (file or directory)
    Used by storage providers to track metadata
    """
    
    def __init__(self, name: str, is_dir: bool, parent_path: str = None, 
                 modified_at: str = None, metadata: Dict = None):
        self.name = name
        self.is_dir = is_dir
        self.parent_path = parent_path or ""
        self.modified_at = modified_at or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        self.metadata = metadata or {}
        self.id = str(uuid.uuid4())  # Unique identifier for node
        
    def get_path(self) -> str:
        """Get full path for this node"""
        if not self.parent_path:
            return "/" if not self.name else f"/{self.name}"
        elif self.parent_path == "/":
            return f"/{self.name}"
        else:
            return f"{self.parent_path}/{self.name}"
            
    def to_dict(self) -> Dict:
        """Convert node info to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "is_dir": self.is_dir,
            "parent_path": self.parent_path,
            "full_path": self.get_path(),
            "modified_at": self.modified_at,
            "metadata": self.metadata
        }
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'FSNodeInfo':
        """Create node info from dictionary"""
        node = cls(
            name=data["name"],
            is_dir=data["is_dir"],
            parent_path=data["parent_path"],
            modified_at=data["modified_at"],
            metadata=data.get("metadata", {})
        )
        node.id = data["id"]
        return node