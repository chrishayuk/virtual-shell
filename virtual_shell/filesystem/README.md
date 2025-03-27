# Virtual Shell Filesystem

A modular virtual filesystem with pluggable storage providers designed for use in virtual shell environments, web applications, and educational tools.

## Features

- **Modular Design**: Core filesystem logic separate from storage implementation
- **Multiple Storage Providers**:
  - In-memory storage
  - SQLite-based storage
  - PyodideFS integration for web environments
  - AWS S3 storage
  - Easy to add custom providers
- **Full Filesystem Operations**:
  - File and directory creation
  - Reading and writing files
  - Copying and moving files
  - Path traversal and management
  - File searching
- **Efficient Path Resolution**: Handles relative and absolute paths correctly
- **Metadata Management**: Track creation dates, modification times, and other metadata

## Installation

```bash
pip install virtual-shell
```

## Basic Usage

```python
from virtual_shell.filesystem import VirtualFileSystem

# Create filesystem with default memory provider
fs = VirtualFileSystem()

# Create some directories
fs.mkdir("/home/user/documents")

# Create and write to a file
fs.write_file("/home/user/documents/hello.txt", "Hello, Virtual World!")

# Read from a file
content = fs.read_file("/home/user/documents/hello.txt")
print(f"File content: {content}")

# List directory contents
files = fs.ls("/home/user/documents")
print(f"Files: {files}")
```

## Storage Providers

### Memory Provider

The default provider that stores everything in memory.

```python
fs = VirtualFileSystem("memory")
```

### SQLite Provider

Stores the filesystem in a SQLite database, either in memory or on disk.

```python
fs = VirtualFileSystem("sqlite", db_path="filesystem.db")
```

### Pyodide Provider

Integrates with the Pyodide filesystem for use in web browsers.

```python
fs = VirtualFileSystem("pyodide", base_path="/home/pyodide")
```

### S3 Provider

Stores files and metadata in an AWS S3 bucket.

```python
fs = VirtualFileSystem("s3", 
                      bucket_name="my-bucket",
                      aws_access_key_id="YOUR_KEY",
                      aws_secret_access_key="YOUR_SECRET",
                      region_name="us-east-1")
```

## Switching Providers

You can change the storage provider during runtime:

```python
# Start with memory provider
fs = VirtualFileSystem("memory")

# Create a file
fs.write_file("/test.txt", "This is in memory")

# Switch to SQLite provider
fs.change_provider("sqlite", db_path=":memory:")

# Create another file (in SQLite now)
fs.write_file("/test2.txt", "This is in SQLite")
```

## Advanced Operations

```python
# Search for files matching a pattern
results = fs.search("/home", "*.txt", recursive=True)

# Find all files and directories (recursively)
all_items = fs.find("/home")

# Copy a file
fs.cp("/home/user/file.txt", "/home/backup/file.txt")

# Move a file
fs.mv("/home/user/temp.txt", "/home/user/documents/final.txt")

# Get storage statistics
stats = fs.get_storage_stats()
```

## Creating Custom Providers

You can create custom storage providers by extending the `StorageProvider` base class:

```python
from virtual_shell.filesystem import StorageProvider, register_provider

class MyCustomProvider(StorageProvider):
    # Implement required methods
    ...

# Register your provider
register_provider("custom", MyCustomProvider)

# Use your provider
fs = VirtualFileSystem("custom", **provider_args)
```

## License

MIT