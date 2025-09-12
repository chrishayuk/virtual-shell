# tests/sandbox/test_mcp_loader.py

import sys
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# Import the modules we'll be testing
from chuk_virtual_shell.commands.mcp.mcp_command_loader import (
    load_mcp_tools_for_server,
    create_mcp_command_class,
    register_mcp_commands,
)

# Import the actual functions we need to patch at their source

# Create module level patches
stdio_client_patch = patch("chuk_mcp.mcp_client.stdio_client", autospec=True)
send_tools_list_patch = patch("chuk_mcp.mcp_client.send_tools_list", autospec=True)
send_initialize_patch = patch("chuk_mcp.mcp_client.send_initialize", autospec=True)
send_ping_patch = patch("chuk_mcp.mcp_client.send_ping", autospec=True)


@pytest.mark.anyio
async def test_load_mcp_tools_for_server():
    """
    Test that load_mcp_tools_for_server calls send_tools_list and
    returns the list of tools properly.
    """
    # 1) Mock out stdio_client so it doesn't actually connect anywhere.
    mock_read_stream = MagicMock()
    mock_write_stream = MagicMock()

    # We'll use an AsyncMock context manager so 'async with' works as expected
    mock_stdio_context = AsyncMock()
    mock_stdio_context.__aenter__.return_value = (mock_read_stream, mock_write_stream)
    mock_stdio_context.__aexit__.return_value = None

    # Create mocks for the library functions
    mock_stdio_client = stdio_client_patch.start()
    mock_send_tools_list = send_tools_list_patch.start()
    mock_send_initialize = send_initialize_patch.start()
    mock_send_ping = send_ping_patch.start()

    try:
        # Configure mocks
        mock_stdio_client.return_value = mock_stdio_context
        mock_send_initialize.return_value = True  # Init successful
        mock_send_ping.return_value = True  # Ping successful
        mock_send_tools_list.return_value = {
            "tools": [{"name": "toolA"}, {"name": "toolB"}]
        }

        # Here is our fake config
        mcp_config = {
            "server_name": "testServer",
            "config_path": "fake_config.json",
        }

        tools = await load_mcp_tools_for_server(mcp_config)

        # 3) Assertions
        assert tools == [
            {"name": "toolA"},
            {"name": "toolB"},
        ], "Expected the mocked list of tools to be returned."
        mock_send_tools_list.assert_awaited_once(), "send_tools_list should be called exactly once."
    finally:
        # Stop all patches
        stdio_client_patch.stop()
        send_tools_list_patch.stop()
        send_initialize_patch.stop()
        send_ping_patch.stop()


def test_create_mcp_command_class():
    """
    Test that create_mcp_command_class builds a ShellCommand subclass with
    the correct name and help_text, and that it has proper sync and async methods.
    """
    # 1) Fake tool and config
    tool = {
        "name": "myTestTool",
        "description": "A test tool.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "SQL query to execute"}
            },
            "required": ["query"],
        },
    }

    mcp_config = {
        "server_name": "testServer",
        "config_path": "fake_config.json",
    }

    # 2) Create the dynamic command class
    CommandClass = create_mcp_command_class(tool, mcp_config)
    assert CommandClass.name == "myTestTool"
    assert "A test tool." in CommandClass.help_text
    assert CommandClass.category == "mcp"

    # 3) Instantiate it with a mock "shell_context"
    mock_shell_context = MagicMock()
    cmd_instance = CommandClass(mock_shell_context)

    # 4) Test the execute method - it should return a message about async execution
    result = cmd_instance.execute(["arg1", "--option", "val"])
    assert "should be executed asynchronously" in result

    # 5) Test the input formatting with SQL query arguments
    from chuk_virtual_shell.commands.mcp.mcp_input_formatter import format_mcp_input

    formatted = format_mcp_input(["SELECT", "*", "FROM", "table"], tool["inputSchema"])
    assert "query" in formatted
    assert formatted["query"] == "SELECT * FROM table"


