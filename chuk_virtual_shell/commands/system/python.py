# src/chuk_virtual_shell/commands/system/python.py
"""
chuk_virtual_shell/commands/system/python.py - Execute Python scripts in virtual environment
"""

from chuk_virtual_shell.commands.command_base import ShellCommand
from chuk_virtual_shell.interpreters.python_interpreter import VirtualPythonInterpreter


class PythonCommand(ShellCommand):
    name = "python"
    help_text = """python - Execute Python scripts in virtual environment
Usage: python [OPTIONS] [SCRIPT] [ARGS]...
       python -c COMMAND
Options:
  -c        Execute command string
  -m        Run module as script
  -i        Interactive mode (limited support)
  -V        Print version
Examples:
  python script.py          Execute script file
  python -c "print('hi')"   Execute command string
  python -m module          Run module as script"""
    category = "system"

    def __init__(self, shell_context=None):
        super().__init__(shell_context)
        self.interpreter = None

    def execute(self, args):
        """Synchronous execution"""
        return self._execute_sync(args)

    async def execute_async(self, args):
        """Asynchronous execution"""
        if not self.interpreter:
            self.interpreter = VirtualPythonInterpreter(self.shell)

        # Parse for common cases
        if not args:
            return "Python interactive mode not fully supported"

        # Handle -c option
        if "-c" in args:
            idx = args.index("-c")
            if idx + 1 < len(args):
                command = args[idx + 1]
                return await self.interpreter.execute_code(command)
            return "python: -c requires an argument"

        # Handle -m option
        if "-m" in args:
            idx = args.index("-m")
            if idx + 1 < len(args):
                # module = args[idx + 1]  # Will be used when module execution is implemented
                return "Python module execution not fully implemented"
            return "python: -m requires an argument"

        # Handle version
        if "-V" in args or "--version" in args:
            return "Python 3.x.x (virtual environment)"

        # Try to execute as script
        script_path = args[0]
        script_args = args[1:] if len(args) > 1 else []

        if not self.shell.fs.exists(script_path):
            return f"python: can't open file '{script_path}': No such file or directory"

        return await self.interpreter.run_script(script_path, script_args)

    def _execute_sync(self, args):
        """Synchronous execution"""
        if not self.interpreter:
            self.interpreter = VirtualPythonInterpreter(self.shell)

        # Parse for common cases
        if not args:
            return "Python interactive mode not fully supported"

        # Handle -c option
        if "-c" in args:
            idx = args.index("-c")
            if idx + 1 < len(args):
                command = args[idx + 1]
                return self.interpreter.execute_code_sync(command)
            return "python: -c requires an argument"

        # Handle -m option
        if "-m" in args:
            idx = args.index("-m")
            if idx + 1 < len(args):
                # module = args[idx + 1]  # Will be used when module execution is implemented
                return "Python module execution not fully implemented"
            return "python: -m requires an argument"

        # Handle version
        if "-V" in args or "--version" in args:
            return "Python 3.x.x (virtual environment)"

        # Try to execute as script
        script_path = args[0]
        script_args = args[1:] if len(args) > 1 else []

        if not self.shell.fs.exists(script_path):
            return f"python: can't open file '{script_path}': No such file or directory"

        return self.interpreter.run_script_sync(script_path, script_args)


class Python3Command(PythonCommand):
    """Alias for python command"""

    name = "python3"
