# chuk_virtual_shell/sandbox/loader/mcp_config_loader.py
"""
Module for extracting and validating MCP server configurations
from a sandbox configuration.
"""
import logging
from typing import Dict, Any, List

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

    return validated_servers

