"""
chuk_virtual_shell/commands/mcp/mcp_command_loader.py - Load MCP commands dynamically

This module provides functionality to connect to MCP servers and dynamically
create and register commands for all tools available on those servers.
"""
import logging
import asyncio
import json
import uuid
from typing import List, Dict, Any, Optional

from chuk_virtual_shell.commands.command_base import ShellCommand

logger = logging.getLogger(__name__)

# Helper function for tool execution
async def send_tool_execute(read_stream, write_stream, tool_name, input_data, timeout=10.0):
    """
    Send a tool execution request and get the response.
    
    Args:
        read_stream: Stream for reading responses
        write_stream: Stream for sending requests
        tool_name: Name of the tool to execute
        input_data: Input data for the tool
        timeout: Timeout in seconds
        
    Returns:
        Response object or None if failed
    """
    try:
        # Generate a unique ID for this request
        message_id = str(uuid.uuid4())
        
        # Create the request payload
        request = {
            "jsonrpc": "2.0",
            "id": message_id,
            "method": "tools/execute",
            "params": {
                "name": tool_name,
                "input": input_data
            }
        }
        
        # Encode as JSON and send
        request_json = json.dumps(request)
        await write_stream.send(request_json)
        
        # Wait for response
        response_json = await read_stream.receive()
        
        # Parse the response
        response = json.loads(response_json)
        
        # Validate the response
        if "id" not in response or response.get("id") != message_id:
            logger.warning(f"Received response with mismatched ID: {response}")
            return None
            
        return response
    except Exception as e:
        logger.exception(f"Error sending tool execute request: {e}")
        return None

