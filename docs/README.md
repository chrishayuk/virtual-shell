# Chuk Virtual Shell - Documentation

Complete documentation for the Chuk Virtual Shell, including commands, APIs, and integration guides.

## 📚 Documentation Structure

- **[Session API](session-api.md)** - Session management API for stateful execution
- **[Command Reference](#command-categories)** - All available shell commands
- **[Examples](../examples/)** - Demo scripts and usage examples
- **[Integration Guide](#integration-guide)** - Using with AI agents and applications

## 🔄 Session Management

The shell provides enterprise-grade session management for maintaining state across commands:

- **Persistent Context**: Working directory, environment variables, and command history
- **Streaming Output**: Real-time output with sequence IDs for ordering
- **Process Control**: Cancellation and timeout support
- **Multi-Session**: Isolated sessions for concurrent operations

See the [Session API Documentation](session-api.md) for detailed usage.

## Command Categories

### Filesystem Commands (`/commands/filesystem/`)
File and directory manipulation commands:
- `cat` - Display file contents
- `cp` - Copy files and directories  
- `df` - Display filesystem disk space usage
- `du` - Display directory space usage
- `echo` - Display text
- `find` - Search for files and directories
- `mkdir` - Create directories
- `more` - Display file contents page by page
- `mv` - Move/rename files and directories
- `quota` - Display disk usage quotas
- `rm` - Remove files
- `rmdir` - Remove directories
- `touch` - Create empty files or update timestamps

### Navigation Commands (`/commands/navigation/`)
Directory navigation and listing:
- `cd` - Change directory
- `ls` - List directory contents  
- `pwd` - Print working directory
- `tree` - Display directory tree structure

### Text Processing Commands (`/commands/text/`)
Text manipulation and analysis:
- `awk` - Pattern scanning and processing
- `diff` - Compare files line by line
- `grep` - Search text patterns in files
- `head` - Display first lines of files
- `patch` - Apply difference patches to files
- `sed` - Stream editor for text transformation
- `sort` - Sort lines in text files
- `tail` - Display last lines of files
- `uniq` - Report or omit repeated lines
- `wc` - Word, line, character, and byte count

### System Commands (`/commands/system/`)
System operations and utilities:
- `clear` - Clear terminal screen
- `exit` - Exit shell
- `help` - Display help information
- `history` - Display and search command history
- `python` - Execute Python code
- `script` - Execute shell scripts
- `sh` - Execute shell commands
- `time` - Time command execution
- `timings` - Display command execution statistics
- `uptime` - Display system uptime
- `which` - Locate commands in PATH
- `whoami` - Display current user

### Environment Commands (`/commands/environment/`)
Environment variable management:
- `alias` - Create command aliases
- `env` - Display environment variables
- `export` - Set environment variables
- `unalias` - Remove command aliases

### MCP Commands (`/commands/mcp/`)
Model Context Protocol integration:
- Dynamic MCP command loading and execution

## Usage

Each command documentation includes:
- Description and purpose
- Syntax and usage patterns
- Available options and flags
- Practical examples
- See also references to related commands

## Command Structure

All commands inherit from `ShellCommand` base class and implement:
- `name` - Command identifier
- `help_text` - Built-in help documentation
- `category` - Command categorization
- `execute(args)` - Main command logic

## Integration Guide

### For AI Agents

The Chuk Virtual Shell is designed for AI agent integration with stateful sessions:

```python
from chuk_virtual_shell.session import ShellSessionManager
from chuk_virtual_shell.shell_interpreter import ShellInterpreter

# Initialize
manager = ShellSessionManager(
    shell_factory=lambda: ShellInterpreter()
)

# Create persistent session
session_id = await manager.create_session()

# Execute multi-step workflow
await manager.run_command(session_id, "mkdir /project")
await manager.run_command(session_id, "cd /project")
await manager.run_command(session_id, "echo '# API' > README.md")
# Context maintained throughout!

# Clean up
await manager.close_session(session_id)
```

### For Applications

Embed the shell in your Python applications:

```python
from chuk_virtual_shell.shell_interpreter import ShellInterpreter

# Create shell instance
shell = ShellInterpreter()

# Execute commands
result = shell.execute("ls -la")
print(result)

# Access filesystem directly
shell.fs.write_file("/test.txt", "Hello World")
content = shell.fs.read_file("/test.txt")
```

### For Testing

Use the virtual shell for isolated testing environments:

```python
import pytest
from chuk_virtual_shell.shell_interpreter import ShellInterpreter

@pytest.fixture
def shell():
    return ShellInterpreter()

def test_my_script(shell):
    # Test in isolated environment
    shell.execute("mkdir /test")
    shell.execute("echo 'test' > /test/file.txt")
    result = shell.execute("cat /test/file.txt")
    assert "test" in result
```

## Advanced Features

### Custom Storage Providers

Implement custom storage backends:

```python
from chuk_virtual_fs import FileSystemProvider

class MyCustomProvider(FileSystemProvider):
    def read_file(self, path):
        # Custom implementation
        pass
    
    def write_file(self, path, content):
        # Custom implementation
        pass
```

### Custom Commands

Add new commands to the shell:

```python
from chuk_virtual_shell.commands.command_base import ShellCommand

class MyCommand(ShellCommand):
    name = "mycommand"
    help_text = "My custom command"
    category = "custom"
    
    def execute(self, args):
        return "Command output"
```

### Shell Configuration

Configure the shell with `.shellrc`:

```bash
# /home/user/.shellrc
export PATH=/usr/local/bin:/usr/bin:/bin
export EDITOR=vim

# Aliases
alias ll="ls -la"
alias la="ls -a"

# Enable command timing
timings -e
```

## Performance

The virtual shell is optimized for:
- **Fast Command Execution**: In-memory operations
- **Efficient Streaming**: Chunked output with minimal overhead
- **Scalable Sessions**: Support for hundreds of concurrent sessions
- **Low Memory Footprint**: Lazy loading and efficient data structures

## Security

- **Sandboxed Execution**: All operations in virtual filesystem
- **No System Access**: Commands cannot access host system
- **Session Isolation**: Complete isolation between sessions
- **Safe for Untrusted Input**: Built for AI agent usage

## Support

- **GitHub Issues**: Report bugs and request features
- **Documentation**: This guide and API docs
- **Examples**: See `examples/` directory for demos
- **Tests**: Comprehensive test suite with 940+ tests