"""
chuk_virtual_shell/commands/system/sh.py - Execute shell scripts in virtual environment
"""
import asyncio
from chuk_virtual_shell.commands.command_base import ShellCommand
from chuk_virtual_shell.interpreters.bash_interpreter import VirtualBashInterpreter

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

    async def execute_async(self, args):
        """Execute shell script or command asynchronously"""
        if not self.interpreter:
            self.interpreter = VirtualBashInterpreter(self.shell)

        # Parse options
        options = {
            'command': False,
            'exit_on_error': False,
            'debug': False,
            'verbose': False
        }

        script_path = None
        command_string = None
        script_args = []

        i = 0
        while i < len(args):
            arg = args[i]
            if arg == '-c':
                options['command'] = True
                if i + 1 < len(args):
                    command_string = args[i + 1]
                    i += 1
                else:
                    return "sh: option requires an argument -- 'c'"
            elif arg == '-e':
                options['exit_on_error'] = True
            elif arg == '-x':
                options['debug'] = True
            elif arg == '-v':
                options['verbose'] = True
            elif arg.startswith('-'):
                return f"sh: invalid option -- '{arg[1:]}'"
            elif not script_path and not options['command']:
                script_path = arg
            else:
                script_args.append(arg)
            i += 1

        # Execute command string if -c was provided
        if options['command']:
            if command_string:
                return await self.interpreter.execute_line(command_string)
            else:
                return "sh: -c requires an argument"

        # Execute script file
        if script_path:
            # Check if file exists
            if not self.shell.fs.exists(script_path):
                return f"sh: {script_path}: No such file or directory"

            # Check if it's a file
            if not self.shell.fs.is_file(script_path):
                return f"sh: {script_path}: Is a directory"

            # Execute the script
            return await self.interpreter.run_script(script_path)

        # Interactive mode not supported
        return "sh: interactive mode not supported"

    def execute(self, args):
        """Synchronous wrapper for async execution"""
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
            # Fallback to sync execution with limited features
            return self._execute_sync(args)

    def _execute_sync(self, args):
        """Simplified synchronous execution"""
        if not args:
            return "sh: interactive mode not supported"

        # Handle -c option
        if '-c' in args:
            idx = args.index('-c')
            if idx + 1 < len(args):
                command = args[idx + 1]
                return self.shell.execute(command)
            return "sh: -c requires an argument"

        # Try to execute as script
        script_path = args[0]
        if not self.shell.fs.exists(script_path):
            return f"sh: {script_path}: No such file or directory"

        # Read and execute script line by line (simplified)
        content = self.shell.fs.read_file(script_path)
        if content is None:
            return f"sh: {script_path}: Cannot read file"

        results = []
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith('#'):
                result = self.shell.execute(line)
                if result:
                    results.append(result)

        return '\n'.join(results)
