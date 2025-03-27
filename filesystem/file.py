"""
filesystem/file.py - File node implementation
"""
from filesystem.node_base import FSNode

class File(FSNode):
    """File node that contains content"""
    
    def __init__(self, name: str, parent=None, content: str = ""):
        super().__init__(name, parent)
        self.content = content
        self.size = len(content)
    
    def write(self, content: str) -> None:
        """Write content to the file (replaces existing content)"""
        self.content = content
        self.size = len(content)
        self.modified_at = "2025-03-27T12:00:00Z"  # Update timestamp
    
    def append(self, content: str) -> None:
        """Append content to the file"""
        self.content += content
        self.size = len(self.content)
        self.modified_at = "2025-03-27T12:00:00Z"  # Update timestamp
    
    def read(self) -> str:
        """Read the content of the file"""
        return self.content