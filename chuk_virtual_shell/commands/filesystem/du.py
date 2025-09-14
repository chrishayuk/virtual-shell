"""
chuk_virtual_shell/commands/filesystem/du.py - Display disk usage statistics
"""

import argparse
import os
from typing import List, Dict, Tuple, Optional
from chuk_virtual_shell.commands.command_base import ShellCommand


class DuCommand(ShellCommand):
    name = "du"
    help_text = (
        "du - Display disk usage statistics\n"
        "Usage: du [-ahkmscdx] [-d depth] [--max-depth=N] [path ...]\n"
        "Options:\n"
        "  -a, --all             Show all files, not just directories\n"
        "  -h, --human-readable  Print sizes in human readable format (e.g., 1K, 234M)\n"
        "  -k                    Display sizes in kilobytes (default)\n"
        "  -m                    Display sizes in megabytes\n"
        "  -s, --summarize       Display only a total for each argument\n"
        "  -c, --total           Produce a grand total\n"
        "  -d, --max-depth=N     Print totals only to depth N\n"
        "  -x, --one-file-system Do not cross filesystem boundaries\n"
        "  -L, --dereference     Dereference symbolic links\n"
        "  -P, --no-dereference  Do not dereference symbolic links (default)\n"
        "  -b, --bytes           Display sizes in bytes\n"
        "  --apparent-size       Display apparent sizes rather than disk usage\n"
        "  --time                Show time of last modification\n"
        "  --exclude=PATTERN     Exclude files matching PATTERN\n"
        "  --help                Display this help and exit\n"
        "If no path is provided, the current directory is used."
    )
    category = "filesystem"

    def execute(self, args: List[str]) -> str:
        parser = argparse.ArgumentParser(prog=self.name, add_help=False)
        parser.add_argument(
            "-a", "--all", action="store_true", 
            help="Show all files, not just directories"
        )
        parser.add_argument(
            "-h", "--human-readable", action="store_true",
            help="Print sizes in human readable format"
        )
        parser.add_argument(
            "-k", action="store_true",
            help="Display sizes in kilobytes (default)"
        )
        parser.add_argument(
            "-m", action="store_true",
            help="Display sizes in megabytes"
        )
        parser.add_argument(
            "-b", "--bytes", action="store_true",
            help="Display sizes in bytes"
        )
        parser.add_argument(
            "-s", "--summarize", action="store_true",
            help="Display only a total for each argument"
        )
        parser.add_argument(
            "-c", "--total", action="store_true", 
            help="Produce a grand total"
        )
        parser.add_argument(
            "-d", "--max-depth", type=int, metavar="N",
            help="Print totals only to depth N"
        )
        parser.add_argument(
            "-x", "--one-file-system", action="store_true",
            help="Do not cross filesystem boundaries"
        )
        parser.add_argument(
            "-L", "--dereference", action="store_true",
            help="Dereference symbolic links"
        )
        parser.add_argument(
            "-P", "--no-dereference", action="store_true",
            help="Do not dereference symbolic links"
        )
        parser.add_argument(
            "--apparent-size", action="store_true",
            help="Display apparent sizes rather than disk usage"
        )
        parser.add_argument(
            "--time", nargs="?", const="mtime", 
            help="Show time of last modification (mtime, atime, ctime, birth)"
        )
        parser.add_argument(
            "--time-style", type=str,
            help="Time format style (full-iso, long-iso, iso)"
        )
        parser.add_argument(
            "--exclude", type=str, action="append", default=[],
            help="Exclude files matching pattern"
        )
        parser.add_argument(
            "-B", "--block-size", type=str,
            help="Scale sizes by SIZE before printing"
        )
        parser.add_argument(
            "-D", "--dereference-args", action="store_true",
            help="Dereference only symlinks that are command line arguments"
        )
        parser.add_argument(
            "-S", "--separate-dirs", action="store_true",
            help="Do not include size of subdirectories"
        )
        parser.add_argument(
            "-0", "--null", action="store_true",
            help="End each output line with 0 byte rather than newline"
        )
        parser.add_argument(
            "--files0-from", type=str,
            help="Read null-terminated file names from FILE"
        )
        parser.add_argument(
            "--threshold", type=str,
            help="Exclude entries smaller/greater than SIZE"
        )
        parser.add_argument(
            "--help", action="store_true",
            help="Display help and exit"
        )
        parser.add_argument("paths", nargs="*", help="Paths to analyze")

        try:
            parsed_args = parser.parse_args(args)
        except SystemExit:
            return self.get_help()
            
        # Handle help flag
        if parsed_args.help:
            return self.get_help()

        # Handle block size option
        if parsed_args.block_size:
            try:
                divisor = self._parse_block_size(parsed_args.block_size)
                unit_suffix = ""
            except ValueError:
                divisor = 1024
                unit_suffix = ""
        elif parsed_args.bytes:
            divisor = 1
            unit_suffix = ""
        elif parsed_args.m:
            divisor = 1024 * 1024
            unit_suffix = ""
        else:  # Default to kilobytes
            divisor = 1024
            unit_suffix = ""

        results = []
        grand_total = 0
        
        # Handle --files0-from option
        if parsed_args.files0_from:
            paths = self._read_files0_from(parsed_args.files0_from)
        else:
            # Default to current directory if no paths specified
            paths = parsed_args.paths if parsed_args.paths else ["."]

        for path in paths:
            # Resolve path to absolute
            abs_path = self.shell.fs.resolve_path(path)

            # Check if path exists
            exists = self._check_if_exists(abs_path)

            if not exists:
                results.append(f"du: cannot access '{path}': No such file or directory")
                continue

            # Check if path matches exclude patterns
            if self._should_exclude(path, parsed_args.exclude):
                continue

            # Check if path is a directory or file
            is_dir = self._is_directory(abs_path)

            if is_dir:
                # For directories, compute size recursively
                dir_items = self._get_dir_items(
                    abs_path, 
                    parsed_args.all,
                    parsed_args.summarize,
                    parsed_args.max_depth,
                    0,  # current depth
                    parsed_args.exclude
                )

                if parsed_args.summarize:
                    # Only display the total for this directory
                    total_size = sum(size for _, size in dir_items)
                    size_str = self._format_size(
                        total_size, divisor, parsed_args.human_readable
                    )
                    results.append(f"{size_str}\t{path}")
                    grand_total += total_size
                else:
                    # Display all items based on options
                    for item_path, size in dir_items:
                        # Format relative to the original path for display
                        display_path = item_path
                        if item_path != abs_path:
                            # Make path relative for display
                            if item_path.startswith(abs_path):
                                rel_path = item_path[len(abs_path):].lstrip("/")
                                if rel_path:
                                    display_path = os.path.join(path, rel_path)
                                else:
                                    display_path = path
                            else:
                                display_path = item_path

                        # Check threshold if specified
                        if parsed_args.threshold:
                            if not self._check_threshold(size, parsed_args.threshold):
                                continue
                        
                        size_str = self._format_size(
                            size, divisor, parsed_args.human_readable
                        )
                        
                        # Add time if requested
                        if parsed_args.time:
                            time_type = parsed_args.time if isinstance(parsed_args.time, str) else "mtime"
                            mod_time = self._get_modification_time(item_path)
                            if parsed_args.time_style:
                                mod_time = self._format_time(mod_time, parsed_args.time_style)
                            results.append(f"{size_str}\t{mod_time}\t{display_path}")
                        else:
                            results.append(f"{size_str}\t{display_path}")
                        
                        if item_path == abs_path:
                            grand_total += size
            else:
                # For files, just get the size
                try:
                    size = self._get_file_size(abs_path)
                    size_str = self._format_size(
                        size, divisor, parsed_args.human_readable
                    )
                    
                    if parsed_args.time:
                        mod_time = self._get_modification_time(abs_path)
                        results.append(f"{size_str}\t{mod_time}\t{path}")
                    else:
                        results.append(f"{size_str}\t{path}")
                    grand_total += size
                except Exception as e:
                    results.append(f"du: cannot access '{path}': {str(e)}")

        # Add grand total if requested
        if parsed_args.total and (len(paths) > 1 or parsed_args.total):
            size_str = self._format_size(
                grand_total, divisor, parsed_args.human_readable
            )
            results.append(f"{size_str}\ttotal")

        # Handle null termination
        if hasattr(parsed_args, 'null') and parsed_args.null:
            separator = "\0"
        else:
            separator = "\n"
        
        return separator.join(results) if results else ""

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

    def _get_dir_items(
        self, 
        dir_path: str, 
        show_all: bool,
        summarize: bool,
        max_depth: Optional[int],
        current_depth: int,
        exclude_patterns: List[str]
    ) -> List[Tuple[str, int]]:
        """
        Get list of (path, size) tuples for a directory.
        
        Args:
            dir_path: Path to the directory
            show_all: If True, include files in output
            summarize: If True, only return the total
            max_depth: Maximum depth to recurse (None for unlimited)
            current_depth: Current recursion depth
            exclude_patterns: Patterns to exclude
            
        Returns:
            List of (path, size) tuples
        """
        items = []
        total_size = 0

        # Get all contents
        try:
            contents = []
            if hasattr(self.shell.fs, "ls"):
                contents = self.shell.fs.ls(dir_path)
            elif hasattr(self.shell.fs, "list_dir"):
                contents = self.shell.fs.list_dir(dir_path)
        except Exception:
            # Return empty if we can't list the directory
            return [(dir_path, 0)]

        # Calculate size for each item
        for item in contents:
            item_path = os.path.join(dir_path, item)
            
            # Check exclude patterns
            if self._should_exclude(item, exclude_patterns):
                continue

            if self._is_directory(item_path):
                # Check if we should show this directory based on depth
                if max_depth is not None and current_depth >= max_depth:
                    # Just get total size without recursing or showing subdirectories
                    sub_size = self._get_total_size(item_path, exclude_patterns)
                    total_size += sub_size
                    # Only show this directory itself if within depth limit
                    if not summarize and current_depth < max_depth:
                        items.append((item_path, sub_size))
                else:
                    # Recursively get subdirectory items
                    sub_items = self._get_dir_items(
                        item_path, show_all, False, max_depth, 
                        current_depth + 1, exclude_patterns
                    )
                    
                    # Add subdirectory's total to our total
                    sub_total = sum(size for _, size in sub_items)
                    total_size += sub_total
                    
                    if not summarize:
                        # Only add the directory itself at current depth
                        items.append((item_path, sub_total))
                        # Add subdirectory items only if they're within max_depth
                        if max_depth is None or current_depth + 1 < max_depth:
                            items.extend(sub_items)
            else:
                # Add file size
                try:
                    file_size = self._get_file_size(item_path)
                    total_size += file_size
                    
                    # Include file in output if show_all is True
                    if show_all and not summarize:
                        items.append((item_path, file_size))
                except Exception:
                    # Skip if we can't get the size
                    pass

        # Add this directory's total to the results
        if summarize:
            return [(dir_path, total_size)]
        else:
            # Add directory total at the end
            items.append((dir_path, total_size))
            return items

    def _get_total_size(self, dir_path: str, exclude_patterns: List[str]) -> int:
        """Get total size of a directory without detailed breakdown."""
        total = 0
        
        try:
            contents = []
            if hasattr(self.shell.fs, "ls"):
                contents = self.shell.fs.ls(dir_path)
            elif hasattr(self.shell.fs, "list_dir"):
                contents = self.shell.fs.list_dir(dir_path)
        except Exception:
            return 0
            
        for item in contents:
            item_path = os.path.join(dir_path, item)
            
            if self._should_exclude(item, exclude_patterns):
                continue
                
            if self._is_directory(item_path):
                total += self._get_total_size(item_path, exclude_patterns)
            else:
                try:
                    total += self._get_file_size(item_path)
                except Exception:
                    pass
                    
        return total

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
                    if isinstance(content, bytes):
                        return len(content)
                    elif isinstance(content, str):
                        # Count bytes, not characters
                        return len(content.encode('utf-8'))
                    else:
                        return len(str(content))
                return 0
        except Exception:
            return 0

    def _get_modification_time(self, path: str) -> str:
        """Get modification time of a file/directory."""
        # This is a placeholder - real implementation would get actual mtime
        # For now, return a sample time
        return "2024-01-01 12:00"
    
    def _parse_block_size(self, size_str: str) -> int:
        """Parse block size string like 1K, 1M, etc."""
        multipliers = {
            'K': 1024, 'k': 1024,
            'M': 1024*1024, 'm': 1024*1024,
            'G': 1024*1024*1024, 'g': 1024*1024*1024,
            'T': 1024*1024*1024*1024, 't': 1024*1024*1024*1024
        }
        
        if size_str[-1] in multipliers:
            try:
                return int(size_str[:-1]) * multipliers[size_str[-1]]
            except ValueError:
                raise ValueError(f"Invalid block size: {size_str}")
        else:
            try:
                return int(size_str)
            except ValueError:
                raise ValueError(f"Invalid block size: {size_str}")
    
    def _read_files0_from(self, filename: str) -> List[str]:
        """Read null-terminated file names from a file."""
        try:
            content = self.shell.fs.read_file(filename)
            if content:
                # Split by null bytes
                return [p for p in content.split('\0') if p]
            return []
        except:
            return []
    
    def _check_threshold(self, size: int, threshold: str) -> bool:
        """Check if size meets threshold criteria."""
        try:
            if threshold.startswith('+'):
                # Size must be greater than threshold
                threshold_val = self._parse_block_size(threshold[1:])
                return size > threshold_val
            elif threshold.startswith('-'):
                # Size must be less than threshold
                threshold_val = self._parse_block_size(threshold[1:])
                return size < threshold_val
            else:
                # Size must be greater than threshold (default)
                threshold_val = self._parse_block_size(threshold)
                return size > threshold_val
        except:
            return True  # If can't parse, include the item
    
    def _format_time(self, time_str: str, style: str) -> str:
        """Format time according to style."""
        # Simplified implementation - just return the time string
        # Real implementation would format according to style
        return time_str

    def _should_exclude(self, path: str, patterns: List[str]) -> bool:
        """Check if path matches any exclude pattern."""
        if not patterns:
            return False
            
        import fnmatch
        path_basename = os.path.basename(path)
        
        for pattern in patterns:
            if fnmatch.fnmatch(path_basename, pattern):
                return True
            if fnmatch.fnmatch(path, pattern):
                return True
                
        return False

    def _format_size(self, size_bytes: int, divisor: int, human: bool) -> str:
        """Format size for display."""
        if human:
            return self._format_human_readable(size_bytes)
        else:
            # Round up for block sizes
            if divisor > 1:
                blocks = (size_bytes + divisor - 1) // divisor
                return str(blocks)
            else:
                return str(size_bytes)

    def _format_human_readable(self, size_bytes: int) -> str:
        """Convert a size in bytes into a human-readable string."""
        if size_bytes == 0:
            return "0"
            
        # Handle negative sizes
        negative = size_bytes < 0
        size_bytes = abs(size_bytes)
        
        units = ['B', 'K', 'M', 'G', 'T', 'P', 'E']
        unit_index = 0
        size_float = float(size_bytes)
        
        # Find appropriate unit
        while size_float >= 1024 and unit_index < len(units) - 1:
            size_float /= 1024.0
            unit_index += 1
        
        # Format based on size
        if unit_index == 0:  # Bytes
            result = f"{int(size_float)}{units[unit_index]}"
        elif size_float >= 10:
            result = f"{int(size_float)}{units[unit_index]}"
        else:
            result = f"{size_float:.1f}{units[unit_index]}"
        
        return f"-{result}" if negative else result