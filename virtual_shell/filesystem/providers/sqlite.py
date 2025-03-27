"""
virtual_shell/filesystem/providers/sqlite.py - SQLite-based storage provider
"""
import json
import time
import posixpath
from typing import Dict, List, Optional

from virtual_shell.filesystem.provider_base import StorageProvider
from virtual_shell.filesystem.node_info import FSNodeInfo


class SqliteStorageProvider(StorageProvider):
    """SQLite-based storage provider"""
    
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.conn = None
        
    def initialize(self) -> bool:
        """Initialize the database"""
        try:
            import sqlite3
            self.conn = sqlite3.connect(self.db_path)
            
            # Create tables
            cursor = self.conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS nodes (
                path TEXT PRIMARY KEY,
                node_data TEXT NOT NULL
            )
            ''')
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_content (
                path TEXT PRIMARY KEY,
                content TEXT,
                size INTEGER
            )
            ''')
            
            # Create root node if it doesn't exist
            root_info = FSNodeInfo("", True)
            root_data = json.dumps(root_info.to_dict())
            
            cursor.execute(
                "INSERT OR IGNORE INTO nodes VALUES (?, ?)",
                ("/", root_data)
            )
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error initializing SQLite storage: {e}")
            return False
            
    def create_node(self, node_info: FSNodeInfo) -> bool:
        """Create a new node"""
        if not self.conn:
            return False
            
        try:
            path = node_info.get_path()
            
            # Check if node already exists
            cursor = self.conn.cursor()
            cursor.execute("SELECT 1 FROM nodes WHERE path = ?", (path,))
            if cursor.fetchone():
                return False
                
            # Ensure parent exists
            parent_path = posixpath.dirname(path)
            if parent_path != path:
                cursor.execute("SELECT 1 FROM nodes WHERE path = ?", (parent_path,))
                if not cursor.fetchone():
                    return False
                    
            # Insert node
            node_data = json.dumps(node_info.to_dict())
            cursor.execute(
                "INSERT INTO nodes VALUES (?, ?)",
                (path, node_data)
            )
            
            # Initialize empty content for files
            if not node_info.is_dir:
                cursor.execute(
                    "INSERT INTO file_content VALUES (?, ?, ?)",
                    (path, "", 0)
                )
                
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error creating node: {e}")
            self.conn.rollback()
            return False
            
    def delete_node(self, path: str) -> bool:
        """Delete a node"""
        if not self.conn:
            return False
            
        try:
            cursor = self.conn.cursor()
            
            # Check if node exists
            cursor.execute("SELECT node_data FROM nodes WHERE path = ?", (path,))
            result = cursor.fetchone()
            if not result:
                return False
                
            node_data = json.loads(result[0])
            is_dir = node_data["is_dir"]
            
            # Check if directory is empty
            if is_dir:
                cursor.execute("SELECT 1 FROM nodes WHERE path LIKE ?", (path + "/%",))
                if cursor.fetchone():
                    return False
                    
            # Delete node
            cursor.execute("DELETE FROM nodes WHERE path = ?", (path,))
            
            # Delete content if it's a file
            if not is_dir:
                cursor.execute("DELETE FROM file_content WHERE path = ?", (path,))
                
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting node: {e}")
            self.conn.rollback()
            return False
            
    def get_node_info(self, path: str) -> Optional[FSNodeInfo]:
        """Get information about a node"""
        if not self.conn:
            return None
            
        # Normalize path
        if not path:
            path = "/"
        elif path != "/" and path.endswith("/"):
            path = path[:-1]
            
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT node_data FROM nodes WHERE path = ?", (path,))
            result = cursor.fetchone()
            
            if not result:
                return None
                
            node_data = json.loads(result[0])
            return FSNodeInfo.from_dict(node_data)
        except Exception as e:
            print(f"Error getting node info: {e}")
            return None
            
    def list_directory(self, path: str) -> List[str]:
        """List contents of a directory"""
        if not self.conn:
            return []
            
        # Normalize path
        if not path:
            path = "/"
        elif path != "/" and path.endswith("/"):
            path = path[:-1]
            
        try:
            cursor = self.conn.cursor()
            
            # Check if path is a directory
            cursor.execute("SELECT node_data FROM nodes WHERE path = ?", (path,))
            result = cursor.fetchone()
            
            if not result:
                return []
                
            node_data = json.loads(result[0])
            if not node_data["is_dir"]:
                return []
                
            # Find direct children
            path_prefix = path if path == "/" else path + "/"
            cursor.execute(
                "SELECT node_data FROM nodes WHERE path LIKE ? AND path != ?",
                (path_prefix + "%", path)
            )
            
            results = []
            for row in cursor.fetchall():
                child_path = json.loads(row[0])["full_path"]
                relative_path = child_path[len(path_prefix):]
                
                # Only include direct children
                if "/" not in relative_path:
                    results.append(relative_path)
                    
            return results
        except Exception as e:
            print(f"Error listing directory: {e}")
            return []
            
    def write_file(self, path: str, content: str) -> bool:
        """Write content to a file"""
        if not self.conn:
            return False
            
        try:
            cursor = self.conn.cursor()
            
            # Check if path exists and is a file
            cursor.execute("SELECT node_data FROM nodes WHERE path = ?", (path,))
            result = cursor.fetchone()
            
            if not result:
                return False
                
            node_data = json.loads(result[0])
            if node_data["is_dir"]:
                return False
                
            # Update content
            size = len(content.encode('utf-8'))
            cursor.execute(
                "UPDATE file_content SET content = ?, size = ? WHERE path = ?",
                (content, size, path)
            )
            
            # Update modification time
            node_data["modified_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            cursor.execute(
                "UPDATE nodes SET node_data = ? WHERE path = ?",
                (json.dumps(node_data), path)
            )
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error writing file: {e}")
            self.conn.rollback()
            return False
            
    def read_file(self, path: str) -> Optional[str]:
        """Read content from a file"""
        if not self.conn:
            return None
            
        try:
            cursor = self.conn.cursor()
            
            # Check if path exists and is a file
            cursor.execute("SELECT node_data FROM nodes WHERE path = ?", (path,))
            result = cursor.fetchone()
            
            if not result:
                return None
                
            node_data = json.loads(result[0])
            if node_data["is_dir"]:
                return None
                
            # Get content
            cursor.execute("SELECT content FROM file_content WHERE path = ?", (path,))
            result = cursor.fetchone()
            
            return result[0] if result else ""
        except Exception as e:
            print(f"Error reading file: {e}")
            return None
            
    def get_storage_stats(self) -> Dict:
        """Get storage statistics"""
        if not self.conn:
            return {"error": "Database not initialized"}
            
        try:
            cursor = self.conn.cursor()
            
            # Count files and directories
            cursor.execute("SELECT COUNT(*) FROM nodes")
            total_nodes = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM nodes WHERE json_extract(node_data, '$.is_dir') = 1")
            dir_count = cursor.fetchone()[0]
            
            file_count = total_nodes - dir_count
            
            # Get total size
            cursor.execute("SELECT SUM(size) FROM file_content")
            total_size = cursor.fetchone()[0] or 0
            
            return {
                "total_size_bytes": total_size,
                "total_size_mb": total_size / (1024 * 1024),
                "file_count": file_count,
                "directory_count": dir_count,
                "node_count": total_nodes
            }
        except Exception as e:
            print(f"Error getting storage stats: {e}")
            return {"error": str(e)}
            
    def cleanup(self) -> Dict:
        """Perform cleanup operations"""
        if not self.conn:
            return {"error": "Database not initialized"}
            
        try:
            cursor = self.conn.cursor()
            
            # Get current total size
            cursor.execute("SELECT SUM(size) FROM file_content")
            size_before = cursor.fetchone()[0] or 0
            
            # Remove files in /tmp
            cursor.execute(
                "SELECT path FROM nodes WHERE path LIKE '/tmp/%' AND json_extract(node_data, '$.is_dir') = 0"
            )
            tmp_paths = [row[0] for row in cursor.fetchall()]
            
            removed = 0
            for path in tmp_paths:
                cursor.execute("DELETE FROM file_content WHERE path = ?", (path,))
                cursor.execute("DELETE FROM nodes WHERE path = ?", (path,))
                removed += 1
                
            self.conn.commit()
            
            # Get new total size
            cursor.execute("SELECT SUM(size) FROM file_content")
            size_after = cursor.fetchone()[0] or 0
            
            return {
                "bytes_freed": size_before - size_after,
                "files_removed": removed
            }
        except Exception as e:
            print(f"Error during cleanup: {e}")
            self.conn.rollback()
            return {"error": str(e)}