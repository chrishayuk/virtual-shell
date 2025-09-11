"""
commands/file/more.py - Display file contents page by page
"""

import shutil
from chuk_virtual_shell.commands.command_base import ShellCommand


class MoreCommand(ShellCommand):
    name = "more"
    help_text = "more - Display file contents page by page\nUsage: more [file]..."
    category = "file"

    def execute(self, args):
        if not args:
            return "more: missing operand"

        # Get terminal size for paging
        terminal_width, terminal_height = shutil.get_terminal_size((80, 24))
        page_size = terminal_height - 2  # Leave a couple lines for prompts

        results = []

        for path in args:
            content = self.shell.fs.read_file(path)
            if content is None:
                return f"more: {path}: No such file"

            # Split content into lines
            lines = content.splitlines()

            # Add file header if multiple files
            if len(args) > 1:
                results.append(f"\n::::::::::::::\n{path}\n::::::::::::::\n")

            # Display content with paging
            total_lines = len(lines)
            current_line = 0

            # Simple paging for terminal display
            # In a real more command, this would handle interactive input
            # For our simplified version, we'll just display page by page
            while current_line < total_lines:
                # Calculate end of current page
                end_line = min(current_line + page_size, total_lines)

                # Display current page
                page_content = "\n".join(lines[current_line:end_line])
                results.append(page_content)

                # Show page info
                if end_line < total_lines:
                    percent = int((end_line / total_lines) * 100)
                    results.append(f"\n--More--({percent}%)")

                # Move to next page
                current_line = end_line

                # In a real more command, we would wait for user input here
                # For our simplified version, we'll just continue

        return "\n".join(results)
