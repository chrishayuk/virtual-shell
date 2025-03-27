# PyodideShell

A modular virtual shell with a pluggable storage architecture that can be exposed as a telnet server using Pyodide.

## Overview

PyodideShell provides a complete virtual shell environment with flexible storage options, making it secure, sandboxed, and adaptable to various use cases. It includes:

- A fully functional virtual filesystem with pluggable storage providers
- A command-line interface with common Unix commands
- Telnet server capabilities for remote access

## Project Structure

The project is organized in a highly modular way with a clear separation of concerns:

```
pyodideshell/
├── main.py                          # Main entry point
├── shell_interpreter.py             # Core shell interpreter
├── telnet_server.py                 # Telnet server implementation
├── command_base.py                  # Base command class
├── filesystem/                      # Filesystem module
│   ├── __init__.py                  # Package initialization
│   ├── node_base.py                 # Base node class
│   ├── directory.py                 # Directory implementation
│   ├── file.py                      # File implementation
│   ├── fs_manager.py                # Filesystem manager
│   ├── node_info.py                 # Node metadata for providers
│   ├── provider_base.py             # Abstract provider interface
│   └── providers/                   # Storage providers
│       ├── __init__.py              # Provider registry
│       ├── memory.py                # In-memory provider
│       ├── sqlite.py                # SQLite provider
│       └── s3.py                    # S3 storage provider
└── commands/                        # Command modules
    ├── __init__.py                  # Command aggregation
    ├── navigation/                  # Navigation commands
    │   ├── __init__.py              # Package initialization
    │   ├── ls.py                    # List directory contents
    │   ├── cd.py                    # Change directory
    │   └── pwd.py                   # Print working directory
    ├── file/                        # File manipulation commands
    │   ├── __init__.py              # Package initialization
    │   ├── mkdir.py                 # Make directory
    │   ├── touch.py                 # Create empty file
    │   ├── cat.py                   # Display file contents
    │   ├── echo.py                  # Echo text with redirection
    │   ├── rm.py                    # Remove files
    │   └── rmdir.py                 # Remove empty directories
    ├── environment/                 # Environment commands
    │   ├── __init__.py              # Package initialization
    │   ├── env.py                   # Display environment variables
    │   └── export.py                # Set environment variables
    └── system/                      # System commands
        ├── __init__.py              # Package initialization
        ├── clear.py                 # Clear screen
        ├── exit.py                  # Exit shell
        └── help.py                  # Display help
```

## Core Features

### Modular Design

- Each component is isolated in its own module
- Commands are organized by category
- Filesystem components are separated by responsibility

### Pluggable Storage Architecture

The filesystem now supports multiple storage backends through a provider-based architecture:

- **Memory Provider**: Fast, in-memory storage (default)
- **SQLite Provider**: Persistent storage using SQLite database
- **S3 Provider**: Cloud storage using Amazon S3 or compatible services

You can easily switch between providers or create custom ones to suit your needs.

### Virtual Filesystem

- Hierarchical directory structure with files and folders
- Support for absolute and relative paths
- Common operations: create, read, write, delete
- Consistent API regardless of the underlying storage

### Command System

All commands are implemented as separate classes that extend the `ShellCommand` base class, making it easy to add new commands.

### Available Commands

- **Navigation**: ls, cd, pwd
- **File Management**: cat, echo, touch, mkdir, rm, rmdir
- **Environment**: env, export
- **System**: help, exit, clear

## Usage

### Interactive Mode with Default Provider

```bash
uv run virtual-shell
```

### Interactive Mode with Specific Provider

```bash
# Use SQLite storage
uv run virtual-shell --fs-provider sqlite --fs-provider-args 'db_path=my_shell.db'

# Use S3 storage
uv run virtual-shell --fs-provider s3 --fs-provider-args '{"bucket_name": "my-bucket", "prefix": "shell1"}'
```

### List Available Providers

```bash
python main.py --fs-provider list
```

### Telnet Server Mode

```bash
# With default memory provider
python main.py --telnet

# With SQLite provider
python main.py --telnet --fs-provider sqlite --fs-provider-args 'db_path=telnet_shell.db'
```

Then connect using any telnet client:

```bash
telnet localhost 8023
```

### Script Execution

```bash
# Run a script with specific provider
python main.py --script my_script.sh --fs-provider sqlite --fs-provider-args 'db_path=my_shell.db'
```

### Pyodide Mode

When running in a browser environment with Pyodide, the shell operates in interactive mode:

```python
import main
main.run_interactive_shell("sqlite", {"db_path": ":memory:"})  # With provider selection
```

## Command Examples

```
ls /                    # List files in root directory
cd /home/user           # Change directory
pwd                     # Show current directory
mkdir my_folder         # Create a directory
touch file.txt          # Create an empty file
echo "Hello" > file.txt # Create a file with content
cat file.txt            # Display file content
rm file.txt             # Remove a file
env                     # Show environment variables
export VAR=value        # Set environment variable
help ls                 # Show help for a command
exit                    # Exit the shell
```

## Storage Providers

### Memory Provider

In-memory storage that is fast but does not persist data. Ideal for temporary shells:

```bash
python main.py --fs-provider memory
```

### SQLite Provider

Stores the filesystem in a SQLite database for persistence:

```bash
# Use file-based database
python main.py --fs-provider sqlite --fs-provider-args 'db_path=my_shell.db'

# Use in-memory database
python main.py --fs-provider sqlite --fs-provider-args '{"db_path": ":memory:"}'
```

### S3 Provider

Stores the filesystem in an Amazon S3 bucket or compatible service:

```bash
python main.py --fs-provider s3 --fs-provider-args '{
  "bucket_name": "my-shell-bucket",
  "prefix": "user1",
  "region_name": "us-west-2"
}'
```

## Extending PyodideShell

### Adding New Commands

1. Create a new Python file in the appropriate category subfolder under `commands/`
2. Implement a class that extends `ShellCommand`
3. Register the command in the `commands/__init__.py` file

Example:

```python
# commands/file/example.py
from command_base import ShellCommand

class ExampleCommand(ShellCommand):
    name = "example"
    help_text = "example - Description of what it does\nUsage: example [args]"
    
    def execute(self, args):
        # Command implementation
        return "Example command output"
```

### Creating Custom Storage Providers

1. Create a new Python file in the `filesystem/providers/` directory
2. Implement a class that extends `StorageProvider`
3. Register the provider in the `filesystem/providers/__init__.py` file

Example:

```python
# filesystem/providers/custom.py
from virtual_shell.filesystem.provider_base import StorageProvider
from virtual_shell.filesystem.node_info import FSNodeInfo

class CustomStorageProvider(StorageProvider):
    """Custom storage provider implementation"""
    
    def __init__(self, custom_arg=None):
        self.custom_arg = custom_arg
        # Initialize your storage here
        
    def initialize(self) -> bool:
        # Initialize your storage backend
        return True
        
    # Implement other required methods...
```

Then register in `providers/__init__.py`:

```python
from virtual_shell.filesystem.providers.custom import CustomStorageProvider
register_provider("custom", CustomStorageProvider)
```

## Security Considerations

- PyodideShell runs with no access to the host system by default (memory provider)
- Commands are limited to predefined functionality
- Provider access can be controlled through appropriate credentials
- Telnet server can be configured with access controls

## Future Enhancements

- User authentication and permissions system
- Multi-user support with session isolation
- Command history and tab completion
- More advanced file operations
- Additional storage providers (Redis, IndexedDB, etc.)
- Provider data migration tools