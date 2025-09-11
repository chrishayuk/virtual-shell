"""
chuk_virtual_shell/commands/filesystem/cat.py - Display file contents command
"""

from chuk_virtual_shell.commands.command_base import ShellCommand


class CatCommand(ShellCommand):
    name = "cat"
    help_text = "cat - Display file contents\nUsage: cat [file]..."
    category = "file"

    def execute(self, args):
        # Check if we have stdin input (from input redirection or pipe)
        if not args:
            # If no arguments, read from stdin if available
            if hasattr(self.shell, "_stdin_buffer") and self.shell._stdin_buffer:
                result = self.shell._stdin_buffer
                # Clear the buffer after use
                self.shell._stdin_buffer = None
                return result
            return "cat: missing operand"

        result = []
        for path in args:
            content = self.shell.fs.read_file(path)
            if content is None:
                return f"cat: {path}: No such file"
            result.append(content)

        return "".join(result)
