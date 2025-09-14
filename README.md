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
```

### Basic Usage

```bash
# Start interactive shell
uv run chuk-virtual-shell

# Use a pre-configured sandbox
uv run chuk-virtual-shell --sandbox ai_sandbox

# Start MCP server for AI agents
uv run python -m chuk_virtual_shell.mcp_server
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

Current test status: **1411 tests passing** (18 skipped)

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