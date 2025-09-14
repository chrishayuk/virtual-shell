# MCP Integration Guide

Chuk Virtual Shell provides a complete MCP (Model Context Protocol) server implementation, making it easy to integrate with AI agents like Claude Code, Cline, Aider, and other MCP-compatible tools.

## Table of Contents

- [Quick Start](#quick-start)
- [MCP Tools](#mcp-tools)
- [Configuration](#configuration)
- [Integration Examples](#integration-examples)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)

## Quick Start

### 1. Install Dependencies

```bash
# Install chuk-virtual-shell
pip install chuk-virtual-shell

# Or for development
git clone https://github.com/your-org/chuk-virtual-shell
cd chuk-virtual-shell
uv sync
```

### 2. Test the MCP Server

```bash
# Run the MCP server directly
python -m chuk_virtual_shell.mcp_server

# Or test with the demo client
python examples/mcp_client_demo.py
```

### 3. Configure Claude Desktop

Add to your Claude Desktop MCP configuration file (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "chuk-virtual-shell": {
      "command": "python",
      "args": ["-m", "chuk_virtual_shell.mcp_server"],
      "env": {
        "CHUK_SANDBOX": "ai_sandbox",
        "CHUK_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

## MCP Tools

The Chuk Virtual Shell MCP server exposes these tools:

### Shell Execution

#### `shell_run`
Execute commands in a persistent virtual shell session.

**Parameters:**
- `command` (required): Shell command to execute
- `session_id` (optional): Session ID to use (creates new if not provided)
- `timeout` (optional): Command timeout in seconds (default: 30)

**Example:**
```json
{
  "name": "shell_run",
  "arguments": {
    "command": "ls -la /workspace",
    "session_id": "session_123",
    "timeout": 60
  }
}
```

**Response:**
```json
{
  "session_id": "session_123",
  "command": "ls -la /workspace", 
  "stdout": "total 4\ndrwxr-xr-x 2 user user 4096 Dec 1 10:00 .\n...",
  "stderr": "",
  "return_code": 0,
  "execution_time": 0.025
}
```

### Session Management

#### `shell_session_create`
Create a new shell session with optional sandbox configuration.

**Parameters:**
- `sandbox` (optional): Sandbox name (`ai_sandbox`, `default`, `readonly`)

#### `shell_session_list`
List all active shell sessions.

#### `shell_session_info`
Get detailed information about a specific session.

**Parameters:**
- `session_id` (required): Session ID to query

#### `shell_session_close`
Close and clean up a shell session.

**Parameters:**
- `session_id` (required): Session ID to close

### File System Operations

#### `fs_read`
Read a file from the virtual filesystem.

**Parameters:**
- `path` (required): File path to read
- `session_id` (optional): Session to read from

#### `fs_write`
Write content to a file in the virtual filesystem.

**Parameters:**
- `path` (required): File path to write
- `content` (required): File content
- `session_id` (optional): Session to write to

#### `fs_list`
List directory contents in the virtual filesystem.

**Parameters:**
- `path` (optional): Directory path (default: ".")
- `session_id` (optional): Session to list from

## Configuration

### Environment Variables

Configure the MCP server using environment variables:

- `CHUK_SANDBOX`: Sandbox configuration (`ai_sandbox`, `default`, `readonly`, `none`)
- `CHUK_FS_PROVIDER`: Filesystem provider (`memory`, `sqlite`, `s3`)
- `CHUK_LOG_LEVEL`: Logging level (`DEBUG`, `INFO`, `WARN`, `ERROR`)

### Sandbox Configurations

#### `ai_sandbox` (Recommended for AI agents)
- Restricted to `/sandbox` directory
- Safe environment for code execution
- Pre-configured with common tools
- Resource limits enabled

#### `default`
- Balanced development environment
- Access to `/home/user` and common directories
- More tools available
- Moderate resource limits

#### `readonly`
- Read-only filesystem access
- Perfect for code analysis and exploration
- Cannot modify files
- Minimal resource usage

#### `none`
- Full virtual filesystem access
- No sandbox restrictions
- Maximum flexibility
- Use with caution

## Integration Examples

### Claude Code Integration

Claude Code can use the shell for persistent development workflows:

```
You can help me build a web application. I'll need you to:

1. Create a project structure
2. Set up configuration files  
3. Write the main application code
4. Create tests
5. Build and run the application

Use the shell tools to maintain state between steps.
```

Claude will automatically use the MCP tools to:
- Create a session with `shell_session_create`
- Execute commands with `shell_run` to set up the project
- Use `fs_write` to create files
- Maintain context across all operations

### Cline Integration

Cline can use the shell for agentic coding:

```python
# Cline will use shell_run to execute commands
# Session state persists across all operations
await mcp_client.call_tool("shell_run", {
    "command": "mkdir -p src tests docs",
    "session_id": session_id
})

await mcp_client.call_tool("shell_run", {
    "command": "cd src && touch main.py config.py", 
    "session_id": session_id  # Same session!
})

# Working directory and environment persist
await mcp_client.call_tool("shell_run", {
    "command": "pwd && ls -la",  # Will show /src
    "session_id": session_id
})
```

### Aider Integration

Aider can leverage the shell for comprehensive development:

```python
# Set up development environment
session_result = await mcp_client.call_tool("shell_session_create", {
    "sandbox": "default"
})
session_id = session_result["session_id"]

# Install dependencies
await mcp_client.call_tool("shell_run", {
    "command": "cd /workspace && npm init -y && npm install express",
    "session_id": session_id
})

# Create and edit files
await mcp_client.call_tool("fs_write", {
    "path": "/workspace/server.js",
    "content": "const express = require('express');\n...",
    "session_id": session_id
})

# Run tests
await mcp_client.call_tool("shell_run", {
    "command": "npm test",
    "session_id": session_id
})
```

## Advanced Usage

### Multi-Session Workflows

Use multiple sessions for isolation:

```python
# Main development session
dev_session = await mcp_client.call_tool("shell_session_create", {
    "sandbox": "default"
})

# Testing session (isolated)
test_session = await mcp_client.call_tool("shell_session_create", {
    "sandbox": "ai_sandbox"
})

# Each session maintains independent state
await mcp_client.call_tool("shell_run", {
    "command": "export ENV=development && cd /project",
    "session_id": dev_session["session_id"]
})

await mcp_client.call_tool("shell_run", {
    "command": "export ENV=testing && cd /tests", 
    "session_id": test_session["session_id"]
})
```

### Error Handling

Handle command failures gracefully:

```python
result = await mcp_client.call_tool("shell_run", {
    "command": "make build",
    "session_id": session_id
})

if result["return_code"] != 0:
    print(f"Build failed: {result['stderr']}")
    
    # Try alternative approach
    result = await mcp_client.call_tool("shell_run", {
        "command": "gcc -o app main.c",
        "session_id": session_id
    })
```

### Complex File Operations

Combine shell commands and direct file operations:

```python
# Use shell for complex operations
await mcp_client.call_tool("shell_run", {
    "command": "find /project -name '*.py' | head -10 > python_files.txt",
    "session_id": session_id
})

# Read the result with direct file access
file_list = await mcp_client.call_tool("fs_read", {
    "path": "/python_files.txt",
    "session_id": session_id
})

print(f"Found Python files:\n{file_list['content']}")
```

## Best Practices

### 1. Session Management

- **Create sessions early**: Establish sessions at the start of workflows
- **Reuse sessions**: Maintain state across related operations
- **Clean up sessions**: Close sessions when workflows complete
- **Use appropriate sandboxes**: Match sandbox to security requirements

### 2. Error Handling

- **Check return codes**: Always verify command execution success
- **Handle timeouts**: Set appropriate timeouts for long-running commands
- **Graceful degradation**: Have fallback strategies for failures

### 3. Security

- **Use sandboxes**: Always use sandboxed environments for untrusted code
- **Validate input**: Sanitize file paths and command arguments
- **Limit resources**: Configure appropriate resource limits
- **Monitor execution**: Log and monitor command execution

### 4. Performance

- **Batch operations**: Group related commands in single sessions
- **Avoid unnecessary sessions**: Reuse existing sessions when possible
- **Stream large outputs**: Handle large command outputs appropriately
- **Cache results**: Store intermediate results in files when needed

## Troubleshooting

### Common Issues

#### Connection Errors

```bash
# Test server connectivity
python -c "
import asyncio
from chuk_virtual_shell.mcp_server import ChukMCPServer
server = ChukMCPServer()
print('Server can be imported successfully')
"
```

#### Permission Errors

```bash
# Check sandbox configuration
CHUK_SANDBOX=ai_sandbox python -m chuk_virtual_shell.mcp_server
```

#### Module Import Errors

```bash
# Verify installation
python -c "import chuk_virtual_shell; print(chuk_virtual_shell.__file__)"
```

### Debug Mode

Enable debug logging:

```bash
CHUK_LOG_LEVEL=DEBUG python -m chuk_virtual_shell.mcp_server
```

### Testing

Run the comprehensive demo:

```bash
python examples/mcp_client_demo.py
```

Expected output should show:
- ✅ Session creation
- ✅ Command execution with state persistence  
- ✅ File operations
- ✅ Multi-session isolation
- ✅ Session management

## API Reference

### Request Format

All MCP requests follow this format:

```json
{
  "method": "tools/call",
  "params": {
    "name": "tool_name",
    "arguments": {
      "param1": "value1"
    }
  },
  "id": 1
}
```

### Response Format

Successful responses:

```json
{
  "result": {
    "key": "value"
  },
  "id": 1
}
```

Error responses:

```json
{
  "error": {
    "code": -32602,
    "message": "Invalid params"
  },
  "id": 1
}
```

### Error Codes

- `-32700`: Parse error (invalid JSON)
- `-32600`: Invalid request
- `-32601`: Method not found
- `-32602`: Invalid params
- `-32603`: Internal error

## Resources

- [MCP Specification](https://modelcontextprotocol.io/specification/)
- [Claude Desktop MCP Guide](https://docs.anthropic.com/en/docs/build-with-claude/mcp)
- [Example Integrations](../examples/)
- [Security Configuration](./security.md)

For questions or issues, please open an issue on GitHub or contact the development team.