"""
chuk_virtual_shell/commands/system/uptime.py - time
"""

import time
from chuk_virtual_shell.commands.command_base import ShellCommand


class UptimeCommand(ShellCommand):
    name = "uptime"
    help_text = "uptime - Display how long the shell has been running\nUsage: uptime"
    category = "system"

    def execute(self, args):
        if args:
            return self.get_help()
        # Calculate uptime based on the shell's start time.
        current_time = time.time()
        uptime_seconds = int(current_time - self.shell.start_time)
        # Format uptime as hours, minutes, seconds.
        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"Uptime: {hours}h {minutes}m {seconds}s"
