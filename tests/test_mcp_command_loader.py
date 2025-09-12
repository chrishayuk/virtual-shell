"""
tests/commands/mcp/test_mcp_command_loader.py - Tests for MCP command loader

Tests the core functionality of the MCP command loader, including:
- Creating command classes from tool definitions
- Loading tools from MCP servers
- Registering MCP commands with the shell
"""

import pytest
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
    # Import the input formatter to test input formatting
    from chuk_virtual_shell.commands.mcp.mcp_input_formatter import format_mcp_input

    # Test with query-type tool
    query_tool = {
        "name": "query_tool",
        "description": "A query tool",
        "inputSchema": {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "SQL query"}},
            "required": ["query"],
        },
    }

    # Create the command class
    CommandClass = create_mcp_command_class(query_tool, {})
    CommandClass(MagicMock())

    # Test the input formatting with a query
    input_data = format_mcp_input(
        ["SELECT", "*", "FROM", "table"], query_tool["inputSchema"]
    )
    assert "query" in input_data
    assert input_data["query"] == "SELECT * FROM table"

    # Test with table name type tool
    table_tool = {
        "name": "table_tool",
        "description": "A table tool",
        "inputSchema": {
            "type": "object",
            "properties": {
                "table_name": {"type": "string", "description": "Table name"}
            },
            "required": ["table_name"],
        },
    }

    # Create the command class
    CommandClass = create_mcp_command_class(table_tool, {})
    CommandClass(MagicMock())

    # Test the input formatting with a table name
    input_data = format_mcp_input(["users"], table_tool["inputSchema"])
    assert "table_name" in input_data
    assert input_data["table_name"] == "users"

    # Test with no-args tool
    no_args_tool = {
        "name": "no_args_tool",
        "description": "A tool without arguments",
        "inputSchema": {"type": "object", "properties": {}},
    }

    # Create the command class
    CommandClass = create_mcp_command_class(no_args_tool, {})
    CommandClass(MagicMock())

    # Test the input formatting with no arguments
    input_data = format_mcp_input([], no_args_tool["inputSchema"])
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
    with (
        patch(
            "chuk_mcp.mcp_client.stdio_client",
            return_value=mock_stdio_context,
            autospec=True,
        ) as mock_stdio_client,
        patch(
            "chuk_mcp.mcp_client.send_initialize", return_value=True, autospec=True
        ) as mock_send_initialize,
        patch(
            "chuk_mcp.mcp_client.send_ping", return_value=True, autospec=True
        ) as mock_send_ping,
        patch(
            "chuk_mcp.mcp_client.send_tools_list",
            return_value={"tools": [{"name": "tool1"}, {"name": "tool2"}]},
            autospec=True,
        ) as mock_send_tools_list,
    ):

        # Create config object
        config = {"server_name": "test_server", "config_path": "test_config.json"}

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
    with (
        patch(
            "chuk_mcp.mcp_client.stdio_client",
            return_value=mock_stdio_context,
            autospec=True,
        ),
        patch("chuk_mcp.mcp_client.send_initialize", return_value=False, autospec=True),
    ):  # Initialize fails

        # Create config object
        config = {"server_name": "test_server", "config_path": "test_config.json"}

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
            self.mcp_servers = [{"server_name": "server1"}, {"server_name": "server2"}]

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
    with (
        patch(
            "chuk_virtual_shell.commands.mcp.mcp_command_loader.load_mcp_tools_for_server",
            side_effect=mock_load_tools,
        ) as mock_load,
        patch(
            "chuk_virtual_shell.commands.mcp.mcp_command_loader.create_mcp_command_class",
            side_effect=mock_create_command,
        ) as mock_create,
    ):

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
    with patch(
        "chuk_virtual_shell.commands.mcp.mcp_command_loader.load_mcp_tools_for_server"
    ) as mock_load:
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
                {"server_name": "bad_server"},
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
    with (
        patch(
            "chuk_virtual_shell.commands.mcp.mcp_command_loader.load_mcp_tools_for_server",
            side_effect=mock_load_tools,
        ),
        patch(
            "chuk_virtual_shell.commands.mcp.mcp_command_loader.create_mcp_command_class",
            side_effect=mock_create_command,
        ),
    ):

        # Call the function under test
        await register_mcp_commands(shell)

        # Verify only the good server's command was registered
        assert len(shell.commands) == 1
        assert "good_tool" in shell.commands


