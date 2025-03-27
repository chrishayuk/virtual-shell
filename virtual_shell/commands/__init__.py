"""
virtual_shell/commands/__init__.py - Command module package initialization
"""
# Navigation commands
from virtual_shell.commands.navigation.ls import LsCommand
from virtual_shell.commands.navigation.cd import CdCommand
from virtual_shell.commands.navigation.pwd import PwdCommand

# File system commands
from virtual_shell.commands.filesystem.mkdir import MkdirCommand
from virtual_shell.commands.filesystem.touch import TouchCommand
from virtual_shell.commands.filesystem.cat import CatCommand
from virtual_shell.commands.filesystem.echo import EchoCommand
from virtual_shell.commands.filesystem.rm import RmCommand
from virtual_shell.commands.filesystem.rmdir import RmdirCommand

# Environment commands
from virtual_shell.commands.environment.env import EnvCommand
from virtual_shell.commands.environment.export import ExportCommand

# System commands
from virtual_shell.commands.system.clear import ClearCommand
from virtual_shell.commands.system.exit import ExitCommand
from virtual_shell.commands.system.help import HelpCommand

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
]