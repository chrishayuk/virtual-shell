# src/chuk_virtual_shell/commands/environment/env.py
"""
chuk_virtual_shell/commands/environment/env.py - Set environment variables command
"""

import argparse
from chuk_virtual_shell.commands.command_base import ShellCommand


class EnvCommand(ShellCommand):
    name = "env"
    help_text = (
        "env - Display environment variables\n"
        "Usage: env [filter]\n"
        "If a filter is provided, only display variables whose names contain the filter text."
    )
    category = "environment"

    def execute(self, args):
        parser = argparse.ArgumentParser(prog=self.name, add_help=False)
        parser.add_argument(
            "filter",
            nargs="?",
            default=None,
            help="Optional filter substring to match variable names",
        )
        try:
            parsed_args = parser.parse_args(args)
        except SystemExit:
            return self.get_help()

        # Retrieve the shell's environment variables
        env_vars = self.shell.environ

        # Apply filtering if a filter argument is provided
        if parsed_args.filter:
            env_vars = {k: v for k, v in env_vars.items() if parsed_args.filter in k}

        # Format the environment variables as "KEY=value" lines
        output_lines = [f"{k}={v}" for k, v in env_vars.items()]
        return "\n".join(output_lines)
