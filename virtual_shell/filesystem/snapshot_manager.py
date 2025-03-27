"""
virtual_shell/filesystem/snapshot_manager.py - Snapshot and restore functionality for virtual filesystem
"""
import os
import json
import time
import datetime
from typing import Dict, List, Optional, Any, Set

class SnapshotManager:
    """
    Provides snapshot and restore capabilities for the virtual filesystem
    
    This allows saving the current state of the filesystem and restoring it later,
    which is useful for:
    - Creating savepoints during operations
    - Implementing undo/redo functionality
    - Sharing filesystem states between sessions
    - Testing and development scenarios
    """
    
    def __init__(self, fs):
        """
        Initialize the snapshot manager
        
        Args:
            fs: The virtual filesystem instance to manage
        """
        self.fs = fs
        self.snapshots = {}
        self.snapshot_metadata = {}
    
    def create_snapshot(self, name: Optional[str] = None, description: str = "") -> str:
        """
        Create a snapshot of the current filesystem state
        
        Args:
            name: Optional name for the snapshot (auto-generated if not provided)
            description: Optional description of the snapshot
            
        Returns:
            The name/ID of the created snapshot
        """
        # Generate a name if not provided
        if name is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            name = f"snapshot_{timestamp}"
        
        # Create the snapshot data
        snapshot_data = self._serialize_filesystem()
        
        # Store the snapshot
        self.snapshots[name] = snapshot_data
        
        # Store metadata
        self.snapshot_metadata[name] = {
            "created": time.time(),
            "description": description,
            "fs_provider": self.fs.get_provider_name(),
            "stats": self.fs.get_storage_stats()
        }
        
        return name
    
    def restore_snapshot(self, name: str) -> bool:
        """
        Restore the filesystem to a previously saved snapshot
        
        Args:
            name: Name/ID of the snapshot to restore
            
        Returns:
            True if restore was successful, False otherwise
        """
        if name not in self.snapshots:
            return False
        
        # Get the snapshot data
        snapshot_data = self.snapshots[name]
        
        # Restore the filesystem from the snapshot
        success = self._deserialize_filesystem(snapshot_data)
        
        return success
    
    def delete_snapshot(self, name: str) -> bool:
        """
        Delete a saved snapshot
        
        Args:
            name: Name/ID of the snapshot to delete
            
        Returns:
            True if snapshot was deleted, False if it doesn't exist
        """
        if name not in self.snapshots:
            return False
        
        # Remove the snapshot and its metadata
        del self.snapshots[name]
        if name in self.snapshot_metadata:
            del self.snapshot_metadata[name]
        
        return True
    
    def list_snapshots(self) -> List[Dict[str, Any]]:
        """
        List all available snapshots with their metadata
        
        Returns:
            List of dictionaries containing snapshot information
        """
        result = []
        
        for name, metadata in self.snapshot_metadata.items():
            snapshot_info = {
                "name": name,
                "created": metadata["created"],
                "description": metadata["description"],
                "provider": metadata.get("fs_provider", "unknown"),
                "stats": metadata.get("stats", {})
            }
            result.append(snapshot_info)
        
        # Sort by creation time (newest first)
        result.sort(key=lambda x: x["created"], reverse=True)
        
        return result
    
    def export_snapshot(self, name: str, file_path: str) -> bool:
        """
        Export a snapshot to a file
        
        Args:
            name: Name/ID of the snapshot to export
            file_path: Path to save the snapshot file
            
        Returns:
            True if export was successful, False otherwise
        """
        if name not in self.snapshots:
            return False
        
        try:
            # Create export data with both snapshot and metadata
            export_data = {
                "snapshot": self.snapshots[name],
                "metadata": self.snapshot_metadata.get(name, {})
            }
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            # Write to file
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error exporting snapshot: {e}")
            return False
    
    def import_snapshot(self, file_path: str, new_name: Optional[str] = None) -> Optional[str]:
        """
        Import a snapshot from a file
        
        Args:
            file_path: Path to the snapshot file
            new_name: Optional new name for the imported snapshot
            
        Returns:
            Name of the imported snapshot or None if import failed
        """
        try:
            # Read from file
            with open(file_path, 'r') as f:
                import_data = json.load(f)
            
            # Extract snapshot and metadata
            if not isinstance(import_data, dict) or "snapshot" not in import_data:
                print("Invalid snapshot file format")
                return None
            
            snapshot_data = import_data["snapshot"]
            metadata = import_data.get("metadata", {})
            
            # Determine snapshot name
            name = new_name
            if name is None:
                # Use original name if available, otherwise generate one
                name = metadata.get("name")
                if name is None or name in self.snapshots:
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    name = f"imported_{timestamp}"
            
            # Store the snapshot and metadata
            self.snapshots[name] = snapshot_data
            
            # Update metadata
            if metadata:
                self.snapshot_metadata[name] = metadata
            else:
                self.snapshot_metadata[name] = {
                    "created": time.time(),
                    "description": f"Imported from {os.path.basename(file_path)}",
                    "imported": True
                }
            
            return name
        except Exception as e:
            print(f"Error importing snapshot: {e}")
            return None
    
    def _serialize_filesystem(self) -> Dict:
        """
        Serialize the current filesystem state into a portable format
        
        Returns:
            Dictionary representation of the filesystem
        """
        # Start with empty structure
        fs_data = {
            "version": 1,
            "timestamp": time.time(),
            "provider": self.fs.get_provider_name(),
            "directories": {},
            "files": {}
        }
        
        # Get all paths from the filesystem
        paths = self.fs.find("/", recursive=True)
        
        # Process each path
        for path in paths:
            node_info = self.fs.get_node_info(path)
            if not node_info:
                continue
            
            # Store directories and files separately
            if node_info.is_dir:
                fs_data["directories"][path] = {
                    "name": node_info.name,
                    "parent": node_info.parent_path
                }
            else:
                # Read file content
                content = self.fs.read_file(path) or ""
                fs_data["files"][path] = {
                    "name": node_info.name,
                    "parent": node_info.parent_path,
                    "content": content
                }
        
        return fs_data
    
    def _deserialize_filesystem(self, fs_data: Dict) -> bool:
        """
        Restore filesystem state from serialized data
        
        Args:
            fs_data: Dictionary representation of filesystem state
            
        Returns:
            True if restore was successful, False otherwise
        """
        try:
            # Verify data format
            if not isinstance(fs_data, dict) or "version" not in fs_data:
                return False
                
            # Get paths that should exist after restore
            snapshot_dirs = set(fs_data.get("directories", {}).keys())
            snapshot_files = set(fs_data.get("files", {}).keys())
            snapshot_paths = snapshot_dirs.union(snapshot_files)
            
            # Get current filesystem paths
            current_paths = set(self.fs.find("/", recursive=True))
            
            # Identify paths that exist now but shouldn't after restore
            # We need to remove these
            paths_to_remove = current_paths - snapshot_paths
            # Skip system directories
            system_dirs = {"/bin", "/etc", "/var", "/usr", "/sbin"}
            paths_to_remove = {path for path in paths_to_remove if not any(path == sys_dir or path.startswith(sys_dir + "/") for sys_dir in system_dirs)}
            # Skip /home (base for test directories)
            paths_to_remove = {path for path in paths_to_remove if path != "/home"}
            
            # Sort paths to remove, deepest paths first
            sorted_paths_to_remove = sorted(paths_to_remove, key=lambda p: -p.count('/'))
            
            # Remove paths that shouldn't exist
            for path in sorted_paths_to_remove:
                try:
                    # Get path info to see if it's a file or directory
                    node_info = self.fs.get_node_info(path)
                    if node_info:
                        self.fs.rm(path)
                except Exception as e:
                    print(f"Error removing path {path}: {e}")
            
            # First create all directories
            for path, dir_info in sorted(fs_data.get("directories", {}).items()):
                if path == "/":
                    continue  # Skip root directory
                
                # Make sure parent directories exist
                parent_path = dir_info.get("parent", os.path.dirname(path))
                if parent_path != "/" and not self.fs.get_node_info(parent_path):
                    # Create parent directory first
                    self._ensure_directory(parent_path)
                
                # Create directory if it doesn't exist
                if not self.fs.get_node_info(path):
                    self.fs.mkdir(path)
            
            # Then create all files
            for path, file_info in fs_data.get("files", {}).items():
                # Make sure parent directory exists
                parent_path = file_info.get("parent", os.path.dirname(path))
                if parent_path != "/" and not self.fs.get_node_info(parent_path):
                    # Create parent directory first
                    self._ensure_directory(parent_path)
                
                # Write file content (overwriting if it exists)
                content = file_info.get("content", "")
                self.fs.write_file(path, content)
            
            return True
        except Exception as e:
            print(f"Error restoring filesystem: {e}")
            return False
    
    def _ensure_directory(self, path: str) -> bool:
        """
        Ensure a directory exists, creating parent directories as needed
        
        Args:
            path: Directory path to create
            
        Returns:
            True if successful, False otherwise
        """
        # Special case for root
        if path == "/":
            return True
            
        # Split path into components
        components = path.strip('/').split('/')
        
        # Start with root
        current_path = "/"
        
        for component in components:
            if not component:
                continue
            
            # Update current path
            if current_path.endswith('/'):
                current_path = current_path + component
            else:
                current_path = current_path + '/' + component
            
            # Check if directory exists
            info = self.fs.get_node_info(current_path)
            if not info:
                # Create directory
                success = self.fs.mkdir(current_path)
                if not success:
                    print(f"Failed to create directory: {current_path}")
                    return False
            elif not info.is_dir:
                # Path exists but is not a directory
                print(f"Path exists but is not a directory: {current_path}")
                return False
        
        return True