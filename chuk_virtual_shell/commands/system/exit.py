# src/chuk_virtual_shell/commands/system/exit.py
"""
chuk_virtual_shell/commands/system/exit.py - Exit the shell command
"""

import argparse
from chuk_virtual_shell.commands.command_base import ShellCommand


class ExitCommand(ShellCommand):
    name = "exit"
    help_text = (
        "exit - Exit the shell\nUsage: exit\nExits the shell session gracefully."
    )
    category = "system"

    def execute(self, args):
        parser = argparse.ArgumentParser(prog=self.name, add_help=False)
        # Accept an optional --force flag but ignore any unknown extra arguments.
        parser.add_argument(
            "--force", action="store_true", help="Force exit immediately (optional)"
        )
        parser.parse_known_args(args)
        self.shell.running = False
        return "Goodbye!"
