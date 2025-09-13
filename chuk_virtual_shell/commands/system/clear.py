# src/chuk_virtual_shell/commands/system/clear.py
"""
chuk_virtual_shell/commands/system/clear.py - Clear the screen command
"""

import argparse
from chuk_virtual_shell.commands.command_base import ShellCommand


class ClearCommand(ShellCommand):
    name = "clear"
    help_text = (
        "clear - Clear the screen\n"
        "Usage: clear\n"
        "Clears the terminal display using ANSI escape codes."
    )
    category = "system"

    def execute(self, args):
        parser = argparse.ArgumentParser(prog=self.name, add_help=False)
        # Ignore any extra arguments.
        parser.parse_known_args(args)
        return "\033[2J\033[H"
