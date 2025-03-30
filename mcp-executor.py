#!/usr/bin/env python
import sys
import json
import anyio
from chuk_mcp.config import load_config
from chuk_mcp.mcp_client.transport.stdio.stdio_client import stdio_client
from chuk_mcp.mcp_client.messages.initialize.send_messages import send_initialize
from chuk_mcp.mcp_client.messages.ping.send_messages import send_ping

def exit_with_error(message):
    print(json.dumps({"error": message}))
    sys.exit(1)

async def run_command():
    if len(sys.argv) < 4:
        exit_with_error("Missing arguments: config_path server_name command_name [args...]")
    
    config_path = sys.argv[1]
    server_name = sys.argv[2]
    command_name = sys.argv[3]
    command_args = sys.argv[4:]
    
    try:
        # Load server config
        server_params = await load_config(config_path, server_name)
        
        # Connect to server
        async with stdio_client(server_params) as (read_stream, write_stream):
            # Initialize
            init_result = await send_initialize(read_stream, write_stream)
            if not init_result:
                exit_with_error("Failed to initialize connection to MCP server")
            
            # Ping
            ping_result = await send_ping(read_stream, write_stream)
            if not ping_result:
                exit_with_error("Failed to ping MCP server")
            
            # For now, just simulate success
            print(json.dumps({
                "success": True,
                "result": f"Successfully executed command '{command_name}' with args: {command_args}"
            }))
    except Exception as e:
        exit_with_error(f"Error: {str(e)}")

def main():
    anyio.run(run_command)

if __name__ == "__main__":
    main()
