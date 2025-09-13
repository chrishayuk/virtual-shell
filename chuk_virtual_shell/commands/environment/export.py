# src/chuk_virtual_shell/commands/environment/export.py
import argparse
from chuk_virtual_shell.commands.command_base import ShellCommand


class ExportCommand(ShellCommand):
    name = "export"
    help_text = (
        "export - Set environment variables\n"
        "Usage: export KEY=VALUE [KEY2=VALUE2 ...]\n"
        "Sets environment variables in the current shell session. "
        "Each assignment must be in the format KEY=VALUE."
    )
    category = "environment"

    def execute(self, args):
        parser = argparse.ArgumentParser(prog=self.name, add_help=False)
        parser.add_argument(
            "assignments", nargs="*", help="Assignments in KEY=VALUE format"
        )
        try:
            parsed_args = parser.parse_args(args)
        except SystemExit:
            # If argument parsing fails, show help text.
            return self.get_help()

        messages = []
        for assignment in parsed_args.assignments:
            if "=" not in assignment:
                messages.append(
                    f"export: invalid assignment '{assignment}' (expected KEY=VALUE)"
                )
                continue
            key, value = assignment.split("=", 1)
            if not key:
                messages.append("export: missing variable name")
                continue
            # Set the variable in the shell environment.
            self.shell.environ[key] = value

        # If any errors occurred, return the error messages, otherwise return an empty string.
        return "\n".join(messages) if messages else ""
