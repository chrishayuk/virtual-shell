"""
virtual_shell/filesystem/security_wrapper.py - Security wrapper for storage providers
"""
import posixpath
import re
from typing import Dict, List, Optional, Any, Set

from virtual_shell.filesystem.provider_base import StorageProvider
from virtual_shell.filesystem.node_info import FSNodeInfo


class SecurityWrapper(StorageProvider):
    """
    Security wrapper for storage providers to add sandboxing and resource limits
    
    Provides:
    - File size limits
    - Total storage quota
    - Path traversal protection
    - Restricted paths and file types
    - Read-only mode
    """
    
    def __init__(
        self, 
        provider: StorageProvider,
        max_file_size: int = 10 * 1024 * 1024,  # 10MB default max file size
        max_total_size: int = 100 * 1024 * 1024,  # 100MB default total quota
        read_only: bool = False,
        allowed_paths: List[str] = None,
        denied_paths: List[str] = None,
        denied_patterns: List[str] = None,
        max_path_depth: int = 10,
        max_files: int = 1000,
        setup_allowed_paths: bool = True
    ):
        """
        Initialize the security wrapper
        
        Args:
            provider: The underlying storage provider to wrap
            max_file_size: Maximum size in bytes for any single file
            max_total_size: Maximum total storage quota in bytes
            read_only: If True, all write operations will be denied
            allowed_paths: List of path prefixes that are allowed (None means all)
            denied_paths: List of path prefixes that are denied
            denied_patterns: List of regex patterns for denied filenames
            max_path_depth: Maximum allowed directory depth
            max_files: Maximum number of files allowed
            setup_allowed_paths: Whether to automatically create allowed paths
        """
        self.provider = provider
        self.max_file_size = max_file_size
        self.max_total_size = max_total_size
        self.read_only = read_only
        self.allowed_paths = allowed_paths or ["/"]
        self.denied_paths = denied_paths or ["/etc/passwd", "/etc/shadow"]
        self.denied_patterns = [re.compile(p) for p in (denied_patterns or [r"\.\.", r"\.env"])]
        self.max_path_depth = max_path_depth
        self.max_files = max_files
        self._violation_log = []
        
        # For tracking current directory in some provider implementations
        if hasattr(provider, 'current_directory_path'):
            self.current_directory_path = provider.current_directory_path
            
        # Setup allowed paths if requested
        if setup_allowed_paths:
            self._setup_allowed_paths()
    
    def _setup_allowed_paths(self) -> None:
        """
        Create all allowed paths to ensure they exist before applying restrictions.
        This temporarily disables security checks to set up the basic structure.
        """
        # Save original read-only state and temporarily disable it
        original_read_only = self.read_only
        self.read_only = False
        
        # Flag to skip security checks during setup
        self._in_setup = True
        
        try:
            # Create each allowed path if it doesn't exist
            for path in self.allowed_paths:
                if path == "/":
                    continue  # Root always exists
                    
                # Normalize path
                path = posixpath.normpath(path)
                
                # Skip if path already exists
                if self.provider.get_node_info(path):
                    continue
                    
                # Create path components
                components = path.strip('/').split('/')
                current_path = ""
                
                for component in components:
                    if not component:
                        continue
                        
                    parent_path = current_path or "/"
                    current_path = posixpath.join(parent_path, component)
                    
                    # Create directory if it doesn't exist
                    if not self.provider.get_node_info(current_path):
                        node_info = FSNodeInfo(component, True, parent_path)
                        self.provider.create_node(node_info)
        finally:
            # Restore original read-only state
            self.read_only = original_read_only
            self._in_setup = False
    
    def _log_violation(self, operation: str, path: str, reason: str) -> None:
        """Log a security violation"""
        violation = {
            "operation": operation,
            "path": path,
            "reason": reason,
            "timestamp": "2025-03-27T12:00:00Z"  # In a real implementation, use actual time
        }
        self._violation_log.append(violation)
        print(f"Security violation: {reason} (op: {operation}, path: {path})")
    
    def get_violation_log(self) -> List[Dict]:
        """Get the security violation log"""
        return self._violation_log.copy()
    
    def clear_violations(self) -> None:
        """Clear the security violation log"""
        self._violation_log = []
    
    def _is_path_allowed(self, path: str, operation: str) -> bool:
        """
        Check if a path is allowed based on security rules
        
        Args:
            path: Path to check
            operation: Operation being performed (for logging)
            
        Returns:
            True if path is allowed, False otherwise
        """
        # Skip security checks if we're in setup mode
        if hasattr(self, '_in_setup') and self._in_setup:
            return True
            
        # Normalize path
        path = posixpath.normpath(path)
        
        # Root path is always allowed for reading
        if path == "/" and operation in ["get_node_info", "list_directory"]:
            return True
            
        # Check read-only mode for write operations
        if self.read_only and operation in ["create_node", "delete_node", "write_file"]:
            self._log_violation(operation, path, "Filesystem is in read-only mode")
            return False
        
        # Check path depth
        path_depth = len([p for p in path.split("/") if p])
        if path_depth > self.max_path_depth:
            self._log_violation(operation, path, f"Path depth exceeds maximum ({path_depth} > {self.max_path_depth})")
            return False
        
        # Check allowed paths
        if self.allowed_paths != ["/"]:
            # Special case for root path
            if path == "/":
                # Allow reading the root path for navigation
                if operation in ["get_node_info", "list_directory"]:
                    return True
                    
            if not any(path == allowed or path.startswith(allowed + '/') for allowed in self.allowed_paths):
                self._log_violation(operation, path, "Path not in allowed paths list")
                return False
        
        # Check denied paths
        if any(path == denied or path.startswith(denied + '/') for denied in self.denied_paths):
            self._log_violation(operation, path, "Path in denied paths list")
            return False
        
        # Check denied patterns
        basename = posixpath.basename(path)
        if any(pattern.search(basename) for pattern in self.denied_patterns):
            self._log_violation(operation, path, "Path matches denied pattern")
            return False
        
        return True
    
    def initialize(self) -> bool:
        """Initialize the provider"""
        return self.provider.initialize()
    
    def create_node(self, node_info: FSNodeInfo) -> bool:
        """Create a new node with security checks"""
        path = node_info.get_path()
        
        # Security checks
        if not self._is_path_allowed(path, "create_node"):
            return False
        
        # Check file count limit
        if not node_info.is_dir:
            stats = self.get_storage_stats()
            if stats.get("file_count", 0) >= self.max_files:
                self._log_violation("create_node", path, f"File count exceeds maximum ({self.max_files})")
                return False
        
        return self.provider.create_node(node_info)
    
    def delete_node(self, path: str) -> bool:
        """Delete a node with security checks"""
        # Security checks
        if not self._is_path_allowed(path, "delete_node"):
            return False
        
        return self.provider.delete_node(path)
    
    def get_node_info(self, path: str) -> Optional[FSNodeInfo]:
        """Get information about a node with security checks"""
        # Security checks for reading
        if not self._is_path_allowed(path, "get_node_info"):
            return None
        
        return self.provider.get_node_info(path)
    
    def list_directory(self, path: str) -> List[str]:
        """List contents of a directory with security checks"""
        # Security checks for reading
        if not self._is_path_allowed(path, "list_directory"):
            return []
        
        return self.provider.list_directory(path)
    
    def write_file(self, path: str, content: str) -> bool:
        """Write content to a file with security checks"""
        # Security checks
        if not self._is_path_allowed(path, "write_file"):
            return False
        
        # Check file size limit
        content_size = len(content.encode('utf-8'))
        if content_size > self.max_file_size:
            self._log_violation("write_file", path, 
                               f"File size exceeds maximum ({content_size} > {self.max_file_size} bytes)")
            return False
        
        # Check total storage quota
        stats = self.get_storage_stats()
        current_size = stats.get("total_size_bytes", 0)
        
        # Get current file size if it exists
        current_content = self.read_file(path)
        current_file_size = len(current_content.encode('utf-8')) if current_content else 0
        
        # Calculate new total size
        new_total_size = current_size - current_file_size + content_size
        
        if new_total_size > self.max_total_size:
            self._log_violation("write_file", path, 
                              f"Total storage quota exceeded ({new_total_size} > {self.max_total_size} bytes)")
            return False
        
        return self.provider.write_file(path, content)
    
    def read_file(self, path: str) -> Optional[str]:
        """Read content from a file with security checks"""
        # Security checks for reading
        if not self._is_path_allowed(path, "read_file"):
            return None
        
        return self.provider.read_file(path)
    
    def get_storage_stats(self) -> Dict:
        """Get storage statistics"""
        stats = self.provider.get_storage_stats()
        
        # Add security-related stats
        stats.update({
            "max_file_size": self.max_file_size,
            "max_total_size": self.max_total_size,
            "max_files": self.max_files,
            "read_only": self.read_only,
            "allowed_paths": self.allowed_paths,
            "security_violations": len(self._violation_log)
        })
        
        return stats
    
    def cleanup(self) -> Dict:
        """Perform cleanup operations"""
        return self.provider.cleanup()
    
    # Forward any additional provider-specific attributes
    def __getattr__(self, name):
        return getattr(self.provider, name)