def create_mcp_command_class(tool: Dict[str, Any], mcp_config: Any) -> type:
    """
    Dynamically create a command class for an MCP tool.
    
    Args:
        tool: Tool definition dictionary from the MCP server
        mcp_config: Configuration for connecting to the MCP server
        
    Returns:
        A dynamically created ShellCommand subclass for the tool
    """
    tool_name = tool["name"]
    description = tool.get("description", "MCP tool command")
    input_schema = tool.get("inputSchema", {})
    
    class MCPCommand(ShellCommand):
        name = tool_name
        help_text = description
        category = "mcp"  # Categorize all MCP commands
        
        def __init__(self, shell_context):
            super().__init__(shell_context)
            self.mcp_config = mcp_config
            self.tool_schema = input_schema
        
        def execute(self, args):
            """
            Synchronous implementation - indicates this is an async command
            
            For compatibility with existing shell, but indicates that
            async execution is preferred for this command.
            """
            return f"MCP command '{tool_name}' should be executed asynchronously for best results."
        
        async def execute_async(self, args):
            """
            Asynchronous implementation that connects to the MCP server
            
            Args:
                args: Command arguments
                
            Returns:
                Result from the MCP tool execution
            """
            logger.debug(f"Executing MCP command '{tool_name}' with args: {args}")
            
            # Format arguments based on the tool's schema
            input_data = self._format_input(args)
            
            try:
                # Import here to avoid circular imports
                from chuk_mcp.mcp_client.transport.stdio.stdio_client import stdio_client
                from chuk_mcp.mcp_client.messages.initialize.send_messages import send_initialize
                from chuk_mcp.mcp_client.messages.ping.send_messages import send_ping
                
                # Connect to the MCP server
                async with stdio_client(self.mcp_config) as (read_stream, write_stream):
                    # Initialize the connection
                    init_result = await send_initialize(read_stream, write_stream)
                    if not init_result:
                        return f"Failed to initialize connection to MCP server for tool '{tool_name}'"
                    
                    # Send a ping to confirm the connection
                    ping_result = await send_ping(read_stream, write_stream)
                    if not ping_result:
                        return f"Failed to ping MCP server for tool '{tool_name}'"
                    
                    # Execute the tool
                    response = await send_tool_execute(read_stream, write_stream, tool_name, input_data)
                    
                    # Check if we have an error
                    if not response:
                        return f"Failed to execute tool '{tool_name}' - no response received"
                        
                    if "error" in response:
                        error_data = response.get("error", {})
                        error_msg = error_data.get("message", str(error_data))
                        return f"Error executing tool '{tool_name}': {error_msg}"
                    
                    # Get the result
                    result = response.get("result", {})
                    
                    # Format the output based on the schema and data
                    return self._format_output_based_on_schema(result)
                    
            except Exception as e:
                logger.exception(f"Error executing MCP tool '{tool_name}'")
                return f"Error executing MCP tool '{tool_name}': {str(e)}"
            
        def _format_input(self, args):
            """
            Format the input arguments based on the tool's schema
            
            Args:
                args: Command arguments
                
            Returns:
                Formatted input data matching the tool's schema
            """
            # Simple implementation - could be enhanced based on specific tool schemas
            if not self.tool_schema:
                return {"args": args}
                
            properties = self.tool_schema.get("properties", {})
            required = self.tool_schema.get("required", [])
            
            # Handle common patterns
            
            # 1. No args required (tools with empty properties object)
            if not properties:
                return {}
                
            # 2. Single required property
            if len(required) == 1 and len(args) > 0:
                prop_name = required[0]
                
                # Special case for query-based tools: join all args into a single query string
                if prop_name == "query" and len(args) > 0:
                    return {prop_name: " ".join(args)}
                
                # For other single-property tools, just use the first arg
                return {prop_name: args[0]}
            
            # 3. Property named "query" (common for database tools)
            if "query" in properties and args:
                return {"query": " ".join(args)}
            
            # Default case - just pass args as-is
            return {"args": args}
        
        def _format_output_based_on_schema(self, result):
            """
            Format the output based on the result data structure and input schema.
            Uses schema information to determine the appropriate formatting.
            
            Args:
                result: Result data from the tool execution
                
            Returns:
                Formatted output string
            """
            # Handle empty result
            if not result:
                return f"Tool '{tool_name}' executed successfully, but returned no data."
            
            # Look at the structure of the result to determine best formatting
            
            # Case 1: List-like results (arrays of strings/objects)
            if isinstance(result, list):
                return self._format_list_result(result)
            
            # Case 2: Simple object with arrays
            for key, value in result.items():
                if isinstance(value, list) and value:
                    # If the key name suggests it's a list of items (plural noun)
                    if key.endswith('s') and not key.endswith('status'):
                        item_name = key[:-1] if key.endswith('s') else key
                        return self._format_named_list(item_name, value)
            
            # Case 3: Structure with rows/columns data (common in query results)
            if 'rows' in result and isinstance(result.get('rows'), list):
                return self._format_tabular_data(result)
            
            # Default case: Pretty-print the JSON
            return json.dumps(result, indent=2, sort_keys=True)
        
        def _format_list_result(self, items):
            """Format a list of items"""
            if not items:
                return "No items returned."
                
            # Check if list contains simple strings
            if all(isinstance(item, str) for item in items):
                return "\n".join([f"  - {item}" for item in items])
                
            # If list contains objects, format as pretty JSON
            return json.dumps(items, indent=2)
        
        def _format_named_list(self, item_name, items):
            """Format a named list of items"""
            if not items:
                return f"No {item_name}s found."
                
            # Check if list contains simple strings
            if all(isinstance(item, str) for item in items):
                return f"{item_name.capitalize()} list:\n" + "\n".join([f"  - {item}" for item in items])
                
            # If list contains objects, format as pretty JSON
            return f"{item_name.capitalize()} list:\n" + json.dumps(items, indent=2)
        
        def _format_tabular_data(self, data):
            """Format data that has rows and columns"""
            rows = data.get('rows', [])
            if not rows:
                return "Query returned no results."
                
            columns = data.get('columns', [])
            if not columns and rows and isinstance(rows[0], list):
                # Generate numeric column names if missing
                columns = [f"Col{i+1}" for i in range(len(rows[0]))]
                
            if columns and rows:
                # Create header row
                output = "| " + " | ".join(str(col) for col in columns) + " |\n"
                output += "|" + "---|" * len(columns) + "\n"
                
                # Add data rows
                for row in rows:
                    row_values = [str(cell) if cell is not None else "NULL" for cell in row]
                    output += "| " + " | ".join(row_values) + " |\n"
                return output
                
            # Fallback to JSON if structure doesn't fit tabular format
            return json.dumps(rows, indent=2)
        
    return MCPCommand

