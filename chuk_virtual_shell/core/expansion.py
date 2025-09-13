# chuk_virtual_shell/core/expandsion.py
"""
chuk_virtual_shell/core/expansion.py - Shell expansion utilities

Handles all shell expansions including variables, globs, tildes, aliases,
and command substitution.
"""

import re
import shlex
import fnmatch
import os
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from chuk_virtual_shell.shell_interpreter import ShellInterpreter


class ExpansionHandler:
    """Handles all shell expansions (variables, globs, tilde, command substitution)."""
    
    def __init__(self, shell: 'ShellInterpreter'):
        self.shell = shell
    
    def expand_all(self, cmd_line: str) -> str:
        """
        Apply all expansions in the correct order.
        
        Args:
            cmd_line: Command line to expand
            
        Returns:
            Fully expanded command line
        """
        cmd_line = self.expand_variables(cmd_line)
        cmd_line = self.expand_globs(cmd_line)
        cmd_line = self.expand_tilde(cmd_line)
        return cmd_line
    
    def expand_command_substitution(self, cmd_line: str, depth: int = 0) -> str:
        """
        Expand command substitutions $(command) and `command`.
        
        Args:
            cmd_line: Command line potentially containing substitutions
            depth: Recursion depth to prevent infinite loops
            
        Returns:
            Command line with substitutions expanded
        """
        if depth > 5:  # Prevent infinite recursion
            return cmd_line
        
        # Handle $(command) - need to properly match nested parentheses
        while True:
            # Find $( but not $((
            start = 0
            found = False
            while start < len(cmd_line):
                idx = cmd_line.find('$(', start)
                if idx == -1:
                    break
                # Check if it's arithmetic $((
                if idx + 2 < len(cmd_line) and cmd_line[idx+2] == '(':
                    start = idx + 3
                    continue
                
                # Find matching closing paren, handling nesting
                paren_count = 1
                end = idx + 2
                while end < len(cmd_line) and paren_count > 0:
                    if cmd_line[end] == '(':
                        paren_count += 1
                    elif cmd_line[end] == ')':
                        paren_count -= 1
                    end += 1
                
                if paren_count == 0:
                    # Found a complete substitution
                    command = cmd_line[idx+2:end-1]
                    
                    # Check if the command itself contains substitutions
                    if '$(' in command or '`' in command:
                        # Recursively expand nested substitutions first
                        command = self.expand_command_substitution(command, depth + 1)
                    
                    # Execute the command (with expansions but no more substitution)
                    from chuk_virtual_shell.core.executor import CommandExecutor
                    executor = CommandExecutor(self.shell)
                    result = executor.execute_without_substitution(command)
                    # Remove trailing newline for substitution
                    if result and result.endswith("\n"):
                        result = result[:-1]
                    # Replace in the command line
                    cmd_line = cmd_line[:idx] + result + cmd_line[end:]
                    found = True
                    break
                
                start = idx + 2
            
            if not found:
                break
        
        # Handle backticks
        while '`' in cmd_line:
            idx = cmd_line.find('`')
            if idx == -1:
                break
            end = cmd_line.find('`', idx + 1)
            if end == -1:
                break
            
            command = cmd_line[idx+1:end]
            from chuk_virtual_shell.core.executor import CommandExecutor
            executor = CommandExecutor(self.shell)
            result = executor.execute_without_substitution(command)
            if result and result.endswith("\n"):
                result = result[:-1]
            cmd_line = cmd_line[:idx] + result + cmd_line[end+1:]
        
        return cmd_line
    
    def expand_variables(self, cmd_line: str) -> str:
        """
        Expand environment variables ($VAR and ${VAR}).
        
        Args:
            cmd_line: Command line containing variables
            
        Returns:
            Command line with variables expanded
        """
        # First expand arithmetic expressions $((...))
        cmd_line = self.expand_arithmetic(cmd_line)
        
        # Special variables
        cmd_line = cmd_line.replace("$?", str(self.shell.return_code))
        cmd_line = cmd_line.replace("$$", str(id(self.shell)))
        cmd_line = cmd_line.replace("$#", "0")
        
        # ${VAR} format
        def expand_braces(match):
            var_name = match.group(1)
            return self.shell.environ.get(var_name, "")
        
        cmd_line = re.sub(r"\$\{([^}]+)\}", expand_braces, cmd_line)
        
        # $VAR format
        def expand_simple(match):
            var_name = match.group(1)
            return self.shell.environ.get(var_name, "")
        
        # Match $VARNAME where VARNAME is alphanumeric starting with letter/underscore
        cmd_line = re.sub(r"\$([A-Za-z_][A-Za-z0-9_]*)", expand_simple, cmd_line)
        
        return cmd_line
    
    def expand_arithmetic(self, cmd_line: str) -> str:
        """
        Expand arithmetic expressions $((...)).
        
        Args:
            cmd_line: Command line containing arithmetic expressions
            
        Returns:
            Command line with arithmetic evaluated
        """
        def evaluate_arithmetic(match):
            expr = match.group(1)
            
            # First expand any $VAR references to their values
            def expand_var(m):
                var_name = m.group(1)
                return self.shell.environ.get(var_name, "0")
            expr = re.sub(r'\$([A-Za-z_][A-Za-z0-9_]*)', expand_var, expr)
            
            # Then replace bare variable names
            for var_name in re.findall(r'[A-Za-z_][A-Za-z0-9_]*', expr):
                if var_name in self.shell.environ:
                    var_value = self.shell.environ[var_name]
                    # Try to convert to int, default to 0 if not numeric
                    try:
                        var_value = str(int(var_value))
                    except (ValueError, TypeError):
                        var_value = "0"
                    expr = re.sub(r'\b' + var_name + r'\b', var_value, expr)
            
            # Safely evaluate the arithmetic expression
            try:
                # Only allow safe operations
                result = eval(expr, {"__builtins__": {}}, {})
                return str(result)
            except Exception as e:
                # If evaluation fails, return the original expression
                return f"$(({expr}))"
        
        # Match $((...)) pattern
        cmd_line = re.sub(r'\$\(\(([^)]+)\)\)', evaluate_arithmetic, cmd_line)
        return cmd_line
    
    def expand_globs(self, cmd_line: str) -> str:
        """
        Expand glob patterns (wildcards) in the command line.
        Supports *, ?, and [].
        
        Args:
            cmd_line: Command line containing glob patterns
            
        Returns:
            Command line with globs expanded
        """
        try:
            # Parse the command line preserving quotes
            parts = shlex.split(cmd_line)
        except ValueError:
            # If shlex fails, return as-is
            return cmd_line
        
        expanded_parts = []
        for part in parts:
            # Check if this part contains glob characters
            if any(char in part for char in ["*", "?", "["]):
                # Try to expand the glob pattern
                matches = self._match_glob_pattern(part)
                if matches:
                    expanded_parts.extend(matches)
                else:
                    # No matches, keep the pattern as-is
                    expanded_parts.append(part)
            else:
                expanded_parts.append(part)
        
        # Reconstruct the command line
        return self._reconstruct_command_line(expanded_parts)
    
    def expand_tilde(self, cmd_line: str) -> str:
        """
        Expand tilde (~) to home directory.
        
        Args:
            cmd_line: Command line containing tildes
            
        Returns:
            Command line with tildes expanded
        """
        try:
            parts = shlex.split(cmd_line)
        except ValueError:
            parts = cmd_line.split()
        
        expanded_parts = []
        home = self.shell.environ.get("HOME", "/home/user")
        
        for part in parts:
            if part == "~":
                expanded_parts.append(home)
            elif part.startswith("~/"):
                expanded_parts.append(home + part[1:])
            else:
                expanded_parts.append(part)
        
        return self._reconstruct_command_line(expanded_parts)
    
    def expand_aliases(self, cmd_line: str) -> str:
        """
        Expand command aliases.
        
        Args:
            cmd_line: Command line potentially starting with an alias
            
        Returns:
            Command line with alias expanded
        """
        if not hasattr(self.shell, "aliases") or not self.shell.aliases:
            return cmd_line
        
        # Split the command line to get the first word (command)
        try:
            parts = shlex.split(cmd_line)
            if not parts:
                return cmd_line
        except ValueError:
            # If shlex fails, try simple split
            parts = cmd_line.split()
            if not parts:
                return cmd_line
        
        # Check if the first word is an alias
        cmd = parts[0]
        if cmd in self.shell.aliases:
            # Replace with alias value
            alias_value = self.shell.aliases[cmd]
            if len(parts) > 1:
                # Append remaining arguments
                expanded = alias_value + " " + " ".join(parts[1:])
            else:
                expanded = alias_value
            
            # Prevent infinite recursion by tracking expansion depth
            if not hasattr(self, "_alias_depth"):
                self._alias_depth = 0
            
            self._alias_depth += 1
            if self._alias_depth < 10:  # Max recursion depth
                # Recursively expand in case alias contains other aliases
                expanded = self.expand_aliases(expanded)
            
            self._alias_depth -= 1
            if self._alias_depth == 0:
                del self._alias_depth
            
            return expanded
        
        return cmd_line
    
    def _match_glob_pattern(self, pattern: str) -> List[str]:
        """
        Match glob pattern against files in the virtual filesystem.
        
        Args:
            pattern: Glob pattern to match
            
        Returns:
            List of matching file paths
        """
        matches = []
        original_pattern = pattern
        
        # Handle absolute vs relative patterns
        if pattern.startswith("/"):
            # Absolute pattern
            search_path = "/"
            pattern = pattern[1:] if len(pattern) > 1 else ""
            is_absolute = True
        else:
            # Relative pattern
            search_path = self.shell.fs.pwd()
            is_absolute = False
        
        # Get the directory to search in
        if "/" in pattern:
            # Pattern includes directory
            dir_parts = pattern.rsplit("/", 1)
            if is_absolute:
                # For absolute patterns, build from root
                search_dir = "/" + dir_parts[0] if dir_parts[0] else "/"
            else:
                # For relative patterns, join with base path
                search_dir = os.path.join(search_path, dir_parts[0]) if dir_parts[0] else search_path
            file_pattern = dir_parts[1]
        else:
            # Pattern is just for files in current/base directory
            search_dir = search_path
            file_pattern = pattern
        
        # Normalize the search directory path
        search_dir = search_dir.replace("\\", "/")
        if search_dir != "/" and search_dir.endswith("/"):
            search_dir = search_dir[:-1]
        
        # List files in the search directory
        try:
            entries = self.shell.fs.ls(search_dir)
            if entries:
                for entry in entries:
                    # Skip . and ..
                    if entry in [".", ".."]:
                        continue
                    
                    # Check if the entry matches the pattern
                    if fnmatch.fnmatch(entry, file_pattern):
                        # Build the full path
                        if search_dir == "/":
                            full_path = "/" + entry
                        else:
                            full_path = search_dir + "/" + entry
                        
                        # For patterns with directories, always return full paths
                        # For simple patterns in current dir, return just filenames
                        if "/" in original_pattern or is_absolute:
                            matches.append(full_path)
                        else:
                            # Simple pattern in current directory
                            matches.append(entry)
        except:
            pass
        
        return sorted(matches)
    
    def _reconstruct_command_line(self, parts: List[str]) -> str:
        """
        Reconstruct command line from parts, preserving empty strings
        and quoting strings with spaces.
        
        Args:
            parts: List of command parts
            
        Returns:
            Reconstructed command line
        """
        result_parts = []
        for part in parts:
            if part == "":
                # Preserve empty strings with quotes
                result_parts.append('""')
            elif " " in part:
                result_parts.append(shlex.quote(part))
            else:
                result_parts.append(part)
        return " ".join(result_parts)