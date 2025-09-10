# Virtual Shell Example Scripts

This directory contains example scripts demonstrating the capabilities of the virtual shell environment.

## Bash Scripts (.sh)

- `hello_world.sh` - Basic hello world script
- `file_operations.sh` - Demonstrates file operations in virtual FS
- `text_processing.sh` - Shows text processing with grep, sed, awk
- `control_flow.sh` - Examples of if statements, loops, and functions

## Python Scripts (.py)

- `hello_world.py` - Basic Python hello world
- `file_operations.py` - File I/O with virtual filesystem
- `data_processing.py` - Process data files using Python
- `system_interaction.py` - Interact with virtual OS and subprocess

## Usage

These scripts can be executed within the virtual shell environment:

```bash
# Execute bash script
sh examples/hello_world.sh

# Execute Python script  
python examples/hello_world.py

# Or make executable and run directly (if supported)
./examples/file_operations.sh
```

## Features Demonstrated

- **Virtual Filesystem**: All file operations work within the virtual FS
- **Environment Variables**: Scripts can read and set environment variables
- **Command Execution**: Scripts can execute other virtual shell commands
- **Piping and Redirection**: Full support for pipes and redirects
- **Text Processing**: grep, sed, awk, sort, uniq, etc.
- **Python Integration**: Full Python environment with virtual FS access