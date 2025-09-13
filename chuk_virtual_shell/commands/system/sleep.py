# src/chuk_virtual_shell/commands/system/sleep.py
"""
Sleep command - delay for a specified amount of time.

The 'sleep' command pauses execution for the specified number of seconds.
"""

import time
import asyncio
import inspect
from chuk_virtual_shell.commands.command_base import ShellCommand


class SleepCommand(ShellCommand):
    """
    Sleep command - pauses execution for specified duration.
    """
    
    name = "sleep"
    help_text = "sleep - Pause execution for specified number of seconds"
    category = "system"

    def __init__(self, shell):
        """Initialize the sleep command."""
        super().__init__(shell)

    def execute(self, args):
        """
        Execute the sleep command synchronously.
        
        Args:
            args: List containing the duration in seconds
            
        Returns:
            Empty string on success, error message on failure
        """
        if not args:
            return "sleep: missing operand"
        
        try:
            # Parse the duration (supports decimal values)
            duration = float(args[0])
            
            if duration < 0:
                return "sleep: invalid time interval"
            
            # Sleep for the specified duration
            time.sleep(duration)
            self.shell.return_code = 0
            return ""
            
        except ValueError:
            return f"sleep: invalid time interval '{args[0]}'"
        except KeyboardInterrupt:
            # Handle Ctrl+C during sleep
            self.shell.return_code = 130
            return ""
    
    async def execute_async(self, args):
        """
        Execute the sleep command asynchronously.
        
        Args:
            args: List containing the duration in seconds
            
        Returns:
            Empty string on success, error message on failure
        """
        if not args:
            return "sleep: missing operand"
        
        try:
            # Parse the duration (supports decimal values)
            duration = float(args[0])
            
            if duration < 0:
                return "sleep: invalid time interval"
            
            # Sleep asynchronously for the specified duration
            await asyncio.sleep(duration)
            self.shell.return_code = 0
            return ""
            
        except ValueError:
            return f"sleep: invalid time interval '{args[0]}'"
        except asyncio.CancelledError:
            # Handle cancellation during async sleep
            self.shell.return_code = 130
            return ""