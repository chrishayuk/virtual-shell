"""
chuk_virtual_shell/commands/filesystem/find.py - Find files and directories
"""

import argparse
import fnmatch
import re
import time
from typing import List, Optional
from chuk_virtual_shell.commands.command_base import ShellCommand


class FindCommand(ShellCommand):
    name = "find"
    help_text = (
        "find - Search for files in a directory hierarchy\n"
        "Usage: find [path...] [expression]\n"
        "Options:\n"
        "  -name pattern       File name matches pattern (wildcards)\n"
        "  -iname pattern      Like -name but case insensitive\n"
        "  -path pattern       File path matches pattern\n"
        "  -regex pattern      File name matches regular expression\n"
        "  -type d|f           File is of type d (directory) or f (file)\n"
        "  -size [+|-]n[cwbkMG] File size is n units (c:bytes, w:2-byte words, b:512-byte blocks, k:KB, M:MB, G:GB)\n"
        "  -empty              File is empty\n"
        "  -maxdepth levels    Descend at most levels\n"
        "  -mindepth levels    Do not apply tests at levels less than levels\n"
        "  -mtime [-|+]n       File was modified n*24 hours ago\n"
        "  -newer file         File is newer than file\n"
        "  -exec cmd {} \\;     Execute command for each match\n"
        "  -print              Print matched files (default)\n"
        "  -print0             Print with null separator\n"
        "  -delete             Delete matched files\n"
        "  -prune              Do not descend into directories\n"
        "  -o, -or             Logical OR\n"
        "  -a, -and            Logical AND (default)\n"
        "  -not, !             Logical NOT\n"
        "  --help              Display this help and exit\n"
        "If no path is specified, the current directory is used."
    )
    category = "filesystem"

    def execute(self, args: List[str]) -> str:
        # Handle help first
        if "--help" in args:
            return self.get_help()
        
        # Determine paths to search - collect all non-option arguments at the beginning
        paths = []
        option_start = len(args)
        
        for i, arg in enumerate(args):
            if arg.startswith('-'):
                option_start = i
                break
            else:
                paths.append(arg)
        
        # Default to current directory if no paths specified
        if not paths:
            paths = ["."]
        
        # Parse the remaining arguments as options
        option_args = args[option_start:]
        
        # Manual parsing for options that can have values starting with '-'
        parsed_options = {
            'name': None, 'iname': None, 'path': None, 'type': None,
            'maxdepth': None, 'mindepth': 0, 'regex': None, 'size': None,
            'empty': False, 'mtime': None, 'newer': None, 'exec': None,
            'print': False, 'print0': False, 'delete': False, 'prune': False
        }
        
        i = 0
        while i < len(option_args):
            arg = option_args[i]
            
            if arg == '-name' and i + 1 < len(option_args):
                parsed_options['name'] = option_args[i + 1]
                i += 2
            elif arg == '-iname' and i + 1 < len(option_args):
                parsed_options['iname'] = option_args[i + 1]
                i += 2
            elif arg == '-path' and i + 1 < len(option_args):
                parsed_options['path'] = option_args[i + 1]
                i += 2
            elif arg == '-type' and i + 1 < len(option_args):
                if option_args[i + 1] in ['d', 'f']:
                    parsed_options['type'] = option_args[i + 1]
                i += 2
            elif arg == '-maxdepth' and i + 1 < len(option_args):
                try:
                    parsed_options['maxdepth'] = int(option_args[i + 1])
                except ValueError:
                    pass
                i += 2
            elif arg == '-mindepth' and i + 1 < len(option_args):
                try:
                    parsed_options['mindepth'] = int(option_args[i + 1])
                except ValueError:
                    pass
                i += 2
            elif arg == '-regex' and i + 1 < len(option_args):
                parsed_options['regex'] = option_args[i + 1]
                i += 2
            elif arg == '-size' and i + 1 < len(option_args):
                parsed_options['size'] = option_args[i + 1]
                i += 2
            elif arg == '-mtime' and i + 1 < len(option_args):
                parsed_options['mtime'] = option_args[i + 1]
                i += 2
            elif arg == '-newer' and i + 1 < len(option_args):
                parsed_options['newer'] = option_args[i + 1]
                i += 2
            elif arg == '-exec':
                # Collect all arguments until ';'
                exec_args = []
                i += 1
                while i < len(option_args) and option_args[i] != ';':
                    exec_args.append(option_args[i])
                    i += 1
                parsed_options['exec'] = exec_args
                i += 1
            elif arg == '-empty':
                parsed_options['empty'] = True
                i += 1
            elif arg == '-print':
                parsed_options['print'] = True
                i += 1
            elif arg == '-print0':
                parsed_options['print0'] = True
                i += 1
            elif arg == '-delete':
                parsed_options['delete'] = True
                i += 1
            elif arg == '-prune':
                parsed_options['prune'] = True
                i += 1
            else:
                i += 1
        
        # Convert to namespace for compatibility
        class ParsedArgs:
            def __init__(self, options):
                for key, value in options.items():
                    setattr(self, key, value)
        
        parsed_args = ParsedArgs(parsed_options)

        results = []

        for path in paths:
            # Resolve path to absolute
            abs_path = self.shell.fs.resolve_path(path)
            node_info = self.shell.fs.get_node_info(abs_path)

            # If the path does not exist, output an error message.
            if not node_info:
                results.append(f"find: '{path}': No such file or directory")
                continue

            # Compile regex pattern if provided
            regex_pattern = None
            if parsed_args.regex:
                try:
                    regex_pattern = re.compile(parsed_args.regex)
                except re.error:
                    results.append(
                        f"find: invalid regular expression '{parsed_args.regex}'"
                    )
                    continue

            # Search recursively
            found_paths = self._find_recursive(
                abs_path,
                0,
                parsed_args.maxdepth,
                parsed_args.mindepth,
                parsed_args.name,
                parsed_args.iname,
                parsed_args.path,
                parsed_args.type,
                regex_pattern,
                parsed_args.size,
                parsed_args.empty,
                parsed_args.mtime,
                parsed_args.newer,
                parsed_args.prune
            )

            # Process found paths
            for found_path in found_paths:
                # Execute command if -exec specified
                if parsed_args.exec:
                    self._execute_command(found_path, parsed_args.exec)
                    
                # Delete if -delete specified
                elif parsed_args.delete:
                    self._delete_path(found_path)
                    
                # Otherwise print the path
                else:
                    # Format output based on options
                    if parsed_args.name and not parsed_args.path:
                        # Show only the matching file's basename
                        display_path = (
                            found_path.split("/")[-1] if "/" in found_path else found_path
                        )
                    else:
                        display_path = found_path
                    
                    if parsed_args.print0:
                        results.append(display_path + "\0")
                    else:
                        results.append(display_path)

        if parsed_args.print0:
            return "".join(results).rstrip("\0")
        else:
            return "\n".join(results) if results else ""

    def _find_recursive(
        self,
        path: str,
        current_depth: int,
        max_depth: Optional[int],
        min_depth: int,
        name_pattern: Optional[str],
        iname_pattern: Optional[str],
        path_pattern: Optional[str],
        type_filter: Optional[str],
        regex_pattern: Optional[re.Pattern],
        size_filter: Optional[str],
        empty_filter: bool,
        mtime_filter: Optional[str],
        newer_file: Optional[str],
        prune: bool
    ) -> List[str]:
        """
        Recursively find files and directories that match the given criteria.
        """
        if max_depth is not None and current_depth > max_depth:
            return []

        results = []
        node_info = self.shell.fs.get_node_info(path)
        if not node_info:
            return []

        include_this = current_depth >= min_depth

        # Filter by type
        if type_filter == "d" and not node_info.is_dir:
            include_this = False
        elif type_filter == "f" and node_info.is_dir:
            include_this = False

        # Get basename for name matching
        base_name = path.split("/")[-1] if "/" in path else path or path

        # Name pattern matching
        if name_pattern and include_this:
            if not fnmatch.fnmatch(base_name, name_pattern):
                include_this = False

        # Case-insensitive name pattern
        if iname_pattern and include_this:
            if not fnmatch.fnmatch(base_name.lower(), iname_pattern.lower()):
                include_this = False

        # Path pattern matching
        if path_pattern and include_this:
            if not fnmatch.fnmatch(path, path_pattern):
                include_this = False

        # Regex pattern matching
        if regex_pattern and include_this:
            if not regex_pattern.search(base_name):
                include_this = False

        # Size filter
        if size_filter and include_this:
            if not self._check_size_filter(path, size_filter):
                include_this = False

        # Empty filter
        if empty_filter and include_this:
            if not self._is_empty(path):
                include_this = False

        # Modification time filter
        if mtime_filter and include_this:
            if not self._check_mtime_filter(path, mtime_filter):
                include_this = False

        # Newer than file filter
        if newer_file and include_this:
            if not self._is_newer_than(path, newer_file):
                include_this = False

        if include_this:
            results.append(path)

        # Recurse into directories unless pruned
        if node_info.is_dir and not prune:
            try:
                contents = self.shell.fs.ls(path)
                for item in contents:
                    item_path = path.rstrip("/") + "/" + item
                    results.extend(
                        self._find_recursive(
                            item_path,
                            current_depth + 1,
                            max_depth,
                            min_depth,
                            name_pattern,
                            iname_pattern,
                            path_pattern,
                            type_filter,
                            regex_pattern,
                            size_filter,
                            empty_filter,
                            mtime_filter,
                            newer_file,
                            False  # Don't propagate prune to children
                        )
                    )
            except Exception as e:
                if hasattr(self.shell, 'error_log'):
                    self.shell.error_log.append(f"find: '{path}': {str(e)}")

        return results

    def _check_size_filter(self, path: str, size_filter: str) -> bool:
        """Check if file matches size filter."""
        # Parse size filter (e.g., +10k, -5M, 100c)
        if not size_filter:
            return True
            
        comparison = '='
        if size_filter[0] == '+':
            comparison = '>'
            size_filter = size_filter[1:]
        elif size_filter[0] == '-':
            comparison = '<'
            size_filter = size_filter[1:]
        
        # Parse unit
        unit = 'c'  # Default to bytes
        if size_filter and size_filter[-1] in 'cwbkMG':
            unit = size_filter[-1]
            size_filter = size_filter[:-1]
        
        try:
            size_value = int(size_filter)
        except ValueError:
            return False
        
        # Convert to bytes
        multipliers = {
            'c': 1,           # bytes
            'w': 2,           # 2-byte words
            'b': 512,         # 512-byte blocks
            'k': 1024,        # kilobytes
            'M': 1024*1024,   # megabytes
            'G': 1024*1024*1024  # gigabytes
        }
        size_bytes = size_value * multipliers.get(unit, 1)
        
        # Get actual file size
        try:
            if hasattr(self.shell.fs, 'get_size'):
                actual_size = self.shell.fs.get_size(path)
            else:
                content = self.shell.fs.read_file(path)
                if content is not None:
                    actual_size = len(content) if isinstance(content, (str, bytes)) else 0
                else:
                    actual_size = 0
        except:
            return False
        
        # Compare
        if comparison == '>':
            return actual_size > size_bytes
        elif comparison == '<':
            return actual_size < size_bytes
        else:
            return actual_size == size_bytes

    def _is_empty(self, path: str) -> bool:
        """Check if file/directory is empty."""
        node_info = self.shell.fs.get_node_info(path)
        if not node_info:
            return False
            
        if node_info.is_dir:
            # Check if directory is empty
            try:
                contents = self.shell.fs.ls(path)
                return len(contents) == 0
            except:
                return False
        else:
            # Check if file is empty
            try:
                if hasattr(self.shell.fs, 'get_size'):
                    return self.shell.fs.get_size(path) == 0
                else:
                    content = self.shell.fs.read_file(path)
                    return content is None or len(content) == 0
            except:
                return False

    def _check_mtime_filter(self, path: str, mtime_filter: str) -> bool:
        """Check modification time filter."""
        # This is a simplified implementation
        # Real implementation would check actual modification times
        return True

    def _is_newer_than(self, path: str, reference_file: str) -> bool:
        """Check if file is newer than reference file."""
        # This is a simplified implementation
        # Real implementation would compare actual modification times
        return True

    def _execute_command(self, path: str, exec_args: List[str]):
        """Execute command for matched path."""
        # Replace {} with the path
        cmd_args = [arg.replace('{}', path) for arg in exec_args if arg != ';']
        # Execute the command (simplified)
        if cmd_args and hasattr(self.shell, 'execute'):
            self.shell.execute(' '.join(cmd_args))

    def _delete_path(self, path: str):
        """Delete matched path."""
        node_info = self.shell.fs.get_node_info(path)
        if node_info:
            if node_info.is_dir:
                self.shell.fs.rmdir(path)
            else:
                self.shell.fs.rm(path)