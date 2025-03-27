# Virtual Shell Filesystem

A modular virtual filesystem with pluggable storage providers and advanced management capabilities, designed for use in virtual shell environments, web applications, and educational tools.

## Features

- **Modular Design**: Core filesystem logic separate from storage implementation
- **Multiple Storage Providers**:
  - In-memory storage
  - SQLite-based storage
  - PyodideFS integration for web environments
  - AWS S3 storage
  - Easy to add custom providers
- **Advanced Filesystem Management**:
  - Snapshots and versioning
  - Template-based filesystem setup
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
from virtual_shell.filesystem.snapshot_manager import SnapshotManager
from virtual_shell.filesystem.template_loader import TemplateLoader

# Create filesystem with default memory provider
fs = VirtualFileSystem()

# Create some directories
fs.mkdir("/home/user/documents")

# Create and write to a file
fs.write_file("/home/user/documents/hello.txt", "Hello, Virtual World!")

# Read from a file
content = fs.read_file("/home/user/documents/hello.txt")
print(f"File content: {content}")
```

## Snapshot Management

Snapshots allow you to save and restore filesystem states:

```python
# Create a snapshot manager
snapshot_mgr = SnapshotManager(fs)

# Create a snapshot
initial_snapshot = snapshot_mgr.create_snapshot(
    "project_start", 
    "Initial project setup"
)

# Make some changes
fs.write_file("/home/user/documents/notes.txt", "Project ideas")

# Create another snapshot
working_snapshot = snapshot_mgr.create_snapshot(
    "first_draft", 
    "Added initial notes"
)

# List available snapshots
snapshots = snapshot_mgr.list_snapshots()
for snap in snapshots:
    print(f"Snapshot: {snap['name']} - {snap['description']}")

# Restore to a previous state
snapshot_mgr.restore_snapshot(initial_snapshot)

# Export a snapshot
snapshot_mgr.export_snapshot(working_snapshot, "/backup/snapshot.json")

# Import a snapshot
imported_snapshot = snapshot_mgr.import_snapshot("/backup/snapshot.json")
```

## Template Management

Create and load filesystem templates easily:

```python
# Create template loader
template_loader = TemplateLoader(fs)

# Define a project template
project_template = {
    "directories": [
        "/home/project/src",
        "/home/project/tests"
    ],
    "files": [
        {
            "path": "/home/project/README.md",
            "content": "# ${project_name}\n\n${project_description}"
        },
        {
            "path": "/home/project/src/main.py",
            "content": "def main():\n    print('Hello, ${project_name}!')"
        }
    ]
}

# Apply template with variable substitution
template_loader.apply_template(
    project_template, 
    variables={
        "project_name": "MyAwesomeProject",
        "project_description": "A sample project created from a template"
    }
)

# Load template from a file
template_loader.load_template("project_template.yaml")

# Quickly load multiple files
template_loader.quick_load({
    "/home/project/config.ini": "key=value",
    "/home/project/requirements.txt": "requests==2.26.0"
})
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

## Key Benefits

- **Flexibility**: Switch between storage providers seamlessly
- **Versioning**: Save and restore filesystem states
- **Reproducibility**: Use templates to set up consistent environments
- **Isolation**: Completely virtual filesystem with no host system dependencies

## Use Cases

- Development sandboxing
- Educational environments
- Web-based IDEs
- Reproducible computing environments
- Testing and simulation

## Contributing

Contributions are welcome! Please submit pull requests or open issues on our GitHub repository.

## License

MIT