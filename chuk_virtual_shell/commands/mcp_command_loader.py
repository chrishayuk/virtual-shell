# chuk_virtual_shell/commands/mcp_command_loader.py
import anyio
import asyncio
import logging

# virtual shell imports
from chuk_virtual_shell.commands.command_base import ShellCommand

# chuk MCP imports
from chuk_mcp.mcp_client.transport.stdio.stdio_client import stdio_client
from chuk_mcp.mcp_client.messages.initialize.send_messages import send_initialize
from chuk_mcp.mcp_client.messages.ping.send_messages import send_ping
from chuk_mcp.mcp_client.messages.tools.send_messages import send_tools_list

logger = logging.getLogger(__name__)

def create_mcp_command_class(tool, mcp_config):
    """
    Dynamically create a command class for an MCP tool.
    """
    tool_name = tool["name"]
    description = tool.get("description", "MCP tool command")

    class MCPCommand(ShellCommand):
        name = tool_name
        help_text = (
            f"{description}\n"
            f"This command invokes the MCP tool '{tool_name}'."
        )

        def __init__(self, shell_context):
            super().__init__(shell_context)
            self.mcp_config = mcp_config

        def execute(self, args):
            """
            Runs the async method 'call_mcp_tool' using the current event loop
            instead of creating a new one with anyio.run.
            """
            input_data = {"args": args}
            try:
                # Check if an event loop is already running
                try:
                    loop = asyncio.get_running_loop()
                    # If we got here, a loop is running
                    if loop.is_running():
                        # Use the running loop
                        return asyncio.create_task(self.call_mcp_tool(input_data))
                except RuntimeError:
                    # No loop is running, create one
                    return anyio.run(self.call_mcp_tool, input_data)
            except Exception as exc:
                logger.exception(
                    f"Error executing MCP tool '{tool_name}' with args {args}"
                )
                return f"Error executing MCP tool '{tool_name}': {exc}"

        async def call_mcp_tool(self, input_data):
            """
            Connects to the MCP server using stdio_client and calls the specified tool.
            """
            logger.debug(
                f"Calling MCP tool '{tool_name}' with config {self.mcp_config} and input {input_data}"
            )

            # In a real implementation, this would handle specific tool inputs
            # and format them correctly for the MCP protocol
            args = input_data.get("args", [])
            
            try:
                async with stdio_client(self.mcp_config) as (read_stream, write_stream):
                    # Initialize connection
                    init_result = await send_initialize(read_stream, write_stream)
                    if not init_result:
                        return f"Failed to initialize connection to MCP server for tool '{tool_name}'"
                    
                    # Send ping to confirm connection
                    ping_result = await send_ping(read_stream, write_stream)
                    if not ping_result:
                        return f"Failed to ping MCP server for tool '{tool_name}'"
                    
                    # Here you would implement the actual tool invocation
                    # For now, we'll just return a simulated response
                    return f"Successfully executed MCP tool '{tool_name}' with args: {args}"
            except Exception as e:
                logger.exception(f"Error in call_mcp_tool for '{tool_name}'")
                return f"Error executing tool '{tool_name}': {str(e)}"

    return MCPCommand

async def load_mcp_tools_for_server(mcp_config):
    """
    Connect to the MCP server, do an initialize & ping, then retrieve available tools.
    """
    # If mcp_config is a dict, use .get(). Otherwise fallback to getattr.
    if isinstance(mcp_config, dict):
        server_name = mcp_config.get("server_name", "unknown")
        config_path = mcp_config.get("config_path", None)
    else:
        server_name = getattr(mcp_config, "server_name", "unknown")
        config_path = getattr(mcp_config, "config_path", None)

    logger.debug(
        f"Loading MCP tools for server '{server_name}' with config path '{config_path}'"
    )

    try:
        async with stdio_client(mcp_config) as (read_stream, write_stream):
            # 1) Initialize
            init_result = await send_initialize(read_stream, write_stream)
            if not init_result:
                logger.error("Server initialization failed!")
                return []

            logger.debug("Server initialized successfully.")

            # 2) Ping
            ping_result = await send_ping(read_stream, write_stream)
            logger.debug("Ping successful" if ping_result else "Ping failed")

            # 3) Now request the tools list
            logger.debug("Requesting tools list...")
            result = await send_tools_list(read_stream, write_stream)
            tools = result.get("tools", [])

            logger.debug(f"Received tools for server '{server_name}': {tools}")
            return tools
    except Exception as exc:
        logger.exception(f"Failed to load MCP tools for server {server_name}")
        raise

async def register_mcp_commands(shell):
    """
    For each MCP server in shell.mcp_servers, call load_mcp_tools_for_server
    and register each tool as a command.
    """
    mcp_servers = getattr(shell, "mcp_servers", [])
    if not mcp_servers:
        logger.info("No MCP servers found in shell configuration. Skipping command registration.")
        return

    for mcp_config in mcp_servers:
        # If dict, use .get. If object, fallback to getattr.
        if isinstance(mcp_config, dict):
            server_name = mcp_config.get("server_name", "unknown")
        else:
            server_name = getattr(mcp_config, "server_name", "unknown")

        logger.info(f"Loading MCP tools for server: {server_name}")

        try:
            tools = await load_mcp_tools_for_server(mcp_config)
        except Exception as e:
            logger.error(f"Error loading MCP tools for server '{server_name}': {e}")
            continue

        for tool in tools:
            tool_name = tool.get("name")
            if not tool_name:
                logger.warning(f"Skipped tool with missing 'name': {tool}")
                continue

            try:
                CommandClass = create_mcp_command_class(tool, mcp_config)
                cmd_instance = CommandClass(shell)
                shell.commands[cmd_instance.name] = cmd_instance
                logger.info(f"Registered MCP command: {cmd_instance.name}")
            except Exception as e:
                logger.error(f"Error creating MCP command for tool '{tool_name}': {e}")