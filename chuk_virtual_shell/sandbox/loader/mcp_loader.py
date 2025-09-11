"""
chuk_virtual_shell/sandbox/loader/mcp_loader.py - MCP configuration and command loading

This module handles loading MCP server configurations from a sandbox and
initializing MCP commands for the shell.
"""

import logging
import traceback
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


def load_mcp_servers(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract the list of MCP server configurations from the sandbox config.

    Args:
        config: The sandbox configuration dictionary.

    Returns:
        A list of MCP server configuration dictionaries.
        Each config should contain at least keys like "config_path" and "server_name".
    """
    logger.debug(f"Loading MCP servers from config: {type(config)}")

    if "mcp_servers" not in config:
        logger.warning("No 'mcp_servers' section found in config")
        return []

    mcp_servers = config.get("mcp_servers", [])
    logger.debug(f"Raw MCP server configurations: {mcp_servers}")

    if not isinstance(mcp_servers, list):
        logger.error(f"'mcp_servers' section is not a list: {type(mcp_servers)}")
        return []

    validated_servers = []

    for i, server in enumerate(mcp_servers):
        logger.debug(f"Processing MCP server {i}: {server}")

        if not isinstance(server, dict):
            logger.warning(f"MCP server config is not a dictionary: {type(server)}")
            continue

        # Filter out servers missing required keys instead of applying defaults
        if "config_path" not in server or "server_name" not in server:
            logger.warning(f"MCP server missing required keys, skipping: {server}")
            continue

        validated_servers.append(server)

    logger.info(f"Loaded {len(validated_servers)} MCP server configurations")
    logger.debug(f"Validated MCP servers: {validated_servers}")
    return validated_servers


async def register_mcp_commands_with_shell(shell) -> Optional[str]:
    """
    Register MCP commands with a shell instance.

    This function takes a shell instance and registers MCP commands with it
    based on its configured MCP servers.

    Args:
        shell: The shell interpreter instance

    Returns:
        str: Error message if something went wrong, None if successful
    """
    if not hasattr(shell, "mcp_servers"):
        logger.warning("Shell instance does not have 'mcp_servers' attribute")
        return "Shell instance does not have 'mcp_servers' attribute"

    if not shell.mcp_servers:
        logger.info("No MCP servers configured, skipping MCP command registration")
        return None

    # Enhanced debugging
    logger.debug(f"MCP servers type: {type(shell.mcp_servers)}")
    logger.debug(f"MCP servers content: {shell.mcp_servers}")

    try:
        # Import the MCP command loader with updated import path
        try:
            from chuk_virtual_shell.commands.mcp.mcp_command_loader import (
                register_mcp_commands,
            )
        except ImportError as e:
            logger.error(f"Error importing MCP command loader: {e}")
            traceback.print_exc()
            return f"Error importing MCP command loader: {e}"

        await register_mcp_commands(shell)
        logger.info(
            f"MCP commands registered successfully for {len(shell.mcp_servers)} servers"
        )
        return None
    except Exception as e:
        error_msg = f"Error registering MCP commands: {str(e)}"
        logger.exception(error_msg)
        return error_msg


async def initialize_mcp(shell) -> Optional[str]:
    """
    Complete initialization of MCP for a shell.

    This is a convenience function that can be called during shell
    initialization to set up all MCP-related functionality.

    Args:
        shell: The shell interpreter instance

    Returns:
        str: Error message if something went wrong, None if successful
    """
    # Register commands for any MCP servers already configured
    return await register_mcp_commands_with_shell(shell)
