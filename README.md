# Chuk Virtual Shell 🐚

A powerful virtual shell environment with MCP (Model Context Protocol) integration and AI agents as Unix processes, perfect for AI automation and sandboxed execution environments.

[![Tests](https://img.shields.io/badge/tests-1420%20passing-green)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-85%25-yellow)](tests/)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](pyproject.toml)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

## 🌟 Highlight: AI Agents as Unix Processes

**Revolutionary Feature**: Run AI agents as first-class shell processes! Agents behave like Unix commands with PIDs, pipes, background execution, and process management.

```bash
# Run agents like shell commands
echo "Hello" | agent assistant.agent

# Agent pipelines
cat data.csv | agent analyzer.agent | agent reporter.agent > report.md

# Background agents
agent monitor.agent -b &

# Process management
agent -l  # List agents
agent -k agent_1  # Kill agent
```

🎬 **[Watch the Demo](examples/README_AGENTS.md)** | 📖 **[Full Documentation](docs/AGENTS.md)**

## 🌟 Overview

Chuk Virtual Shell provides a complete POSIX-like virtual shell environment designed specifically for AI agents and automation:

- **🤖 AI Agents as Shell Processes**: Run AI agents as first-class Unix processes with PIDs, piping, and background execution
- **🔄 MCP Server Integration**: Full Model Context Protocol support for AI agents like Claude, Cline, and Aider
- **📊 Persistent Sessions**: Stateful command execution with maintained context across interactions
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

### 🤖 AI Agents as Unix Processes

Revolutionary feature: AI agents run as shell processes with full Unix semantics:

```bash
# Run an agent like any command
agent assistant.agent

# Pipe input to agents
echo "analyze this" | agent analyzer.agent

# Chain agents in pipelines
cat data.csv | agent parser.agent | agent reporter.agent > report.txt

# Background execution
agent monitor.agent -b &

# Process management
agent -l                    # List running agents
agent -k agent_123          # Kill an agent
agent -s agent_123          # Check agent status
```

**Agent Features:**
- **Process IDs**: Each agent gets a unique PID
- **I/O Redirection**: Full support for `<`, `>`, `>>`, and `|`
- **Background Execution**: Run agents with `&` or `-b` flag
- **Process Management**: List, kill, and monitor agent processes
- **Tool Access**: Agents can execute shell commands
- **Memory Modes**: Session or persistent memory across invocations
- **LLM Integration**: Supports OpenAI, Anthropic, and other providers via [chuk-llm](https://github.com/chrishayuk/chuk-llm)

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

<<<<<<< HEAD
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
- **[System](docs/commands/system/README.md)**: clear, exit, help, history, python, script, sh, time, timings, uptime, which, whoami, **agent**
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

### AI Agent Demos

#### Single Agent Demo
Run AI agents as shell processes:

```bash
# Clean demo with filtered output
uv run python demo.py

# Full demo with all output
uv run python examples/agent_clean_demo.py
```

#### Multi-Agent Collaboration
Watch multiple agents work together as a team:

```bash
# Software development team simulation
uv run python examples/software_team_demo.py

# Multi-agent collaboration with pipelines
uv run python run_multi_agent.py
```

These demos showcase:
- ✅ AI agents running as Unix processes with PIDs
- ✅ Agent pipelines and I/O redirection
- ✅ Parallel agent execution
- ✅ Multi-agent collaboration and communication
- ✅ Real LLM integration (OpenAI, Anthropic via chuk-llm)
- ✅ Background agent processes

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
=======
## 📝 Command Examples
>>>>>>> main

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

<<<<<<< HEAD
Run `make help` to see all available targets:

- **Testing**: `test`, `coverage`, `coverage-html`
- **Code Quality**: `lint`, `format`, `typecheck`
- **Building**: `build`, `check-build`, `clean`
- **Publishing**: `publish`, `publish-test`
- **Version Management**: `version`, `bump-patch`, `bump-minor`, `bump-major`
- **Release Workflow**: `release-patch`, `release-minor`, `release-major`

## AI Agent System

### Creating Agent Definitions

Agents are defined in YAML files with a special `#!agent` shebang:

```yaml
#!agent
name: assistant
model: gpt-3.5-turbo
system_prompt: |
  You are a helpful AI assistant.
  Use the available tools to help users.
tools:
  - ls
  - cat
  - echo
  - grep
input: stdin
output: stdout
memory: session
temperature: 0.7
max_tokens: 500
timeout: 30
```

### Multi-Agent Collaboration Example

Create specialized agents that work together:

```python
# From examples/software_team_demo.py
shell.execute("agent /team/product_owner.agent < requirements.txt")
shell.execute("agent /team/tech_lead.agent < user_stories.txt")
shell.execute("agent /team/backend_dev.agent -b")  # Background
shell.execute("agent /team/qa_engineer.agent < code.py")
```

### Agent Pipeline Processing

```bash
# Data processing pipeline
cat raw_data.csv | \
  agent parser.agent | \
  agent analyzer.agent | \
  agent formatter.agent > report.md

# Parallel processing
for file in *.txt; do
  agent processor.agent < "$file" &
done
wait  # Wait for all background agents
```

### Configuring LLM Providers

Set up your API keys for real LLM integration:

```bash
# In .env file or environment
export OPENAI_API_KEY=your_key
export ANTHROPIC_API_KEY=your_key

# Install chuk-llm for LLM support
pip install chuk-llm
```

## Future Enhancements

- User authentication and permissions system
- Multi-user support with session isolation
- Command history and tab completion
- More advanced file operations
- Additional storage providers (Redis, IndexedDB, etc.)
- Provider data migration tools
- **AI Agent Enhancements**:
  - Agent-to-agent direct communication protocols
  - Distributed agent execution across machines
  - Agent marketplace for sharing definitions
  - Visual agent pipeline builder
  - Agent resource limits and quotas
  - Event-triggered agent activation

---

**Ready to give your AI agents a powerful shell environment? Get started with `uv pip install chuk-virtual-shell`!** 🚀
