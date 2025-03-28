# chuk_virtual_shell/commands/filesystem/mv.py
from chuk_virtual_shell.commands.command_base import ShellCommand

class MvCommand(ShellCommand):
    name = "mv"
    help_text = "mv - Move or rename files\nUsage: mv [source...] destination"
    category = "file"
    
    def execute(self, args):
        if len(args) < 2:
            return "mv: missing operand"
        
        *sources, destination = args
        
        if len(sources) > 1 and not self.shell.fs.isdir(destination):
            return f"mv: target '{destination}' is not a directory"
        
        for src in sources:
            content = self.shell.fs.read_file(src)
            if content is None:
                return f"mv: {src}: No such file"
            
            # Determine destination path
            if self.shell.fs.isdir(destination):
                import os
                dest_path = os.path.join(destination, src.split("/")[-1])
            else:
                dest_path = destination
                
            if not self.shell.fs.write_file(dest_path, content):
                return f"mv: failed to write to '{dest_path}'"
            
            self.shell.fs.delete_file(src)
        return ""
