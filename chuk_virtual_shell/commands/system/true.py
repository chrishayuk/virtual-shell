# src/chuk_virtual_shell/commands/system/true.py
"""
True command - always returns success.

The 'true' command always exits with a status of 0 (success).
Used in shell scripts and conditionals.
"""

from chuk_virtual_shell.commands.command_base import ShellCommand


class TrueCommand(ShellCommand):
    """
    True command - always returns success (exit code 0).
    """
    
    name = "true"
    help_text = "true - Always returns success (exit code 0)"
    category = "system"

    def __init__(self, shell):
        """Initialize the true command."""
        super().__init__(shell)

    def execute(self, args):
        """
        Execute the true command.
        
        Args:
            args: Arguments (ignored)
            
        Returns:
            Empty string (sets return code to 0)
        """
        self.shell.return_code = 0
        return ""