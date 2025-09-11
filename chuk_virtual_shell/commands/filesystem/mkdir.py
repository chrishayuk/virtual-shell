"""
chuk_virtual_shell/commands/filesystem/mkdir.py - Create directory command
"""

from chuk_virtual_shell.commands.command_base import ShellCommand


class MkdirCommand(ShellCommand):
    name = "mkdir"
    help_text = "mkdir - Create directory\nUsage: mkdir [-p] [directory]..."
    category = "file"

    def execute(self, args):
        if not args:
            return "mkdir: missing operand"

        # Check for -p flag
        create_parents = False
        dirs = []
        for arg in args:
            if arg == "-p":
                create_parents = True
            elif not arg.startswith("-"):
                dirs.append(arg)

        if not dirs:
            return "mkdir: missing operand"

        for path in dirs:
            if create_parents:
                # Create parent directories as needed
                parts = path.strip("/").split("/")
                current = ""
                for part in parts:
                    current = f"{current}/{part}" if current else f"/{part}"
                    if not self.shell.fs.exists(current):
                        if not self.shell.fs.mkdir(current):
                            return f"mkdir: cannot create directory '{current}'"
            else:
                if not self.shell.fs.mkdir(path):
                    return f"mkdir: cannot create directory '{path}'"

        return ""
