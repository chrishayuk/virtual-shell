"""
commands/environment/export.py - Set environment variables command
"""
from command_base import ShellCommand
   
class EnvCommand(ShellCommand):
    name = "env"
    help_text = "env - Display environment variables\nUsage: env"
    category = "environment"
    
    def execute(self, args):
        return "\n".join([f"{k}={v}" for k, v in self.shell.environ.items()])