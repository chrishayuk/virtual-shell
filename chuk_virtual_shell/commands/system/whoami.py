"""
chuk_virtual_shell/chuk_virtual_shell/commands/system/script.py - Run shell scripts command
"""

from chuk_virtual_shell.commands.command_base import ShellCommand


class WhoamiCommand(ShellCommand):
    name = "whoami"
    help_text = "whoami - Display the current user\nUsage: whoami"
    category = "system"

    def execute(self, args):
        if args:
            return self.get_help()
        # Retrieve the username from the shell's environment.
        return self.shell.environ.get("USER", "unknown")