# Test async execution of MCP commands - mocking at the right level to exercise the code paths
@pytest.mark.anyio
async def test_mcp_command_async_execution_import_success():
    """Test successful MCP command execution covering import paths"""
    tool = {"name": "test_tool", "description": "Test tool"}
    config = {"server_name": "test_server"}

    CommandClass = create_mcp_command_class(tool, config)
    cmd = CommandClass(MagicMock())

    # Mock all the imports and calls as they happen in the actual execute_async method
    mock_read_stream = AsyncMock()
    mock_write_stream = AsyncMock()
    mock_stdio_context = AsyncMock()
    mock_stdio_context.__aenter__.return_value = (mock_read_stream, mock_write_stream)
    mock_stdio_context.__aexit__.return_value = None

    # Mock the path that execute_async actually takes with successful response
    mock_modules = {
        "chuk_mcp": MagicMock(),
        "chuk_mcp.mcp_client": MagicMock(),
        "chuk_mcp.mcp_client.transport": MagicMock(),
        "chuk_mcp.mcp_client.transport.stdio": MagicMock(),
        "chuk_mcp.mcp_client.transport.stdio.stdio_client": MagicMock(),
        "chuk_mcp.mcp_client.messages": MagicMock(),
        "chuk_mcp.mcp_client.messages.initialize": MagicMock(),
        "chuk_mcp.mcp_client.messages.initialize.send_messages": MagicMock(),
        "chuk_mcp.mcp_client.messages.ping": MagicMock(),
        "chuk_mcp.mcp_client.messages.ping.send_messages": MagicMock(),
    }

    mock_stdio_client = MagicMock(return_value=mock_stdio_context)
    mock_send_initialize = AsyncMock(return_value=True)
    mock_send_ping = AsyncMock(return_value=True)
    mock_send_tools_call = AsyncMock(
        return_value={"content": [{"type": "text", "text": "Success!"}]}
    )

    # Set up module mocks
    mock_modules["chuk_mcp.mcp_client.transport.stdio.stdio_client"].stdio_client = (
        mock_stdio_client
    )
    mock_modules[
        "chuk_mcp.mcp_client.messages.initialize.send_messages"
    ].send_initialize = mock_send_initialize
    mock_modules["chuk_mcp.mcp_client.messages.ping.send_messages"].send_ping = (
        mock_send_ping
    )

    with (
        patch.dict("sys.modules", mock_modules),
        patch(
            "chuk_virtual_shell.commands.mcp.mcp_command_loader.send_tools_call",
            mock_send_tools_call,
        ),
    ):

        result = await cmd.execute_async(["test"])
        assert "Success!" in result
        mock_send_initialize.assert_awaited_once()
        mock_send_ping.assert_awaited_once()
        mock_send_tools_call.assert_awaited_once()


@pytest.mark.anyio
async def test_mcp_command_async_execution_init_failure():
    """Test async execution when initialization fails"""
    tool = {"name": "test_tool", "description": "Test tool"}
    config = {"server_name": "test_server"}

    CommandClass = create_mcp_command_class(tool, config)
    cmd = CommandClass(MagicMock())

    mock_read_stream = AsyncMock()
    mock_write_stream = AsyncMock()
    mock_stdio_context = AsyncMock()
    mock_stdio_context.__aenter__.return_value = (mock_read_stream, mock_write_stream)
    mock_stdio_context.__aexit__.return_value = None

    mock_modules = {
        "chuk_mcp": MagicMock(),
        "chuk_mcp.mcp_client": MagicMock(),
        "chuk_mcp.mcp_client.transport": MagicMock(),
        "chuk_mcp.mcp_client.transport.stdio": MagicMock(),
        "chuk_mcp.mcp_client.transport.stdio.stdio_client": MagicMock(),
        "chuk_mcp.mcp_client.messages": MagicMock(),
        "chuk_mcp.mcp_client.messages.initialize": MagicMock(),
        "chuk_mcp.mcp_client.messages.initialize.send_messages": MagicMock(),
        "chuk_mcp.mcp_client.messages.ping": MagicMock(),
        "chuk_mcp.mcp_client.messages.ping.send_messages": MagicMock(),
    }

    mock_stdio_client = MagicMock(return_value=mock_stdio_context)
    mock_send_initialize = AsyncMock(return_value=False)  # Init fails

    mock_modules["chuk_mcp.mcp_client.transport.stdio.stdio_client"].stdio_client = (
        mock_stdio_client
    )
    mock_modules[
        "chuk_mcp.mcp_client.messages.initialize.send_messages"
    ].send_initialize = mock_send_initialize

    with patch.dict("sys.modules", mock_modules):
        result = await cmd.execute_async(["test"])
        assert "Failed to initialize connection" in result
        assert "test_tool" in result


