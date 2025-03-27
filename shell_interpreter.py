"""
shell_interpreter.py - Core shell interpreter for PyodideShell
"""
# Import necessary modules
from filesystem import VirtualFileSystem
from command_loader import CommandLoader

class ShellInterpreter:
    def __init__(self, fs=None):
        # Initialize filesystem
        self.fs = fs if fs is not None else VirtualFileSystem()
        
        # Set up environment
        self.environ = {
            "HOME": "/home/user",
            "PATH": "/bin:/usr/bin",
            "USER": "user",
            "SHELL": "/bin/bash",
            "PWD": self.fs.pwd(),
        }
        
        self.running = True
        
        # Register commands - using command loader for dynamic discovery
        self.commands = {}
        self._load_commands()
    
    def _load_commands(self):
        """Dynamically load all available commands"""
        # Use the command loader to discover commands
        discovered_commands = CommandLoader.discover_commands(self)
        
        # Register all discovered commands
        self.commands.update(discovered_commands)
        
        # Optionally, load commands from external paths
        # This could be used to load user-defined commands
        # external_commands = CommandLoader.load_commands_from_path(self, "path/to/user/commands")
        # self.commands.update(external_commands)
    
    def _register_command(self, command):
        """Register a single command with the shell"""
        self.commands[command.name] = command
    
    def parse_command(self, cmd_line):
        """Parse a command line into command and arguments"""
        if not cmd_line or not cmd_line.strip():
            return None, []
            
        parts = cmd_line.strip().split()
        cmd = parts[0]
        args = parts[1:]
        return cmd, args
    
    def execute(self, cmd_line):
        """Execute a command line"""
        cmd, args = self.parse_command(cmd_line)
        
        if not cmd:
            return ""
            
        if cmd in self.commands:
            return self.commands[cmd].execute(args)
        else:
            return f"{cmd}: command not found"
    
    def prompt(self):
        """Return the command prompt"""
        username = self.environ.get("USER", "user")
        hostname = "pyodide"
        pwd = self.environ.get("PWD", "/")
        return f"{username}@{hostname}:{pwd}$ "