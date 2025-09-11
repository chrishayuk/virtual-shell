"""
chuk_virtual_shell/commands/system/python.py - Execute Python scripts in virtual environment
"""
import asyncio
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

    async def execute_async(self, args):
        """Execute Python script or command asynchronously"""
        if not self.interpreter:
            self.interpreter = VirtualPythonInterpreter(self.shell)

        # Parse options
        command_string = None
        module_name = None
        script_path = None
        script_args = []
        show_version = False
        interactive = False

        i = 0
        while i < len(args):
            arg = args[i]
            if arg == '-c':
                if i + 1 < len(args):
                    command_string = args[i + 1]
                    i += 1
                else:
                    return "python: -c requires an argument"
            elif arg == '-m':
                if i + 1 < len(args):
                    module_name = args[i + 1]
                    i += 1
                else:
                    return "python: -m requires an argument"
            elif arg == '-V' or arg == '--version':
                show_version = True
            elif arg == '-i':
                interactive = True
            elif arg.startswith('-'):
                return f"python: invalid option -- '{arg}'"
            elif not script_path and not command_string and not module_name:
                script_path = arg
            else:
                script_args.append(arg)
            i += 1

        # Handle version flag
        if show_version:
            return "Python 3.x.x (virtual environment)"

        # Execute command string if -c was provided
        if command_string:
            return await self.interpreter.execute_code(command_string)

        # Handle module execution
        if module_name:
            # Simplified module execution
            return f"python: module execution not fully implemented: {module_name}"

        # Execute script file
        if script_path:
            # Check if file exists
            if not self.shell.fs.exists(script_path):
                return f"python: can't open file '{script_path}': No such file or directory"

            # Check if it's a file
            if not self.shell.fs.is_file(script_path):
                return f"python: '{script_path}' is a directory, not a Python file"

            # Execute the script
            return await self.interpreter.run_script(script_path, script_args)

        # Interactive mode
        if interactive or not args:
            return "Python interactive mode not fully supported\nUse 'python -c \"code\"' or 'python script.py' instead"

    def execute(self, args):
        """Synchronous wrapper for execution"""
        # Try to run async if possible
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're already in an async context
                task = asyncio.create_task(self.execute_async(args))
                return asyncio.run_until_complete(task)
            else:
                # Create new event loop
                return asyncio.run(self.execute_async(args))
        except Exception:
            # Fallback to sync execution
            return self._execute_sync(args)

    def _execute_sync(self, args):
        """Synchronous execution"""
        if not self.interpreter:
            self.interpreter = VirtualPythonInterpreter(self.shell)

        # Parse for common cases
        if not args:
            return "Python interactive mode not fully supported"

        # Handle -c option
        if '-c' in args:
            idx = args.index('-c')
            if idx + 1 < len(args):
                command = args[idx + 1]
                return self.interpreter.execute_code_sync(command)
            return "python: -c requires an argument"

        # Handle version
        if '-V' in args or '--version' in args:
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