@pytest.mark.anyio
async def test_mcp_command_async_execution_ping_failure():
    """Test async execution when ping fails"""
    tool = {"name": "test_tool", "description": "Test tool"}
    config = {"server_name": "test_server"}

    CommandClass = create_mcp_command_class(tool, config)
    cmd = CommandClass(MagicMock())

    mock_read_stream = AsyncMock()
    mock_write_stream = AsyncMock()
    mock_stdio_context = AsyncMock()
    mock_stdio_context.__aenter__.return_value = (mock_read_stream, mock_write_stream)
    mock_stdio_context.__aexit__.return_value = None

    mock_modules = {
        "chuk_mcp": MagicMock(),
        "chuk_mcp.mcp_client": MagicMock(),
        "chuk_mcp.mcp_client.transport": MagicMock(),
        "chuk_mcp.mcp_client.transport.stdio": MagicMock(),
        "chuk_mcp.mcp_client.transport.stdio.stdio_client": MagicMock(),
        "chuk_mcp.mcp_client.messages": MagicMock(),
        "chuk_mcp.mcp_client.messages.initialize": MagicMock(),
        "chuk_mcp.mcp_client.messages.initialize.send_messages": MagicMock(),
        "chuk_mcp.mcp_client.messages.ping": MagicMock(),
        "chuk_mcp.mcp_client.messages.ping.send_messages": MagicMock(),
    }

    mock_stdio_client = MagicMock(return_value=mock_stdio_context)
    mock_send_initialize = AsyncMock(return_value=True)
    mock_send_ping = AsyncMock(return_value=False)  # Ping fails

    mock_modules["chuk_mcp.mcp_client.transport.stdio.stdio_client"].stdio_client = (
        mock_stdio_client
    )
    mock_modules[
        "chuk_mcp.mcp_client.messages.initialize.send_messages"
    ].send_initialize = mock_send_initialize
    mock_modules["chuk_mcp.mcp_client.messages.ping.send_messages"].send_ping = (
        mock_send_ping
    )

    with patch.dict("sys.modules", mock_modules):
        result = await cmd.execute_async(["test"])
        assert "Failed to ping MCP server" in result
        assert "test_tool" in result


@pytest.mark.anyio
async def test_mcp_command_async_execution_no_response():
    """Test async execution when no response is received"""
    tool = {"name": "test_tool", "description": "Test tool"}
    config = {"server_name": "test_server"}

    CommandClass = create_mcp_command_class(tool, config)
    cmd = CommandClass(MagicMock())

    mock_read_stream = AsyncMock()
    mock_write_stream = AsyncMock()
    mock_stdio_context = AsyncMock()
    mock_stdio_context.__aenter__.return_value = (mock_read_stream, mock_write_stream)
    mock_stdio_context.__aexit__.return_value = None

    mock_modules = {
        "chuk_mcp": MagicMock(),
        "chuk_mcp.mcp_client": MagicMock(),
        "chuk_mcp.mcp_client.transport": MagicMock(),
        "chuk_mcp.mcp_client.transport.stdio": MagicMock(),
        "chuk_mcp.mcp_client.transport.stdio.stdio_client": MagicMock(),
        "chuk_mcp.mcp_client.messages": MagicMock(),
        "chuk_mcp.mcp_client.messages.initialize": MagicMock(),
        "chuk_mcp.mcp_client.messages.initialize.send_messages": MagicMock(),
        "chuk_mcp.mcp_client.messages.ping": MagicMock(),
        "chuk_mcp.mcp_client.messages.ping.send_messages": MagicMock(),
    }

    mock_stdio_client = MagicMock(return_value=mock_stdio_context)
    mock_send_initialize = AsyncMock(return_value=True)
    mock_send_ping = AsyncMock(return_value=True)
    mock_send_tools_call = AsyncMock(return_value=None)  # No response

    mock_modules["chuk_mcp.mcp_client.transport.stdio.stdio_client"].stdio_client = (
        mock_stdio_client
    )
    mock_modules[
        "chuk_mcp.mcp_client.messages.initialize.send_messages"
    ].send_initialize = mock_send_initialize
    mock_modules["chuk_mcp.mcp_client.messages.ping.send_messages"].send_ping = (
        mock_send_ping
    )

    with (
        patch.dict("sys.modules", mock_modules),
        patch(
            "chuk_virtual_shell.commands.mcp.mcp_command_loader.send_tools_call",
            mock_send_tools_call,
        ),
    ):

        result = await cmd.execute_async(["test"])
        assert "Failed to execute tool 'test_tool' - no response received" in result


