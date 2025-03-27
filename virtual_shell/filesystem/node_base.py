"""
virtual_shell/filesystem/node_base.py - Base class for filesystem nodes
"""
class FSNode:
    """Base class for all filesystem nodes (files and directories)"""
    
    def __init__(self, name: str, parent=None):
        self.name = name
        self.parent = parent
        self.created_at = "2025-03-27T12:00:00Z"  # Example timestamp
        self.modified_at = self.created_at
        self.permissions = "rwxr-xr-x"  # Default permissions
        
    def get_path(self) -> str:
        """Get the full path of this node"""
        if self.parent is None:
            return "/"
        elif self.parent.get_path() == "/":
            return f"/{self.name}"
        else:
            return f"{self.parent.get_path()}/{self.name}"