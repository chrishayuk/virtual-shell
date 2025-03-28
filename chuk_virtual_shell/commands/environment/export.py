"""
chuk_virtual_shell/commands/environment/export.py - Set environment variables command
"""
from chuk_virtual_shell.commands.command_base import ShellCommand

class ExportCommand(ShellCommand):
    name = "export"
    help_text = "export - Set environment variables\nUsage: export KEY=VALUE..."
    category = "environment"
    
    def execute(self, args):
        if not args:
            return ""
            
        for arg in args:
            if "=" in arg:
                key, value = arg.split("=", 1)
                self.shell.environ[key] = value
                
        return ""