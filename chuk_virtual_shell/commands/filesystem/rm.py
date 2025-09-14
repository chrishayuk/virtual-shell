"""
chuk_virtual_shell/commands/filesystem/rm.py - Remove files command
"""

from chuk_virtual_shell.commands.command_base import ShellCommand


class RmCommand(ShellCommand):
    name = "rm"
    help_text = """rm - Remove files and directories
Usage: rm [OPTION]... FILE...
Options:
  -r, -R    Remove directories and their contents recursively
  -f        Force removal, ignore nonexistent files, never prompt
  -i        Interactive mode, prompt before every removal
  -v        Verbose mode, explain what is being done
  --help    Display this help and exit"""
    category = "file"

    def execute(self, args):
        if not args:
            return "rm: missing operand"

        # Parse options
        recursive = False
        force = False
        interactive = False
        verbose = False
        
        files = []
        i = 0
        while i < len(args):
            arg = args[i]
            if arg.startswith("-") and arg != "-":
                if arg == "--help":
                    return self.help_text
                elif arg == "--":
                    files.extend(args[i+1:])
                    break
                else:
                    # Process flags (can be combined like -rf)
                    for flag in arg[1:]:
                        if flag in ['r', 'R']:
                            recursive = True
                        elif flag == 'f':
                            force = True
                        elif flag == 'i':
                            interactive = True
                        elif flag == 'v':
                            verbose = True
                        else:
                            if not force:
                                return f"rm: invalid option -- '{flag}'"
            else:
                files.append(arg)
            i += 1

        if not files:
            return "rm: missing operand"

        results = []
        errors = []
        
        for path in files:
            # Check if path exists
            if not self.shell.fs.exists(path):
                if not force:
                    errors.append(f"rm: cannot remove '{path}': No such file or directory")
                continue
            
            # Check if it's a directory
            if self.shell.fs.is_dir(path):
                if not recursive:
                    errors.append(f"rm: cannot remove '{path}': Is a directory")
                    continue
                    
                # Remove directory recursively
                if not self._remove_recursive(path, force, verbose, results, errors):
                    if not force:
                        errors.append(f"rm: cannot remove '{path}'")
            else:
                # Remove file
                if interactive:
                    # In non-interactive shell, skip interactive prompts
                    continue
                    
                if self.shell.fs.rm(path):
                    if verbose:
                        results.append(f"removed '{path}'")
                else:
                    if not force:
                        errors.append(f"rm: cannot remove '{path}': Permission denied")

        # Combine results and errors
        output = []
        if verbose and results:
            output.extend(results)
        if errors:
            output.extend(errors)
            
        return "\n".join(output) if output else ""
    
    def _remove_recursive(self, path, force, verbose, results, errors):
        """Recursively remove a directory and its contents"""
        # First, find all files/dirs that start with this path
        # This handles the flat structure of DummyFileSystem
        to_remove = []
        
        # Collect all paths that are under this directory
        for fs_path in list(self.shell.fs.files.keys()):
            if fs_path == path or fs_path.startswith(path + "/"):
                to_remove.append(fs_path)
        
        # Sort in reverse order so we remove deepest items first
        to_remove.sort(reverse=True)
        
        # Remove files and empty directories
        for item_path in to_remove:
            if item_path == path:
                continue  # Handle the parent directory last
                
            if self.shell.fs.is_dir(item_path):
                # Remove empty directory
                if hasattr(self.shell.fs, 'rmdir'):
                    if self.shell.fs.rmdir(item_path):
                        if verbose:
                            results.append(f"removed directory '{item_path}'")
                    elif not force:
                        # Directory not empty or other error
                        pass
            else:
                # Remove file
                if self.shell.fs.rm(item_path):
                    if verbose:
                        results.append(f"removed '{item_path}'")
                elif not force:
                    errors.append(f"rm: cannot remove '{item_path}'")
                    return False
        
        # Now remove the parent directory itself
        if hasattr(self.shell.fs, 'rmdir'):
            # First try to remove it as empty dir
            if self.shell.fs.rmdir(path):
                if verbose:
                    results.append(f"removed directory '{path}'")
                return True
            else:
                # If it fails, force remove from files dict
                if path in self.shell.fs.files:
                    del self.shell.fs.files[path]
                    if verbose:
                        results.append(f"removed directory '{path}'")
                    return True
        
        return False
