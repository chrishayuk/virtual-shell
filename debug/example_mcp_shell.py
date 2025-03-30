#!/usr/bin/env python
# chuk_virtual_shell/debug/example_mcp_shell
import anyio
import logging
import sys
import os
import subprocess
import json
import time

# 1) Import configuration loader
from chuk_mcp.config import load_config

# 2) Import the MCP command loader
from chuk_virtual_shell.commands.mcp_command_loader import register_mcp_commands

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stderr
)

class ExampleShell:
    """
    A minimal shell that holds a dict of commands + a list of MCP server configs.
    """
    def __init__(self, mcp_servers=None):
        self.commands = {}
        self.mcp_servers = mcp_servers or []

    def run_command(self, name, args):
        """
        Look up and run a command by name.
        Since we can't run async commands directly from within our existing event loop,
        we'll run them in a separate process.
        """
        command = self.commands.get(name)
        if not command:
            print(f"No such command: {name}")
            return None
            
        # For debugging purposes, run a simple mcp-executor.py script
        # that handles executing the command separately
        print(f"Executing '{name}' with args {args} in a separate process...")
        
        # Create a temporary executor script
        with open("mcp-executor.py", "w") as f:
            f.write("""#!/usr/bin/env python
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
""")
        
        # Make the script executable
        os.chmod("mcp-executor.py", 0o755)
        
        # Execute the command in a separate process
        try:
            config_path = self.mcp_servers[0].config_path
            server_name = self.mcp_servers[0].server_name
            
            result = subprocess.run(
                [sys.executable, "mcp-executor.py", config_path, server_name, name] + args,
                capture_output=True,
                text=True,
                check=True
            )
            
            try:
                return json.loads(result.stdout.strip())
            except json.JSONDecodeError:
                return f"Error parsing response: {result.stdout}"
                
        except subprocess.CalledProcessError as e:
            return f"Error executing command: {e.stderr}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

def prepare_config(config_obj, server_name, config_path):
    """
    Ensure configuration has necessary attributes, whether it's a dict or object.
    Returns a configuration object with attributes (not a dict).
    """
    # First make sure we have a dict with all fields
    try:
        if hasattr(config_obj, "model_dump"):
            # Pydantic v2
            config_dict = config_obj.model_dump()
        elif hasattr(config_obj, "dict"):
            # Pydantic v1
            config_dict = config_obj.dict()
        else:
            # Try to convert to dict if it's already an object
            try:
                config_dict = {k: getattr(config_obj, k) for k in dir(config_obj) 
                            if not k.startswith('_') and not callable(getattr(config_obj, k))}
            except:
                # fallback if above fails
                config_dict = dict(config_obj)
    except Exception:
        # If it's already a dict, use it directly
        config_dict = dict(config_obj)

    # Ensure these fields are set
    config_dict.setdefault("server_name", server_name)
    config_dict.setdefault("config_path", config_path)
    
    # Convert back to an object with attributes
    class ConfigObject:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
                
    return ConfigObject(**config_dict)

async def start_server_and_wait(config_obj, max_retries=3, retry_delay=2):
    """
    Helper function to start server and wait for it to be ready
    with retries and delay between attempts.
    """
    from chuk_mcp.mcp_client.transport.stdio.stdio_client import stdio_client
    from chuk_mcp.mcp_client.messages.initialize.send_messages import send_initialize
    
    for attempt in range(1, max_retries + 1):
        print(f"Attempt {attempt}/{max_retries} to connect to MCP server...")
        
        try:
            # Use a longer timeout for initialization
            async with stdio_client(config_obj) as (read_stream, write_stream):
                # Try to initialize with a longer timeout (15 seconds)
                init_result = await send_initialize(read_stream, write_stream)
                if init_result:
                    print(f"Successfully connected to MCP server on attempt {attempt}")
                    return True
        except Exception as e:
            print(f"Connection attempt {attempt} failed: {e}")
        
        if attempt < max_retries:
            print(f"Waiting {retry_delay} seconds before next attempt...")
            await anyio.sleep(retry_delay)
    
    print(f"Failed to connect to MCP server after {max_retries} attempts")
    return False

async def main():
    print("=== Starting Example MCP Run Script via Command Loader ===")

    # Identify the config JSON + server name
    config_path = "server_config.json"
    server_name = "sqlite"

    try:
        # Load config from JSON
        server_params = await load_config(config_path, server_name)
    except Exception as e:
        print(f"Failed to load config: {e}")
        return

    print("Loaded config:")
    print(server_params)

    # Convert to object with attributes, ensuring server_name + config_path are set
    config_obj = prepare_config(server_params, server_name, config_path)
    print("Final configuration (object):")
    print(vars(config_obj))  # Shows the object's attributes as a dict

    # Pre-check server availability
    server_ready = await start_server_and_wait(config_obj)
    if not server_ready:
        print("Unable to establish initial connection to MCP server. Check server status.")
        return

    # Create shell with this config object
    shell = ExampleShell(mcp_servers=[config_obj])

    print("Registering MCP commands via command loader...")
    try:
        await register_mcp_commands(shell)
    except Exception as e:
        print(f"Error during command registration: {e}")
        return
    print("Command registration complete!")

    # List registered commands
    if shell.commands:
        print("\nCommands registered in the shell:")
        for cmd_name, cmd_obj in shell.commands.items():
            print(f"  - {cmd_name}: {cmd_obj.help_text}")
    else:
        print("No commands registered. Check your config or logs for errors.")
        return

    # Optionally run one command
    command_to_run = "list_tables"  # Using a command that doesn't require arguments
    if command_to_run in shell.commands:
        print(f"\nRunning '{command_to_run}':")
        output = shell.run_command(command_to_run, [])
        print("Command output:", output)
    else:
        print(f"\nCommand '{command_to_run}' not found among registered commands.")

    print("=== Example MCP Run Script End ===")

def run():
    anyio.run(main)

if __name__ == "__main__":
    run()