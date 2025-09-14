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
        "Usage: df [-ahikPT] [-B SIZE] [-t TYPE] [-x TYPE] [path...]\n"
        "Options:\n"
        "  -a, --all             Include all filesystems\n"
        "  -h, --human-readable  Print sizes in human readable format (e.g., 1K, 234M)\n"
        "  -i, --inodes          Display inode usage information instead of block usage\n"
        "  -k                    Use 1024-byte blocks (default)\n"
        "  -B, --block-size=SIZE Use SIZE-byte blocks\n"
        "  -P, --portability     Use POSIX output format\n"
        "  -T, --print-type      Print filesystem type\n"
        "  -t, --type=TYPE       Limit listing to filesystems of type TYPE\n"
        "  -x, --exclude-type=TYPE  Exclude filesystems of type TYPE\n"
        "  --total               Produce a grand total\n"
        "  --help                Display this help and exit\n"
        "If no path is provided, all mounted filesystems are shown."
    )
    category = "filesystem"

    def execute(self, args: List[str]) -> str:
        parser = argparse.ArgumentParser(prog=self.name, add_help=False)
        parser.add_argument(
            "-a", "--all", action="store_true", help="Include all filesystems"
        )
        parser.add_argument(
            "-h",
            "--human-readable",
            action="store_true",
            help="Print sizes in human readable format",
        )
        parser.add_argument(
            "-i", "--inodes", action="store_true", help="Display inode information"
        )
        parser.add_argument(
            "-k", action="store_true", help="Use 1024-byte blocks (default)"
        )
        parser.add_argument(
            "-B", "--block-size", type=str, help="Use SIZE-byte blocks"
        )
        parser.add_argument(
            "-P", "--portability", action="store_true", help="Use POSIX output format"
        )
        parser.add_argument(
            "-T", "--print-type", action="store_true", help="Print filesystem type"
        )
        parser.add_argument(
            "-t", "--type", type=str, help="Limit listing to filesystems of type TYPE"
        )
        parser.add_argument(
            "-x", "--exclude-type", type=str, help="Exclude filesystems of type TYPE"
        )
        parser.add_argument(
            "--total", action="store_true", help="Produce a grand total"
        )
        parser.add_argument(
            "--help", action="store_true", help="Display help and exit"
        )
        parser.add_argument("paths", nargs="*", help="Paths to show disk space for")

        try:
            parsed_args = parser.parse_args(args)
        except SystemExit:
            return self.get_help()
        
        # Handle help flag
        if parsed_args.help:
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

        # Determine block size
        block_size = 1024  # Default to 1K blocks
        if parsed_args.block_size:
            # Parse block size (e.g., "1K", "1M", "512")
            size_str = parsed_args.block_size.upper()
            try:
                if size_str.endswith('K'):
                    block_size = int(size_str[:-1]) * 1024
                elif size_str.endswith('M'):
                    block_size = int(size_str[:-1]) * 1024 * 1024
                elif size_str.endswith('G'):
                    block_size = int(size_str[:-1]) * 1024 * 1024 * 1024
                else:
                    block_size = int(size_str)
            except ValueError:
                return f"df: invalid block size: '{parsed_args.block_size}'"

        # Display header
        if parsed_args.inodes:
            if parsed_args.print_type:
                results.append("Filesystem     Type       Inodes  IUsed    IFree IUse% Mounted on")
            else:
                results.append("Filesystem      Inodes  IUsed    IFree IUse% Mounted on")
        elif parsed_args.portability:
            # POSIX format
            if parsed_args.print_type:
                results.append("Filesystem     Type      512-blocks      Used Available Capacity Mounted on")
            else:
                results.append("Filesystem     512-blocks      Used Available Capacity Mounted on")
        else:
            # Format block label based on size
            if block_size >= 1024 * 1024 * 1024:
                block_label = f"{block_size // (1024 * 1024 * 1024)}G-blocks"
            elif block_size >= 1024 * 1024:
                block_label = f"{block_size // (1024 * 1024)}M-blocks"
            elif block_size >= 1024:
                block_label = f"{block_size // 1024}K-blocks"
            else:
                block_label = f"{block_size}-blocks"
                
            if parsed_args.print_type:
                results.append(f"Filesystem     Type      {block_label:>10}    Used    Available Use% Mounted on")
            else:
                results.append(f"Filesystem     {block_label:>10}    Used    Available Use% Mounted on")

        # Track totals if requested
        total_total = 0
        total_used = 0
        total_available = 0
        
        for path in paths:
            # Resolve path to absolute
            abs_path = self.shell.fs.resolve_path(path)

            # Check if path exists
            if not self.shell.fs.get_node_info(abs_path):
                results.append(f"df: {path}: No such file or directory")
                continue
                
            # Get filesystem type
            fs_type = storage_stats.get("fs_type", "vfs")
            
            # Check type filters
            if parsed_args.type and fs_type != parsed_args.type:
                continue
            if parsed_args.exclude_type and fs_type == parsed_args.exclude_type:
                continue

            # If we're showing inodes (file count) information
            if parsed_args.inodes:
                # Get file counts
                total_files = storage_stats.get("max_files", 10000)
                used_files = storage_stats.get("file_count", 0)
                free_files = max(0, total_files - used_files)

                # Calculate usage percentage
                if total_files > 0:
                    use_percent = (used_files / total_files) * 100
                    percent_str = f"{int(use_percent)}%"
                else:
                    percent_str = "-"

                # Format the line
                filesystem = storage_stats.get("provider_name", "vfs")
                if parsed_args.print_type:
                    results.append(
                        f"{filesystem:<14} {fs_type:<10} {total_files:7d} {used_files:7d} {free_files:7d} {percent_str:>4} {abs_path}"
                    )
                else:
                    results.append(
                        f"{filesystem:<14} {total_files:7d} {used_files:7d} {free_files:7d} {percent_str:>4} {abs_path}"
                    )

            else:
                # Get block sizes
                total_size = storage_stats.get("max_total_size", 104857600)  # Default 100MB
                used_size = storage_stats.get("total_size_bytes", 0)
                free_size = max(0, total_size - used_size)
                
                # Update totals
                if parsed_args.total:
                    total_total += total_size
                    total_used += used_size
                    total_available += free_size

                # Format sizes based on flags
                if parsed_args.portability:
                    # POSIX format uses 512-byte blocks
                    total_str = f"{total_size // 512:10d}"
                    used_str = f"{used_size // 512:10d}"
                    free_str = f"{free_size // 512:10d}"
                elif parsed_args.human_readable:
                    total_str = self._format_size(total_size)
                    used_str = self._format_size(used_size)
                    free_str = self._format_size(free_size)
                else:
                    # Convert to specified block size
                    total_str = f"{total_size // block_size:10d}"
                    used_str = f"{used_size // block_size:10d}"
                    free_str = f"{free_size // block_size:10d}"

                # Calculate usage percentage
                if total_size > 0:
                    use_percent = (used_size / total_size) * 100
                    if parsed_args.portability:
                        percent_str = f"{int(use_percent + 0.5)}%"  # Round up
                    else:
                        percent_str = f"{int(use_percent)}%"
                else:
                    percent_str = "-"

                # Format the line
                filesystem = storage_stats.get("provider_name", "vfs")
                if parsed_args.print_type:
                    results.append(
                        f"{filesystem:<14} {fs_type:<10} {total_str:>10} {used_str:>10} {free_str:>10} {percent_str:>4} {abs_path}"
                    )
                else:
                    results.append(
                        f"{filesystem:<14} {total_str:>10} {used_str:>10} {free_str:>10} {percent_str:>4} {abs_path}"
                    )

        # Add total line if requested
        if parsed_args.total and not parsed_args.inodes and total_total > 0:
            if parsed_args.human_readable:
                total_str = self._format_size(total_total)
                used_str = self._format_size(total_used)
                avail_str = self._format_size(total_available)
            else:
                total_str = f"{total_total // block_size:10d}"
                used_str = f"{total_used // block_size:10d}"
                avail_str = f"{total_available // block_size:10d}"
            
            use_percent = int((total_used / total_total) * 100) if total_total > 0 else 0
            
            if parsed_args.print_type:
                results.append(
                    f"{'total':<14} {'-':<10} {total_str:>10} {used_str:>10} {avail_str:>10} {use_percent:>3}% -"
                )
            else:
                results.append(
                    f"{'total':<14} {total_str:>10} {used_str:>10} {avail_str:>10} {use_percent:>3}% -"
                )
        
        return "\n".join(results)

    def _format_size(self, size_bytes: int) -> str:
        """Convert a size in bytes into a human-readable string."""
        if size_bytes == 0:
            return "0"
        
        # Handle negative sizes (shouldn't happen but be safe)
        negative = size_bytes < 0
        size_bytes = abs(size_bytes)
        
        units = ['B', 'K', 'M', 'G', 'T', 'P', 'E']
        unit_index = 0
        size_float = float(size_bytes)
        
        # For bytes, don't divide
        if size_float < 1024:
            result = f"{int(size_float)}{units[unit_index]}"
        else:
            # Move to next unit
            while size_float >= 1024 and unit_index < len(units) - 1:
                size_float /= 1024.0
                unit_index += 1
            
            # Format based on size
            if size_float >= 100:
                result = f"{int(size_float)}{units[unit_index]}"
            elif size_float >= 10:
                result = f"{size_float:.1f}{units[unit_index]}"
            else:
                result = f"{size_float:.2f}{units[unit_index]}"
        
        return f"-{result}" if negative else result
