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
            "directory",
            nargs="?",
            default=None,
            help="Directory to list (default: current directory)",
        )
        try:
            parsed_args, _ = parser.parse_known_args(args)
        except SystemExit:
            return self.get_help()

        # Determine the directory: if none provided, use the current directory from filesystem
        # First try to get current directory from filesystem directly, if available
        if parsed_args.directory:
            dir_arg = parsed_args.directory
        elif hasattr(self.shell.fs, "pwd") and callable(self.shell.fs.pwd):
            dir_arg = (
                self.shell.fs.pwd()
            )  # Get current directory directly from filesystem
        else:
            # Fall back to environment variable if filesystem doesn't track current directory
            dir_arg = self.shell.environ.get("PWD", ".")

        # Resolve the directory path
        resolved_dir = self.shell.resolve_path(dir_arg)

        # Verify the directory exists and is a directory
        if not self._directory_exists(resolved_dir):
            return f"ls: cannot access '{dir_arg}': No such file or directory"

        try:
            files = self.shell.fs.ls(resolved_dir)

            # Add special directory entries . and .. if in all mode
            if parsed_args.all and isinstance(files, list):
                files = ["."] + ([".."] if resolved_dir != "/" else []) + files

        except Exception as e:
            return f"ls: error: {e}"

        # Filter out hidden files if --all is not specified
        if not parsed_args.all and isinstance(files, list):
            files = [f for f in files if not f.startswith(".")]

        # Ensure files is a list before sorting
        if not isinstance(files, list):
            return f"ls: unexpected result from filesystem: {files}"

        files = sorted(files)

        if parsed_args.long:
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
