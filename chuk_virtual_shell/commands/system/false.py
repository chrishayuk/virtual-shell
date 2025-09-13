# src/chuk_virtual_shell/commands/system/false.py
"""
False command - always returns failure.

The 'false' command always exits with a status of 1 (failure).
Used in shell scripts and conditionals.
"""

from chuk_virtual_shell.commands.command_base import ShellCommand


class FalseCommand(ShellCommand):
    """
    False command - always returns failure (exit code 1).
    """
    
    name = "false"
    help_text = "false - Always returns failure (exit code 1)"
    category = "system"

    def __init__(self, shell):
        """Initialize the false command."""
        super().__init__(shell)

    def execute(self, args):
        """
        Execute the false command.
        
        Args:
            args: Arguments (ignored)
            
        Returns:
            Empty string (sets return code to 1)
        """
        self.shell.return_code = 1
        return ""