async def load_mcp_tools_for_server(mcp_config: Any) -> List[Dict[str, Any]]:
    """
    Connect to an MCP server and retrieve its available tools.
    
    Args:
        mcp_config: Configuration for connecting to the MCP server
        
    Returns:
        List of tool definitions from the server
    """
    # Determine the server name for logging
    if isinstance(mcp_config, dict):
        server_name = mcp_config.get("server_name", "unknown")
    else:
        server_name = getattr(mcp_config, "server_name", "unknown")
    
    logger.info(f"Loading tools from MCP server: {server_name}")
    
    try:
        # Import here to avoid circular imports
        from chuk_mcp.mcp_client.transport.stdio.stdio_client import stdio_client
        from chuk_mcp.mcp_client.messages.initialize.send_messages import send_initialize
        from chuk_mcp.mcp_client.messages.ping.send_messages import send_ping
        from chuk_mcp.mcp_client.messages.tools.send_messages import send_tools_list
        
        # Connect to the MCP server
        async with stdio_client(mcp_config) as (read_stream, write_stream):
            # Initialize the connection with a longer timeout (15 seconds)
            init_result = await send_initialize(read_stream, write_stream, timeout=15.0)
            if not init_result:
                logger.error(f"Failed to initialize connection to MCP server: {server_name}")
                return []
            
            logger.debug(f"Successfully initialized connection to MCP server: {server_name}")
            
            # Send a ping to confirm the connection
            ping_result = await send_ping(read_stream, write_stream)
            if not ping_result:
                logger.error(f"Failed to ping MCP server: {server_name}")
                return []
            
            logger.debug(f"Successfully pinged MCP server: {server_name}")
            
            # Request the list of available tools
            tools_result = await send_tools_list(read_stream, write_stream)
            tools = tools_result.get("tools", [])
            
            logger.info(f"Loaded {len(tools)} tools from MCP server: {server_name}")
            logger.debug(f"Tool names: {[tool.get('name') for tool in tools]}")
            
            return tools
            
    except Exception as e:
        logger.exception(f"Error loading tools from MCP server: {server_name}")
        return []

async def register_mcp_commands(shell) -> None:
    """
    Register commands for all tools available on all configured MCP servers.
    
    Args:
        shell: The shell interpreter to register commands with
    """
    # Get all configured MCP servers
    mcp_servers = getattr(shell, "mcp_servers", [])
    if not mcp_servers:
        logger.info("No MCP servers configured, skipping command registration")
        return
    
    logger.info(f"Registering commands from {len(mcp_servers)} MCP servers")
    
    # Process each server
    for mcp_config in mcp_servers:
        try:
            # Get the server name for logging
            if isinstance(mcp_config, dict):
                server_name = mcp_config.get("server_name", "unknown")
            else:
                server_name = getattr(mcp_config, "server_name", "unknown")
            
            logger.info(f"Loading tools from MCP server: {server_name}")
            
            # Load all tools from the server
            tools = await load_mcp_tools_for_server(mcp_config)
            
            # Create and register a command for each tool
            for tool in tools:
                tool_name = tool.get("name")
                if not tool_name:
                    logger.warning("Skipping tool with missing name")
                    continue
                
                try:
                    # Create a command class for the tool
                    command_class = create_mcp_command_class(tool, mcp_config)
                    
                    # Instantiate and register the command
                    command = command_class(shell)
                    shell._register_command(command)
                    
                    logger.info(f"Registered MCP command: {tool_name}")
                    
                except Exception as e:
                    logger.exception(f"Error registering MCP command for tool: {tool_name}")
            
        except Exception as e:
            logger.exception(f"Error processing MCP server: {server_name}")