@pytest.mark.anyio
async def test_mcp_command_async_execution_error_response():
    """Test async execution when error response is received"""
    tool = {"name": "test_tool", "description": "Test tool"}
    config = {"server_name": "test_server"}

    CommandClass = create_mcp_command_class(tool, config)
    cmd = CommandClass(MagicMock())

    mock_read_stream = AsyncMock()
    mock_write_stream = AsyncMock()
    mock_stdio_context = AsyncMock()
    mock_stdio_context.__aenter__.return_value = (mock_read_stream, mock_write_stream)
    mock_stdio_context.__aexit__.return_value = None

    mock_modules = {
        "chuk_mcp": MagicMock(),
        "chuk_mcp.mcp_client": MagicMock(),
        "chuk_mcp.mcp_client.transport": MagicMock(),
        "chuk_mcp.mcp_client.transport.stdio": MagicMock(),
        "chuk_mcp.mcp_client.transport.stdio.stdio_client": MagicMock(),
        "chuk_mcp.mcp_client.messages": MagicMock(),
        "chuk_mcp.mcp_client.messages.initialize": MagicMock(),
        "chuk_mcp.mcp_client.messages.initialize.send_messages": MagicMock(),
        "chuk_mcp.mcp_client.messages.ping": MagicMock(),
        "chuk_mcp.mcp_client.messages.ping.send_messages": MagicMock(),
    }

    mock_stdio_client = MagicMock(return_value=mock_stdio_context)
    mock_send_initialize = AsyncMock(return_value=True)
    mock_send_ping = AsyncMock(return_value=True)
    mock_send_tools_call = AsyncMock(
        return_value={"error": {"message": "Tool execution failed"}}
    )

    mock_modules["chuk_mcp.mcp_client.transport.stdio.stdio_client"].stdio_client = (
        mock_stdio_client
    )
    mock_modules[
        "chuk_mcp.mcp_client.messages.initialize.send_messages"
    ].send_initialize = mock_send_initialize
    mock_modules["chuk_mcp.mcp_client.messages.ping.send_messages"].send_ping = (
        mock_send_ping
    )

    with (
        patch.dict("sys.modules", mock_modules),
        patch(
            "chuk_virtual_shell.commands.mcp.mcp_command_loader.send_tools_call",
            mock_send_tools_call,
        ),
    ):

        result = await cmd.execute_async(["test"])
        assert "Error executing tool 'test_tool': Tool execution failed" in result


@pytest.mark.anyio
async def test_mcp_command_async_execution_error_without_message():
    """Test async execution when error response has no message"""
    tool = {"name": "test_tool", "description": "Test tool"}
    config = {"server_name": "test_server"}

    CommandClass = create_mcp_command_class(tool, config)
    cmd = CommandClass(MagicMock())

    mock_read_stream = AsyncMock()
    mock_write_stream = AsyncMock()
    mock_stdio_context = AsyncMock()
    mock_stdio_context.__aenter__.return_value = (mock_read_stream, mock_write_stream)
    mock_stdio_context.__aexit__.return_value = None

    mock_modules = {
        "chuk_mcp": MagicMock(),
        "chuk_mcp.mcp_client": MagicMock(),
        "chuk_mcp.mcp_client.transport": MagicMock(),
        "chuk_mcp.mcp_client.transport.stdio": MagicMock(),
        "chuk_mcp.mcp_client.transport.stdio.stdio_client": MagicMock(),
        "chuk_mcp.mcp_client.messages": MagicMock(),
        "chuk_mcp.mcp_client.messages.initialize": MagicMock(),
        "chuk_mcp.mcp_client.messages.initialize.send_messages": MagicMock(),
        "chuk_mcp.mcp_client.messages.ping": MagicMock(),
        "chuk_mcp.mcp_client.messages.ping.send_messages": MagicMock(),
    }

    mock_stdio_client = MagicMock(return_value=mock_stdio_context)
    mock_send_initialize = AsyncMock(return_value=True)
    mock_send_ping = AsyncMock(return_value=True)
    error_dict = {"code": 500}
    mock_send_tools_call = AsyncMock(return_value={"error": error_dict})

    mock_modules["chuk_mcp.mcp_client.transport.stdio.stdio_client"].stdio_client = (
        mock_stdio_client
    )
    mock_modules[
        "chuk_mcp.mcp_client.messages.initialize.send_messages"
    ].send_initialize = mock_send_initialize
    mock_modules["chuk_mcp.mcp_client.messages.ping.send_messages"].send_ping = (
        mock_send_ping
    )

    with (
        patch.dict("sys.modules", mock_modules),
        patch(
            "chuk_virtual_shell.commands.mcp.mcp_command_loader.send_tools_call",
            mock_send_tools_call,
        ),
    ):

        result = await cmd.execute_async(["test"])
        assert "Error executing tool 'test_tool'" in result
        assert str(error_dict) in result


