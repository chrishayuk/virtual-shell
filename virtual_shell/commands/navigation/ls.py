"""
virtual_shell/commands/navigation/ls.py - List directory contents command
"""
from virtual_shell.commands.command_base import ShellCommand

class LsCommand(ShellCommand):
    name = "ls"
    help_text = "ls - List directory contents\nUsage: ls [directory]"
    category = "navigation"
    
    def execute(self, args):
        path = args[0] if args else None
        files = self.shell.fs.ls(path)
        return " ".join(sorted(files))