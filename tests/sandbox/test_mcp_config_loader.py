# tests/test_mcp_command_loader.py

import pytest
import anyio
from unittest.mock import AsyncMock, MagicMock, patch

from chuk_virtual_shell.commands.mcp_command_loader import (
    load_mcp_tools_for_server,
    create_mcp_command_class,
    register_mcp_commands,
)

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
    mock_stdio_context.__aexit__.return_value = False

    # 2) Also mock send_tools_list to return a known list of tools
    with patch(
        "chuk_virtual_shell.commands.mcp_command_loader.stdio_client",
        return_value=mock_stdio_context
    ), patch(
        "chuk_virtual_shell.commands.mcp_command_loader.send_tools_list",
        return_value={"tools": [{"name": "toolA"}, {"name": "toolB"}]}
    ) as mock_send_tools_list:
        # Here is our fake config
        mcp_config = {
            "server_name": "testServer",
            "config_path": "fake_config.json",
        }

        tools = await load_mcp_tools_for_server(mcp_config)

        # 3) Assertions
        assert tools == [{"name": "toolA"}, {"name": "toolB"}], \
            "Expected the mocked list of tools to be returned."
        mock_send_tools_list.assert_awaited_once(), \
            "send_tools_list should be called exactly once."

def test_create_mcp_command_class():
    """
    Test that create_mcp_command_class builds a ShellCommand subclass with
    the correct name and help_text, and that .execute() invokes the MCP logic.
    """
    # 1) Fake tool and config
    tool = {"name": "myTestTool", "description": "A test tool."}
    mcp_config = {
        "server_name": "testServer",
        "config_path": "fake_config.json",
    }

    # 2) Create the dynamic command class
    CommandClass = create_mcp_command_class(tool, mcp_config)
    assert CommandClass.name == "myTestTool"
    assert "A test tool." in CommandClass.help_text

    # 3) Instantiate it with a mock "shell_context"
    mock_shell_context = MagicMock()
    cmd_instance = CommandClass(mock_shell_context)

    # 4) Patch cmd_instance.call_mcp_tool so we don't do real I/O
    with patch.object(cmd_instance, "call_mcp_tool", return_value="fake-result") as mock_call:
        # .execute() is a sync call that internally does anyio.run(...)
        result = cmd_instance.execute(["arg1", "--option", "val"])
        mock_call.assert_called_once()
        # 'result' should be the fake string returned by the mock
        assert result == "fake-result"

@pytest.mark.anyio
async def test_register_mcp_commands():
    """
    Test that register_mcp_commands loads tools for each server and
    registers them as commands on the shell.
    """

    class MockShell:
        """
        A simple mock shell containing a list of MCP servers 
        and a dict where commands get stored.
        """
        def __init__(self):
            self.commands = {}
            self.mcp_servers = [
                {
                    "server_name": "serverOne",
                    "config_path": "conf1.json",
                },
                {
                    "server_name": "serverTwo",
                    "config_path": "conf2.json",
                },
            ]

    shell = MockShell()

    # We'll mock load_mcp_tools_for_server so we don't do real I/O
    async def mock_load_tools(mcp_config):
        if mcp_config["server_name"] == "serverOne":
            return [{"name": "toolOneA"}, {"name": "toolOneB"}]
        elif mcp_config["server_name"] == "serverTwo":
            return [{"name": "toolTwoA"}]
        else:
            return []

    with patch(
        "chuk_virtual_shell.commands.mcp_command_loader.load_mcp_tools_for_server",
        side_effect=mock_load_tools
    ):
        # Since register_mcp_commands is async, we must await it
        await register_mcp_commands(shell)

    # Now verify commands were registered
    assert "toolOneA" in shell.commands
    assert "toolOneB" in shell.commands
    assert "toolTwoA" in shell.commands

    # Spot-check one
    cmd_instance = shell.commands["toolOneA"]
    assert cmd_instance.name == "toolOneA"
    # 'execute' should be a sync method that calls 'call_mcp_tool' via anyio.run
    assert callable(cmd_instance.execute)
