"""
chuk_virtual_shell/commands/filesystem/rmdir.py - Remove empty directories command
"""

from chuk_virtual_shell.commands.command_base import ShellCommand


class RmdirCommand(ShellCommand):
    name = "rmdir"
    help_text = "rmdir - Remove empty directories\nUsage: rmdir [directory]..."
    category = "file"

    def execute(self, args):
        if not args:
            return "rmdir: missing operand"

        for path in args:
            if not self.shell.fs.rmdir(path):
                return (
                    f"rmdir: cannot remove '{path}': Directory not empty or not found"
                )

        return ""
