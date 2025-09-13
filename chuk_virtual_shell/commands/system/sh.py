# src/chuk_virtual_shell/commands/system/sh.py
"""
chuk_virtual_shell/commands/system/sh.py - Execute shell scripts in virtual environment
"""

from chuk_virtual_shell.commands.command_base import ShellCommand


class ShCommand(ShellCommand):
    name = "sh"
    help_text = """sh - Execute shell script or command
Usage: sh [OPTIONS] [SCRIPT] [ARGS]...
       sh -c COMMAND
Options:
  -c        Execute command string
  -e        Exit on error
  -x        Print commands as executed (debug)
  -v        Verbose mode
Examples:
  sh script.sh          Execute script file
  sh -c "echo hello"    Execute command string"""
    category = "system"

    def __init__(self, shell_context=None):
        super().__init__(shell_context)
        self.interpreter = None

    def execute(self, args):
        """Synchronous execution"""
        return self._execute_sync(args)

    async def execute_async(self, args):
        """Asynchronous execution"""
        if not args:
            return "sh: interactive mode not supported"

        # Handle -c option
        if "-c" in args:
            idx = args.index("-c")
            if idx + 1 < len(args):
                command = args[idx + 1]
                # Execute command asynchronously
                result = self.shell.execute(command)
                return result
            return "sh: -c requires an argument"

        # Try to execute as script
        script_path = args[0]
        if not self.shell.fs.exists(script_path):
            return f"sh: {script_path}: No such file or directory"

        # Check if it's a directory
        if self.shell.fs.is_dir(script_path):
            return f"sh: {script_path}: Is a directory"

        # Read and execute script line by line asynchronously
        content = self.shell.fs.read_file(script_path)
        if content is None:
            return f"sh: {script_path}: Cannot read file"

        results = []
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                # Execute each line (could be made more async if needed)
                result = self.shell.execute(line)
                if result:
                    results.append(result)

        return "\n".join(results)

    def _execute_sync(self, args):
        """Simplified synchronous execution"""
        if not args:
            return "sh: interactive mode not supported"

        # Handle -c option
        if "-c" in args:
            idx = args.index("-c")
            if idx + 1 < len(args):
                command = args[idx + 1]
                return self.shell.execute(command)
            return "sh: -c requires an argument"

        # Try to execute as script
        script_path = args[0]
        if not self.shell.fs.exists(script_path):
            return f"sh: {script_path}: No such file or directory"

        # Check if it's a directory
        if self.shell.fs.is_dir(script_path):
            return f"sh: {script_path}: Is a directory"

        # Read and execute script line by line (simplified)
        content = self.shell.fs.read_file(script_path)
        if content is None:
            return f"sh: {script_path}: Cannot read file"

        results = []
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                result = self.shell.execute(line)
                if result:
                    results.append(result)

        return "\n".join(results)
