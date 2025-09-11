"""
chuk_virtual_shell/commands/filesystem/touch.py - Create empty file command
"""

from chuk_virtual_shell.commands.command_base import ShellCommand


class TouchCommand(ShellCommand):
    name = "touch"
    help_text = "touch - Create empty file\nUsage: touch [file]..."
    category = "file"

    def execute(self, args):
        if not args:
            return "touch: missing operand"

        for path in args:
            if not self.shell.fs.touch(path):
                return f"touch: cannot touch '{path}'"

        return ""
