"""
commands/system/exit.py - Exit the shell command
"""
from command_base import ShellCommand

class ExitCommand(ShellCommand):
    name = "exit"
    help_text = "exit - Exit the shell\nUsage: exit"
    category = "system"
    
    def execute(self, args):
        self.shell.running = False
        return "Goodbye!"