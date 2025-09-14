"""
chuk_virtual_shell/commands/filesystem/more.py - Display file contents page by page
"""

import shutil
import argparse
import re
from typing import List, Optional, Tuple
from chuk_virtual_shell.commands.command_base import ShellCommand


class MoreCommand(ShellCommand):
    name = "more"
    help_text = (
        "more - Display file contents page by page\n"
        "Usage: more [options] [file...]\n"
        "Options:\n"
        "  -d, --silent         Prompt with helpful messages\n"
        "  -l, --logical        Do not pause after form feed (^L)\n"
        "  -f, --no-pause       Count logical lines, not screen lines\n"
        "  -p, --print-over     Clear screen before displaying\n"
        "  -c, --clean-print    Paint each screen from top, clearing lines\n"
        "  -s, --squeeze        Squeeze multiple blank lines into one\n"
        "  -u, --plain          Suppress underlining\n"
        "  -n, --lines NUM      Lines per screenful\n"
        "  -NUM                 Same as --lines NUM\n"
        "  +NUM                 Start at line NUM\n"
        "  +/PATTERN            Start at first occurrence of PATTERN\n"
        "  --help               Display this help and exit\n"
        "  --version            Display version and exit\n"
        "\n"
        "Interactive commands:\n"
        "  SPACE                Display next page\n"
        "  RETURN               Display next line\n"
        "  q                    Quit\n"
        "  /PATTERN             Search for pattern\n"
        "  =                    Show current line number\n"
        "  h                    Show help\n"
        "\n"
        "If no file is specified, reads from standard input."
    )
    category = "filesystem"

    def execute(self, args: List[str]) -> str:
        # Parse arguments manually to handle special syntax like +NUM and +/PATTERN
        files = []
        lines_per_page = None
        start_line = None
        start_pattern = None
        squeeze_blank = False
        clear_screen = False
        clean_print = False
        suppress_underline = False
        no_pause = False
        silent = False
        
        i = 0
        while i < len(args):
            arg = args[i]
            
            # Handle help and version
            if arg in ["--help", "-h"]:
                return self.get_help()
            if arg == "--version":
                return "more version 1.0.0"
            
            # Handle +NUM (start at line)
            if arg.startswith("+") and len(arg) > 1:
                if arg[1] == "/":
                    # +/PATTERN
                    start_pattern = arg[2:]
                else:
                    # +NUM
                    try:
                        start_line = int(arg[1:])
                    except ValueError:
                        pass
            
            # Handle -NUM (lines per page)
            elif arg.startswith("-") and len(arg) > 1 and arg[1:].isdigit():
                try:
                    lines_per_page = int(arg[1:])
                except ValueError:
                    pass
            
            # Handle regular options
            elif arg in ["-d", "--silent"]:
                silent = True
            elif arg in ["-l", "--logical"]:
                # Ignore form feeds (not implemented in simplified version)
                pass
            elif arg in ["-f", "--no-pause"]:
                no_pause = True
            elif arg in ["-p", "--print-over"]:
                clear_screen = True
            elif arg in ["-c", "--clean-print"]:
                clean_print = True
            elif arg in ["-s", "--squeeze"]:
                squeeze_blank = True
            elif arg in ["-u", "--plain"]:
                suppress_underline = True
            elif arg in ["-n", "--lines"]:
                if i + 1 < len(args):
                    try:
                        lines_per_page = int(args[i + 1])
                        i += 1
                    except ValueError:
                        return f"more: invalid number of lines: {args[i + 1]}"
            elif not arg.startswith("-"):
                files.append(arg)
            
            i += 1

        # Read from stdin if no files specified
        if not files:
            # Check if stdin has content
            if hasattr(self.shell, '_stdin_buffer') and self.shell._stdin_buffer:
                content = self.shell._stdin_buffer
                return self._display_content(
                    content, "<stdin>", lines_per_page, start_line, 
                    start_pattern, squeeze_blank, clear_screen, clean_print, 
                    silent
                )
            else:
                return "more: missing operand"

        # Process files
        results = []
        
        for file_path in files:
            # Check if file exists
            if not self.shell.fs.exists(file_path):
                results.append(f"more: {file_path}: No such file or directory")
                continue
            
            # Check if it's a directory
            if self.shell.fs.is_dir(file_path):
                results.append(f"more: {file_path}: Is a directory")
                continue
            
            # Read file content
            content = self.shell.fs.read_file(file_path)
            if content is None:
                results.append(f"more: {file_path}: Cannot read file")
                continue
            
            # Add file header if multiple files
            if len(files) > 1:
                results.append(f"\n::::::::::::::\n{file_path}\n::::::::::::::")
            
            # Display the content
            display_result = self._display_content(
                content, file_path, lines_per_page, start_line,
                start_pattern, squeeze_blank, clear_screen, clean_print,
                silent
            )
            results.append(display_result)

        return "\n".join(results)

    def _display_content(
        self, 
        content: str, 
        filename: str,
        lines_per_page: Optional[int],
        start_line: Optional[int],
        start_pattern: Optional[str],
        squeeze_blank: bool,
        clear_screen: bool,
        clean_print: bool,
        silent: bool
    ) -> str:
        """Display content with paging and options."""
        # Split content into lines
        lines = content.splitlines()
        
        # Apply squeeze blank lines if requested
        if squeeze_blank:
            squeezed_lines = []
            prev_blank = False
            for line in lines:
                if line.strip() == "":
                    if not prev_blank:
                        squeezed_lines.append(line)
                    prev_blank = True
                else:
                    squeezed_lines.append(line)
                    prev_blank = False
            lines = squeezed_lines
        
        # Find start position
        start_idx = 0
        if start_line:
            start_idx = max(0, min(start_line - 1, len(lines)))
        elif start_pattern:
            # Search for pattern
            pattern = re.compile(start_pattern)
            for i, line in enumerate(lines):
                if pattern.search(line):
                    start_idx = i
                    break
        
        # Determine page size
        if lines_per_page is None:
            terminal_width, terminal_height = shutil.get_terminal_size((80, 24))
            lines_per_page = terminal_height - 2  # Leave room for prompts
        
        # Display content with paging
        output_lines = []
        current_line = start_idx
        total_lines = len(lines)
        
        if clear_screen or clean_print:
            # Add ANSI clear screen code (simplified)
            output_lines.append("[Screen cleared]")
        
        while current_line < total_lines:
            # Calculate end of current page
            end_line = min(current_line + lines_per_page, total_lines)
            
            # Display current page
            page_content = "\n".join(lines[current_line:end_line])
            output_lines.append(page_content)
            
            # Show progress indicator
            if end_line < total_lines:
                percent = int((end_line / total_lines) * 100)
                if silent:
                    prompt = f"--More--({percent}%) [Press space to continue, 'q' to quit]"
                else:
                    prompt = f"--More--({percent}%)"
                output_lines.append(prompt)
            
            # Move to next page
            current_line = end_line
        
        return "\n".join(output_lines)

    def get_help(self):
        """Return help text."""
        return self.help_text