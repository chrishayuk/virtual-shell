"""
chuk_virtual_shell/commands/filesystem/echo.py - Echo arguments command
"""

from chuk_virtual_shell.commands.command_base import ShellCommand


class EchoCommand(ShellCommand):
    name = "echo"
    help_text = "echo - Echo arguments\nUsage: echo [text] [> file | >> file]"
    category = "file"

    def execute(self, args):
        if not args:
            return ""

        # Handle redirection
        output = " ".join(args)
        redirection = None

        if ">" in args:
            redirect_index = args.index(">")
            output = " ".join(args[:redirect_index])
            if redirect_index + 1 < len(args):
                redirection = args[redirect_index + 1]

        elif ">>" in args:
            redirect_index = args.index(">>")
            output = " ".join(args[:redirect_index])
            if redirect_index + 1 < len(args):
                redirection = args[redirect_index + 1]
                # Append mode - concatenate directly without adding newline
                current = self.shell.fs.read_file(redirection) or ""
                output = current + output

        if redirection:
            if not self.shell.fs.write_file(redirection, output):
                return f"echo: cannot write to '{redirection}'"
            return ""

        return output
