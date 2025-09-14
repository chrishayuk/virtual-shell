# Chuk Virtual Shell 🐚

A powerful virtual shell environment with MCP (Model Context Protocol) integration, perfect for AI agents and sandboxed execution environments.

[![Tests](https://img.shields.io/badge/tests-1420%20passing-green)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-85%25-yellow)](tests/)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](pyproject.toml)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

## 🌟 Overview

Chuk Virtual Shell provides a complete POSIX-like virtual shell environment designed specifically for AI agents and automation:

- **🤖 MCP Server Integration**: Full Model Context Protocol support for AI agents like Claude, Cline, and Aider
- **🔄 Persistent Sessions**: Stateful command execution with maintained context across interactions
- **🔒 User Isolation**: Complete session and task isolation between users
- **📁 Virtual Filesystem**: Pluggable storage providers (memory, SQLite, S3)
- **🎯 50+ Built-in Commands**: Comprehensive Unix-like command set
- **⚡ Advanced I/O**: Full pipeline, redirection, and here-doc support
- **🏖️ Pre-configured Sandboxes**: Ready-to-use secure environments
- **🔌 Extensible Architecture**: Easy to add custom commands and storage providers

## 🚀 Quick Start

### Requirements

- Python 3.11 or higher (tested through Python 3.12)
- Works on Windows, macOS, and Linux
- MCP server functionality requires Unix-like OS (Linux/macOS) due to uvloop dependency

### Installation

```bash
# Install with uv (recommended)
uv pip install chuk-virtual-shell

# Or with pip
pip install chuk-virtual-shell

# For MCP server functionality, install optional dependency (Unix/macOS only)
uv pip install chuk-virtual-shell[mcp-server]
# Or with pip
pip install chuk-virtual-shell[mcp-server]

# Note: MCP server requires Unix-like OS (Linux/macOS) due to uvloop dependency
# Windows users can use WSL or run the shell without MCP server features

# For development (if you cloned the repo)
cd chuk-virtual-shell
uv sync

# Or run directly without installation using uvx
uvx chuk-virtual-shell
```

### Basic Usage

```bash
# Start interactive shell
uv run chuk-virtual-shell

# Use a pre-configured sandbox (recommended)
uv run chuk-virtual-shell --sandbox ai_sandbox

# Start MCP server for AI agents
uv run python -m chuk_virtual_shell.mcp_server

# Run with different storage backends
uv run chuk-virtual-shell --fs-provider sqlite --fs-provider-args 'db_path=my_shell.db'

# Run scripts
uv run chuk-virtual-shell examples/hello_world.sh

# Start telnet server for remote access
uv run chuk-virtual-shell --telnet --port 8023
```

### MCP Integration for AI Agents

```python
# See examples/mcp_client_demo.py for complete example
from examples.mcp_client_demo import SimpleMCPClient

client = SimpleMCPClient()
await client.start_server()

# Create isolated session
result = await client.call_tool("bash", {"command": "pwd"})
session_id = result["session_id"]

# Commands share state within session
await client.call_tool("bash", {
    "command": "export PROJECT=MyApp && mkdir -p /project/src",
    "session_id": session_id
})

# State persists across commands
result = await client.call_tool("bash", {
    "command": "echo $PROJECT && ls /project",
    "session_id": session_id
})
# Output: MyApp\nsrc
```

### Try the Interactive Demo

```bash
# Run the complete MCP demonstration
uv run examples/mcp_client_demo.py

# Expected output shows:
# ✅ User isolation and session management
# ✅ State persistence across commands  
# ✅ Background task execution
# ✅ Multiple concurrent sessions
# ✅ Complex multi-step workflows
```

## 📚 Key Features

### 🤖 MCP Server Capabilities

Full Model Context Protocol implementation with user isolation:

```python
# Available MCP tools:
- bash           # Execute shell commands with session persistence
- whoami         # Get user context and session info
- list_sessions  # List all active sessions for current user
- get_session_state  # Get session details (pwd, env, lifetime)
- destroy_session    # Clean up sessions
- get_task_output    # Get background task results
- cancel_task        # Cancel running background tasks
```

**User Isolation Features:**
- Each user gets isolated sessions and tasks
- Sessions maintain state (PWD, env vars, files) between commands
- Background task execution with streaming output
- Automatic session cleanup on disconnect
- Per-user resource limits and quotas

**Advanced Shell Features via MCP:**
- Full stderr redirection (`2>`, `2>>`, `2>&1`)
- Combined output redirection (`&>`, `&>>`)
- Complex pipelines and command chaining
- Quoted filename support with spaces
- All 50+ built-in shell commands available

### 🔄 Session Management

Stateful sessions that maintain context - essential for AI workflows:

```python
from chuk_virtual_shell.session import ShellSessionManager
from chuk_virtual_shell.shell_interpreter import ShellInterpreter

# Create session manager
manager = ShellSessionManager(shell_factory=lambda: ShellInterpreter())

# Create persistent session
session_id = await manager.create_session()

# Commands share state
await manager.run_command(session_id, "cd /project")
await manager.run_command(session_id, "export API_KEY=secret")
await manager.run_command(session_id, "echo 'data' > file.txt")

# State persists
result = await manager.run_command(session_id, "pwd && echo $API_KEY && cat file.txt")
# Output: /project\nsecret\ndata
```

### 📋 Advanced I/O Redirection

Comprehensive redirection support (see [docs/features/redirection.md](docs/features/redirection.md)):

```bash
# Output redirection
echo "Hello" > output.txt
echo "World" >> output.txt

# Input redirection  
sort < unsorted.txt > sorted.txt

# Pipelines
cat data.txt | grep "pattern" | sort | uniq > results.txt

# Here-documents (in scripts)
cat << EOF > config.yaml
server: localhost
port: 8080
EOF

# Advanced redirection
command 2> errors.txt          # Stderr redirection
command 2>&1                    # Merge stderr to stdout
command &> all_output.txt       # Combined output
command 2>> errors.txt         # Append stderr
command &>> all.txt            # Append combined output
```

### 🎭 Quoting and Escaping

Full quoting semantics (see [docs/features/quoting.md](docs/features/quoting.md)):

```bash
# Single quotes - literal
echo 'Hello $USER'              # Output: Hello $USER

# Double quotes - with expansion
echo "Hello $USER"              # Output: Hello alice

# Backslash escaping
echo "Price: \$100"             # Output: Price: $100
echo file\ with\ spaces.txt     # Output: file with spaces.txt

# Mixed quoting
echo "It's"' a nice day'        # Output: It's a nice day
```

### 🏖️ Pre-configured Sandboxes

Ready-to-use secure environments:

```yaml
# config/ai_sandbox.yaml - Restricted AI agent environment
environment:
  HOME: /sandbox
  USER: ai
  PATH: /bin
  SANDBOX_MODE: restricted

filesystem:
  provider: memory
  
initialization:
  - mkdir -p /sandbox/workspace
  - echo "AI Sandbox Ready" > /sandbox/README.txt
```

Available sandboxes:
- `ai_sandbox` - Restricted environment for AI code execution
- `default` - Balanced development environment  
- `readonly` - Read-only exploration
- `e2b` - E2B.dev compatible environment
- `tigris` - Tigris Data S3-compatible storage

## 📊 Feature Matrix

| Feature Category | Feature | Status | Notes |
|-----------------|---------|--------|-------|
| **MCP Integration** | MCP Server | ✅ | Full protocol support |
| | User Isolation | ✅ | Session & task isolation |
| | Background Tasks | ✅ | Async execution with streaming |
| | Session Persistence | ✅ | State maintained across commands |
| **I/O Redirection** | Basic pipes (`\|`) | ✅ | Multi-stage pipelines |
| | Output redirect (`>`, `>>`) | ✅ | Write and append |
| | Input redirect (`<`) | ✅ | Read from files |
| | Stderr redirect (`2>`, `2>>`) | ✅ | Full stderr redirection |
| | Combined (`2>&1`, `&>`, `&>>`) | ✅ | Merge stdout/stderr |
| | Here-docs (`<<`) | ⚡ | Works in script runner |
| **Shell Operators** | Chaining (`&&`, `\|\|`, `;`) | ✅ | Full conditional execution |
| | Command substitution (`$()`) | ✅ | Both syntaxes supported |
| | Variable expansion | ✅ | `$VAR`, `${VAR}` |
| | Glob patterns (`*`, `?`) | ✅ | Full support |
| **Control Flow** | if/then/else | ✅ | Conditional logic |
| | for/while loops | ✅ | Full iteration support |
| | case statements | ✅ | Pattern matching |
| | Functions | ❌ | Planned |
| **Commands** | File operations | ✅ | cp, mv, rm, mkdir, touch |
| | Text processing | ✅ | grep, sed, awk, sort, uniq |
| | File viewing | ✅ | cat, head, tail, more |
| | System utilities | ✅ | find, which, tree, date |

**Legend:**
- ✅ **Full Support**: Complete implementation with tests
- ⚡ **Partial Support**: Works with limitations
- 🚧 **In Development**: Parser/infrastructure ready
- ❌ **Not Supported**: Not yet implemented

## 🛠️ Architecture

```
┌─────────────────────────────────────────────────┐
│           MCP Client (AI Agent)                 │
└─────────────────┬───────────────────────────────┘
                  │ MCP Protocol
┌─────────────────▼───────────────────────────────┐
│           MCP Server (chuk_virtual_shell)       │
│  ┌──────────────────────────────────────────┐  │
│  │  User Isolation & Session Management     │  │
│  └──────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────┐  │
│  │  Shell Interpreter & Command Executor    │  │
│  └──────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────┐  │
│  │  Virtual Filesystem (Memory/SQLite/S3)   │  │
│  └──────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
```

## 🎯 Shell Operators and Features

### Command Chaining
```bash
# && - Execute next command only if previous succeeds
mkdir /tmp && cd /tmp && echo "Success"

# || - Execute next command only if previous fails
cd /nonexistent || echo "Directory not found"

# ; - Execute commands sequentially regardless of status
echo "First"; echo "Second"; echo "Third"
```

### Variable Expansion
```bash
# Set and use environment variables
export NAME="World"
echo "Hello $NAME"                    # Output: Hello World
echo "Path: ${HOME}/documents"        # Output: Path: /home/user/documents

# Special variables
echo "Exit code: $?"                  # Last command's exit code
echo "Current dir: $PWD"              # Current working directory
```

### Wildcard/Glob Expansion
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

### Command Substitution
```bash
# Modern $() syntax
echo "Current time: $(date)"
export COUNT=$(ls | wc -l)

# Legacy backtick syntax
echo "User: `whoami`"
```

### I/O Redirection and Pipelines
```bash
# Output redirection
echo "Hello" > file.txt               # Write to file
echo "World" >> file.txt              # Append to file

# Input redirection
wc < file.txt                         # Read from file

# Stderr redirection
command 2> errors.txt                 # Redirect stderr
command 2>&1                          # Merge stderr to stdout
command &> all_output.txt             # Combined output

# Pipelines
cat file.txt | grep pattern           # Basic pipe
cat data.csv | awk -F, '{print $1}' | sort  # Multi-stage pipeline
```

### Shell Configuration (.shellrc)
```bash
# The shell automatically loads ~/.shellrc on startup
cat > ~/.shellrc << 'EOF'
# Environment variables
export EDITOR=nano
export PATH=/usr/local/bin:/usr/bin:/bin

# Aliases
alias ll="ls -la"
alias ..="cd .."
alias grep="grep -i"

# Enable command timing
timings -e
EOF
```

## 📝 Command Examples

### Basic Navigation and File Management
```bash
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
tree                    # Show directory structure
```

### Text Processing Commands
```bash
# grep - Search for patterns in files
grep "pattern" file.txt         # Search for pattern
grep -i "pattern" file.txt      # Case-insensitive search
grep -n "pattern" file.txt      # Show line numbers
grep -v "pattern" file.txt      # Invert match

# awk - Pattern scanning and processing
awk '{print $1}' file.txt       # Print first field
awk -F: '{print $2}' file.txt   # Use : as field separator
awk '{sum+=$1} END {print sum}' # Sum first column

# sed - Stream editor
sed 's/old/new/' file.txt       # Replace first occurrence
sed 's/old/new/g' file.txt      # Replace all occurrences
sed -i 's/old/new/g' file.txt   # Edit file in-place

# sort and uniq
sort file.txt                   # Sort lines
sort -n numbers.txt             # Numeric sort
uniq file.txt                   # Remove duplicates
sort file.txt | uniq -c         # Count occurrences

# head/tail
head -n 5 file.txt              # First 5 lines
tail -n 5 file.txt              # Last 5 lines
```

### Environment and System Commands
```bash
env                     # Show environment variables
export VAR=value        # Set environment variable
alias ll="ls -la"       # Create alias
history                 # Show command history
which command           # Find command location
whoami                  # Display current user
date                    # Show current date/time
timings                 # Show command execution stats
```

## 🗂️ Storage Providers

### Memory Provider (Default)
In-memory storage that is fast but does not persist data:
```bash
uv run chuk-virtual-shell --fs-provider memory
```

### SQLite Provider
Stores the filesystem in a SQLite database for persistence:
```bash
# File-based database
uv run chuk-virtual-shell --fs-provider sqlite --fs-provider-args 'db_path=my_shell.db'

# In-memory database
uv run chuk-virtual-shell --fs-provider sqlite --fs-provider-args 'db_path=:memory:'
```

### S3 Provider
Stores the filesystem in Amazon S3 or compatible service:
```bash
# Set up credentials in .env file
cat > .env << EOF
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1
S3_BUCKET_NAME=my-shell-bucket
EOF

# Use S3 storage (automatically loads .env)
uv run chuk-virtual-shell --fs-provider s3

# Or specify bucket explicitly
uv run chuk-virtual-shell --fs-provider s3 --fs-provider-args '{"bucket_name": "my-bucket"}'
```

## 📋 Running Examples

The `examples/` directory contains demonstration scripts showing the virtual shell's capabilities:

### MCP Client Demo
```bash
# Run the complete MCP demonstration
uv run examples/mcp_client_demo.py

# Shows:
# ✅ User isolation and session management
# ✅ State persistence across commands  
# ✅ Background task execution
# ✅ Multiple concurrent sessions
# ✅ Complex multi-step workflows
```

### Shell Script Examples
```bash
# Basic shell operations
uv run chuk-virtual-shell examples/hello_world.sh

# File operations and manipulation
uv run chuk-virtual-shell examples/file_operations.sh

# Text processing with grep, awk, sed
uv run chuk-virtual-shell examples/text_processing.sh

# Advanced redirection and pipelines
uv run chuk-virtual-shell examples/redirection_pipeline_demo.sh

# Shell control flow (if/for/while/case)
uv run chuk-virtual-shell examples/control_flow.sh

# Working demo of all features
uv run chuk-virtual-shell examples/working_demo.sh
```

### Session Management Demo
```bash
# Run session demo to see persistence features
uv run python examples/session_demo.py

# Demonstrates:
# - Stateful command execution
# - Working directory persistence
# - Environment variable persistence
# - Command history tracking
# - Multi-session isolation
```

### Running Scripts in Different Ways
```bash
# Method 1: As command-line argument
uv run chuk-virtual-shell examples/text_processing.sh

# Method 2: From within interactive shell
uv run chuk-virtual-shell
$ script examples/hello_world.sh

# Method 3: With specific sandbox
uv run chuk-virtual-shell --sandbox ai_sandbox examples/secure_script.sh

# Method 4: With persistent storage
uv run chuk-virtual-shell --fs-provider sqlite --fs-provider-args 'db_path=session.db' examples/data_processing.sh
```

## 📖 Documentation

- [POSIX Compatibility Matrix](docs/POSIX_COMPATIBILITY.md) - Detailed POSIX.1-2017 compliance
- [MCP Integration Guide](docs/mcp_integration.md)
- [Session Management](docs/session_management.md)
- [Redirection Guide](docs/features/redirection.md)
- [Quoting Guide](docs/features/quoting.md)
- [Command Reference](docs/commands/)
- [Sandbox Configuration](docs/sandbox_configuration.md)
- [API Documentation](docs/api/)

## 🧪 Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=chuk_virtual_shell

# Run specific test categories
uv run pytest tests/test_mcp_server.py
uv run pytest tests/test_quoting_comprehensive.py
uv run pytest tests/test_advanced_redirection.py
```

Current test status: **1398 tests passing** (9 skipped)

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/chrishayuk/chuk-virtual-shell.git
cd chuk-virtual-shell

# Install with dev dependencies
uv pip install -e ".[dev]"

# Run tests
uv run pytest

# Run linting
uv run ruff check .

# Run type checking
uv run mypy chuk_virtual_shell
```

## 🔧 Troubleshooting

### MCP Server Issues

**Problem**: `ModuleNotFoundError: No module named 'chuk_mcp_server'`

**Solution**: Install the MCP server optional dependency:
```bash
uv pip install chuk-virtual-shell[mcp-server]
# or with pip
pip install chuk-virtual-shell[mcp-server]
```

**Problem**: `RuntimeError: uvloop does not support Windows at the moment`

**Solution**: MCP server functionality requires Unix-like OS due to uvloop dependency:
- **Linux/macOS**: Install normally with `[mcp-server]` extra
- **Windows**: Use WSL (Windows Subsystem for Linux) or run without MCP features
- **Alternative**: Use the shell directly without MCP server integration

**Problem**: MCP demo fails with JSON decode error

**Solution**: Ensure the MCP server dependency is installed and the server is accessible:
```bash
# Test MCP server directly
uv run python -m chuk_virtual_shell.mcp_server

# Run the interactive demo
uv run examples/mcp_client_demo.py
```

### General Issues

**Problem**: Command not found errors

**Solution**: Ensure you're using the correct command syntax. Check available commands:
```bash
# In interactive mode
help

# Check specific command help
help ls
```

**Problem**: File permission errors

**Solution**: The virtual filesystem has simulated permissions. Use appropriate commands:
```bash
# Create directories with proper paths
mkdir -p /path/to/directory

# Check current working directory
pwd
```

## 🔧 Extending Chuk Virtual Shell

### Adding New Commands

1. Create a new Python file in the appropriate category subfolder under `chuk_virtual_shell/commands/`
2. Implement a class that extends `ShellCommand`
3. Register the command in the module's `__init__.py`

Example:
```python
# chuk_virtual_shell/commands/system/example.py
from chuk_virtual_shell.commands.command_base import ShellCommand

class ExampleCommand(ShellCommand):
    name = "example"
    help_text = "example - Description of what it does\nUsage: example [args]"
    
    def execute(self, args):
        # Command implementation
        return "Example command output"
```

### Creating Custom Storage Providers

1. Create a new Python file in the `chuk_virtual_fs/providers/` directory
2. Implement a class that extends `StorageProvider`
3. Register the provider in the providers registry

Example:
```python
# chuk_virtual_fs/providers/custom.py
from chuk_virtual_fs.provider_base import StorageProvider

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

### Custom Sandbox Configurations

Create custom sandbox configurations by creating YAML files:
```yaml
# config/my_sandbox.yaml
environment:
  HOME: /my_home
  USER: myuser
  PATH: /usr/local/bin:/usr/bin:/bin
  CUSTOM_VAR: custom_value

filesystem:
  provider: memory

security_policy:
  allowed_paths:
    - /my_home
    - /tmp
  denied_patterns:
    - "*.secret"

initialization:
  - mkdir -p /my_home/workspace
  - echo "Welcome to My Sandbox" > /my_home/README.txt
```

Then use it:
```bash
uv run chuk-virtual-shell --sandbox config/my_sandbox.yaml
```

## 🚀 Cross-Platform Compatibility

Chuk Virtual Shell is fully compatible across multiple operating systems:

- **Windows** - Full shell functionality with native path handling
- **macOS** - Complete functionality on Apple Silicon and Intel Macs  
- **Linux** - Tested on Ubuntu, Debian, and other distributions

**Platform-Specific Notes:**
- MCP server functionality requires Unix-like OS (Linux/macOS) due to uvloop dependency
- Windows users can use WSL or run the shell without MCP server features
- Virtual filesystem uses forward slashes (`/`) internally for consistent behavior
- CI/CD pipeline tests on all platforms with Python 3.11+

## 🧩 Modular Architecture

The project follows a highly modular design:

```
chuk_virtual_shell/
├── shell_interpreter.py           # Core shell interpreter
├── session/                       # Session management
├── core/                          # Core shell functionality
│   ├── executor.py                # Command execution engine
│   ├── redirection.py             # I/O redirection parser
│   └── control_flow_executor.py   # Control flow (if/for/while)
├── commands/                      # Command modules
│   ├── filesystem/                # File operations (cp, mv, rm, etc.)
│   ├── navigation/                # Directory navigation (ls, cd, pwd)
│   ├── text/                      # Text processing (grep, sed, awk)
│   ├── system/                    # System utilities (which, history, etc.)
│   └── mcp/                       # Dynamic MCP command loading
├── sandbox/                       # Sandbox configuration and loading
└── mcp_server.py                  # MCP server implementation
```

Each component is designed to be:
- **Independent**: Minimal cross-dependencies
- **Testable**: Comprehensive unit and integration tests
- **Extensible**: Easy to add new functionality
- **Maintainable**: Clear separation of concerns

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- Built for AI agents using [Model Context Protocol](https://modelcontextprotocol.io)
- Inspired by Unix shell design principles
- Virtual filesystem powered by [chuk-virtual-fs](https://github.com/chrishayuk/chuk-virtual-fs)

## 📮 Contact

- GitHub: [@chrishayuk](https://github.com/chrishayuk)
- Issues: [GitHub Issues](https://github.com/chrishayuk/chuk-virtual-shell/issues)

---

**Ready to give your AI agents a powerful shell environment? Get started with `uv pip install chuk-virtual-shell`!** 🚀