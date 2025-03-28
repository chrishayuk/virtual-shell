"""
chuk_virtual_shell/commands/filesystem/find.py - Find files and directories
"""
import argparse
import fnmatch
import os
import re
from typing import List, Optional
from chuk_virtual_shell.commands.command_base import ShellCommand

class FindCommand(ShellCommand):
    name = "find"
    help_text = (
        "find - Search for files in a directory hierarchy\n"
        "Usage: find [path...] [expression]\n"
        "Options:\n"
        "  -name pattern       File name matches pattern\n"
        "  -type d|f           File is of type d (directory) or f (file)\n"
        "  -maxdepth levels    Descend at most levels (a non-negative integer) levels\n"
        "  -regex pattern      File name matches regular expression pattern\n"
        "If no path is specified, the current directory is used."
    )
    category = "filesystem"
    
    def execute(self, args: List[str]) -> str:
        parser = argparse.ArgumentParser(prog=self.name, add_help=False)
        parser.add_argument('paths', nargs='*', default=['.'], help='Paths to search')
        parser.add_argument('-name', type=str, help='Search for files matching pattern')
        parser.add_argument('-type', choices=['d', 'f'], help='Search for files of type (d=directory, f=file)')
        parser.add_argument('-maxdepth', type=int, help='Maximum depth to search')
        parser.add_argument('-regex', type=str, help='Search for files matching regex pattern')
        
        try:
            # Parse known args and keep the rest
            parsed_args, _ = parser.parse_known_args(args)
        except SystemExit:
            return self.get_help()
        
        results = []
        
        for path in parsed_args.paths:
            # Resolve path to absolute
            abs_path = self.shell.fs.resolve_path(path)
            node_info = self.shell.fs.get_node_info(abs_path)
            
            if not node_info:
                results.append(f"find: '{path}': No such file or directory")
                continue
            
            # Compile regex pattern if provided
            regex_pattern = None
            if parsed_args.regex:
                try:
                    regex_pattern = re.compile(parsed_args.regex)
                except re.error:
                    results.append(f"find: invalid regular expression '{parsed_args.regex}'")
                    continue
            
            # Search recursively
            found_paths = self._find_recursive(
                abs_path, 
                0,
                parsed_args.maxdepth,
                parsed_args.name, 
                parsed_args.type,
                regex_pattern
            )
            
            # Format results based on the original search path
            for found_path in found_paths:
                # Make the path relative to the original path for better display
                if path == '.':
                    # For current directory searches, show full path from current dir
                    display_path = found_path
                    if display_path.startswith(abs_path):
                        # Make relative to current dir if possible
                        rel_path = found_path[len(abs_path):].lstrip('/')
                        if rel_path:
                            display_path = rel_path
                        else:
                            display_path = '.'
                else:
                    # For other path searches, preserve the original path form
                    display_path = found_path
                    if found_path == abs_path:
                        display_path = path
                    elif found_path.startswith(abs_path + '/'):
                        # Make it relative to the search path
                        rel_path = found_path[len(abs_path)+1:]
                        display_path = os.path.join(path, rel_path)
                
                results.append(display_path)
        
        if not results:
            return ""
        
        return "\n".join(results)
    
    def _find_recursive(self, 
                       path: str, 
                       current_depth: int, 
                       max_depth: Optional[int], 
                       name_pattern: Optional[str], 
                       type_filter: Optional[str],
                       regex_pattern: Optional[re.Pattern] = None) -> List[str]:
        """
        Recursively find files and directories that match the given criteria.
        
        Args:
            path: Path to search
            current_depth: Current recursion depth
            max_depth: Maximum depth to search (None for unlimited)
            name_pattern: Pattern to match for file/directory names
            type_filter: 'd' for directories, 'f' for files, None for both
            regex_pattern: Regular expression pattern to match file/directory names
            
        Returns:
            List of paths that match the criteria
        """
        # Check if max depth reached
        if max_depth is not None and current_depth > max_depth:
            return []
        
        results = []
        node_info = self.shell.fs.get_node_info(path)
        
        if not node_info:
            return []
        
        # Check if this path matches the criteria
        include_this = True
        
        # Check type filter
        if type_filter == 'd' and not node_info.is_dir:
            include_this = False
        elif type_filter == 'f' and node_info.is_dir:
            include_this = False
        
        # Get just the base name of the path
        base_name = os.path.basename(path) or path
        
        # Check name pattern
        if name_pattern and include_this:
            if not fnmatch.fnmatch(base_name, name_pattern):
                include_this = False
        
        # Check regex pattern
        if regex_pattern and include_this:
            if not regex_pattern.search(base_name):
                include_this = False
        
        # Add this path if it matches
        if include_this:
            results.append(path)
        
        # Recursively search subdirectories
        if node_info.is_dir:
            try:
                contents = self.shell.fs.ls(path)
                for item in contents:
                    item_path = os.path.join(path, item)
                    item_results = self._find_recursive(
                        item_path, 
                        current_depth + 1, 
                        max_depth, 
                        name_pattern, 
                        type_filter,
                        regex_pattern
                    )
                    results.extend(item_results)
            except Exception as e:
                # Log error but continue with other directories
                # This could happen if permission is denied for a directory
                self.shell.error_log.append(f"find: '{path}': {str(e)}")
        
        return results