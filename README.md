# Chuk Virtual Shell

A powerful virtual shell with session management, perfect for AI agents and sandboxed execution environments.

## Overview

Chuk Virtual Shell provides a complete virtual shell environment with enterprise-grade features:

- **Session Management**: Stateful sessions with persistent working directory, environment, and command history
- **Virtual Filesystem**: Pluggable storage providers (memory, SQLite, S3)
- **Rich Command Set**: 50+ Unix-like commands including text processing, file operations, and system utilities
- **Bash-Compatible Operators**: Full support for &&, ||, ;, variable expansion, wildcards, and command substitution
- **AI Agent Ready**: Built for multi-step workflows with context preservation
- **Extensible Architecture**: Easy to add new commands and storage providers
- **Telnet Server**: Remote access capabilities for distributed systems

## Key Features

### 🔄 Session Management

Chuk Virtual Shell provides stateful sessions that maintain context across multiple commands - essential for AI agents and complex workflows:

```python
from chuk_virtual_shell.session import ShellSessionManager
from chuk_virtual_shell.shell_interpreter import ShellInterpreter

# Create session manager
manager = ShellSessionManager(shell_factory=lambda: ShellInterpreter())

# Create a persistent session
session_id = await manager.create_session()

# Commands share state
await manager.run_command(session_id, "cd /project")
await manager.run_command(session_id, "export API_KEY=secret")
await manager.run_command(session_id, "echo 'test' > file.txt")

# State persists: working dir, env vars, files
await manager.run_command(session_id, "pwd")  # Returns: /project
```

**Session Features:**
- **Persistent State**: Working directory, environment variables, and command history maintained across commands
- **Streaming Output**: Real-time output streaming with sequence IDs for proper ordering
- **Process Control**: Cancellation support and configurable timeouts (up to 10 minutes)
- **Multi-Session Isolation**: Run multiple isolated sessions concurrently
- **Backend Persistence**: Optional persistence with `chuk-sessions` library
- **PTY Support**: Full pseudo-terminal support for interactive applications

### 🎯 Built for AI Agents

Perfect for agentic coding workflows where context matters:

```python
# See examples/agentic_coding_demo.py for full example
agent = CodingAgent(session_manager)
await agent.start_project("api-service", "FastAPI")
await agent.execute_task(create_structure_task)
await agent.execute_task(implement_endpoints_task)
await agent.execute_task(add_tests_task)
# Context maintained throughout!
```

### 📁 Virtual Filesystem

Complete filesystem abstraction with multiple storage backends:
- **Memory**: Fast in-memory storage (default)
- **SQLite**: Persistent local storage
- **S3**: Cloud storage for distributed systems

### 🛠️ Rich Command Set

Over 50 Unix-like commands with full implementations:
- **File Operations**: cp, mv, rm, mkdir, touch, find, ls, cat, head, tail
- **Text Processing**: grep, sed, awk, sort, uniq, wc, cut, tr
- **System Utilities**: which, history, tree, timings, date, whoami, uname
- **Environment**: export, alias, source (.shellrc support), env
- **Shell Features**: Command chaining (&&, ||, ;), variable expansion ($VAR), wildcards (*, ?), command substitution ($()), tilde expansion (~)

## Installation

### Requirements

- Python 3.9 or higher (tested through Python 3.12)
- Works on Windows, macOS, and Linux
- No platform-specific dependencies

### Quick Start with uvx (Easiest)

Run directly without installation using uvx:

```bash
# Install uv if you haven't already
pip install uv

# Run the virtual shell directly
uvx chuk-virtual-shell

# Or use the shorter alias
uvx virtual-shell
```

### Install with uv (Recommended for Development)

```bash
# Clone the repository
git clone https://github.com/yourusername/pyodideshell.git
cd pyodideshell

# Install dependencies and run
uv run virtual-shell
```

### Install with pip

```bash
# Clone the repository
git clone https://github.com/yourusername/pyodideshell.git
cd pyodideshell

# Install in development mode
pip install -e .

# Run the shell
virtual-shell
```

