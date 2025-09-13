# src/chuk_virtual_shell/commands/navigation/cd.py
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
        "Use 'cd -' to return to the previous directory.\n"
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
        
        # Handle cd - (previous directory)
        if target == "-":
            # Get the previous directory from OLDPWD
            target = self.shell.environ.get("OLDPWD", None)
            if not target:
                return "cd: OLDPWD not set"
            # Print the directory we're changing to (standard behavior)
            print_dir = True
        else:
            print_dir = False

        # Store current directory as OLDPWD before changing
        current_dir = self.shell.fs.pwd()

        # Attempt to change directory via the filesystem. Security checks are handled by the fs.
        if self.shell.fs.cd(target):
            # Update OLDPWD with the previous directory
            self.shell.environ["OLDPWD"] = current_dir
            # Update PWD with the new directory
            self.shell.environ["PWD"] = self.shell.fs.pwd()
            # If using cd -, print the new directory
            if print_dir:
                return self.shell.fs.pwd()
            return ""
        else:
            return f"cd: {target}: No such directory"
