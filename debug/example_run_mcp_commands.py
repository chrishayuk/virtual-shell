#!/usr/bin/env python
# chuk_mcp/debug/example_run_mcp_commands.py
import anyio
import logging
import sys

# From chuk_mcp
from chuk_mcp.config import load_config
from chuk_mcp.mcp_client.messages.initialize.send_messages import send_initialize
from chuk_mcp.mcp_client.messages.ping.send_messages import send_ping
from chuk_mcp.mcp_client.messages.tools.send_messages import send_tools_list
from chuk_mcp.mcp_client.transport.stdio.stdio_client import stdio_client

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)


async def main():
    print("=== Starting Example MCP Run Script ===")

    # Update these as needed
    config_path = "server_config.json"
    server_name = "sqlite"

    try:
        server_params = await load_config(config_path, server_name)
    except Exception as e:
        print(f"Failed to load config: {e}")
        return

    # Connect and interact with the MCP server
    async with stdio_client(server_params) as (read_stream, write_stream):
        init_result = await send_initialize(read_stream, write_stream)
        if not init_result:
            print("Server initialization failed")
            return
        print("We're connected!!!")

        # Send a ping
        ping_result = await send_ping(read_stream, write_stream)
        print("Ping successful" if ping_result else "Ping failed")

        # Request the tool list
        tools_result = await send_tools_list(read_stream, write_stream)
        if tools_result is not None:
            print("Tools available on the server:")
            print(tools_result)
        else:
            print("Failed to retrieve tools list")

    print("=== Example MCP Run Script End ===")


def run():
    """Synchronous wrapper for our async main()."""
    anyio.run(main)


if __name__ == "__main__":
    run()
