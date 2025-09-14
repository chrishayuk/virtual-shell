"""
tests/chuk_virtual_shell/commands/navigation/test_pwd_command.py
"""

import argparse
from chuk_virtual_shell.commands.command_base import ShellCommand


class PwdCommand(ShellCommand):
    name = "pwd"
    help_text = (
        "pwd - Print working directory\n"
        "Usage: pwd\n"
        "Displays the current working directory of the virtual shell."
    )
    category = "navigation"

    def execute(self, args):
        parser = argparse.ArgumentParser(prog=self.name, add_help=False)
        # We don't expect any arguments for pwd; extra arguments are ignored.
        parser.parse_known_args(args)
        try:
            return self.shell.fs.pwd()
        except Exception as e:
            return f"pwd: error: {e}"
