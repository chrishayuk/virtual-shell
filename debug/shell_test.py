import asyncio
import logging
from chuk_virtual_shell.shell_interpreter import ShellInterpreter
from chuk_virtual_shell.sandbox.loader.mcp_loader import initialize_mcp

# Set up logging
logging.basicConfig(level=logging.DEBUG)


def convert_dict_to_object(d):
    """Convert a dictionary to an object with attributes"""

    class ConfigObject:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    return ConfigObject(**d)


async def main():
    # Create the shell with your sandbox config
    shell = ShellInterpreter(
        sandbox_yaml="/Users/christopherhay/chris-source/agent-x/chuk-virtual-shell/config/default.yaml"
    )

    # Convert dictionary MCP configs to objects with attributes
    if shell.mcp_servers:
        print(f"Original MCP servers: {shell.mcp_servers}")
        shell.mcp_servers = [
            convert_dict_to_object(server) for server in shell.mcp_servers
        ]
        print(f"Converted MCP servers: {shell.mcp_servers}")

        # Now initialize MCP commands
        result = await initialize_mcp(shell)
        print(f"MCP initialization result: {result}")

        # List registered MCP commands
        print("MCP commands registered:")
        for name, cmd in shell.commands.items():
            if hasattr(cmd, "get_category") and cmd.get_category() == "mcp":
                print(f"  - {name}")
    else:
        print("No MCP servers configured")


asyncio.run(main())
