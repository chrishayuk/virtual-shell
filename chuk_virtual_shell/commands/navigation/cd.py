"""
chuk_virtual_shell/commands/navigation/cd.py - Change directory command
"""

import argparse
from chuk_virtual_shell.commands.command_base import ShellCommand


class CdCommand(ShellCommand):
    name = "cd"
    help_text = (
        "cd - Change directory\n"
        "Usage: cd [directory]\n"
        "If no directory is provided, the home directory is used.\n"
        "Access is restricted to directories within the sandbox."
    )
    category = "navigation"

    def execute(self, args):
        parser = argparse.ArgumentParser(prog=self.name, add_help=False)
        parser.add_argument(
            "directory",
            nargs="?",
            default=self.shell.environ.get("HOME", "/"),
            help="Directory to change to (defaults to HOME)",
        )
        try:
            parsed_args, _ = parser.parse_known_args(args)
        except SystemExit:
            return self.get_help()

        target = parsed_args.directory

        # Attempt to change directory via the filesystem. Security checks are handled by the fs.
        if self.shell.fs.cd(target):
            self.shell.environ["PWD"] = self.shell.fs.pwd()
            return ""
        else:
            return f"cd: {target}: No such directory"
