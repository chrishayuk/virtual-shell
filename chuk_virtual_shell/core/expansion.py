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

    # Placeholders for escaped special characters
    ESCAPED_STAR = "\x00ESCAPED_STAR\x00"
    ESCAPED_QUEST = "\x00ESCAPED_QUEST\x00"
    ESCAPED_LBRACK = "\x00ESCAPED_LBRACK\x00"
    ESCAPED_PIPE = "\x00ESCAPED_PIPE\x00"
    ESCAPED_DOLLAR = "\x00ESCAPED_DOLLAR\x00"
    ESCAPED_SPACE = "\x00ESCAPED_SPACE\x00"

    def __init__(self, shell: "ShellInterpreter"):
        self.shell = shell

    def expand_all(self, cmd_line: str) -> str:
        """
        Apply all expansions in the correct order.
        Respects quoting rules - no expansion in single quotes.

        Args:
            cmd_line: Command line to expand

        Returns:
            Fully expanded command line
        """
        # The order is important:
        # 1. Command substitution (respects single quotes)
        # 2. Variable expansion (respects single quotes, uses placeholders for escaped chars)
        # 3. Glob expansion (after quotes are processed, avoids escaped chars)
        # 4. Tilde expansion (at the beginning of words)
        # 5. Restore escaped characters
        cmd_line = self.expand_command_substitution(cmd_line)
        cmd_line = self.expand_variables(cmd_line)
        cmd_line = self.expand_globs(cmd_line)
        cmd_line = self.expand_tilde(cmd_line)
        cmd_line = self._restore_escaped_chars(cmd_line)
        return cmd_line

    def _is_in_single_quotes(self, text: str, position: int) -> bool:
        """
        Check if a position in text is inside single quotes.

        Args:
            text: The text to check
            position: The position to check

        Returns:
            True if the position is inside single quotes
        """
        in_single = False
        escaped = False

        for i in range(position):
            if escaped:
                escaped = False
                continue

            if text[i] == "\\":
                escaped = True
            elif text[i] == "'":
                in_single = not in_single

        return in_single

    def expand_command_substitution(self, cmd_line: str, depth: int = 0) -> str:
        """
        Expand command substitutions $(command) and `command`.
        Respects single quotes - no expansion inside them.

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
                idx = cmd_line.find("$(", start)
                if idx == -1:
                    break

                # Skip if inside single quotes
                if self._is_in_single_quotes(cmd_line, idx):
                    start = idx + 2
                    continue

                # Check if it's arithmetic $((
                if idx + 2 < len(cmd_line) and cmd_line[idx + 2] == "(":
                    start = idx + 3
                    continue

                # Find matching closing paren, handling nesting
                paren_count = 1
                end = idx + 2
                while end < len(cmd_line) and paren_count > 0:
                    if cmd_line[end] == "(":
                        paren_count += 1
                    elif cmd_line[end] == ")":
                        paren_count -= 1
                    end += 1

                if paren_count == 0:
                    # Found a complete substitution
                    command = cmd_line[idx + 2 : end - 1]

                    # Check if the command itself contains substitutions
                    if "$(" in command or "`" in command:
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
        while "`" in cmd_line:
            idx = cmd_line.find("`")
            if idx == -1:
                break

            # Skip if inside single quotes
            if self._is_in_single_quotes(cmd_line, idx):
                # Find next backtick to skip the whole thing
                next_idx = cmd_line.find("`", idx + 1)
                if next_idx == -1:
                    break
                idx = cmd_line.find("`", next_idx + 1)
                if idx == -1:
                    break
                continue

            end = cmd_line.find("`", idx + 1)
            if end == -1:
                break

            command = cmd_line[idx + 1 : end]
            from chuk_virtual_shell.core.executor import CommandExecutor

            executor = CommandExecutor(self.shell)
            result = executor.execute_without_substitution(command)
            if result and result.endswith("\n"):
                result = result[:-1]
            cmd_line = cmd_line[:idx] + result + cmd_line[end + 1 :]

        return cmd_line

    def expand_variables(self, cmd_line: str) -> str:
        """
        Expand environment variables ($VAR and ${VAR}).
        Respects single quotes - no expansion inside them.

        Args:
            cmd_line: Command line containing variables

        Returns:
            Command line with variables expanded
        """
        # Check if this is a heredoc command - if so, only process the first line
        if "\n" in cmd_line and ("<<" in cmd_line):
            lines = cmd_line.split("\n")
            first_line = lines[0]
            rest_lines = lines[1:]

            # Process only the first line for variable expansion
            expanded_first = self._expand_variables_line(first_line)

            # Reconstruct with original newlines (heredoc content unchanged)
            if rest_lines:
                return expanded_first + "\n" + "\n".join(rest_lines)
            else:
                return expanded_first
        else:
            # Regular variable expansion for non-heredoc commands
            return self._expand_variables_line(cmd_line)

    def _expand_variables_line(self, cmd_line: str) -> str:
        """
        Expand variables in a single line.

        Args:
            cmd_line: Single line to expand

        Returns:
            Line with variables expanded
        """
        # First expand arithmetic expressions $((...))
        cmd_line = self.expand_arithmetic(cmd_line)

        # Process the command line respecting quotes
        result = []
        i = 0
        while i < len(cmd_line):
            # Check for single quotes
            if cmd_line[i] == "'":
                # Find closing quote
                end = cmd_line.find("'", i + 1)
                if end == -1:
                    # No closing quote, take rest of string
                    result.append(cmd_line[i:])
                    break
                else:
                    # Copy content without expansion
                    result.append(cmd_line[i : end + 1])
                    i = end + 1
            # Check for double quotes
            elif cmd_line[i] == '"':
                # Find closing quote
                end = cmd_line.find('"', i + 1)
                if end == -1:
                    # No closing quote, expand rest of string
                    segment = cmd_line[i:]
                    segment = self._expand_segment(segment)
                    result.append(segment)
                    break
                else:
                    # Expand content inside double quotes
                    segment = cmd_line[i : end + 1]
                    # Expand variables but keep the quotes
                    inner = segment[1:-1]
                    inner = self._expand_segment(inner)
                    result.append('"' + inner + '"')
                    i = end + 1
            else:
                # Find next quote
                single_idx = cmd_line.find("'", i)
                double_idx = cmd_line.find('"', i)

                if single_idx == -1 and double_idx == -1:
                    # No more quotes, expand rest
                    segment = cmd_line[i:]
                    segment = self._expand_segment(segment)
                    result.append(segment)
                    break
                elif single_idx == -1:
                    next_quote = double_idx
                elif double_idx == -1:
                    next_quote = single_idx
                else:
                    next_quote = min(single_idx, double_idx)

                # Expand segment before quote
                segment = cmd_line[i:next_quote]
                segment = self._expand_segment(segment)
                result.append(segment)
                i = next_quote

        return "".join(result)

    def _expand_segment(self, segment: str) -> str:
        """Expand variables in an unquoted segment, respecting backslash escapes."""
        # Replace escaped glob/special characters with placeholders
        result = []
        i = 0
        while i < len(segment):
            if segment[i] == "\\" and i + 1 < len(segment):
                next_char = segment[i + 1]
                if next_char == "*":
                    result.append(self.ESCAPED_STAR)
                    i += 2
                elif next_char == "?":
                    result.append(self.ESCAPED_QUEST)
                    i += 2
                elif next_char == "[":
                    result.append(self.ESCAPED_LBRACK)
                    i += 2
                elif next_char == "|":
                    result.append(self.ESCAPED_PIPE)
                    i += 2
                elif next_char == "$":
                    result.append(self.ESCAPED_DOLLAR)
                    i += 2
                elif next_char == " ":
                    result.append(self.ESCAPED_SPACE)
                    i += 2
                else:
                    # Other escaped characters - just remove the backslash
                    result.append(next_char)
                    i += 2
            elif segment[i] == "$" and i + 1 < len(segment):
                # Variable expansion
                if segment[i + 1] == "?":
                    result.append(str(self.shell.return_code))
                    i += 2
                elif segment[i + 1] == "$":
                    result.append(str(id(self.shell)))
                    i += 2
                elif segment[i + 1] == "#":
                    result.append("0")
                    i += 2
                elif segment[i + 1] == "{":
                    # ${VAR} format
                    end = segment.find("}", i + 2)
                    if end != -1:
                        var_name = segment[i + 2 : end]
                        result.append(self.shell.environ.get(var_name, ""))
                        i = end + 1
                    else:
                        result.append(segment[i])
                        i += 1
                else:
                    # $VAR format
                    match = re.match(r"\$([A-Za-z_][A-Za-z0-9_]*)", segment[i:])
                    if match:
                        var_name = match.group(1)
                        result.append(self.shell.environ.get(var_name, ""))
                        i += len(match.group(0))
                    else:
                        result.append(segment[i])
                        i += 1
            else:
                result.append(segment[i])
                i += 1

        return "".join(result)

    def _restore_escaped_chars(self, text: str) -> str:
        """Restore escaped characters from placeholders."""
        text = text.replace(self.ESCAPED_STAR, "*")
        text = text.replace(self.ESCAPED_QUEST, "?")
        text = text.replace(self.ESCAPED_LBRACK, "[")
        # Don't restore ESCAPED_PIPE or ESCAPED_SPACE here - they need special handling
        # text = text.replace(self.ESCAPED_PIPE, '|')
        # text = text.replace(self.ESCAPED_SPACE, ' ')
        text = text.replace(self.ESCAPED_DOLLAR, "$")
        return text

    def restore_escaped_pipes(self, text: str) -> str:
        """Restore escaped pipes - called after pipeline processing."""
        return text.replace(self.ESCAPED_PIPE, "|")

    def restore_escaped_spaces(self, text: str) -> str:
        """Restore escaped spaces - called after command parsing."""
        return text.replace(self.ESCAPED_SPACE, " ")

    def restore_escaped_spaces_in_args(self, args: list) -> list:
        """Restore escaped spaces in argument list."""
        return [self.restore_escaped_spaces(arg) for arg in args]

    def expand_arithmetic(self, cmd_line: str) -> str:
        """
        Expand arithmetic expressions $((...)).
        Respects single quotes - no expansion inside them.

        Args:
            cmd_line: Command line containing arithmetic expressions

        Returns:
            Command line with arithmetic evaluated
        """
        result = []
        i = 0

        while i < len(cmd_line):
            # Check for single quotes
            if cmd_line[i] == "'":
                # Find closing quote
                end = cmd_line.find("'", i + 1)
                if end == -1:
                    # No closing quote, take rest of string
                    result.append(cmd_line[i:])
                    break
                else:
                    # Copy content without expansion
                    result.append(cmd_line[i : end + 1])
                    i = end + 1
            # Check for arithmetic expansion
            elif cmd_line[i : i + 3] == "$((" and not self._is_in_single_quotes(
                cmd_line, i
            ):
                # Find closing ))
                end = cmd_line.find("))", i + 3)
                if end == -1:
                    result.append(cmd_line[i])
                    i += 1
                else:
                    expr = cmd_line[i + 3 : end]

                    # First expand any $VAR references to their values
                    def expand_var(m):
                        var_name = m.group(1)
                        return self.shell.environ.get(var_name, "0")

                    expr = re.sub(r"\$([A-Za-z_][A-Za-z0-9_]*)", expand_var, expr)

                    # Then replace bare variable names
                    for var_name in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", expr):
                        if var_name in self.shell.environ:
                            var_value = self.shell.environ[var_name]
                            # Try to convert to int, default to 0 if not numeric
                            try:
                                var_value = str(int(var_value))
                            except (ValueError, TypeError):
                                var_value = "0"
                            expr = re.sub(r"\b" + var_name + r"\b", var_value, expr)

                    # Safely evaluate the arithmetic expression
                    try:
                        # Only allow safe operations
                        evaluated = eval(expr, {"__builtins__": {}}, {})
                        result.append(str(evaluated))
                    except Exception:
                        # If evaluation fails, return the original expression
                        result.append(f"$(({expr}))")

                    i = end + 2
            else:
                # Regular character
                result.append(cmd_line[i])
                i += 1

        return "".join(result)

    def expand_globs(self, cmd_line: str) -> str:
        """
        Expand glob patterns (wildcards) in the command line.
        Supports *, ?, and [].
        Respects quotes - no expansion in single or double quotes.

        Args:
            cmd_line: Command line containing glob patterns

        Returns:
            Command line with globs expanded
        """
        # Check if this is a heredoc command - if so, only process the first line
        if "\n" in cmd_line and ("<<" in cmd_line):
            lines = cmd_line.split("\n")
            first_line = lines[0]
            rest_lines = lines[1:]

            # Process only the first line for glob expansion
            expanded_first = self._expand_globs_line(first_line)

            # Reconstruct with original newlines (heredoc content unchanged)
            if rest_lines:
                return expanded_first + "\n" + "\n".join(rest_lines)
            else:
                return expanded_first
        else:
            # Regular glob expansion for non-heredoc commands
            return self._expand_globs_line(cmd_line)

    def _expand_globs_line(self, cmd_line: str) -> str:
        """
        Expand globs in a single line.

        Args:
            cmd_line: Single line to expand

        Returns:
            Line with globs expanded
        """
        # We need to manually parse the command line to preserve quote information
        result = []
        current_word = []
        in_single_quote = False
        in_double_quote = False
        escaped = False
        i = 0

        while i < len(cmd_line):
            char = cmd_line[i]

            if escaped:
                current_word.append(char)
                escaped = False
                i += 1
                continue

            if char == "\\":
                escaped = True
                current_word.append(char)
                i += 1
                continue

            if char == "'" and not in_double_quote:
                in_single_quote = not in_single_quote
                current_word.append(char)
                i += 1
                continue

            if char == '"' and not in_single_quote:
                in_double_quote = not in_double_quote
                current_word.append(char)
                i += 1
                continue

            if char in " \t" and not in_single_quote and not in_double_quote:
                # End of word
                if current_word:
                    word = "".join(current_word)
                    # Check if word needs glob expansion
                    if not (word.startswith('"') or word.startswith("'")):
                        # Check for glob characters that are not escaped (placeholders)
                        if any(c in word for c in ["*", "?", "["]) and not any(
                            placeholder in word
                            for placeholder in [
                                self.ESCAPED_STAR,
                                self.ESCAPED_QUEST,
                                self.ESCAPED_LBRACK,
                            ]
                        ):
                            # Has unescaped glob chars, try to expand
                            matches = self._match_glob_pattern(word)
                            if matches:
                                # Add each match with space separation
                                for idx, match in enumerate(matches):
                                    if idx > 0:
                                        result.append(" ")
                                    result.append(match)
                            else:
                                result.append(word)
                        else:
                            # No unescaped glob chars or contains escaped placeholders
                            result.append(word)
                    else:
                        # Word is quoted, no expansion
                        result.append(word)
                    current_word = []
                result.append(char)
                i += 1
                continue

            current_word.append(char)
            i += 1

        # Handle last word
        if current_word:
            word = "".join(current_word)
            # Check if word needs glob expansion
            if not (word.startswith('"') or word.startswith("'")):
                # Check for glob characters that are not escaped (placeholders)
                if any(c in word for c in ["*", "?", "["]) and not any(
                    placeholder in word
                    for placeholder in [
                        self.ESCAPED_STAR,
                        self.ESCAPED_QUEST,
                        self.ESCAPED_LBRACK,
                    ]
                ):
                    # Has unescaped glob chars, try to expand
                    matches = self._match_glob_pattern(word)
                    if matches:
                        # Add each match with space separation
                        for idx, match in enumerate(matches):
                            if idx > 0:
                                result.append(" ")
                            result.append(match)
                    else:
                        result.append(word)
                else:
                    # No unescaped glob chars or contains escaped placeholders
                    result.append(word)
            else:
                # Word is quoted, no expansion
                result.append(word)

        return "".join(result)

    def expand_tilde(self, cmd_line: str) -> str:
        """
        Expand tilde (~) to home directory.

        Args:
            cmd_line: Command line containing tildes

        Returns:
            Command line with tildes expanded
        """
        # Check if this is a heredoc command - if so, only process the first line
        if "\n" in cmd_line and ("<<" in cmd_line):
            lines = cmd_line.split("\n")
            first_line = lines[0]
            rest_lines = lines[1:]

            # Process only the first line for tilde expansion
            expanded_first = self._expand_tilde_line(first_line)

            # Reconstruct with original newlines
            if rest_lines:
                return expanded_first + "\n" + "\n".join(rest_lines)
            else:
                return expanded_first
        else:
            # Regular tilde expansion for non-heredoc commands
            return self._expand_tilde_line(cmd_line)

    def _expand_tilde_line(self, line: str) -> str:
        """
        Expand tilde in a single line.

        Args:
            line: Single line to expand

        Returns:
            Line with tildes expanded
        """
        try:
            parts = shlex.split(line)
        except ValueError:
            parts = line.split()

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
                search_dir = (
                    os.path.join(search_path, dir_parts[0])
                    if dir_parts[0]
                    else search_path
                )
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
        except Exception:
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
