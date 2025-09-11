"""
chuk_virtual_shell/commands/filesystem/__init__.py - Filesystem commands package

This module imports and exports the filesystem-related command classes,
including directory and file operations, as well as disk usage (du) and quota commands.
These commands are automatically registered by the command loader.
"""

from chuk_virtual_shell.commands.filesystem.mkdir import MkdirCommand
from chuk_virtual_shell.commands.filesystem.touch import TouchCommand
from chuk_virtual_shell.commands.filesystem.cat import CatCommand
from chuk_virtual_shell.commands.filesystem.echo import EchoCommand
from chuk_virtual_shell.commands.filesystem.rm import RmCommand
from chuk_virtual_shell.commands.filesystem.rmdir import RmdirCommand
from chuk_virtual_shell.commands.filesystem.more import MoreCommand
from chuk_virtual_shell.commands.filesystem.du import DuCommand
from chuk_virtual_shell.commands.filesystem.quota import QuotaCommand
from chuk_virtual_shell.commands.filesystem.cp import CpCommand
from chuk_virtual_shell.commands.filesystem.mv import MvCommand

__all__ = [
    "MkdirCommand",
    "TouchCommand",
    "CatCommand",
    "EchoCommand",
    "RmCommand",
    "RmdirCommand",
    "MoreCommand",
    "DuCommand",
    "QuotaCommand",
    "CpCommand",
    "MvCommand",
]
