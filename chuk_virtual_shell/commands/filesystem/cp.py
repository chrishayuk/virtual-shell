# chuk_virtual_shell/commands/filesystem/cp.py
from chuk_virtual_shell.commands.command_base import ShellCommand

class CpCommand(ShellCommand):
    name = "cp"
    help_text = "cp - Copy files\nUsage: cp [source...] destination"
    category = "file"
    
    def execute(self, args):
        if len(args) < 2:
            return "cp: missing operand"
        
        *sources, destination = args
        
        # Check if destination is a directory if multiple sources are provided.
        if len(sources) > 1:
            if not self.shell.fs.isdir(destination):
                return f"cp: target '{destination}' is not a directory"
        
        for src in sources:
            content = self.shell.fs.read_file(src)
            if content is None:
                return f"cp: {src}: No such file"
            
            # Determine destination path
            if self.shell.fs.isdir(destination):
                import os
                dest_path = os.path.join(destination, src.split("/")[-1])
            else:
                dest_path = destination
            
            if not self.shell.fs.write_file(dest_path, content):
                return f"cp: failed to write to '{dest_path}'"
                
        return ""
