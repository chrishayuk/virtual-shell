# src/chuk_virtual_shell/commands/system/time.py
"""
chuk_virtual_shell/commands/system/time.py - time
"""

import argparse
import time
from chuk_virtual_shell.commands.command_base import ShellCommand


class TimeCommand(ShellCommand):
    name = "time"
    help_text = (
        "time - Measure the execution time of a command\n"
        "Usage: time [command] [arguments]\n"
        "If a command is provided, this command will execute it and report the time taken.\n"
        "If no command is provided, it prints the current system time."
    )
    category = "system"

    def execute(self, args):
        parser = argparse.ArgumentParser(prog=self.name, add_help=False)
        parser.add_argument("subcommand", nargs="*", help="Command to time")
        parsed_args, unknown = parser.parse_known_args(args)

        if parsed_args.subcommand:
            command_line = " ".join(parsed_args.subcommand)
            start = time.perf_counter()
            result = self.shell.execute(command_line)
            end = time.perf_counter()
            elapsed = end - start
            return f"{result}\nExecution time: {elapsed:.4f} seconds"
        else:
            current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            return f"Current time: {current_time}"
