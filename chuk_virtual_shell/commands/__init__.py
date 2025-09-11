"""
chuk_virtual_shell/commands/__init__.py - Command module package initialization

This module manages the registration and initialization of command classes.
It provides functions to register commands, initialize them with a given shell context,
list available commands, and retrieve command executors.
"""

import logging
from typing import Dict, Optional, Type

# Command registry dictionaries
_COMMAND_EXECUTORS: Dict[str, object] = {}
_COMMAND_CLASSES: Dict[str, Type] = {}


def register_command_class(command_class: Type) -> None:
    """Register a command class (not an instance)."""
    _COMMAND_CLASSES[command_class.name] = command_class


def get_command_executor(name: str) -> Optional[object]:
    """Retrieve a command executor instance by name, if available."""
    return _COMMAND_EXECUTORS.get(name)


def initialize_commands(shell_context) -> None:
    """
    Initialize all command instances with the provided shell context.

    This clears any previously initialized command executors and instantiates
    all registered command classes with the given shell context.
    """
    _COMMAND_EXECUTORS.clear()
    for name, command_class in _COMMAND_CLASSES.items():
        try:
            _COMMAND_EXECUTORS[name] = command_class(shell_context)
        except Exception as e:
            logging.warning(f"Failed to initialize command '{name}': {e}")


def list_commands() -> Dict[str, str]:
    """
    List all available commands with a brief description.

    Returns:
        A dictionary mapping command names to the first line of their help text.
    """
    return {
        name: (cmd.help_text.split("\n")[0] if cmd.help_text else name)
        for name, cmd in _COMMAND_CLASSES.items()
    }


# Import command classes

# Navigation commands
from chuk_virtual_shell.commands.navigation.ls import LsCommand
from chuk_virtual_shell.commands.navigation.cd import CdCommand
from chuk_virtual_shell.commands.navigation.pwd import PwdCommand

# Filesystem commands
from chuk_virtual_shell.commands.filesystem.mkdir import MkdirCommand
from chuk_virtual_shell.commands.filesystem.touch import TouchCommand
from chuk_virtual_shell.commands.filesystem.cat import CatCommand
from chuk_virtual_shell.commands.filesystem.echo import EchoCommand
from chuk_virtual_shell.commands.filesystem.rm import RmCommand
from chuk_virtual_shell.commands.filesystem.rmdir import RmdirCommand

# Environment commands
from chuk_virtual_shell.commands.environment.env import EnvCommand
from chuk_virtual_shell.commands.environment.export import ExportCommand

# System commands (existing)
from chuk_virtual_shell.commands.system.clear import ClearCommand
from chuk_virtual_shell.commands.system.exit import ExitCommand
from chuk_virtual_shell.commands.system.help import HelpCommand

# System commands (new)
from chuk_virtual_shell.commands.system.time import TimeCommand
from chuk_virtual_shell.commands.system.uptime import UptimeCommand
from chuk_virtual_shell.commands.system.whoami import WhoamiCommand
from chuk_virtual_shell.commands.system.date import DateCommand

# Register all command classes using a compact loop.
for command in (
    LsCommand,
    CdCommand,
    PwdCommand,
    MkdirCommand,
    TouchCommand,
    CatCommand,
    EchoCommand,
    RmCommand,
    RmdirCommand,
    EnvCommand,
    ExportCommand,
    ClearCommand,
    ExitCommand,
    HelpCommand,
    TimeCommand,
    UptimeCommand,
    WhoamiCommand,
    DateCommand,
):
    register_command_class(command)

__all__ = [
    # Navigation
    "LsCommand",
    "CdCommand",
    "PwdCommand",
    # Filesystem
    "MkdirCommand",
    "TouchCommand",
    "CatCommand",
    "EchoCommand",
    "RmCommand",
    "RmdirCommand",
    # Environment
    "EnvCommand",
    "ExportCommand",
    # System (existing)
    "ClearCommand",
    "ExitCommand",
    "HelpCommand",
    # System (new)
    "TimeCommand",
    "UptimeCommand",
    "WhoamiCommand",
    # Registry functions
    "get_command_executor",
    "register_command_class",
    "initialize_commands",
    "list_commands",
]
