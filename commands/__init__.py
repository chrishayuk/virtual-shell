"""
commands/__init__.py - Command module package initialization
"""
# Navigation commands
from commands.navigation.ls import LsCommand
from commands.navigation.cd import CdCommand
from commands.navigation.pwd import PwdCommand

# File system commands
from commands.filesystem.mkdir import MkdirCommand
from commands.filesystem.touch import TouchCommand
from commands.filesystem.cat import CatCommand
from commands.filesystem.echo import EchoCommand
from commands.filesystem.rm import RmCommand
from commands.filesystem.rmdir import RmdirCommand

# Environment commands
from commands.environment.env import EnvCommand
from commands.environment.export import ExportCommand

# System commands
from commands.system.clear import ClearCommand
from commands.system.exit import ExitCommand
from commands.system.help import HelpCommand

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