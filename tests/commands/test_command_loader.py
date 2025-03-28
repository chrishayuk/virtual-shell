"""
tests/chuk_virtual_shell/commands/test_command_loader.py
"""
import pytest
from chuk_virtual_shell.commands.command_loader import CommandLoader
from chuk_virtual_shell.commands.command_base import ShellCommand
from tests.dummy_shell import DummyShell

# Test for discover_commands
def test_discover_commands():
    # Create a dummy shell with an empty file system and minimal environment.
    dummy_shell = DummyShell({})
    dummy_shell.environ = {}
    
    # Discover commands using the CommandLoader.
    commands = CommandLoader.discover_commands(dummy_shell)
    
    # Expected command names as defined in CommandLoader.
    expected_commands = [
        "ls", "cd", "pwd",
        "mkdir", "touch", "cat", "echo", "rm", "rmdir", "more",
        "env", "export",
        "clear", "exit", "help", "script"
    ]
    
    # Verify that each expected command is present and is an instance of ShellCommand.
    for cmd_name in expected_commands:
        assert cmd_name in commands, f"Missing command: {cmd_name}"
        assert isinstance(commands[cmd_name], ShellCommand), f"{cmd_name} is not an instance of ShellCommand"
        
# Test for load_commands_from_path (placeholder implementation)
def test_load_commands_from_path():
    dummy_shell = DummyShell({})
    dummy_shell.environ = {}
    
    # The placeholder implementation should return an empty dict.
    commands = CommandLoader.load_commands_from_path(dummy_shell, "/some/path")
    assert commands == {}
