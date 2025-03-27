"""
virtual_shell/commands/navigation/cd.py - Change directory command
"""
from virtual_shell.commands.command_base import ShellCommand

class CdCommand(ShellCommand):
    name = "cd"
    help_text = "cd - Change directory\nUsage: cd [directory]"
    category = "navigation"
    
    def execute(self, args):
        if not args:
            # Default to home directory
            path = self.shell.environ.get("HOME", "/")
        else:
            path = args[0]
            
        if self.shell.fs.cd(path):
            self.shell.environ["PWD"] = self.shell.fs.pwd()
            return ""
        else:
            return f"cd: {path}: No such directory"