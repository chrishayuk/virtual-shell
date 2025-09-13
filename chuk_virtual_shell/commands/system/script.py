# src/chuk_virtual_shell/commands/system/script.py
"""
chuk_virtual_shell/chuk_virtual_shell/commands/system/script.py - Run shell scripts command
"""

import argparse
from chuk_virtual_shell.commands.command_base import ShellCommand
from chuk_virtual_shell.script_runner import ScriptRunner


class ScriptCommand(ShellCommand):
    name = "script"
    help_text = (
        "script - Run one or more shell scripts\n"
        "Usage: script [filename1] [filename2] ...\n"
        "Runs the specified shell script(s) using the virtual shell environment."
    )
    category = "system"

    def execute(self, args):
        if not args:
            return "script: missing operand"
        parser = argparse.ArgumentParser(prog=self.name, add_help=False)
        parser.add_argument(
            "filenames", nargs="+", help="One or more script file paths to run"
        )
        parsed_args, unknown = parser.parse_known_args(args)

        results = []
        runner = ScriptRunner(self.shell)
        for script_path in parsed_args.filenames:
            try:
                result = runner.run_script(script_path)
                results.append(result)
            except Exception as e:
                results.append(f"Error running script '{script_path}': {e}")
        return "\n".join(results)
