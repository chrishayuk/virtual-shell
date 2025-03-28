# chuk_virtual_shell/commands/navigation/ls.py
import argparse
import time
from chuk_virtual_shell.commands.command_base import ShellCommand

class LsCommand(ShellCommand):
    name = "ls"
    help_text = (
        "ls - List directory contents\n"
        "Usage: ls [options] [directory]\n"
        "Options:\n"
        "  -l, --long   Use a long listing format\n"
        "  -a, --all    Include directory entries whose names begin with a dot (hidden files)\n"
        "If no directory is specified, lists the current directory."
    )
    category = "navigation"
    
    def execute(self, args):
        parser = argparse.ArgumentParser(prog=self.name, add_help=False)
        parser.add_argument("-l", "--long", action="store_true", help="Use a long listing format")
        parser.add_argument("-a", "--all", action="store_true", help="Include hidden files")
        parser.add_argument("directory", nargs="?", default=None, help="Directory to list (default: current directory)")
        try:
            parsed_args, _ = parser.parse_known_args(args)
        except SystemExit:
            return self.get_help()
        
        path = parsed_args.directory
        try:
            files = self.shell.fs.ls(path)
        except Exception as e:
            return f"ls: error: {e}"
        
        # Filter out hidden files if --all is not specified.
        if not parsed_args.all:
            files = [f for f in files if not f.startswith('.')]
        
        files = sorted(files)
        
        # If long listing is requested, simulate file details.
        if parsed_args.long:
            lines = []
            # Dummy details for simulation purposes.
            # In a real environment, you'd retrieve file stats from the filesystem.
            for f in files:
                # For directories, you might choose a different permission string.
                mode = "drwxr-xr-x" if self._is_directory(f, path) else "-rw-r--r--"
                nlink = 1
                owner = self.shell.environ.get("USER", "user")
                group = "staff"
                size = 1024  # Dummy file size in bytes.
                mod_date = time.strftime("%b %d %H:%M", time.localtime())
                lines.append(f"{mode} {nlink} {owner} {group} {size} {mod_date} {f}")
            return "\n".join(lines)
        else:
            return " ".join(files)
    
    def _is_directory(self, filename: str, path: str) -> bool:
        """
        Helper method to determine if a given filename is a directory.
        This implementation depends on the VirtualFileSystem.
        """
        # Attempt to construct the full path. The VirtualFileSystem should
        # resolve it appropriately.
        try:
            info = self.shell.fs.get_node_info(filename, base_path=path)
            return info.is_dir if info else False
        except Exception:
            return False
