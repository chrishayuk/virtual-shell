"""
virtual_shell/commands/system/clear.py - Clear the screen command
"""
from virtual_shell.commands.command_base import ShellCommand

class ClearCommand(ShellCommand):
    name = "clear"
    help_text = "clear - Clear the screen\nUsage: clear"
    category = "system"
    
    def execute(self, args):
        return "\033[2J\033[H"  # ANSI escape code to clear screen