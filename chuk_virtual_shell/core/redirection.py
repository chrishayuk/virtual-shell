"""
Advanced redirection handler for shell operations.

Supports:
- Standard output redirection: >, >>
- Standard error redirection: 2>, 2>>
- Combined redirection: &>, &>>, 2>&1
- Input redirection: <
- Here-documents: <<, <<-
- File descriptor manipulation
"""

import re
import logging
from typing import Optional, Tuple, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RedirectionInfo:
    """Information about redirections in a command."""

    command: str  # The command without redirections
    stdin_file: Optional[str] = None  # Input file (<)
    stdout_file: Optional[str] = None  # Output file (> or >>)
    stdout_append: bool = False  # Append mode for stdout
    stderr_file: Optional[str] = None  # Error file (2> or 2>>)
    stderr_append: bool = False  # Append mode for stderr
    stderr_to_stdout: bool = False  # Redirect stderr to stdout (2>&1)
    combined_file: Optional[str] = None  # Combined output (&> or &>>)
    combined_append: bool = False  # Append mode for combined
    heredoc_delimiter: Optional[str] = None  # Heredoc delimiter (<<)
    heredoc_content: Optional[str] = None  # Heredoc content
    heredoc_strip_tabs: bool = False  # Strip leading tabs (<<-)


class RedirectionParser:
    """Parse and handle advanced shell redirections."""

    # Regex patterns for different redirection types - updated to handle quoted filenames
    PATTERNS = {
        # Combined stderr and stdout
        "combined_append": re.compile(r'&>>\s*(?:"([^"]*)"|\'([^\']*)\'|([^\s]+))'),
        "combined": re.compile(r'&>\s*(?:"([^"]*)"|\'([^\']*)\'|([^\s]+))'),
        # Stderr redirection
        "stderr_to_stdout": re.compile(r"2>&1"),
        "stderr_append": re.compile(r'2>>\s*(?:"([^"]*)"|\'([^\']*)\'|([^\s]+))'),
        "stderr": re.compile(r'2>\s*(?:"([^"]*)"|\'([^\']*)\'|([^\s]+))'),
        # Stdout redirection
        "stdout_append": re.compile(r'(?<!2)>>\s*(?:"([^"]*)"|\'([^\']*)\'|([^\s]+))'),
        "stdout": re.compile(r'(?<![2&])>\s*(?:"([^"]*)"|\'([^\']*)\'|([^\s]+))'),
        # Here-documents (must come before stdin to avoid matching << as <)
        "heredoc_strip": re.compile(r"<<-\s*(\S+)"),
        "heredoc": re.compile(r"<<\s*(\S+)"),
        # Input redirection (negative lookbehind to avoid matching <<)
        "stdin": re.compile(r'(?<!<)<(?!<)\s*(?:"([^"]*)"|\'([^\']*)\'|([^\s]+))'),
    }

    def parse(self, command: str) -> RedirectionInfo:
        """
        Parse a command line for redirections.

        Args:
            command: Command line to parse

        Returns:
            RedirectionInfo with parsed redirections
        """
        info = RedirectionInfo(command=command)
        remaining = command

        # Process redirections in order of precedence

        # Combined output (&> and &>>)
        match = self.PATTERNS["combined_append"].search(remaining)
        if match:
            info.combined_file = self._extract_filename(match)
            info.combined_append = True
            remaining = self.PATTERNS["combined_append"].sub("", remaining)
        else:
            match = self.PATTERNS["combined"].search(remaining)
            if match:
                info.combined_file = self._extract_filename(match)
                info.combined_append = False
                remaining = self.PATTERNS["combined"].sub("", remaining)

        # Stderr to stdout (2>&1)
        if self.PATTERNS["stderr_to_stdout"].search(remaining):
            info.stderr_to_stdout = True
            remaining = self.PATTERNS["stderr_to_stdout"].sub("", remaining)

        # Stderr redirection (2> and 2>>)
        if not info.stderr_to_stdout and not info.combined_file:
            match = self.PATTERNS["stderr_append"].search(remaining)
            if match:
                info.stderr_file = self._extract_filename(match)
                info.stderr_append = True
                remaining = self.PATTERNS["stderr_append"].sub("", remaining)
            else:
                match = self.PATTERNS["stderr"].search(remaining)
                if match:
                    info.stderr_file = self._extract_filename(match)
                    info.stderr_append = False
                    remaining = self.PATTERNS["stderr"].sub("", remaining)

        # Stdout redirection (> and >>)
        if not info.combined_file:
            match = self.PATTERNS["stdout_append"].search(remaining)
            if match:
                info.stdout_file = self._extract_filename(match)
                info.stdout_append = True
                remaining = self.PATTERNS["stdout_append"].sub("", remaining)
            else:
                match = self.PATTERNS["stdout"].search(remaining)
                if match:
                    info.stdout_file = self._extract_filename(match)
                    info.stdout_append = False
                    remaining = self.PATTERNS["stdout"].sub("", remaining)

        # Here-documents (<< and <<-) - must come before stdin
        match = self.PATTERNS["heredoc_strip"].search(remaining)
        if match:
            info.heredoc_delimiter = match.group(1)
            info.heredoc_strip_tabs = True
            remaining = self.PATTERNS["heredoc_strip"].sub("", remaining, count=1)
        else:
            match = self.PATTERNS["heredoc"].search(remaining)
            if match:
                info.heredoc_delimiter = match.group(1)
                info.heredoc_strip_tabs = False
                remaining = self.PATTERNS["heredoc"].sub("", remaining, count=1)

        # Input redirection (<)
        match = self.PATTERNS["stdin"].search(remaining)
        if match:
            info.stdin_file = self._extract_filename(match)
            remaining = self.PATTERNS["stdin"].sub("", remaining)

        info.command = remaining.strip()
        return info

    def _extract_filename(self, match):
        """
        Extract filename from regex match with multiple groups.

        The regex patterns capture quoted and unquoted filenames in different groups:
        - Group 1: Double-quoted filename
        - Group 2: Single-quoted filename
        - Group 3: Unquoted filename

        Returns the first non-None group.
        """
        # Return the first non-None group
        for i in range(1, len(match.groups()) + 1):
            if match.group(i) is not None:
                return match.group(i)
        return None

    def is_quoted(self, text: str, position: int) -> bool:
        """
        Check if a position in text is inside quotes.

        Args:
            text: Text to check
            position: Position to check

        Returns:
            True if position is inside quotes
        """
        if position >= len(text):
            return False

        in_single = False
        in_double = False
        escaped = False

        for i, char in enumerate(text):
            if i >= position:
                break

            if escaped:
                escaped = False
                continue

            if char == "\\":
                escaped = True
            elif char == '"' and not in_single:
                in_double = not in_double
            elif char == "'" and not in_double:
                in_single = not in_single

        return in_single or in_double

    def extract_heredoc_content(
        self,
        lines: List[str],
        start_index: int,
        delimiter: str,
        strip_tabs: bool = False,
    ) -> Tuple[str, int]:
        """
        Extract here-document content from script lines.

        Args:
            lines: Script lines
            start_index: Index where heredoc starts
            delimiter: Heredoc delimiter
            strip_tabs: Whether to strip leading tabs

        Returns:
            Tuple of (content, end_index)
        """
        content_lines = []
        end_index = start_index

        for i in range(start_index + 1, len(lines)):
            line = lines[i]

            # Check for delimiter
            if line.strip() == delimiter:
                end_index = i
                break

            # Process line
            if strip_tabs:
                # Remove leading tabs only
                line = line.lstrip("\t")

            content_lines.append(line)
        else:
            # Delimiter not found
            logger.warning(f"Heredoc delimiter '{delimiter}' not found")
            return "", start_index

        return "\n".join(content_lines), end_index


