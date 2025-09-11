"""
chuk_virtual_shell/commands/filesystem/rm.py - Remove files command
"""

from chuk_virtual_shell.commands.command_base import ShellCommand


class RmCommand(ShellCommand):
    name = "rm"
    help_text = "rm - Remove files\nUsage: rm [file]..."
    category = "file"

    def execute(self, args):
        if not args:
            return "rm: missing operand"

        for path in args:
            if not self.shell.fs.rm(path):
                return f"rm: cannot remove '{path}'"

        return ""
