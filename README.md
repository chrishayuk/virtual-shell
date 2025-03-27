# PyodideShell

A modular virtual shell with an in-memory filesystem that can be exposed as a telnet server using Pyodide.

## Overview

PyodideShell provides a complete virtual shell environment that runs entirely in memory, making it secure and sandboxed. It includes:

- A fully functional virtual filesystem
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
│   └── fs_manager.py                # Filesystem manager
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

### Virtual Filesystem

- Hierarchical directory structure with files and folders
- Support for absolute and relative paths
- Common operations: create, read, write, delete

### Command System

All commands are implemented as separate classes that extend the `ShellCommand` base class, making it easy to add new commands.

### Available Commands

- **Navigation**: ls, cd, pwd
- **File Management**: cat, echo, touch, mkdir, rm, rmdir
- **Environment**: env, export
- **System**: help, exit, clear

## Usage

### Interactive Mode

```bash
python main.py
```

### Telnet Server Mode

```bash
python main.py --telnet
```

Then connect using any telnet client:

```bash
telnet localhost 23
```

### Pyodide Mode

When running in a browser environment with Pyodide, the shell operates in interactive mode:

```python
import main
main.run_interactive_shell()
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

## Extending PyodideShell

### Adding New Commands

1. Create a new Python file in the appropriate category subfolder under `commands/`
2. Implement a class that extends `ShellCommand`
3. Register the command in the `ShellInterpreter._register_commands()` method

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

Then add to `shell_interpreter.py`:

```python
from commands.file.example import ExampleCommand

# In the _register_commands method:
self._register_command(ExampleCommand(self))
```

## Security Considerations

- PyodideShell runs entirely in memory with no access to the host system
- Commands are limited to predefined functionality
- Telnet server can be configured with access controls

## Future Enhancements

- User authentication and permissions system
- Multi-user support with session isolation
- Command history and tab completion
- More advanced file operations