class RedirectionHandler:
    """Handle execution of commands with redirections."""

    def __init__(self, shell):
        """
        Initialize handler with shell reference.

        Args:
            shell: Shell interpreter instance
        """
        self.shell = shell
        self.parser = RedirectionParser()

    def execute_with_redirection(
        self, command: str, capture_stderr: bool = False
    ) -> Tuple[str, str]:
        """
        Execute a command with redirection support.

        Args:
            command: Command to execute
            capture_stderr: Whether to capture stderr separately

        Returns:
            Tuple of (stdout, stderr)
        """
        # Parse redirections
        info = self.parser.parse(command)

        # Set up stdin if needed
        if info.stdin_file:
            try:
                stdin_content = self.shell.fs.read_file(info.stdin_file)
                if stdin_content is None:
                    return "", f"{info.stdin_file}: No such file or directory"
                self.shell._stdin_buffer = stdin_content
            except Exception as e:
                return "", f"Error reading {info.stdin_file}: {e}"

        # Handle heredoc
        if info.heredoc_delimiter:
            # Heredoc content should be provided separately in script context
            # For now, just set empty stdin
            self.shell._stdin_buffer = info.heredoc_content or ""

        # Execute the command
        stdout = ""
        stderr = ""

        try:
            # Execute command (simplified - actual implementation would capture stderr)
            result = self._execute_raw_command(info.command)

            # For now, treat all output as stdout
            # A full implementation would capture stderr separately
            stdout = result

        except Exception as e:
            stderr = str(e)
        finally:
            # Clean up stdin buffer
            if hasattr(self.shell, "_stdin_buffer"):
                del self.shell._stdin_buffer

        # Handle output redirections
        if info.combined_file:
            # Redirect both stdout and stderr to same file
            combined = stdout + stderr if stderr else stdout
            self._write_to_file(info.combined_file, combined, info.combined_append)
            return "", ""

        if info.stdout_file:
            self._write_to_file(info.stdout_file, stdout, info.stdout_append)
            stdout = ""

        if info.stderr_to_stdout:
            # Combine stderr into stdout
            stdout = stdout + stderr if stderr else stdout
            stderr = ""
        elif info.stderr_file:
            self._write_to_file(info.stderr_file, stderr, info.stderr_append)
            stderr = ""

        return stdout, stderr

    def _execute_raw_command(self, command: str) -> str:
        """
        Execute command without redirection handling.

        Args:
            command: Command to execute

        Returns:
            Command output
        """
        # Use the shell's existing execution mechanism
        # This would need to be integrated with the actual executor
        from chuk_virtual_shell.core.parser import CommandParser

        parser = CommandParser()
        cmd, args = parser.parse_command(command)

        if not cmd:
            return ""

        if cmd not in self.shell.commands:
            raise Exception(f"{cmd}: command not found")

        return self.shell.commands[cmd].run(args)

    def _write_to_file(self, filename: str, content: str, append: bool = False):
        """
        Write or append content to a file.

        Args:
            filename: Target file
            content: Content to write
            append: Whether to append or overwrite
        """
        try:
            if append:
                existing = self.shell.fs.read_file(filename)
                if existing:
                    content = existing + "\n" + content if existing else content

            self.shell.fs.write_file(filename, content)
        except Exception as e:
            logger.error(f"Error writing to {filename}: {e}")
