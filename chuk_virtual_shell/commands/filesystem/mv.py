"""
chuk_virtual_shell/commands/filesystem/mv.py - Move or rename files and directories
"""

from chuk_virtual_shell.commands.command_base import ShellCommand


class MvCommand(ShellCommand):
    name = "mv"
    help_text = (
        "mv - Move or rename files and directories\nUsage: mv [source...] destination"
    )
    category = "file"

    def execute(self, args):
        if len(args) < 2:
            return "mv: missing operand"

        *sources, destination = args

        # Check if destination is a directory if multiple sources are provided
        if len(sources) > 1:
            if not self._is_directory(destination):
                return f"mv: target '{destination}' is not a directory"

        for src in sources:
            # Check if source exists
            if not self._file_exists(src):
                return f"mv: cannot stat '{src}': No such file or directory"

            # Determine destination path
            if self._is_directory(destination):
                # If destination is a directory, put the file inside the directory
                # Use portable path operations
                src_basename = src.split("/")[-1] if "/" in src else src
                dest_path = destination.rstrip("/") + "/" + src_basename
            else:
                dest_path = destination

            # Read content of source file
            content = self.shell.fs.read_file(src)
            if content is None:
                return f"mv: cannot read '{src}': Permission denied or file not found"

            # Write content to destination file
            if not self.shell.fs.write_file(dest_path, content):
                return f"mv: failed to write to '{dest_path}'"

            # Remove source file
            if not self._remove_file(src):
                return f"mv: file copied, but failed to remove original at '{src}'"

        return ""

    def _is_directory(self, path):
        """Check if a path is a directory using various possible filesystem APIs."""
        try:
            if hasattr(self.shell.fs, "get_node_info"):
                node_info = self.shell.fs.get_node_info(path)
                return node_info and node_info.is_dir
            elif hasattr(self.shell.fs, "is_dir"):
                return self.shell.fs.is_dir(path)
            elif hasattr(self.shell.fs, "isdir"):
                return self.shell.fs.isdir(path)
            elif hasattr(self.shell.fs, "ls"):
                # Try to list contents - if successful, it's a directory
                try:
                    self.shell.fs.ls(path)
                    return True
                except Exception:
                    return False
            # Remove the test-specific directory naming heuristic
            return False
        except Exception:
            # If any error occurs, assume it's not a directory
            return False

    def _file_exists(self, path):
        """Check if a file exists using various possible filesystem APIs."""
        try:
            if hasattr(self.shell.fs, "get_node_info"):
                return self.shell.fs.get_node_info(path) is not None
            elif hasattr(self.shell.fs, "exists"):
                return self.shell.fs.exists(path)
            elif hasattr(self.shell, "exists"):
                return self.shell.exists(path)
            else:
                # Try to read the file as a fallback
                content = self.shell.fs.read_file(path)
                return content is not None
        except Exception:
            # If any error occurs, assume the file doesn't exist
            return False

    def _remove_file(self, path):
        """Remove a file using various possible filesystem APIs."""
        try:
            if hasattr(self.shell.fs, "rm"):
                return self.shell.fs.rm(path)
            elif hasattr(self.shell.fs, "delete_file"):
                return self.shell.fs.delete_file(path)
            elif hasattr(self.shell.fs, "delete_node"):
                return self.shell.fs.delete_node(path)
            # Remove the test-specific success assumption
            return False
        except Exception:
            # If any error occurs, assume the removal failed
            return False
