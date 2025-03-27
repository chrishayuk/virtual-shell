"""
virtual_shell/commands/filesystem/cat.py - Display file contents command
"""
from virtual_shell.commands.command_base import ShellCommand

class CatCommand(ShellCommand):
    name = "cat"
    help_text = "cat - Display file contents\nUsage: cat [file]..."
    category = "file"
    
    def execute(self, args):
        if not args:
            return "cat: missing operand"
            
        result = []
        for path in args:
            content = self.shell.fs.read_file(path)
            if content is None:
                return f"cat: {path}: No such file"
            result.append(content)
                
        return "".join(result)