@pytest.mark.anyio
async def test_mcp_command_async_execution_exception():
    """Test async execution when an exception occurs during import"""
    tool = {"name": "test_tool", "description": "Test tool"}
    config = {"server_name": "test_server"}

    CommandClass = create_mcp_command_class(tool, config)
    cmd = CommandClass(MagicMock())

    # Don't mock anything to trigger the import failure and catch the exception
    result = await cmd.execute_async(["test"])
    assert "Error executing MCP tool 'test_tool'" in result
    # The exact error message will depend on what import fails first


@pytest.mark.anyio
async def test_load_mcp_tools_with_object_config():
    """Test load_mcp_tools_for_server with object-style config"""

    # Create a config object with attributes instead of dict
    class ConfigObject:
        def __init__(self, server_name):
            self.server_name = server_name

    config = ConfigObject("object_server")

    mock_read_stream = AsyncMock()
    mock_write_stream = AsyncMock()
    mock_stdio_context = AsyncMock()
    mock_stdio_context.__aenter__.return_value = (mock_read_stream, mock_write_stream)
    mock_stdio_context.__aexit__.return_value = None

    mock_stdio_client = MagicMock(return_value=mock_stdio_context)
    mock_send_initialize = AsyncMock(return_value=True)
    mock_send_ping = AsyncMock(return_value=True)
    mock_send_tools_list = AsyncMock(return_value={"tools": [{"name": "object_tool"}]})

    mock_modules = {
        "chuk_mcp": MagicMock(),
        "chuk_mcp.mcp_client": MagicMock(),
    }
    mock_modules["chuk_mcp.mcp_client"].stdio_client = mock_stdio_client
    mock_modules["chuk_mcp.mcp_client"].send_initialize = mock_send_initialize
    mock_modules["chuk_mcp.mcp_client"].send_ping = mock_send_ping
    mock_modules["chuk_mcp.mcp_client"].send_tools_list = mock_send_tools_list

    with patch.dict("sys.modules", mock_modules):
        tools = await load_mcp_tools_for_server(config)
        assert tools == [{"name": "object_tool"}]


@pytest.mark.anyio
async def test_load_mcp_tools_ping_failure():
    """Test load_mcp_tools_for_server when ping fails"""
    config = {"server_name": "test_server"}

    mock_read_stream = AsyncMock()
    mock_write_stream = AsyncMock()
    mock_stdio_context = AsyncMock()
    mock_stdio_context.__aenter__.return_value = (mock_read_stream, mock_write_stream)
    mock_stdio_context.__aexit__.return_value = None

    mock_stdio_client = MagicMock(return_value=mock_stdio_context)
    mock_send_initialize = AsyncMock(return_value=True)
    mock_send_ping = AsyncMock(return_value=False)  # Ping fails

    mock_modules = {
        "chuk_mcp": MagicMock(),
        "chuk_mcp.mcp_client": MagicMock(),
    }
    mock_modules["chuk_mcp.mcp_client"].stdio_client = mock_stdio_client
    mock_modules["chuk_mcp.mcp_client"].send_initialize = mock_send_initialize
    mock_modules["chuk_mcp.mcp_client"].send_ping = mock_send_ping

    with patch.dict("sys.modules", mock_modules):
        tools = await load_mcp_tools_for_server(config)
        assert tools == []


@pytest.mark.anyio
async def test_load_mcp_tools_exception_handling():
    """Test load_mcp_tools_for_server when an exception occurs"""
    config = {"server_name": "error_server"}

    mock_stdio_client = MagicMock(side_effect=Exception("Connection error"))

    mock_modules = {
        "chuk_mcp": MagicMock(),
        "chuk_mcp.mcp_client": MagicMock(),
    }
    mock_modules["chuk_mcp.mcp_client"].stdio_client = mock_stdio_client

    with patch.dict("sys.modules", mock_modules):
        tools = await load_mcp_tools_for_server(config)
        assert tools == []