### Install from PyPI (When Published)

```bash
# Using pip
pip install chuk-virtual-shell

# Using uv
uv pip install chuk-virtual-shell

# Then run
virtual-shell
```

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
    ├── filesystem/                  # File manipulation commands
    │   ├── __init__.py              # Package initialization
    │   ├── cat.py                   # Display file contents
    │   ├── cp.py                    # Copy files
    │   ├── df.py                    # Display filesystem usage
    │   ├── du.py                    # Display disk usage
    │   ├── echo.py                  # Echo text with redirection
    │   ├── find.py                  # Find files by criteria
    │   ├── mkdir.py                 # Make directory
    │   ├── more.py                  # Display file page by page
    │   ├── mv.py                    # Move/rename files
    │   ├── quota.py                 # Display disk quota
    │   ├── rm.py                    # Remove files
    │   ├── rmdir.py                 # Remove empty directories
    │   └── touch.py                 # Create empty file
    ├── text/                        # Text processing commands
    │   ├── __init__.py              # Package initialization
    │   ├── awk.py                   # Pattern scanning and processing
    │   ├── grep.py                  # Search text patterns
    │   ├── head.py                  # Display first lines of file
    │   ├── sed.py                   # Stream editor
    │   ├── sort.py                  # Sort lines
    │   ├── tail.py                  # Display last lines of file
    │   ├── uniq.py                  # Remove duplicate lines
    │   └── wc.py                    # Word, line, byte count
    ├── environment/                 # Environment commands
    │   ├── __init__.py              # Package initialization
    │   ├── env.py                   # Display environment variables
    │   └── export.py                # Set environment variables
    ├── system/                      # System commands
    │   ├── __init__.py              # Package initialization
    │   ├── clear.py                 # Clear screen
    │   ├── exit.py                  # Exit shell
    │   ├── help.py                  # Display help
    │   ├── python.py                # Python interpreter
    │   ├── script.py                # Execute shell scripts
    │   ├── sh.py                    # Execute shell commands
    │   ├── time.py                  # Time command execution
    │   ├── uptime.py                # Display system uptime
    │   └── whoami.py                # Display current user
    └── mcp/                         # MCP command support
        ├── __init__.py              # Package initialization
        ├── mcp_command_loader.py    # Dynamic MCP command loader
        ├── mcp_input_formatter.py   # Format inputs for MCP tools
        └── mcp_output_formatter.py  # Format MCP tool outputs
```

## Core Features

### Shell Operators and Expansion

The shell supports advanced bash-like operators and expansions for powerful command composition:

#### Command Chaining
```bash
# && - Execute next command only if previous succeeds
mkdir /tmp && cd /tmp && echo "Success"

# || - Execute next command only if previous fails
cd /nonexistent || echo "Directory not found"

# ; - Execute commands sequentially regardless of status
echo "First"; echo "Second"; echo "Third"
```

#### Variable Expansion
```bash
# Set and use environment variables
export NAME="World"
echo "Hello $NAME"                    # Output: Hello World
echo "Path: ${HOME}/documents"        # Output: Path: /home/user/documents

