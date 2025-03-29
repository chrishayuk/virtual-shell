# chuk_virtual_shell/commands/mcp_command_loader.py
import anyio
import uuid

# virtual shell loads
from chuk_virtual_shell.commands.command_base import ShellCommand

# chuk mcp loads
from chuk_mcp.mcp_client.transport.stdio.stdio_client import stdio_client
from chuk_mcp.mcp_client.messages.tools.send_messages import send_tools_list

def create_mcp_command_class(tool, mcp_config):
    """
    Dynamically create a command class for an MCP tool.
    
    Args:
        tool (dict): A dictionary representing an MCP tool (must have at least a "name" key).
        mcp_config (dict): The configuration for the MCP server.
    
    Returns:
        A new ShellCommand subclass that calls the MCP tool.
    """
    tool_name = tool["name"]
    description = tool.get("description", "MCP tool command")

    class MCPCommand(ShellCommand):
        name = tool_name
        help_text = f"{description}\nThis command invokes the MCP tool '{tool_name}'."

        def __init__(self, shell_context):
            super().__init__(shell_context)
            # Save the MCP configuration for later use.
            self.mcp_config = mcp_config

        def execute(self, args):
            # For simplicity, we'll pass the arguments as-is.
            # You can extend this to parse the args or validate them against tool["inputSchema"].
            input_data = {"args": args}
            # Run the asynchronous MCP call using anyio.
            result = anyio.run(self.call_mcp_tool, input_data)
            return result

        async def call_mcp_tool(self, input_data):
            """
            Connects to the MCP server and calls the specified tool.
            """
            # Extract necessary parameters from the configuration.
            config_path = self.mcp_config.get("config_path")
            server_name = self.mcp_config.get("server_name")

            # Establish a connection using stdio_client.
            async with stdio_client({"config_path": config_path, "server_name": server_name}) as (read_stream, write_stream):
                # For demonstration, we simply return a message.
                # In practice, match tool_name to an appropriate MCP call.
                # For example, if tool_name == "ping", you could call an async send_ping function.
                # Here we simulate a tool invocation:
                await anyio.sleep(0.1)  # simulate network latency
                return f"Invoked MCP tool '{tool_name}' with input: {input_data}"

    return MCPCommand

async def load_mcp_tools_for_server(mcp_config):
    """
    Connect to an MCP server using the provided configuration and retrieve available tools.
    
    Args:
        mcp_config (dict): MCP server configuration.
    
    Returns:
        list: A list of tool dictionaries.
    """
    async with stdio_client(mcp_config) as (read_stream, write_stream):
        # Send the tools list request. Adjust this if your protocol is different.
        result = await send_tools_list(read_stream, write_stream)
        # Expect the result to have a "tools" key with a list of tool definitions.
        return result.get("tools", [])

def register_mcp_commands(shell):
    """
    For each MCP server defined in the shell's configuration, retrieve tools and register
    corresponding commands into the shell.
    
    Args:
        shell: Your shell interpreter instance.
    """
    # Retrieve the list of MCP servers from the shell. Ensure your sandbox loader
    # sets an attribute like `shell.mcp_servers` when processing the sandbox config.
    mcp_servers = getattr(shell, "mcp_servers", [])
    for mcp_config in mcp_servers:
        try:
            # Load the available tools asynchronously.
            tools = anyio.run(load_mcp_tools_for_server, mcp_config)
        except Exception as e:
            print(f"Error loading MCP tools for server {mcp_config.get('server_name')}: {e}")
            continue

        for tool in tools:
            try:
                # Create the dynamic command class for the tool.
                CommandClass = create_mcp_command_class(tool, mcp_config)
                # Instantiate the command and register it in the shell's commands dictionary.
                command_instance = CommandClass(shell)
                shell.commands[command_instance.name] = command_instance
                print(f"Registered MCP command: {command_instance.name}")
            except Exception as e:
                print(f"Error creating MCP command for tool '{tool.get('name')}': {e}")
