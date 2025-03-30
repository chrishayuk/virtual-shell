"""
tests/commands/mcp/test_mcp_command_loader.py - Tests for MCP command loader

Tests the core functionality of the MCP command loader, including:
- Creating command classes from tool definitions
- Loading tools from MCP servers
- Registering MCP commands with the shell
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from chuk_virtual_shell.commands.command_base import ShellCommand
from chuk_virtual_shell.commands.mcp.mcp_command_loader import (
    create_mcp_command_class,
    load_mcp_tools_for_server,
    register_mcp_commands,
)

# Tests for create_mcp_command_class
def test_create_mcp_command_class_basic():
    """Test that create_mcp_command_class builds a basic command correctly"""
    # Arrange
    tool = {
        "name": "test_tool",
        "description": "A test tool",
    }
    config = {
        "server_name": "test_server",
        "config_path": "test_config.json",
    }
    
    # Act
    CommandClass = create_mcp_command_class(tool, config)
    
    # Assert
    assert issubclass(CommandClass, ShellCommand)
    assert CommandClass.name == "test_tool"
    assert CommandClass.category == "mcp"
    assert "A test tool" in CommandClass.help_text
    
    # Test instance creation
    shell_context = MagicMock()
    instance = CommandClass(shell_context)
    assert instance.mcp_config == config

def test_create_mcp_command_class_with_input_schema():
    """Test command creation with different input schemas"""
    # Test with query-type tool
    query_tool = {
        "name": "query_tool",
        "description": "A query tool",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "SQL query"
                }
            },
            "required": ["query"]
        }
    }
    
    # Create the command class
    CommandClass = create_mcp_command_class(query_tool, {})
    cmd = CommandClass(MagicMock())
    
    # Test the _format_input method with a query
    input_data = cmd._format_input(["SELECT", "*", "FROM", "table"])
    assert "query" in input_data
    assert input_data["query"] == "SELECT * FROM table"
    
    # Test with table name type tool
    table_tool = {
        "name": "table_tool",
        "description": "A table tool",
        "inputSchema": {
            "type": "object",
            "properties": {
                "table_name": {
                    "type": "string",
                    "description": "Table name"
                }
            },
            "required": ["table_name"]
        }
    }
    
    # Create the command class
    CommandClass = create_mcp_command_class(table_tool, {})
    cmd = CommandClass(MagicMock())
    
    # Test the _format_input method with a table name
    input_data = cmd._format_input(["users"])
    assert "table_name" in input_data
    assert input_data["table_name"] == "users"
    
    # Test with no-args tool
    no_args_tool = {
        "name": "no_args_tool",
        "description": "A tool without arguments",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    }
    
    # Create the command class
    CommandClass = create_mcp_command_class(no_args_tool, {})
    cmd = CommandClass(MagicMock())
    
    # Test the _format_input method with no arguments
    input_data = cmd._format_input([])
    assert input_data == {}

def test_mcp_command_execution():
    """Test that MCP commands return appropriate messages when executed"""
    # Create a command class
    tool = {"name": "test_cmd", "description": "Test command"}
    CommandClass = create_mcp_command_class(tool, {})
    cmd = CommandClass(MagicMock())
    
    # Test the execute method - should return a message about async execution
    result = cmd.execute(["arg1", "arg2"])
    assert isinstance(result, str)
    assert "should be executed asynchronously" in result
    assert "test_cmd" in result

# Tests for load_mcp_tools_for_server
@pytest.mark.anyio
async def test_load_mcp_tools_for_server():
    """Test that load_mcp_tools_for_server handles initialization and tool retrieval"""
    # Create mocks for external dependencies
    mock_read_stream = AsyncMock()
    mock_write_stream = AsyncMock()
    
    # Create a context manager for stdio_client
    mock_stdio_context = AsyncMock()
    mock_stdio_context.__aenter__.return_value = (mock_read_stream, mock_write_stream)
    mock_stdio_context.__aexit__.return_value = None
    
    # Apply patches
    with patch("chuk_mcp.mcp_client.transport.stdio.stdio_client.stdio_client", 
               return_value=mock_stdio_context, autospec=True) as mock_stdio_client, \
         patch("chuk_mcp.mcp_client.messages.initialize.send_messages.send_initialize", 
               return_value=True, autospec=True) as mock_send_initialize, \
         patch("chuk_mcp.mcp_client.messages.ping.send_messages.send_ping", 
               return_value=True, autospec=True) as mock_send_ping, \
         patch("chuk_mcp.mcp_client.messages.tools.send_messages.send_tools_list", 
               return_value={"tools": [{"name": "tool1"}, {"name": "tool2"}]}, 
               autospec=True) as mock_send_tools_list:
        
        # Create config object
        config = {
            "server_name": "test_server",
            "config_path": "test_config.json"
        }
        
        # Call the function under test
        tools = await load_mcp_tools_for_server(config)
        
        # Verify the right calls were made
        mock_stdio_client.assert_called_once_with(config)
        mock_send_initialize.assert_awaited_once()
        mock_send_ping.assert_awaited_once()
        mock_send_tools_list.assert_awaited_once()
        
        # Verify we got the expected tools back
        assert tools == [{"name": "tool1"}, {"name": "tool2"}]

@pytest.mark.anyio
async def test_load_mcp_tools_initialization_failure():
    """Test that load_mcp_tools_for_server handles initialization failure"""
    # Create mocks for external dependencies
    mock_read_stream = AsyncMock()
    mock_write_stream = AsyncMock()
    
    # Create a context manager for stdio_client
    mock_stdio_context = AsyncMock()
    mock_stdio_context.__aenter__.return_value = (mock_read_stream, mock_write_stream)
    mock_stdio_context.__aexit__.return_value = None
    
    # Apply patches - this time with initialize returning False
    with patch("chuk_mcp.mcp_client.transport.stdio.stdio_client.stdio_client", 
               return_value=mock_stdio_context, autospec=True), \
         patch("chuk_mcp.mcp_client.messages.initialize.send_messages.send_initialize", 
               return_value=False, autospec=True):  # Initialize fails
        
        # Create config object
        config = {
            "server_name": "test_server",
            "config_path": "test_config.json"
        }
        
        # Call the function under test
        tools = await load_mcp_tools_for_server(config)
        
        # Verify we got an empty list back
        assert tools == []

# Tests for register_mcp_commands
@pytest.mark.anyio
async def test_register_mcp_commands():
    """Test that register_mcp_commands loads tools and registers them correctly"""
    # Create a mock shell
    class MockShell:
        def __init__(self):
            self.commands = {}
            self.mcp_servers = [
                {"server_name": "server1"}, 
                {"server_name": "server2"}
            ]
        
        def _register_command(self, cmd):
            self.commands[cmd.name] = cmd
    
    shell = MockShell()
    
    # Create a mock for load_mcp_tools_for_server that returns different tools for different servers
    async def mock_load_tools(config):
        server_name = config.get("server_name", "")
        if server_name == "server1":
            return [{"name": "tool1a"}, {"name": "tool1b"}]
        elif server_name == "server2":
            return [{"name": "tool2"}]
        return []
    
    # Create a mock for create_mcp_command_class
    def mock_create_command(tool, config):
        # Create a simple command class that just stores its name
        class MockCommand(ShellCommand):
            name = tool.get("name", "unknown")
            category = "mcp"
            help_text = "Mock command"
            
            def __init__(self, shell):
                super().__init__(shell)
                self.config = config
                
            def execute(self, args):
                return f"Executed {self.name}"
        
        return MockCommand
    
    # Apply patches
    with patch("chuk_virtual_shell.commands.mcp.mcp_command_loader.load_mcp_tools_for_server", 
               side_effect=mock_load_tools) as mock_load, \
         patch("chuk_virtual_shell.commands.mcp.mcp_command_loader.create_mcp_command_class", 
               side_effect=mock_create_command) as mock_create:
        
        # Call the function under test
        await register_mcp_commands(shell)
        
        # Verify the expected calls
        assert mock_load.call_count == 2  # Called once for each server
        assert mock_create.call_count == 3  # Called once for each tool (3 total)
        
        # Verify the commands were registered
        assert len(shell.commands) == 3
        assert "tool1a" in shell.commands
        assert "tool1b" in shell.commands
        assert "tool2" in shell.commands
        
        # Verify a command's behavior
        cmd = shell.commands["tool1a"]
        assert cmd.name == "tool1a"
        assert cmd.category == "mcp"
        assert cmd.execute([]) == "Executed tool1a"

@pytest.mark.anyio
async def test_register_mcp_commands_with_empty_server_list():
    """Test that register_mcp_commands handles an empty server list"""
    # Create a mock shell with no servers
    class MockShell:
        def __init__(self):
            self.commands = {}
            self.mcp_servers = []
    
    shell = MockShell()
    
    # Apply a patch to ensure load_mcp_tools_for_server isn't called
    with patch("chuk_virtual_shell.commands.mcp.mcp_command_loader.load_mcp_tools_for_server") as mock_load:
        # Call the function under test
        await register_mcp_commands(shell)
        
        # Verify load_mcp_tools_for_server wasn't called
        mock_load.assert_not_called()
        
        # Verify no commands were registered
        assert len(shell.commands) == 0

@pytest.mark.anyio
async def test_register_mcp_commands_with_server_error():
    """Test that register_mcp_commands handles errors with a specific server"""
    # Create a mock shell
    class MockShell:
        def __init__(self):
            self.commands = {}
            self.mcp_servers = [
                {"server_name": "good_server"}, 
                {"server_name": "bad_server"}
            ]
        
        def _register_command(self, cmd):
            self.commands[cmd.name] = cmd
    
    shell = MockShell()
    
    # Create a mock for load_mcp_tools_for_server that raises an exception for the bad server
    async def mock_load_tools(config):
        server_name = config.get("server_name", "")
        if server_name == "good_server":
            return [{"name": "good_tool"}]
        elif server_name == "bad_server":
            raise Exception("Server connection error")
        return []
    
    # Create a simple mock for create_mcp_command_class
    def mock_create_command(tool, config):
        class MockCommand(ShellCommand):
            name = tool.get("name", "unknown")
            category = "mcp"
            
            def execute(self, args):
                return f"Executed {self.name}"
        
        return MockCommand
    
    # Apply patches
    with patch("chuk_virtual_shell.commands.mcp.mcp_command_loader.load_mcp_tools_for_server", 
               side_effect=mock_load_tools), \
         patch("chuk_virtual_shell.commands.mcp.mcp_command_loader.create_mcp_command_class", 
               side_effect=mock_create_command):
        
        # Call the function under test
        await register_mcp_commands(shell)
        
        # Verify only the good server's command was registered
        assert len(shell.commands) == 1
        assert "good_tool" in shell.commands