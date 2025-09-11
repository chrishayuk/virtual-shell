"""
chuk_virtual_shell/commands/filesystem/df.py - Display disk free space
"""

import argparse
from typing import List
from chuk_virtual_shell.commands.command_base import ShellCommand


class DfCommand(ShellCommand):
    name = "df"
    help_text = (
        "df - Display disk free space\n"
        "Usage: df [-h] [-i] [path...]\n"
        "Options:\n"
        "  -h, --human-readable  Print sizes in human readable format (e.g., 1K, 234M)\n"
        "  -i, --inodes          Display inode usage information instead of block usage\n"
        "If no path is provided, all mounted filesystems are shown."
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
            "-i", "--inodes", action="store_true", help="Display inode information"
        )
        parser.add_argument("paths", nargs="*", help="Paths to show disk space for")

        try:
            parsed_args = parser.parse_args(args)
        except SystemExit:
            return self.get_help()

        # Get storage statistics
        storage_stats = self.shell.fs.get_storage_stats()

        # Format output
        results = []

        # Get paths to check
        paths = parsed_args.paths
        if not paths:
            # Default to root path if no paths provided
            paths = ["/"]

        # Display header
        if parsed_args.inodes:
            results.append("Filesystem      Inodes  IUsed    IFree IUse% Mounted on")
        else:
            results.append(
                "Filesystem     1K-blocks    Used    Available Use% Mounted on"
            )

        for path in paths:
            # Resolve path to absolute
            abs_path = self.shell.fs.resolve_path(path)

            # Check if path exists
            if not self.shell.fs.get_node_info(abs_path):
                results.append(f"df: {path}: No such file or directory")
                continue

            # If we're showing inodes (file count) information
            if parsed_args.inodes:
                # Get file counts
                total_files = storage_stats.get("max_files", 0)
                used_files = storage_stats.get("file_count", 0)
                free_files = total_files - used_files

                # Calculate usage percentage
                if total_files > 0:
                    use_percent = (used_files / total_files) * 100
                    percent_str = f"{int(use_percent)}%"
                else:
                    percent_str = "-"

                # Format the line
                filesystem = storage_stats.get("provider_name", "vfs")
                results.append(
                    f"{filesystem:<14} {total_files:7d} {used_files:7d} {free_files:7d} {percent_str:4} {abs_path}"
                )

            else:
                # Get block sizes (in 1K blocks)
                total_size = storage_stats.get("max_total_size", 0)
                used_size = storage_stats.get("total_size_bytes", 0)
                free_size = total_size - used_size

                # Format sizes based on human-readable flag
                if parsed_args.human_readable:
                    total_str = self._format_size(total_size)
                    used_str = self._format_size(used_size)
                    free_str = self._format_size(free_size)
                else:
                    # Convert to KB for standard df output
                    total_str = f"{total_size // 1024:8d}"
                    used_str = f"{used_size // 1024:8d}"
                    free_str = f"{free_size // 1024:8d}"

                # Calculate usage percentage
                if total_size > 0:
                    use_percent = (used_size / total_size) * 100
                    percent_str = f"{int(use_percent)}%"
                else:
                    percent_str = "-"

                # Format the line
                filesystem = storage_stats.get("provider_name", "vfs")
                results.append(
                    f"{filesystem:<14} {total_str:10} {used_str:8} {free_str:10} {percent_str:4} {abs_path}"
                )

        return "\n".join(results)

    def _format_size(self, size_bytes: int) -> str:
        """Convert a size in bytes into a human-readable string."""
        size_float = float(size_bytes)
        for unit in ["", "K", "M", "G", "T"]:
            if size_float < 1024 or unit == "T":
                if unit == "":
                    return f"{int(size_float)}"
                return f"{size_float / 1024:.1f}{unit}"
            size_float /= 1024
        return f"{size_float:.1f}T"