# Special variables
echo "Exit code: $?"                  # Last command's exit code
echo "Process ID: $$"                 # Shell process ID
echo "Current dir: $PWD"              # Current working directory
```

#### Wildcard/Glob Expansion
```bash
# * - Match any characters
ls *.txt                              # List all .txt files
rm /tmp/*.log                         # Remove all log files

# ? - Match single character
ls test?.py                           # Matches test1.py, test2.py, etc.

# Works with any command
cp *.txt /backup/                     # Copy all text files
grep "error" *.log                    # Search in all log files
```

#### Command Substitution
```bash
# Modern $() syntax
echo "Current time: $(date)"
export COUNT=$(ls | wc -l)

# Legacy backtick syntax
echo "User: `whoami`"
cd `cat /tmp/target_dir.txt`
```

#### Tilde and Path Expansion
```bash
# ~ expands to home directory
cd ~                                  # Go to home directory
ls ~/documents                        # List documents in home

# cd - returns to previous directory
cd /tmp
cd /home
cd -                                  # Returns to /tmp
```

### Shell Configuration (.shellrc)

The shell automatically loads configuration from `~/.shellrc` on startup, allowing you to:
- Set environment variables
- Define command aliases
- Enable features like command timing
- Run initialization commands

Example `.shellrc`:
```bash
# Environment variables
export EDITOR=nano
export MY_PROJECT=/home/user/projects

# Aliases
alias ll="ls -la"
alias ..="cd .."
alias grep="grep --color"

# Enable command timing
timings -e
```

### Command Aliases

Create shortcuts for frequently used commands:
```bash
alias ll="ls -la"          # Create alias
alias                      # List all aliases
unalias ll                 # Remove alias
```

### Command History

Track and search through your command history:
```bash
history                    # Show all history
history 10                 # Show last 10 commands
history grep              # Search for commands containing 'grep'
history -c                # Clear history
```

### Command Timing Statistics

Monitor command execution performance:
```bash
timings -e                # Enable timing
timings                   # Show statistics
timings -s avg            # Sort by average time
timings -c                # Clear statistics
timings -d                # Disable timing
```

### Directory Tree Visualization

Visualize directory structures with the `tree` command:
```bash
tree                      # Show current directory tree
tree -L 2                 # Limit depth to 2 levels
tree -d                   # Show directories only
tree -a                   # Include hidden files
```

### Command Location (which)

Find where commands are located:
```bash
which ls                  # Find the ls command
which -a python          # Find all python executables
```

### Modular Design

- Each component is isolated in its own module
- Commands are organized by category
- Filesystem components are separated by responsibility

### Cross-Platform Compatibility

PyodideShell is fully compatible across multiple operating systems:

- **Windows** - Full support with native path handling
- **macOS** - Complete functionality on Apple Silicon and Intel Macs  
- **Linux** - Tested on Ubuntu, Debian, and other distributions

The virtual filesystem uses forward slashes (`/`) for all path operations internally, ensuring consistent behavior across platforms. The CI/CD pipeline automatically tests on all three major operating systems with Python versions 3.9 through 3.12.

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

The shell includes 50+ commands organized into logical categories. For complete documentation with usage examples, options, and integration guides, see the [Command Documentation](docs/README.md).

- **[Navigation](docs/commands/navigation/README.md)**: ls, cd, pwd, tree
- **[File Management](docs/commands/filesystem/README.md)**: cat, cp, echo, find, mkdir, more, mv, rm, rmdir, touch, df, du, quota  
- **[Text Processing](docs/commands/text/README.md)**: awk, diff, grep, head, patch, sed, sort, tail, uniq, wc
- **[Environment](docs/commands/environment/README.md)**: env, export, alias, unalias
- **[System](docs/commands/system/README.md)**: clear, exit, help, history, python, script, sh, time, timings, uptime, which, whoami
- **[MCP Integration](docs/commands/mcp/README.md)**: Dynamically loaded MCP server commands

### Shell Redirection and Pipelines

The virtual shell supports full input/output redirection and pipelines, enabling powerful command composition:

#### Output Redirection
- `>` - Redirect output to a file (overwrites existing content)
- `>>` - Append output to a file

```bash
echo "Hello" > file.txt          # Write to file
echo "World" >> file.txt         # Append to file
ls -la > directory_list.txt      # Save directory listing
grep ERROR log.txt > errors.txt  # Save filtered output
```

#### Input Redirection
- `<` - Redirect input from a file

```bash
wc < file.txt                    # Count lines/words/bytes from file
sort < unsorted.txt              # Sort file contents
grep pattern < input.txt         # Search in redirected input
sed 's/old/new/g' < input.txt    # Process redirected input
```

#### Pipelines
- `|` - Pipe output of one command to input of another

```bash
cat file.txt | grep pattern      # Search in file output
ls -la | grep ".txt"             # Filter directory listing
cat data.csv | awk -F, '{print $1}' | sort  # Extract and sort CSV column
cat log.txt | grep ERROR | wc -l # Count error lines
```

#### Combined Redirection and Pipelines

```bash
# Sort numbers and save top 3
cat numbers.txt | sort -n | head -n 3 > top3.txt

# Process CSV and save results
awk -F, '{print $1,$3}' < data.csv | sort > names_roles.txt

# Filter logs and save errors
grep ERROR < app.log | sort | uniq > unique_errors.txt

# Complex pipeline with multiple stages
cat access.log | awk '{print $1}' | sort | uniq -c | sort -rn > ip_stats.txt
```

## Documentation

### Command Reference

Complete documentation for all shell commands is available in the [`docs/`](docs/) directory:

- **[Command Documentation Overview](docs/README.md)** - Summary of all command categories
- **[Command Taxonomy Analysis](docs/COMMAND_TAXONOMY.md)** - Detailed analysis of command organization
- **Individual Command Categories:**
  - **[Filesystem Commands](docs/commands/filesystem/README.md)** - File and directory operations
  - **[Navigation Commands](docs/commands/navigation/README.md)** - Directory navigation and listing
  - **[Text Processing Commands](docs/commands/text/README.md)** - Text manipulation and analysis
  - **[System Commands](docs/commands/system/README.md)** - Shell control and system utilities
  - **[Environment Commands](docs/commands/environment/README.md)** - Environment variable management
  - **[MCP Commands](docs/commands/mcp/README.md)** - Dynamic Model Context Protocol integration

Each command includes detailed documentation with:
- **Synopsis and description** - What the command does
- **Options and arguments** - All available flags and parameters
- **Usage examples** - Practical examples from basic to advanced
- **Error handling** - Common error conditions and solutions
- **Integration guides** - How commands work together
- **Implementation notes** - Technical details for advanced users

### Quick Command Reference

For a quick overview of available commands by category:

```bash
help                    # Show all available commands
help <command>          # Show detailed help for specific command
```

## Running Examples

The `examples/` directory contains several demonstration scripts showing the virtual shell's capabilities:

- `hello_world.sh` - Basic shell script demonstration
- `file_operations.sh` - File system operations
- `text_processing.sh` - Text processing commands (grep, awk, sed, etc.)
- `diff_patch_demo.sh` - Demonstrating diff and patch commands
- `redirection_pipeline_demo.sh` - Comprehensive redirection and pipeline examples
- `control_flow.sh` - Shell control flow structures
- `hello_world.py` - Python script execution
- `data_processing.py` - Python data processing
- `file_operations.py` - Python file operations
- `system_interaction.py` - Python system interaction

To run an example script:

```bash
# Method 1: As a command-line argument
uv run python -m chuk_virtual_shell.main examples/text_processing.sh

# Method 2: From within the interactive shell
uv run virtual-shell
$ script /path/to/example.sh

# Method 3: Using Python
from chuk_virtual_shell.shell_interpreter import ShellInterpreter
from chuk_virtual_shell.script_runner import ScriptRunner

shell = ShellInterpreter()
runner = ScriptRunner(shell)

# Copy script to virtual filesystem
with open('examples/text_processing.sh', 'r') as f:
    content = f.read()
shell.fs.write_file('/tmp/script.sh', content)

# Run it
result = runner.run_script('/tmp/script.sh')
print(result)
```

## Usage

### Interactive Mode with Default Provider

```bash
# Using uvx (no installation required)
uvx virtual-shell

# Using uv (if cloned locally)
uv run virtual-shell

# Using pip install
virtual-shell
```

### Interactive Mode with Specific Provider

```bash
# Use SQLite storage
uvx virtual-shell --fs-provider sqlite --fs-provider-args 'db_path=my_shell.db'

# Use S3 storage  
uvx virtual-shell --fs-provider s3 --fs-provider-args '{"bucket_name": "my-bucket", "prefix": "shell1"}'

# Or with uv run if cloned locally
uv run virtual-shell --fs-provider sqlite --fs-provider-args 'db_path=my_shell.db'
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

## Examples

### Session Management Demo

Run the session demo to see all session features in action:

```bash
uv run python examples/session_demo.py
```

This demonstrates:
- ✅ Stateful command execution with persistent context
- ✅ Working directory and environment persistence  
- ✅ Command history tracking
- ✅ Streaming output with sequence IDs for proper ordering
- ✅ Process cancellation and timeout support (configurable up to 10 minutes)
- ✅ Multi-session isolation with concurrent execution

#### Streaming Output Example

The shell provides real-time streaming output with sequence IDs to ensure proper ordering:

```python
# Stream output from long-running commands
async for chunk in manager.run_command(session_id, "ls -la /large_directory"):
    print(f"[Seq {chunk.sequence_id}] {chunk.data}")
    # Output arrives in real-time with sequence IDs
```

#### Cancellation and Timeout Support

Control long-running processes with cancellation and timeouts:

```python
# Set timeout for command execution (in milliseconds)
try:
    async for chunk in manager.run_command(
        session_id, 
        "python long_script.py",
        timeout_ms=5000  # 5 second timeout
    ):
        print(chunk.data)
except asyncio.TimeoutError:
    print("Command timed out")

# Cancel a running command
task = asyncio.create_task(
    manager.run_command(session_id, "sleep 100")
)
# ... later ...
task.cancel()  # Cancel the running command
```

### Agentic Coding Demo

See how AI agents can use sessions for complex development tasks:

```bash
uv run python examples/agentic_coding_demo.py
```

This shows:
- Building a complete FastAPI project step-by-step
- Maintaining context across 50+ commands
- Creating interdependent files and configurations
- Simulating real developer workflows

### Other Examples

```bash
# Basic shell operations
uv run python examples/hello_world.sh

# File operations with new commands
uv run python examples/file_operations.sh  

# All new features (aliases, history, tree, etc.)
uv run python examples/new_features_demo.sh
```

## Command Examples

### Basic Navigation and File Management
```
ls /                    # List files in root directory
cd /home/user           # Change directory
pwd                     # Show current directory
mkdir my_folder         # Create a directory
touch file.txt          # Create an empty file
echo "Hello" > file.txt # Create a file with content
cat file.txt            # Display file content
cp file.txt backup.txt  # Copy a file
mv old.txt new.txt      # Move/rename a file
rm file.txt             # Remove a file
find . -name "*.txt"    # Find files by pattern
```

### Text Processing Commands
```
# grep - Search for patterns in files
grep "pattern" file.txt         # Search for pattern
grep -i "pattern" file.txt      # Case-insensitive search
grep -n "pattern" file.txt      # Show line numbers
grep -c "pattern" file.txt      # Count matches
grep -v "pattern" file.txt      # Invert match (lines without pattern)

# awk - Pattern scanning and processing
awk '{print $1}' file.txt       # Print first field
awk -F: '{print $2}' file.txt   # Use : as field separator
awk 'NR==2' file.txt            # Print second line
awk '{sum+=$1} END {print sum}' # Sum first column

# sed - Stream editor for text transformation
sed 's/old/new/' file.txt       # Replace first occurrence
sed 's/old/new/g' file.txt      # Replace all occurrences
sed 's/old/new/i' file.txt      # Case-insensitive replacement
sed '1d' file.txt               # Delete first line
sed '$d' file.txt               # Delete last line
sed '2,4d' file.txt             # Delete lines 2-4
sed '/pattern/d' file.txt       # Delete lines matching pattern
sed -i 's/old/new/g' file.txt   # Edit file in-place
sed -n '/pattern/p' file.txt    # Print only matching lines
sed -E 's/[0-9]+/NUM/g' file    # Extended regex support

# head/tail - Display beginning/end of files
head file.txt                   # Show first 10 lines
head -n 5 file.txt              # Show first 5 lines
tail file.txt                   # Show last 10 lines
tail -n 5 file.txt              # Show last 5 lines
tail -n +5 file.txt             # Show from line 5 to end

# sort - Sort lines in files
sort file.txt                   # Sort alphabetically
sort -r file.txt                # Reverse sort
sort -n file.txt                # Numeric sort
sort -u file.txt                # Sort and remove duplicates

# uniq - Remove duplicate lines
uniq file.txt                   # Remove consecutive duplicates
uniq -c file.txt                # Count occurrences
uniq -d file.txt                # Show only duplicates
uniq -u file.txt                # Show only unique lines

# wc - Word, line, and byte count
wc file.txt                     # Show lines, words, bytes
wc -l file.txt                  # Count lines only
wc -w file.txt                  # Count words only
wc -c file.txt                  # Count bytes only

# diff - Compare files line by line
diff file1.txt file2.txt        # Show differences
diff -u old.txt new.txt         # Unified diff format
diff -c old.txt new.txt         # Context diff format
diff -i file1 file2             # Case-insensitive comparison
diff -w file1 file2             # Ignore all whitespace
diff -b file1 file2             # Ignore whitespace changes
diff -B file1 file2             # Ignore blank lines
diff -q file1 file2             # Brief - just report if different
diff --side-by-side f1 f2       # Side-by-side comparison

# patch - Apply diff patches to files
patch < changes.patch           # Apply patch from stdin
patch -i changes.patch file.txt # Apply patch from file
patch -R < changes.patch        # Reverse a patch
patch -b < changes.patch        # Create backup (.orig)
patch -o output.txt < patch     # Output to different file
patch --dry-run < test.patch    # Test without applying
patch -p1 < patch               # Strip 1 path component
```

### Environment and System Commands
```
env                     # Show environment variables
export VAR=value        # Set environment variable
whoami                  # Display current user
uptime                  # Show system uptime
time command            # Time command execution
clear                   # Clear screen
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
from chuk_virtual_shell.provider_base import StorageProvider
from chuk_virtual_shell.node_info import FSNodeInfo

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
from chuk_virtual_shell.providers.custom import CustomStorageProvider
register_provider("custom", CustomStorageProvider)
```

## Security Considerations

- PyodideShell runs with no access to the host system by default (memory provider)
- Commands are limited to predefined functionality
- Provider access can be controlled through appropriate credentials
- Telnet server can be configured with access controls

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/chuk-virtual-shell.git
cd chuk-virtual-shell

# Install development dependencies
make install

# Run tests
make test

# Run with coverage
make coverage

# Run linting and formatting
make lint
make format
```

### Building and Publishing

#### Prerequisites

1. Create a PyPI account at https://pypi.org
2. Generate an API token at https://pypi.org/manage/account/token/
3. Configure twine with your PyPI credentials:

```bash
# Option 1: Use keyring (recommended)
pip install keyring
keyring set https://upload.pypi.org/legacy/ __token__
# Enter your PyPI token when prompted

# Option 2: Create ~/.pypirc file
cat > ~/.pypirc << EOF
[pypi]
username = __token__
password = pypi-your-token-here
EOF
chmod 600 ~/.pypirc
```

#### Publishing Process

```bash
# Check current version
make version

# Bump version as needed
make bump-patch  # 0.1.1 -> 0.1.2
make bump-minor  # 0.1.1 -> 0.2.0
make bump-major  # 0.1.1 -> 1.0.0

# Build the package
make build

# Test on TestPyPI first (optional)
make publish-test

# Publish to PyPI
make publish

# Or use the release shortcuts
make release-patch  # Bump, test, and build
make release-minor  # Bump, test, and build
make release-major  # Bump, test, and build
```

### Makefile Targets

Run `make help` to see all available targets:

- **Testing**: `test`, `coverage`, `coverage-html`
- **Code Quality**: `lint`, `format`, `typecheck`
- **Building**: `build`, `check-build`, `clean`
- **Publishing**: `publish`, `publish-test`
- **Version Management**: `version`, `bump-patch`, `bump-minor`, `bump-major`
- **Release Workflow**: `release-patch`, `release-minor`, `release-major`

## Future Enhancements

- User authentication and permissions system
- Multi-user support with session isolation
- Command history and tab completion
- More advanced file operations
- Additional storage providers (Redis, IndexedDB, etc.)
- Provider data migration tools