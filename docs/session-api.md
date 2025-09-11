# Shell Session API Documentation

## Overview

The Shell Session API provides stateful, persistent shell sessions with support for:
- **PTY mode** for interactive TUI applications (vim, top, etc.)
- **Streaming output** with sequence IDs for reliable ordering
- **Process cancellation** with soft/hard timeouts
- **Session persistence** across multiple commands
- **Environment and working directory preservation**

## Architecture

### Session Model

Each session maintains:
- **Working directory** - Persists across commands
- **Environment variables** - Isolated per session
- **Command history** - Tracked for audit/replay
- **Provider mounts** - Named virtual filesystems
- **PTY state** - Terminal size for interactive apps

### Modes

- **`pipe`** - Standard I/O for batch/pipeline operations
- **`pty`** - Pseudo-terminal for interactive TUI applications

## MCP Tools API

### shell.create_session

Creates a new shell session with persistent state.

```json
{
  "mode": "pty",        // "pty" or "pipe" (default: "pipe")
  "rows": 24,           // Terminal rows for PTY mode
  "cols": 80,           // Terminal columns for PTY mode
  "metadata": {}        // Additional session metadata
}
```

**Response:**
```json
{
  "session_id": "uuid-1234",
  "mode": "pty",
  "pty_size": [24, 80]
}
```

### shell.run

Execute a command in a session with streaming output.

```json
{
  "session_id": "uuid-1234",
  "command": "ls -la",
  "timeout_ms": 30000,        // Hard timeout (SIGKILL)
  "soft_timeout_ms": 25000,   // Soft timeout (SIGINT)
  "stream": true              // Stream output chunks
}
```

**Response:**
```json
{
  "command_id": "cmd-5678",
  "state": "completed",
  "exit_code": 0,
  "stdout": "total 24\n...",
  "stderr": "",
  "chunks": [
    {
      "sequence_id": 1,
      "stream_type": "stdout",
      "data": "total 24\n",
      "timestamp": 1234567890.123,
      "truncated": false
    }
  ]
}
```

### shell.stdin

Send input to a running command (for interactive programs).

```json
{
  "session_id": "uuid-1234",
  "command_id": "cmd-5678",
  "data": "yes\n"
}
```

### shell.read

Read streaming output from a command.

```json
{
  "session_id": "uuid-1234",
  "command_id": "cmd-5678",
  "since_sequence": 5    // Read chunks after this sequence ID
}
```

**Response:**
```json
{
  "command_id": "cmd-5678",
  "state": "running",
  "chunks": [...],
  "latest_sequence": 10
}
```

### shell.resize

Resize PTY terminal for interactive applications.

```json
{
  "session_id": "uuid-1234",
  "rows": 40,
  "cols": 120
}
```

### shell.cancel

Cancel a running command with process tree cleanup.

```json
{
  "session_id": "uuid-1234",
  "command_id": "cmd-5678"
}
```

### shell.close_session

Close and clean up a shell session.

```json
{
  "session_id": "uuid-1234"
}
```

### shell.get_session_info

Get information about a session.

```json
{
  "session_id": "uuid-1234"
}
```

**Response:**
```json
{
  "session_id": "uuid-1234",
  "mode": "pipe",
  "cwd": "/home/user",
  "env": {"PATH": "/usr/bin:/bin", ...},
  "history": ["ls", "cd /tmp", ...],
  "created_at": 1234567890.0,
  "last_activity": 1234567900.0,
  "pty_size": null,
  "active_commands": 0
}
```

## Python API

### Creating a Session Manager

```python
from chuk_virtual_shell.session import ShellSessionManager
from chuk_virtual_shell.shell_interpreter import ShellInterpreter

# Create shell factory
def shell_factory():
    return ShellInterpreter()

# Create session manager
manager = ShellSessionManager(
    shell_factory=shell_factory,
    default_ttl=3600  # 1 hour TTL
)
```

### Basic Usage

```python
import asyncio

async def example():
    # Create a session
    session_id = await manager.create_session(mode=SessionMode.PIPE)
    
    # Run commands
    async for chunk in manager.run_command(session_id, "ls -la"):
        print(f"[{chunk.sequence_id}] {chunk.data}")
    
    # Commands share state
    async for chunk in manager.run_command(session_id, "cd /tmp"):
        pass
    
    async for chunk in manager.run_command(session_id, "pwd"):
        print(chunk.data)  # Will print "/tmp"
    
    # Close session
    await manager.close_session(session_id)

asyncio.run(example())
```

### PTY Mode for Interactive Apps

