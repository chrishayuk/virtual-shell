# src/chuk_virtual_shell/commands/system/help.py
"""
chuk_virtual_shell/commands/system/help.py - Help command
"""

import argparse
from chuk_virtual_shell.commands.command_base import ShellCommand


class HelpCommand(ShellCommand):
    name = "help"
    help_text = (
        "help - Display help for commands\n"
        "Usage: help [command]\n"
        "If a command is provided, detailed help for that command is shown. "
        "Otherwise, a summary of available commands by category is displayed."
    )
    category = "system"

    def execute(self, args):
        # Use argparse to optionally accept a command argument.
        parser = argparse.ArgumentParser(prog=self.name, add_help=False)
        parser.add_argument("command", nargs="?", help="Command to display help for")
        try:
            parsed_args = parser.parse_args(args)
        except SystemExit:
            return self.get_help()

        if parsed_args.command:
            cmd_name = parsed_args.command
            if cmd_name in self.shell.commands:
                return self.shell.commands[cmd_name].get_help()
            else:
                return f"help: no help found for '{cmd_name}'"

        # Define predefined command categories.
        categories = {
            "Navigation commands": ["cd", "pwd", "ls"],
            "File commands": ["cat", "echo", "touch", "mkdir", "rm", "rmdir"],
            "Environment commands": ["env", "export"],
            "System commands": ["help", "exit", "clear"],
        }

        result = []
        # List commands by predefined categories.
        for category_name, cmds in categories.items():
            available = sorted(cmd for cmd in cmds if cmd in self.shell.commands)
            if available:
                result.append(f"{category_name}: " + ", ".join(available))

        # Include any additional commands not listed in the predefined categories.
        predefined_set = set(sum(categories.values(), []))
        extra_commands = sorted(list(set(self.shell.commands.keys()) - predefined_set))
        if extra_commands:
            result.append("Other commands: " + ", ".join(extra_commands))

        result.append("Type 'help [command]' for more information")
        return "\n".join(result)
