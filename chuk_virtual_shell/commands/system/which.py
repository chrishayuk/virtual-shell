"""
chuk_virtual_shell/commands/system/which.py - which command implementation

Locates a command in the shell's available commands or in the PATH.
"""

from chuk_virtual_shell.commands.command_base import ShellCommand


class WhichCommand(ShellCommand):
    """Find the location of a command"""

    name = "which"
    help_text = """which - locate a command
    
Usage: which [-a] command [command ...]

Options:
    -a    Print all matching pathnames of each argument

Description:
    The which command searches for the specified command(s) in the shell's
    built-in commands and in directories listed in the PATH environment variable.
    
Examples:
    which ls           # Find the ls command
    which -a python    # Find all python executables
    which cd pwd ls    # Find multiple commands"""

    category = "system"

    def execute(self, args):
        """Execute the which command"""
        show_all = False
        commands_to_find = []

        # Parse arguments
        i = 0
        while i < len(args):
            arg = args[i]
            if arg == "-a":
                show_all = True
            elif arg.startswith("-"):
                return f"which: invalid option -- '{arg[1:]}'\nTry 'which --help' for more information."
            else:
                commands_to_find.append(arg)
            i += 1

        if not commands_to_find:
            return "which: no command specified"

        results = []

        for cmd in commands_to_find:
            found = []

            # First check if it's a built-in shell command
            if cmd in self.shell.commands:
                found.append(f"{cmd}: shell built-in command")
                if not show_all:
                    results.append(found[0])
                    continue

            # Check PATH environment variable
            path_env = self.shell.environ.get("PATH", "/usr/bin:/bin")
            paths = path_env.split(":")

            for path_dir in paths:
                # Resolve the path
                try:
                    resolved_path = self.shell.fs.resolve_path(path_dir)
                except Exception:
                    continue

                # Check if command exists in this directory
                cmd_path = f"{resolved_path}/{cmd}"
                if self.shell.fs.exists(cmd_path) and self.shell.fs.is_file(cmd_path):
                    found.append(cmd_path)
                    if not show_all:
                        break

            # Add results
            if found:
                if show_all:
                    results.extend(found)
                elif cmd not in self.shell.commands:
                    # Only add PATH results if we didn't already add built-in
                    results.extend(found)
            else:
                # Command not found
                if show_all or not results:
                    results.append(f"{cmd} not found")

        return "\n".join(results) if results else "Command not found"
