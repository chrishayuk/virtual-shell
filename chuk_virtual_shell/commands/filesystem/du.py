"""
chuk_virtual_shell/commands/filesystem/du.py - Display disk usage statistics
"""

import argparse
import os
from typing import List, Dict, Tuple
from chuk_virtual_shell.commands.command_base import ShellCommand


class DuCommand(ShellCommand):
    name = "du"
    help_text = (
        "du - Display disk usage statistics\n"
        "Usage: du [-h] [-s] [-c] [path ...]\n"
        "Options:\n"
        "  -h, --human-readable  Print sizes in human readable format (e.g., 1K, 234M)\n"
        "  -s, --summarize       Display only a total for each argument\n"
        "  -c, --total           Produce a grand total\n"
        "If no path is provided, the current directory is used."
    )
    category = "filesystem"

    def execute(self, args: List[str]) -> str:
        parser = argparse.ArgumentParser(prog=self.name, add_help=False)
        parser.add_argument(
            "-h",
            "--human-readable",
            action="store_true",
            help="Print sizes in human readable format",
        )
        parser.add_argument(
            "-s",
            "--summarize",
            action="store_true",
            help="Display only a total for each argument",
        )
        parser.add_argument(
            "-c", "--total", action="store_true", help="Produce a grand total"
        )
        parser.add_argument("paths", nargs="*", default=["."], help="Paths to analyze")

        try:
            parsed_args = parser.parse_args(args)
        except SystemExit:
            return self.get_help()

        results = []
        grand_total = 0

        for path in parsed_args.paths:
            # Resolve path to absolute
            abs_path = self.shell.fs.resolve_path(path)

            # Check if path exists
            exists = self._check_if_exists(abs_path)

            if not exists:
                results.append(f"du: cannot access '{path}': No such file or directory")
                continue

            # Check if path is a directory or file
            is_dir = self._is_directory(abs_path)

            if is_dir:
                # For directories, compute size recursively
                dir_sizes, dir_total = self._get_dir_sizes(
                    abs_path, parsed_args.summarize
                )

                if parsed_args.summarize:
                    # Only display the total for this directory
                    size_str = (
                        self._format_size(dir_total)
                        if parsed_args.human_readable
                        else str(dir_total // 1024)
                    )
                    results.append(f"{size_str}\t{path}")
                else:
                    # Display all subdirectories
                    for sub_path, size in dir_sizes.items():
                        # Format relative to the original path for display
                        display_path = sub_path
                        if sub_path != abs_path:
                            # Make path relative for display
                            if sub_path.startswith(abs_path):
                                rel_path = sub_path[len(abs_path) :].lstrip("/")
                                display_path = os.path.join(path, rel_path)

                        size_str = (
                            self._format_size(size)
                            if parsed_args.human_readable
                            else str(size // 1024)
                        )
                        results.append(f"{size_str}\t{display_path}")

                grand_total += dir_total
            else:
                # For files, just get the size
                try:
                    size = self._get_file_size(abs_path)
                    size_str = (
                        self._format_size(size)
                        if parsed_args.human_readable
                        else str(size // 1024)
                    )
                    results.append(f"{size_str}\t{path}")
                    grand_total += size
                except Exception as e:
                    results.append(f"du: cannot access '{path}': {str(e)}")

        # Add grand total if requested
        if parsed_args.total and len(parsed_args.paths) > 1:
            size_str = (
                self._format_size(grand_total)
                if parsed_args.human_readable
                else str(grand_total // 1024)
            )
            results.append(f"{size_str}\ttotal")

        return "\n".join(results)

    def _check_if_exists(self, path: str) -> bool:
        """Check if a path exists using available APIs."""
        try:
            if hasattr(self.shell, "exists"):
                return self.shell.exists(path)
            elif hasattr(self.shell.fs, "exists"):
                return self.shell.fs.exists(path)
            else:
                # Try to read or list as fallback
                try:
                    # Try reading as file first
                    content = self.shell.fs.read_file(path)
                    if content is not None:
                        return True
                except Exception:
                    pass

                # Then try listing as directory
                try:
                    if hasattr(self.shell.fs, "ls"):
                        self.shell.fs.ls(path)
                        return True
                except Exception:
                    pass

                return False
        except Exception:
            return False

    def _get_dir_sizes(
        self, dir_path: str, summarize: bool = False
    ) -> Tuple[Dict[str, int], int]:
        """
        Calculate sizes for a directory and its subdirectories.

        Args:
            dir_path: Path to the directory
            summarize: If True, only calculate the total without subdirectory details

        Returns:
            Tuple of (dict of path -> size, total size)
        """
        dir_sizes = {}
        total_size = 0

        # Get all contents
        try:
            contents = []
            if hasattr(self.shell.fs, "ls"):
                contents = self.shell.fs.ls(dir_path)
        except Exception:
            # Return empty if we can't list the directory
            return {dir_path: 0}, 0

        # Calculate size for each item
        for item in contents:
            item_path = os.path.join(dir_path, item)

            if self._is_directory(item_path):
                # Recursively calculate subdirectory sizes
                sub_sizes, sub_total = self._get_dir_sizes(item_path, summarize)

                if not summarize:
                    # Add each subdirectory to our results
                    dir_sizes.update(sub_sizes)

                total_size += sub_total
            else:
                # Add file size
                try:
                    file_size = self._get_file_size(item_path)
                    total_size += file_size
                except Exception:
                    # Skip if we can't get the size
                    pass

        # Add this directory's total to the results
        dir_sizes[dir_path] = total_size

        return dir_sizes, total_size

    def _is_directory(self, path: str) -> bool:
        """Check if a path is a directory."""
        try:
            if hasattr(self.shell.fs, "is_dir"):
                return self.shell.fs.is_dir(path)
            elif hasattr(self.shell.fs, "isdir"):
                return self.shell.fs.isdir(path)
            elif hasattr(self.shell.fs, "get_node_info"):
                node_info = self.shell.fs.get_node_info(path)
                return node_info and getattr(node_info, "is_dir", False)
            else:
                # Last resort: try listing it
                try:
                    if hasattr(self.shell.fs, "ls"):
                        self.shell.fs.ls(path)
                        return True
                except Exception:
                    pass
                return False
        except Exception:
            return False

    def _get_file_size(self, path: str) -> int:
        """Get the size of a file."""
        try:
            if hasattr(self.shell.fs, "get_size"):
                return self.shell.fs.get_size(path)
            elif hasattr(self.shell, "get_size"):
                return self.shell.get_size(path)
            else:
                # Read the file and get its length
                content = self.shell.fs.read_file(path)
                if content is not None:
                    return len(content)
                return 0
        except Exception:
            return 0

    def _format_size(self, size_bytes: int) -> str:
        """Convert a size in bytes into a human-readable string."""
        size_float = float(size_bytes)
        for unit in ["B", "K", "M", "G", "T"]:
            if size_float < 1024 or unit == "T":
                if unit == "B":
                    return f"{int(size_float)}{unit}"
                return f"{size_float / 1024:.1f}{unit}"
            size_float /= 1024
        return f"{size_float:.1f}T"
