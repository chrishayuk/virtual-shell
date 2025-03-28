# chuk_virtual_shell/commands/filesystem/cp.py
"""
chuk_virtual_shell/commands/filesystem/cp.py - Copy files command
"""
import os
from chuk_virtual_shell.commands.command_base import ShellCommand

class CpCommand(ShellCommand):
    name = "cp"
    help_text = "cp - Copy files and directories\nUsage: cp [source...] destination"
    category = "file"
    
    def execute(self, args):
        if len(args) < 2:
            return "cp: missing operand"
        
        *sources, destination = args
        
        # Check if destination is a directory if multiple sources are provided
        if len(sources) > 1:
            dest_info = self.shell.fs.get_node_info(destination)
            if not dest_info or not dest_info.is_dir:
                return f"cp: target '{destination}' is not a directory"
        
        for src in sources:
            # Resolve source path
            src_resolved = self.shell.fs.resolve_path(src)
            dest_resolved = self.shell.fs.resolve_path(destination)
            
            # Check if source exists
            src_info = self.shell.fs.get_node_info(src_resolved)
            if not src_info:
                return f"cp: cannot stat '{src}': No such file or directory"
            
            # Determine destination path
            dest_info = self.shell.fs.get_node_info(dest_resolved)
            if dest_info and dest_info.is_dir:
                # If destination is a directory, put the file inside the directory
                src_basename = os.path.basename(src_resolved)
                dest_path = os.path.join(dest_resolved, src_basename)
            else:
                dest_path = dest_resolved
            
            # Handle files vs directories
            if not src_info.is_dir:
                # Copy file
                content = self.shell.fs.read_file(src_resolved)
                if content is None:
                    return f"cp: cannot read '{src}': Permission denied or file not found"
                
                if not self.shell.fs.write_file(dest_path, content):
                    return f"cp: failed to write to '{dest_path}'"
            else:
                # Copy directory - use the fs.cp method if available
                if hasattr(self.shell.fs, 'cp'):
                    if not self.shell.fs.cp(src_resolved, dest_path):
                        return f"cp: failed to copy directory '{src}' to '{destination}'"
                else:
                    # Manual recursive copy if fs.cp is not available
                    # First create the destination directory
                    dest_dir_info = self.shell.fs.get_node_info(dest_path)
                    if not dest_dir_info:
                        if not self.shell.fs.mkdir(dest_path):
                            return f"cp: failed to create directory '{dest_path}'"
                    
                    # Copy files recursively
                    for item in self.shell.fs.ls(src_resolved):
                        item_src = os.path.join(src_resolved, item)
                        item_dest = os.path.join(dest_path, item)
                        
                        item_info = self.shell.fs.get_node_info(item_src)
                        if item_info.is_dir:
                            # Recursively copy subdirectories
                            sub_result = self.execute([item_src, item_dest])
                            if sub_result:  # Error occurred
                                return sub_result
                        else:
                            # Copy file
                            content = self.shell.fs.read_file(item_src)
                            if not self.shell.fs.write_file(item_dest, content):
                                return f"cp: failed to copy '{item_src}' to '{item_dest}'"
                
        return ""