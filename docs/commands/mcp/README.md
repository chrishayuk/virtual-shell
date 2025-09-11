# MCP Commands

Model Context Protocol (MCP) commands provide integration with external MCP servers, allowing the shell to dynamically load and execute tools from connected servers.

## Overview

MCP commands are dynamically generated based on tools available from configured MCP servers. Each tool becomes a command in the shell with its own help text, input formatting, and output processing.

## Architecture

### Command Loading (`mcp_command_loader.py`)
- **Dynamic Command Creation:** Creates shell commands for each MCP tool
- **Server Connection:** Manages connections to MCP servers
- **Tool Registration:** Registers tools as executable commands
- **Error Handling:** Graceful handling of server connection issues

### Input Formatting (`mcp_input_formatter.py`) 
- **Schema-Based Formatting:** Converts command arguments based on tool schemas
- **Query Handling:** Special handling for query-type tools
- **Flexible Input:** Adapts to different tool input requirements

### Output Formatting (`mcp_output_formatter.py`)
- **Response Parsing:** Extracts and parses MCP server responses
- **Format Detection:** Automatically detects JSON, tabular, and text data
- **User-Friendly Display:** Formats output for optimal readability

## Dynamic Command Generation

When the shell starts, it:
1. Connects to configured MCP servers
2. Retrieves available tools from each server
3. Creates a shell command class for each tool
4. Registers commands in the shell's command registry

## Command Execution Flow

1. **User Input:** User runs an MCP command with arguments
2. **Input Formatting:** Arguments are formatted based on tool schema
3. **Server Communication:** Shell connects to MCP server
4. **Tool Execution:** Server executes the tool with formatted input
5. **Response Processing:** Response is parsed and formatted
6. **Output Display:** Formatted result is shown to user

## Input Handling

### Schema-Based Processing
- Tools with schemas get properly formatted arguments
- Required parameters are mapped from command arguments
- Optional parameters are handled gracefully

### Query Tools
Special handling for tools with `query` parameter:
```bash
search_tool hello world                      # Becomes: {"query": "hello world"}
```

### Flexible Mapping
- Single required parameter: Uses first argument
- Multiple parameters: Maps arguments by position
- No schema: Passes arguments as-is

## Output Formatting

### Automatic Format Detection

**JSON Data:**
```json
{
  "name": "John",
  "age": 30
}
```

**Tabular Data:**
```
| Name | Age | City    |
|------|-----|---------|
| John | 30  | Seattle |
| Jane | 25  | Portland|
```

**List Data:**
```
  - Item 1
  - Item 2
  - Item 3
```

## Error Handling

**Server Connection Errors:**
- Graceful fallback when servers are unavailable
- Clear error messages for connection issues
- Continues loading other servers if one fails

**Tool Execution Errors:**
- MCP server errors are displayed to user
- Network issues handled with appropriate messages
- Malformed responses processed safely

**Input Validation:**
- Invalid arguments produce helpful error messages
- Schema validation ensures proper tool input
- Fallback handling for unexpected input formats

## Configuration

MCP servers are configured in the shell's initialization:
```python
shell.mcp_servers = [
    {
        "server_name": "database_tools",
        "command": ["python", "db_server.py"],
        "args": ["--config", "db.json"]
    }
]
```

## Security Considerations

- **Sandboxed Execution:** MCP commands run within shell security constraints
- **Server Isolation:** Each MCP server runs in separate process
- **Input Sanitization:** User input is validated before server transmission
- **Output Processing:** Server responses are safely parsed and formatted

## Performance Features

- **Async Execution:** MCP commands use async/await for better performance
- **Connection Pooling:** Efficient server connection management
- **Error Caching:** Failed servers are handled gracefully
- **Lazy Loading:** Commands are registered only when servers are available

## Debugging

**Logging Support:**
- Command execution is logged with debug information
- Server communication is tracked
- Input/output formatting is logged for troubleshooting

**Error Reporting:**
- Detailed error messages for troubleshooting
- Server connectivity status reporting
- Tool execution status tracking

## Use Cases

**Database Queries:**
```bash
db_query "SELECT * FROM users WHERE active = true"
```

**File Operations:**
```bash  
file_search "*.py" --directory /project
```

**API Calls:**
```bash
api_get /users/123 --format json
```

**Data Processing:**
```bash
data_transform input.csv --operation normalize
```

## Extending MCP Support

To add new MCP capabilities:
1. Configure additional MCP servers
2. Tools automatically become available as commands
3. Custom input/output formatting can be added
4. Server-specific error handling can be implemented

## See Also

- [MCP Protocol](https://modelcontextprotocol.io/) - Official MCP specification
- [Server Configuration](../../README.md#mcp-servers) - Configuring MCP servers
- [Command Registration](../../README.md#commands) - How commands are registered