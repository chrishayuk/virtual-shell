"""
chuk_virtual_shell/commands/__init__.py - Command module package initialization
"""
from typing import Dict, Optional

# Command registry
_COMMAND_EXECUTORS = {}
_COMMAND_CLASSES = {}

def register_command_class(command_class):
    """Register a command class (not instance)"""
    _COMMAND_CLASSES[command_class.name] = command_class

def get_command_executor(name: str):
    """Get a command executor by name"""
    return _COMMAND_EXECUTORS.get(name)

def initialize_commands(shell_context):
    """Initialize all command instances with the shell context"""
    _COMMAND_EXECUTORS.clear()
    for name, command_class in _COMMAND_CLASSES.items():
        try:
            _COMMAND_EXECUTORS[name] = command_class(shell_context)
        except Exception as e:
            import sys
            print(f"Warning: Failed to initialize command '{name}': {e}", file=sys.stderr)

def list_commands() -> Dict[str, str]:
    """List all available commands with their help text"""
    return {name: cmd.help_text.split('\n')[0] if cmd.help_text else name 
            for name, cmd in _COMMAND_CLASSES.items()}

# Import command classes

# Navigation commands
from chuk_virtual_shell.commands.navigation.ls import LsCommand
from chuk_virtual_shell.commands.navigation.cd import CdCommand
from chuk_virtual_shell.commands.navigation.pwd import PwdCommand

# File system commands - using filesystem directory as in original code
from chuk_virtual_shell.commands.filesystem.mkdir import MkdirCommand
from chuk_virtual_shell.commands.filesystem.touch import TouchCommand
from chuk_virtual_shell.commands.filesystem.cat import CatCommand
from chuk_virtual_shell.commands.filesystem.echo import EchoCommand
from chuk_virtual_shell.commands.filesystem.rm import RmCommand
from chuk_virtual_shell.commands.filesystem.rmdir import RmdirCommand

# Environment commands
from chuk_virtual_shell.commands.environment.env import EnvCommand
from chuk_virtual_shell.commands.environment.export import ExportCommand

# System commands
from chuk_virtual_shell.commands.system.clear import ClearCommand
from chuk_virtual_shell.commands.system.exit import ExitCommand
from chuk_virtual_shell.commands.system.help import HelpCommand

# Register all command classes
register_command_class(LsCommand)
register_command_class(CdCommand)
register_command_class(PwdCommand)
register_command_class(MkdirCommand)
register_command_class(TouchCommand)
register_command_class(CatCommand)
register_command_class(EchoCommand)
register_command_class(RmCommand)
register_command_class(RmdirCommand)
register_command_class(EnvCommand)
register_command_class(ExportCommand)
register_command_class(ClearCommand)
register_command_class(ExitCommand)
register_command_class(HelpCommand)

# Export all commands
__all__ = [
    # Navigation
    'LsCommand',
    'CdCommand',
    'PwdCommand',
    
    # Filesystem
    'MkdirCommand',
    'TouchCommand',
    'CatCommand',
    'EchoCommand',
    'RmCommand',
    'RmdirCommand',
    
    # Environment
    'EnvCommand',
    'ExportCommand',
    
    # System
    'ClearCommand',
    'ExitCommand',
    'HelpCommand',
    
    # Registry functions
    'get_command_executor',
    'register_command_class',
    'initialize_commands',
    'list_commands',
]