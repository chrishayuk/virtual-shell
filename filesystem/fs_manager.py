"""
filesystem/fs_manager.py - Virtual filesystem manager
"""
import os
from typing import Dict, List, Optional, Tuple

from filesystem.node_base import FSNode
from filesystem.directory import Directory
from filesystem.file import File

class VirtualFileSystem:
    """
    Manager for the virtual filesystem that provides methods for 
    file and directory manipulation
    """
    
    def __init__(self):
        self.root = Directory("")
        self.current_directory = self.root
        
        # Initialize with some basic directories
        self.mkdir("/bin")
        self.mkdir("/home")
        self.mkdir("/tmp")
        self.mkdir("/etc")
        
        # Add some example files
        self.write_file("/etc/motd", "Welcome to PyodideShell - A Virtual Filesystem in the Browser!\n")
        self.write_file("/etc/passwd", "root:x:0:0:root:/root:/bin/bash\nuser:x:1000:1000:Default User:/home/user:/bin/bash\n")
    
    def resolve_path(self, path: str) -> Tuple[Optional[FSNode], Optional[str]]:
        """Resolve a path to a node and possible remaining path component"""
        if not path:
            return self.current_directory, None
            
        # Handle absolute vs relative paths
        if path.startswith('/'):
            current = self.root
            if path == '/':
                return current, None
            # Strip leading slash for processing
            path = path[1:]
        else:
            current = self.current_directory
            
        # Handle special path components
        if path == '.':
            return current, None
        elif path == '..':
            return current.parent or current, None
            
        # Split path into components
        components = path.split('/')
        
        # Navigate through the path components
        for i, component in enumerate(components):
            if not component or component == '.':
                continue
            elif component == '..':
                current = current.parent or current
            else:
                if isinstance(current, Directory):
                    child = current.get_child(component)
                    if child:
                        current = child
                    else:
                        # Return the last valid node and the remaining path
                        return current, '/'.join(components[i:])
                else:
                    # We've hit a file but still have path components
                    return current, '/'.join(components[i:])
                    
        return current, None
    
    def get_node(self, path: str) -> Optional[FSNode]:
        """Get a node at the specified path"""
        node, remaining = self.resolve_path(path)
        if remaining:
            return None
        return node
    
    def mkdir(self, path: str) -> bool:
        """Create a directory at the specified path"""
        if not path:
            return False
            
        if path.endswith('/'):
            path = path[:-1]
            
        # Handle root directory case
        if path == '/':
            return True  # Root already exists
            
        parent_path = os.path.dirname(path)
        dir_name = os.path.basename(path)
        
        if not dir_name:
            return False
            
        parent, remaining = self.resolve_path(parent_path)
        
        if remaining or not isinstance(parent, Directory):
            return False
            
        # Check if directory already exists
        if parent.get_child(dir_name):
            return False
            
        # Create and add the new directory
        new_dir = Directory(dir_name, parent)
        parent.add_child(new_dir)
        return True
    
    def touch(self, path: str) -> bool:
        """Create an empty file at the specified path if it doesn't exist"""
        if not path:
            return False
            
        parent_path = os.path.dirname(path)
        file_name = os.path.basename(path)
        
        if not file_name:
            return False
            
        parent, remaining = self.resolve_path(parent_path)
        
        if remaining or not isinstance(parent, Directory):
            return False
            
        # Check if file already exists
        if parent.get_child(file_name):
            # Update timestamp but don't modify content
            node = parent.get_child(file_name)
            node.modified_at = "2025-03-27T12:00:00Z"
            return True
            
        # Create and add the new file
        new_file = File(file_name, parent)
        parent.add_child(new_file)
        return True
    
    def write_file(self, path: str, content: str) -> bool:
        """Write content to a file at the specified path"""
        node = self.get_node(path)
        
        if isinstance(node, File):
            # File exists, update content
            node.write(content)
            return True
            
        # Try to create the file
        parent_path = os.path.dirname(path)
        file_name = os.path.basename(path)
        
        if not file_name:
            return False
            
        parent, remaining = self.resolve_path(parent_path)
        
        if remaining or not isinstance(parent, Directory):
            return False
            
        # Create and add the new file with content
        new_file = File(file_name, parent, content)
        parent.add_child(new_file)
        return True
    
    def read_file(self, path: str) -> Optional[str]:
        """Read content from a file at the specified path"""
        node = self.get_node(path)
        
        if isinstance(node, File):
            return node.read()
        return None
    
    def rm(self, path: str) -> bool:
        """Remove a file or empty directory"""
        node = self.get_node(path)
        
        if not node or node == self.root:
            return False
            
        parent = node.parent
        
        if isinstance(node, Directory) and node.children:
            return False  # Directory not empty
            
        return parent.remove_child(node.name) is not None
    
    def rmdir(self, path: str) -> bool:
        """Remove an empty directory"""
        node = self.get_node(path)
        
        if not isinstance(node, Directory) or node == self.root:
            return False
            
        if node.children:
            return False  # Directory not empty
            
        parent = node.parent
        return parent.remove_child(node.name) is not None
    
    def ls(self, path: str = None) -> List[str]:
        """List contents of a directory"""
        if path is None:
            node = self.current_directory
        else:
            node = self.get_node(path)
            
        if not isinstance(node, Directory):
            return []
            
        return list(node.children.keys())
    
    def cd(self, path: str) -> bool:
        """Change current directory"""
        node = self.get_node(path)
        
        if not isinstance(node, Directory):
            return False
            
        self.current_directory = node
        return True
    
    def pwd(self) -> str:
        """Get current working directory path"""
        return self.current_directory.get_path()