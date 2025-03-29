# chuk_virtual_shell/sandbox/loader/mcp_config_loader.py
"""
Module for extracting and validating MCP server configurations
from a sandbox configuration.
"""
from typing import Dict, Any, List

def load_mcp_servers(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract the list of MCP server configurations from the sandbox config.
    
    Args:
        config: The sandbox configuration dictionary.
    
    Returns:
        A list of MCP server configuration dictionaries.
        Each config should contain at least keys like "config_path" and "server_name".
    """
    # get the mcp servers
    mcp_servers = config.get("mcp_servers", [])
    validated_servers = []
    
    # load the servers
    for server in mcp_servers:
        if "config_path" not in server or "server_name" not in server:
            print(f"Warning: MCP server configuration is missing required keys: {server}")
            continue
        validated_servers.append(server)

    # return the servers
    return validated_servers