```python
async def interactive_example():
    # Create PTY session
    session_id = await manager.create_session(
        mode=SessionMode.PTY,
        pty_size=(30, 100)
    )
    
    # Run interactive command
    command_task = asyncio.create_task(
        manager.run_command(session_id, "vim test.txt")
    )
    
    # Send input
    await manager.send_input(session_id, command_id, "iHello World\x1b:wq\n")
    
    # Wait for completion
    async for chunk in command_task:
        print(chunk.data)
```

### Streaming with Cancellation

```python
async def streaming_example():
    session_id = await manager.create_session()
    
    # Start long-running command
    chunks = []
    command_task = asyncio.create_task(
        collect_chunks(session_id, "find / -name '*.log'", chunks)
    )
    
    # Cancel after 5 seconds
    await asyncio.sleep(5)
    await manager.cancel_command(session_id, command_id)
    
    # Process collected chunks
    for chunk in chunks:
        if chunk.truncated:
            print(f"Output truncated at sequence {chunk.sequence_id}")

async def collect_chunks(session_id, command, chunks):
    async for chunk in manager.run_command(session_id, command):
        chunks.append(chunk)
```

## Session Persistence

Sessions are persisted using `chuk-sessions` with configurable backends:

### Memory Backend (Default)
```python
from chuk_sessions import SessionManager

session_backend = SessionManager()  # In-memory
manager = ShellSessionManager(
    shell_factory=shell_factory,
    session_backend=session_backend
)
```

### Redis Backend
```python
from chuk_sessions import SessionManager

session_backend = SessionManager(
    backend="redis",
    redis_url="redis://localhost:6379"
)
manager = ShellSessionManager(
    shell_factory=shell_factory,
    session_backend=session_backend
)
```

## Streaming Output

### Sequence IDs

Each output chunk has a monotonically increasing sequence ID for:
- **Ordering** - Reconstruct output in correct order
- **Resume** - Read chunks after a specific sequence
- **Deduplication** - Identify already-processed chunks

### Truncation

Large outputs can be truncated with the `truncated` flag:
```json
{
  "sequence_id": 1000,
  "stream_type": "stdout",
  "data": "...",
  "truncated": true
}
```

## Timeout and Cancellation

### Soft Timeout (SIGINT)

Sends interrupt signal, allowing graceful shutdown:
```json
{
  "soft_timeout_ms": 25000
}
```

### Hard Timeout (SIGKILL)

Forces termination after timeout:
```json
{
  "timeout_ms": 30000
}
```

### Manual Cancellation

Cancel a running command:
```python
await manager.cancel_command(session_id, command_id)
```

## Error Handling

### Session Not Found
```json
{
  "error": "Session not found or expired"
}
```

### Command Errors
```json
{
  "command_id": "cmd-123",
  "state": "error",
  "exit_code": 1,
  "stderr": "command not found: xyz"
}
```

### Timeout Errors
```json
{
  "command_id": "cmd-123",
  "state": "timeout",
  "exit_code": -1
}
```

## Best Practices

1. **Use PTY mode** for interactive TUI applications (vim, top, htop)
2. **Use pipe mode** for batch operations and pipelines
3. **Set appropriate timeouts** to prevent hanging commands
4. **Monitor sequence IDs** for streaming reliability
5. **Close sessions** when done to free resources
6. **Handle reconnection** by restoring from session ID

## Examples

### Multi-Step Build Process
```python
async def build_project(session_id):
    steps = [
        "git pull",
        "npm install",
        "npm run build",
        "npm test"
    ]
    
    for step in steps:
        print(f"Running: {step}")
        async for chunk in manager.run_command(session_id, step):
            if chunk.stream_type == "stderr":
                print(f"Error: {chunk.data}")
            else:
                print(chunk.data)
```

### Interactive SSH Session
```python
async def ssh_session():
    session_id = await manager.create_session(
        mode=SessionMode.PTY,
        pty_size=(24, 80)
    )
    
    # Start SSH
    async for chunk in manager.run_command(
        session_id,
        "ssh user@host",
        stream=True
    ):
        print(chunk.data, end='')
```

## Migration from Single-Shot Commands

### Before (Single-Shot)
```python
# Each command starts fresh
result1 = shell.execute("cd /tmp")
result2 = shell.execute("pwd")  # Returns "/" not "/tmp"
```

### After (Session-Based)
```python
# Commands share state
session_id = await manager.create_session()
await manager.run_command(session_id, "cd /tmp")
result = await manager.run_command(session_id, "pwd")  # Returns "/tmp"
```