#!/usr/bin/env python
"""
example_mcp_shell.py - Example script demonstrating async mcp shell commands

This example shows how to:
1. Initialize the shell interpreter
2. Register MCP commands asynchronously
3. Execute both sync and async commands
"""

import asyncio
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)

# Import required modules
from chuk_virtual_shell.shell_interpreter import ShellInterpreter
from chuk_virtual_shell.sandbox.loader.mcp_loader import initialize_mcp


def create_config_object(**kwargs):
    """Create a simple configuration object from kwargs"""

    class ConfigObject:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    return ConfigObject(**kwargs)


async def main():
    print("=== Starting Example Async Shell ===")

    # Create shell interpreter
    shell = ShellInterpreter()

    # For this example, we'll manually set up an MCP server config
    # In a real application, this would typically come from a sandbox config
    mcp_config = create_config_object(
        server_name="sqlite",
        command="uvx",
        args=["mcp-server-sqlite", "--db-path", "test.db"],
        env=None,
        config_path="server_config.json",
    )

    # Set the MCP server configuration on the shell
    shell.mcp_servers = [mcp_config]

    # Initialize MCP commands
    print("\nInitializing MCP commands...")
    error = await initialize_mcp(shell)
    if error:
        print(f"Warning: {error}")
        print("Continuing with available commands...")

    # Display available commands
    print("\nAvailable commands:")

    # Group commands by category for better display
    commands_by_category = {}
    for name, cmd in sorted(shell.commands.items()):
        category = cmd.get_category() or "general"
        if category not in commands_by_category:
            commands_by_category[category] = []
        commands_by_category[category].append((name, cmd))

    # Display commands by category
    for category, commands in sorted(commands_by_category.items()):
        print(f"\n{category.upper()} COMMANDS:")
        for name, cmd in commands:
            print(
                f"  - {name}: {cmd.help_text[:40]}{'...' if len(cmd.help_text) > 40 else ''}"
            )

    # Run some standard commands synchronously
    print("\nExecuting commands synchronously:")
    for cmd_line in ["pwd", "echo Hello from the enhanced shell!", "ls /home"]:
        print(f"\n> {cmd_line}")
        result = shell.execute(cmd_line)
        print(result)

    # Run MCP commands using async execution
    # These will only work if MCP initialization succeeded
    print("\nExecuting MCP commands asynchronously:")
    for cmd_line in ["list_tables", "read_query SELECT * FROM example LIMIT 5"]:
        print(f"\n> {cmd_line}")
        if cmd_line.split()[0] in shell.commands:
            result = await shell.execute_async(cmd_line)
            print(result)
        else:
            print(f"Command not available: {cmd_line.split()[0]}")

    print("\n=== Example Complete ===")


if __name__ == "__main__":
    asyncio.run(main())
