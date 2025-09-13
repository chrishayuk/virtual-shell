# src/chuk_virtual_shell/commands/mcp/__imit__.py
"""
chuk_virtual_shell/commands/mcp/__init__.py - MCP command package

This package contains the MCP command loading and execution functionality.
"""

# For convenience, expose important functions at the package level
from chuk_virtual_shell.commands.mcp.mcp_command_loader import (
    register_mcp_commands,
    load_mcp_tools_for_server,
    create_mcp_command_class,
)

__all__ = [
    "register_mcp_commands",
    "load_mcp_tools_for_server",
    "create_mcp_command_class",
]
