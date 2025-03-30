"""
chuk_virtual_shell/sandbox/loader/mcp_loader.py - MCP configuration and command loading

This module handles loading MCP server configurations from a sandbox and
initializing MCP commands for the shell.
"""
import logging
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
    mcp_servers = config.get("mcp_servers", [])
    validated_servers = []
    
    for server in mcp_servers:
        if "config_path" not in server or "server_name" not in server:
            logger.warning(f"MCP server configuration missing required keys: {server}")
            continue
        validated_servers.append(server)

    logger.info(f"Loaded {len(validated_servers)} MCP server configurations")
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
    if not hasattr(shell, 'mcp_servers') or not shell.mcp_servers:
        logger.info("No MCP servers configured, skipping MCP command registration")
        return None
        
    try:
        # Import the MCP command loader with updated import path
        from chuk_virtual_shell.commands.mcp.mcp_command_loader import register_mcp_commands
        await register_mcp_commands(shell)
        logger.info(f"MCP commands registered successfully for {len(shell.mcp_servers)} servers")
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