# Storage Providers

This document details the available storage providers for the Virtual Shell Filesystem and how to implement custom providers.

## Built-in Providers

### Memory Provider

The `MemoryStorageProvider` is the default provider that stores everything in memory.

**Features:**
- Fast access and operations
- No persistence between sessions
- Optional compression for large files

**Usage:**
```python
from virtual_shell.filesystem import VirtualFileSystem

# Default initialization
fs = VirtualFileSystem("memory")

# With custom compression threshold (in bytes)
fs = VirtualFileSystem("memory", compression_threshold=8192)
```

### SQLite Provider

The `SqliteStorageProvider` stores the filesystem in a SQLite database.

**Features:**
- Persistent storage
- Efficient querying and indexing
- Can use in-memory or file-based databases

**Usage:**
```python
# In-memory SQLite database
fs = VirtualFileSystem("sqlite", db_path=":memory:")

# File-based SQLite database
fs = VirtualFileSystem("sqlite", db_path="filesystem.db")
```

**Dependencies:**
- Standard library `sqlite3` module

### Pyodide Provider

The `PyodideStorageProvider` integrates with the Pyodide filesystem in web browsers.

**Features:**
- Works in browser environments using Pyodide
- Maps to the Pyodide virtual filesystem
- Provides persistence in web applications

**Usage:**
```python
fs = VirtualFileSystem("pyodide", base_path="/home/pyodide")
```

**Dependencies:**
- Running in a Pyodide environment

### S3 Provider

The `S3StorageProvider` stores files and metadata in an AWS S3 bucket.

**Features:**
- Cloud-based storage
- Highly scalable and reliable
- Capable of handling very large filesystems

**Usage:**
```python
# With explicit credentials
fs = VirtualFileSystem("s3", 
                     bucket_name="my-bucket",
                     aws_access_key_id="YOUR_KEY",
                     aws_secret_access_key="YOUR_SECRET",
                     region_name="us-east-1")

# Using environment variables or instance profile
fs = VirtualFileSystem("s3",
                     bucket_name="my-bucket",
                     region_name="us-east-1")

# Using an S3-compatible service
fs = VirtualFileSystem("s3",
                     bucket_name="my-bucket",
                     endpoint_url="https://minio.example.com",
                     aws_access_key_id="YOUR_KEY",
                     aws_secret_access_key="YOUR_SECRET")
```

**Dependencies:**
- `boto3` package: `pip install boto3`

## Implementing Custom Providers

You can create custom storage providers by extending the `StorageProvider` base class:

```python
from virtual_shell.filesystem.provider_base import StorageProvider
from virtual_shell.filesystem.node_info import FSNodeInfo
from virtual_shell.filesystem.providers import register_provider

class MyCustomProvider(StorageProvider):
    """My custom storage provider"""
    
    def __init__(self, **kwargs):
        # Initialize your provider
        pass
        
    def initialize(self) -> bool:
        """Initialize the storage provider"""
        # Setup your storage
        return True
        
    def create_node(self, node_info: FSNodeInfo) -> bool:
        """Create a new node (file or directory)"""
        # Implement node creation
        pass
        
    def delete_node(self, path: str) -> bool:
        """Delete a node"""
        # Implement node deletion
        pass
        
    def get_node_info(self, path: str) -> Optional[FSNodeInfo]:
        """Get information about a node"""
        # Implement node info retrieval
        pass
        
    def list_directory(self, path: str) -> List[str]:
        """List contents of a directory"""
        # Implement directory listing
        pass
        
    def write_file(self, path: str, content: str) -> bool:
        """Write content to a file"""
        # Implement file writing
        pass
        
    def read_file(self, path: str) -> Optional[str]:
        """Read content from a file"""
        # Implement file reading
        pass
        
    def get_storage_stats(self) -> Dict:
        """Get storage statistics"""
        # Implement stats gathering
        pass
        
    def cleanup(self) -> Dict:
        """Perform cleanup operations"""
        # Implement cleanup functionality
        pass

# Register your provider
register_provider("custom", MyCustomProvider)

# Use your provider
fs = VirtualFileSystem("custom", **provider_args)
```

## Provider Selection

Providers are selected in order of:

1. Explicitly requested provider name
2. Environment variable `VIRTUAL_FS_PROVIDER`
3. Default "memory" provider

## Provider Requirements

When implementing a provider, ensure:

1. All abstract methods from `StorageProvider` are implemented
2. The root path `/` is always available
3. The provider handles proper path normalization
4. All paths are POSIX-style (using forward slashes)
5. Parent directories are created before child nodes
6. Directory deletion checks for emptiness

## Testing Providers

A test suite for providers is available:

```python
from virtual_shell.filesystem.tests import test_provider

# Test your provider
results = test_provider(MyCustomProvider())
```