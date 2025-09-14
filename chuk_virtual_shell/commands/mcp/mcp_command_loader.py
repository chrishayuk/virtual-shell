# src/chuk_virtual_shell/commands/mcp/mcp_command_loader.py
"""
chuk_virtual_shell/commands/mcp/mcp_command_loader.py - Load MCP commands dynamically

This module provides functionality to connect to MCP servers and dynamically
create and register commands for all tools available on those servers.
It delegates both input and output formatting to separate modules:
  - mcp_input_formatter.py
  - mcp_output_formatter.py
"""

import logging
from typing import List, Dict, Any

# Virtual Shell import
from chuk_virtual_shell.commands.command_base import ShellCommand

# MCP client imports
from chuk_mcp.mcp_client import send_tools_call  # type: ignore

# Import separate formatters
from chuk_virtual_shell.commands.mcp.mcp_output_formatter import (
    parse_mcp_response,
    format_mcp_result,
)
from chuk_virtual_shell.commands.mcp.mcp_input_formatter import format_mcp_input

logger = logging.getLogger(__name__)


def create_mcp_command_class(tool: Dict[str, Any], mcp_config: Any) -> type:
    """
    Dynamically create a command class for an MCP tool.

    Args:
        tool: Tool definition dictionary from the MCP server.
        mcp_config: Configuration for connecting to the MCP server.

    Returns:
        A dynamically created ShellCommand subclass for the tool.
    """
    tool_name = tool["name"]
    description = tool.get("description", "MCP tool command")
    input_schema = tool.get("inputSchema", {})

    class MCPCommand(ShellCommand):
        name = tool_name
        help_text = description
        category = "mcp"  # Categorize all MCP commands under "mcp"

        def __init__(self, shell_context):
            super().__init__(shell_context)
            self.mcp_config = mcp_config
            self.tool_schema = input_schema

        def execute(self, args):
            """
            Synchronous fallback indicating that async execution is preferred.
            """
            return f"MCP command '{tool_name}' should be executed asynchronously for best results."

        async def execute_async(self, args):
            """
            Asynchronously connect to the MCP server, execute the tool, and return formatted output.

            Args:
                args: Command-line arguments provided by the user.

            Returns:
                A user-friendly formatted string of the MCP tool output.
            """
            logger.debug(f"Executing MCP command '{tool_name}' with args: {args}")

            # Delegate input formatting to the input formatter module.
            input_data = format_mcp_input(args, self.tool_schema)

            try:
                # Import here to avoid circular references.
                from chuk_mcp.mcp_client.transport.stdio.stdio_client import (  # type: ignore
                    stdio_client,
                )
                from chuk_mcp.mcp_client.messages.initialize.send_messages import (  # type: ignore
                    send_initialize,
                )
                from chuk_mcp.mcp_client.messages.ping.send_messages import send_ping  # type: ignore

                # Connect to the MCP server.
                async with stdio_client(self.mcp_config) as (read_stream, write_stream):
                    init_result = await send_initialize(read_stream, write_stream)
                    if not init_result:
                        return f"Failed to initialize connection to MCP server for tool '{tool_name}'"

                    # Confirm connection with a ping.
                    ping_result = await send_ping(read_stream, write_stream)
                    if not ping_result:
                        return f"Failed to ping MCP server for tool '{tool_name}'"

                    # Execute the tool.
                    response = await send_tools_call(
                        read_stream, write_stream, tool_name, input_data
                    )
                    if not response:
                        return f"Failed to execute tool '{tool_name}' - no response received"

                    if "error" in response:
                        error_data = response.get("error", {})
                        error_msg = error_data.get("message", str(error_data))
                        return f"Error executing tool '{tool_name}': {error_msg}"

                    # Delegate output formatting:
                    parsed_data = parse_mcp_response(response)
                    return format_mcp_result(parsed_data)

            except Exception as e:
                logger.exception(f"Error executing MCP tool '{tool_name}'")
                return f"Error executing MCP tool '{tool_name}': {str(e)}"

    return MCPCommand


async def load_mcp_tools_for_server(mcp_config: Any) -> List[Dict[str, Any]]:
    """
    Connect to an MCP server and retrieve its available tools.

    Args:
        mcp_config: Configuration for connecting to the MCP server.

    Returns:
        A list of tool definitions (dictionaries) from the server.
    """
    if isinstance(mcp_config, dict):
        server_name = mcp_config.get("server_name", "unknown")
    else:
        server_name = getattr(mcp_config, "server_name", "unknown")

    logger.info(f"Loading tools from MCP server: {server_name}")

    try:
        from chuk_mcp.mcp_client import (
            stdio_client,
            send_initialize,
            send_ping,
            send_tools_list,
        )  # type: ignore

        async with stdio_client(mcp_config) as (read_stream, write_stream):
            # Initialize connection with a 15-second timeout.
            init_result = await send_initialize(read_stream, write_stream, timeout=15.0)
            if not init_result:
                logger.error(
                    f"Failed to initialize connection to MCP server: {server_name}"
                )
                return []
            logger.debug(
                f"Successfully initialized connection to MCP server: {server_name}"
            )

            # Confirm connection with a ping.
            ping_result = await send_ping(read_stream, write_stream)
            if not ping_result:
                logger.error(f"Failed to ping MCP server: {server_name}")
                return []
            logger.debug(f"Successfully pinged MCP server: {server_name}")

            # Retrieve the list of tools.
            tools_result = await send_tools_list(read_stream, write_stream)
            tools = tools_result.get("tools", [])

            logger.info(f"Loaded {len(tools)} tools from MCP server: {server_name}")
            logger.debug(f"Tool names: {[tool.get('name') for tool in tools]}")

            return tools

    except Exception:
        logger.exception(f"Error loading tools from MCP server: {server_name}")
        return []


async def register_mcp_commands(shell) -> None:
    """
    Register commands for all tools available on all configured MCP servers.

    Args:
        shell: The shell interpreter to register commands with.
    """
    mcp_servers = getattr(shell, "mcp_servers", [])
    if not mcp_servers:
        logger.info("No MCP servers configured, skipping command registration")
        return

    logger.info(f"Registering commands from {len(mcp_servers)} MCP servers")

    for mcp_config in mcp_servers:
        try:
            if isinstance(mcp_config, dict):
                server_name = mcp_config.get("server_name", "unknown")
            else:
                server_name = getattr(mcp_config, "server_name", "unknown")

            logger.info(f"Loading tools from MCP server: {server_name}")
            tools = await load_mcp_tools_for_server(mcp_config)

            for tool in tools:
                tool_name = tool.get("name")
                if not tool_name:
                    logger.warning("Skipping tool with missing name")
                    continue

                try:
                    command_class = create_mcp_command_class(tool, mcp_config)
                    command = command_class(shell)
                    shell._register_command(command)
                    logger.info(f"Registered MCP command: {tool_name}")
                except Exception as exc:
                    logger.exception(
                        f"Error registering MCP command for tool '{tool_name}': {exc}"
                    )

        except Exception:
            logger.exception(f"Error processing MCP server: {server_name}")