# Test register_mcp_commands edge cases
@pytest.mark.anyio
async def test_register_mcp_commands_no_servers_attribute():
    """Test register_mcp_commands when shell has no mcp_servers attribute"""

    class MockShellNoServers:
        def __init__(self):
            self.commands = {}
            # No mcp_servers attribute

    shell = MockShellNoServers()

    with patch(
        "chuk_virtual_shell.commands.mcp.mcp_command_loader.load_mcp_tools_for_server"
    ) as mock_load:
        await register_mcp_commands(shell)
        mock_load.assert_not_called()
        assert len(shell.commands) == 0


@pytest.mark.anyio
async def test_register_mcp_commands_with_object_config():
    """Test register_mcp_commands with object-style server config"""

    class ConfigObject:
        def __init__(self, server_name):
            self.server_name = server_name

    class MockShell:
        def __init__(self):
            self.commands = {}
            self.mcp_servers = [ConfigObject("object_server")]

        def _register_command(self, cmd):
            self.commands[cmd.name] = cmd

    shell = MockShell()

    async def mock_load_tools(config):
        return [{"name": "object_tool"}]

    def mock_create_command(tool, config):
        class MockCommand(ShellCommand):
            name = tool.get("name", "unknown")
            category = "mcp"

            def execute(self, args):
                return f"Executed {self.name}"

        return MockCommand

    with (
        patch(
            "chuk_virtual_shell.commands.mcp.mcp_command_loader.load_mcp_tools_for_server",
            side_effect=mock_load_tools,
        ),
        patch(
            "chuk_virtual_shell.commands.mcp.mcp_command_loader.create_mcp_command_class",
            side_effect=mock_create_command,
        ),
    ):

        await register_mcp_commands(shell)
        assert len(shell.commands) == 1
        assert "object_tool" in shell.commands


@pytest.mark.anyio
async def test_register_mcp_commands_tool_without_name():
    """Test register_mcp_commands when a tool has no name"""

    class MockShell:
        def __init__(self):
            self.commands = {}
            self.mcp_servers = [{"server_name": "test_server"}]

        def _register_command(self, cmd):
            self.commands[cmd.name] = cmd

    shell = MockShell()

    async def mock_load_tools(config):
        return [{"description": "Tool without name"}, {"name": "valid_tool"}]

    def mock_create_command(tool, config):
        class MockCommand(ShellCommand):
            name = tool.get("name", "unknown")
            category = "mcp"

            def execute(self, args):
                return f"Executed {self.name}"

        return MockCommand

    with (
        patch(
            "chuk_virtual_shell.commands.mcp.mcp_command_loader.load_mcp_tools_for_server",
            side_effect=mock_load_tools,
        ),
        patch(
            "chuk_virtual_shell.commands.mcp.mcp_command_loader.create_mcp_command_class",
            side_effect=mock_create_command,
        ),
    ):

        await register_mcp_commands(shell)
        # Only the valid tool should be registered
        assert len(shell.commands) == 1
        assert "valid_tool" in shell.commands
        assert "unknown" not in shell.commands


@pytest.mark.anyio
async def test_register_mcp_commands_command_creation_error():
    """Test register_mcp_commands when command creation fails"""

    class MockShell:
        def __init__(self):
            self.commands = {}
            self.mcp_servers = [{"server_name": "test_server"}]

        def _register_command(self, cmd):
            self.commands[cmd.name] = cmd

    shell = MockShell()

    async def mock_load_tools(config):
        return [{"name": "failing_tool"}, {"name": "good_tool"}]

    def mock_create_command(tool, config):
        if tool.get("name") == "failing_tool":
            raise Exception("Command creation failed")

        class MockCommand(ShellCommand):
            name = tool.get("name", "unknown")
            category = "mcp"

            def execute(self, args):
                return f"Executed {self.name}"

        return MockCommand

    with (
        patch(
            "chuk_virtual_shell.commands.mcp.mcp_command_loader.load_mcp_tools_for_server",
            side_effect=mock_load_tools,
        ),
        patch(
            "chuk_virtual_shell.commands.mcp.mcp_command_loader.create_mcp_command_class",
            side_effect=mock_create_command,
        ),
    ):

        await register_mcp_commands(shell)
        # Only the good tool should be registered
        assert len(shell.commands) == 1
        assert "good_tool" in shell.commands
        assert "failing_tool" not in shell.commands
