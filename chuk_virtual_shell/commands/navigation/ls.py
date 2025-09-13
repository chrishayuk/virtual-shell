# src/chuk_virtual_shell/commands/navigation/ls.py
import argparse
import os
import time
from chuk_virtual_shell.commands.command_base import ShellCommand


class LsCommand(ShellCommand):
    name = "ls"
    help_text = (
        "ls - List directory contents\n"
        "Usage: ls [options] [directory]\n"
        "Options:\n"
        "  -l, --long   Use a long listing format\n"
        "  -a, --all    Include hidden files (those beginning with a dot)\n"
        "If no directory is specified, lists the current directory."
    )
    category = "navigation"

    def execute(self, args):
        parser = argparse.ArgumentParser(prog=self.name, add_help=False)
        parser.add_argument(
            "-l", "--long", action="store_true", help="Use a long listing format"
        )
        parser.add_argument(
            "-a", "--all", action="store_true", help="Include hidden files"
        )
        parser.add_argument(
            "paths",
            nargs="*",
            default=None,
            help="Files or directories to list",
        )
        try:
            parsed_args, _ = parser.parse_known_args(args)
        except SystemExit:
            return self.get_help()

        # If no paths provided, use current directory
        if not parsed_args.paths:
            if hasattr(self.shell.fs, "pwd") and callable(self.shell.fs.pwd):
                paths = [self.shell.fs.pwd()]
            else:
                paths = [self.shell.environ.get("PWD", ".")]
        else:
            paths = parsed_args.paths

        # Handle multiple paths
        results = []
        for path in paths:
            # Resolve the path
            resolved_path = self.shell.resolve_path(path)
            
            # Check if it's a file or directory
            try:
                node_info = self.shell.fs.get_node_info(resolved_path)
            except Exception:
                # If get_node_info fails, assume doesn't exist
                node_info = None
                
            if not node_info:
                results.append(f"ls: cannot access '{path}': No such file or directory")
                continue
            
            if node_info.is_dir:
                # List directory contents
                if len(paths) > 1:
                    results.append(f"{path}:")
                result = self._list_directory(resolved_path, parsed_args.long, parsed_args.all)
                results.append(result)
                if len(paths) > 1:
                    results.append("")  # Empty line between directories
            else:
                # It's a file, just list it
                if parsed_args.long:
                    result = self._format_long_listing([path], resolved_path)
                else:
                    result = path
                results.append(result)
        
        return "\n".join(results).strip()

    def _list_directory(self, resolved_dir, long_format, show_all):
        """List contents of a directory"""
        # Verify the directory exists and is a directory
        if not self._directory_exists(resolved_dir):
            return f"ls: cannot access '{resolved_dir}': No such file or directory"

        try:
            files = self.shell.fs.ls(resolved_dir)

            # Add special directory entries . and .. if in all mode
            if show_all and isinstance(files, list):
                files = ["."] + ([".."] if resolved_dir != "/" else []) + files

        except Exception as e:
            return f"ls: error: {e}"

        # Filter out hidden files if --all is not specified
        if not show_all and isinstance(files, list):
            files = [f for f in files if not f.startswith(".")]

        # Ensure files is a list before sorting
        if not isinstance(files, list):
            return f"ls: unexpected result from filesystem: {files}"

        files = sorted(files)

        if long_format:
            lines = []
            for f in files:
                # Skip special directory entries in size calculation
                if f in [".", ".."]:
                    # Handle special directory entries
                    mode = "drwxr-xr-x"
                    nlink = 1
                    owner = self.shell.environ.get("USER", "user")
                    group = "staff"
                    size = 0  # Directory size can be shown as 0
                    mod_date = time.strftime("%b %d %H:%M", time.localtime())
                    lines.append(
                        f"{mode} {nlink} {owner} {group} {size:>5} {mod_date} {f}"
                    )
                    continue

                # Construct the full path of the entry
                full_path = (
                    os.path.join(resolved_dir, f) if resolved_dir != "/" else "/" + f
                )

                # Retrieve node info - if available
                is_dir = False
                if hasattr(self.shell, "get_node_info"):
                    info = self.shell.get_node_info(full_path)
                    is_dir = info and getattr(info, "is_dir", False)
                elif hasattr(self.shell.fs, "is_dir"):
                    is_dir = self.shell.fs.is_dir(full_path)

                # Choose permission string based on whether it's a directory
                mode = "drwxr-xr-x" if is_dir else "-rw-r--r--"
                nlink = 1
                owner = self.shell.environ.get("USER", "user")
                group = "staff"

                # Get file size
                size = 0
                try:
                    if hasattr(self.shell.fs, "get_size"):
                        size = self.shell.fs.get_size(full_path)
                    elif not is_dir and hasattr(self.shell.fs, "read_file"):
                        # Alternative: get size from file content
                        content = self.shell.fs.read_file(full_path)
                        if content is not None:
                            size = len(content)
                except Exception:
                    size = 0  # Default if size can't be determined

                mod_date = time.strftime("%b %d %H:%M", time.localtime())
                # Format the line with right-aligned file size
                lines.append(f"{mode} {nlink} {owner} {group} {size:>5} {mod_date} {f}")

            return "\n".join(lines)
        else:
            return " ".join(files)

    def _format_long_listing(self, files, base_path):
        """Format files in long listing format"""
        lines = []
        for f in files:
            mode = "-rw-r--r--"
            nlink = 1
            owner = self.shell.environ.get("USER", "user")
            group = "staff"
            size = 0
            try:
                full_path = os.path.join(base_path, f) if base_path else f
                if hasattr(self.shell.fs, "get_size"):
                    size = self.shell.fs.get_size(full_path)
                elif hasattr(self.shell.fs, "read_file"):
                    content = self.shell.fs.read_file(full_path)
                    if content is not None:
                        size = len(content)
            except:
                size = 0
            mod_date = time.strftime("%b %d %H:%M", time.localtime())
            lines.append(f"{mode} {nlink} {owner} {group} {size:>5} {mod_date} {f}")
        return "\n".join(lines)

    def _directory_exists(self, path):
        """Check if a directory exists using available methods."""
        try:
            # Try different methods to check if directory exists
            if hasattr(self.shell.fs, "is_dir") and self.shell.fs.exists(path):
                return self.shell.fs.is_dir(path)
            elif hasattr(self.shell, "get_node_info"):
                info = self.shell.get_node_info(path)
                return info and getattr(info, "is_dir", False)
            elif hasattr(self.shell.fs, "ls"):
                # Try listing the directory
                try:
                    self.shell.fs.ls(path)
                    return True
                except Exception:
                    return False
            # Last resort: assume it exists
            return True
        except Exception:
            return False
