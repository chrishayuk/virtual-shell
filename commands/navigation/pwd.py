"""
commands/navigation/pwd.py - Print working directory command
"""
from command_base import ShellCommand

class PwdCommand(ShellCommand):
    name = "pwd"
    help_text = "pwd - Print working directory\nUsage: pwd"
    category = "navigation"
    
    def execute(self, args):
        return self.shell.fs.pwd()