@pytest.mark.anyio
async def test_register_mcp_commands():
    """
    Test that register_mcp_commands loads tools for each server and
    registers them as commands on the shell.
    """

    # Create a dummy test command class
    class TestCommand:
        name = ""
        help_text = "Test command"
        category = "mcp"

        def __init__(self, name, shell):
            self.name = name
            self.shell = shell

        def execute(self, args):
            return f"Executed {self.name}"

        def run(self, args):
            return self.execute(args)

        async def execute_async(self, args):
            return f"Async {self.name}"

    # Create a shell that just stores commands
    class MockShell:
        def __init__(self):
            self.commands = {}
            self.mcp_servers = [
                {"server_name": "server1", "config_path": "config1.json"},
                {"server_name": "server2", "config_path": "config2.json"},
            ]

        def _register_command(self, cmd):
            self.commands[cmd.name] = cmd

    # Create the mock shell
    shell = MockShell()

    # Create a mock function that's called by register_mcp_commands
    async def fake_load_tools(config):
        server = config.get("server_name", "")
        if server == "server1":
            return [{"name": "cmd1"}, {"name": "cmd2"}]
        elif server == "server2":
            return [{"name": "cmd3"}]
        return []

    # Create a mock function that's called to create command classes
    def fake_create_command(tool, config):
        # Instead of creating a class, we'll create a function that returns an instance
        def create_instance(shell):
            return TestCommand(tool["name"], shell)

        return create_instance

    # Mock both functions
    with (
        patch(
            "chuk_virtual_shell.commands.mcp.mcp_command_loader.load_mcp_tools_for_server",
            side_effect=fake_load_tools,
        ),
        patch(
            "chuk_virtual_shell.commands.mcp.mcp_command_loader.create_mcp_command_class",
            side_effect=fake_create_command,
        ),
    ):

        # Run the function we're testing
        await register_mcp_commands(shell)

    # Verify commands were registered
    assert "cmd1" in shell.commands
    assert "cmd2" in shell.commands
    assert "cmd3" in shell.commands


@pytest.mark.anyio
async def test_mcp_loader_integration():
    """
    Test the integration between mcp_loader.py and mcp_command_loader.py
    """
    # Patch the import first to avoid ImportError
    with patch.dict(
        "sys.modules",
        {
            "chuk_virtual_shell.commands.mcp.mcp_command_loader": MagicMock(),
        },
    ):
        # Now we can safely import from mcp_loader
        from chuk_virtual_shell.sandbox.loader.mcp_loader import (
            load_mcp_servers,
            register_mcp_commands_with_shell,
            initialize_mcp,
        )

        # Mock out the register_mcp_commands function that would be imported
        sys.modules[
            "chuk_virtual_shell.commands.mcp.mcp_command_loader"
        ].register_mcp_commands = AsyncMock()

        # Test load_mcp_servers
        config = {
            "mcp_servers": [
                {"server_name": "server1", "config_path": "path1"},
                {"server_name": "server2", "config_path": "path2"},
                {"missing_key": "value"},  # This one should be filtered out
            ]
        }

        result = load_mcp_servers(config)
        assert len(result) == 2
        assert result[0]["server_name"] == "server1"
        assert result[1]["server_name"] == "server2"

        # Test register_mcp_commands_with_shell
        class MockShell:
            def __init__(self):
                self.commands = {}
                self.mcp_servers = result

        shell = MockShell()

        # Since we've already mocked the module, this should work
        error = await register_mcp_commands_with_shell(shell)
        assert error is None

        # Test initialize_mcp
        with patch(
            "chuk_virtual_shell.sandbox.loader.mcp_loader.register_mcp_commands_with_shell",
            new_callable=AsyncMock,
            return_value=None,
        ) as mock_register:
            error = await initialize_mcp(shell)
            assert error is None
            mock_register.assert_awaited_once_with(shell)
