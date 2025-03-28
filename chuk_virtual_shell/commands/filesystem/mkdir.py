"""
chuk_virtual_shell/commands/filesystem/mkdir.py - Create directory command
"""
from chuk_virtual_shell.commands.command_base import ShellCommand

class MkdirCommand(ShellCommand):
    name = "mkdir"
    help_text = "mkdir - Create directory\nUsage: mkdir [directory]..."
    category = "file"
    
    def execute(self, args):
        if not args:
            return "mkdir: missing operand"
            
        for path in args:
            if not self.shell.fs.mkdir(path):
                return f"mkdir: cannot create directory '{path}'"
                
        return ""