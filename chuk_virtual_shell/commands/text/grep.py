# src/chuk_virtual_shell/commands/text/grep.py
"""
chuk_virtual_shell/commands/text/grep.py - Search for patterns in files
"""

import re
from chuk_virtual_shell.commands.command_base import ShellCommand


class GrepCommand(ShellCommand):
    name = "grep"
    help_text = """grep - Search for patterns in files
Usage: grep [OPTIONS] PATTERN [FILE]...
Options:
  -i    Case insensitive search
  -v    Invert match (show non-matching lines)
  -n    Show line numbers
  -c    Count matching lines only
  -r    Recursive search in directories
  -E    Extended regex (ERE)
  -w    Match whole words only
  -l    List only filenames with matches
  -h    Suppress filename prefix"""
    category = "text"

    def execute(self, args):
        if not args:
            return "grep: missing pattern"

        # Parse options
        options = {
            "case_insensitive": False,
            "invert": False,
            "line_numbers": False,
            "count_only": False,
            "recursive": False,
            "extended_regex": False,
            "whole_word": False,
            "files_only": False,
            "no_filename": False,
        }

        pattern = None
        files = []
        i = 0

        # Parse arguments
        while i < len(args):
            arg = args[i]
            if arg.startswith("-") and pattern is None:
                for char in arg[1:]:
                    if char == "i":
                        options["case_insensitive"] = True
                    elif char == "v":
                        options["invert"] = True
                    elif char == "n":
                        options["line_numbers"] = True
                    elif char == "c":
                        options["count_only"] = True
                    elif char == "r":
                        options["recursive"] = True
                    elif char == "E":
                        options["extended_regex"] = True
                    elif char == "w":
                        options["whole_word"] = True
                    elif char == "l":
                        options["files_only"] = True
                    elif char == "h":
                        options["no_filename"] = True
            elif pattern is None:
                pattern = arg
            else:
                files.append(arg)
            i += 1

        if pattern is None:
            return "grep: missing pattern"

        # If no files specified, use stdin (if available)
        if not files:
            # Check if shell has stdin buffer
            if hasattr(self.shell, "_stdin_buffer") and self.shell._stdin_buffer:
                content = self.shell._stdin_buffer
                return self._search_content(content, pattern, options, "<stdin>")
            else:
                return "grep: no input files"

        # Process files
        results = []
        for filepath in files:
            if options["recursive"] and self.shell.fs.is_dir(filepath):
                # Recursive directory search
                dir_results = self._search_directory(filepath, pattern, options)
                if dir_results:
                    results.append(dir_results)
            else:
                # Single file search
                content = self.shell.fs.read_file(filepath)
                if content is None:
                    results.append(f"grep: {filepath}: No such file or directory")
                else:
                    file_results = self._search_content(
                        content, pattern, options, filepath, len(files) > 1
                    )
                    if file_results:
                        results.append(file_results)

        return "\n".join(results) if results else ""

    def _search_content(self, content, pattern, options, filename, show_filename=False):
        """Search for pattern in content"""
        # Prepare regex pattern
        regex_pattern = pattern

        flags = 0
        if options["case_insensitive"]:
            flags |= re.IGNORECASE

        # For basic grep, common regex patterns should still work
        # Don't escape the pattern - let regex compile handle it

        if options["whole_word"]:
            regex_pattern = r"\b" + regex_pattern + r"\b"

        try:
            compiled = re.compile(regex_pattern, flags)
        except re.error as e:
            return f"grep: invalid pattern: {e}"

        lines = content.splitlines()
        matches = []
        match_count = 0

        for line_num, line in enumerate(lines, 1):
            is_match = bool(compiled.search(line))

            if options["invert"]:
                is_match = not is_match

            if is_match:
                match_count += 1

                if options["files_only"]:
                    return filename

                if not options["count_only"]:
                    prefix = ""

                    # Add filename prefix
                    if show_filename and not options["no_filename"]:
                        prefix = f"{filename}:"

                    # Add line number
                    if options["line_numbers"]:
                        prefix += f"{line_num}:"

                    matches.append(prefix + line)

        if options["count_only"]:
            if show_filename and not options["no_filename"]:
                return f"{filename}:{match_count}"
            return str(match_count)

        return "\n".join(matches)

    def _search_directory(self, dirpath, pattern, options):
        """Recursively search directory"""
        results = []

        # List directory contents
        items = self.shell.fs.list_dir(dirpath)

        for item in items:
            item_path = f"{dirpath}/{item}".replace("//", "/")

            if self.shell.fs.is_dir(item_path):
                # Recurse into subdirectory
                sub_results = self._search_directory(item_path, pattern, options)
                if sub_results:
                    results.append(sub_results)
            else:
                # Search file
                content = self.shell.fs.read_file(item_path)
                if content is not None:
                    file_results = self._search_content(
                        content, pattern, options, item_path, True
                    )
                    if file_results:
                        results.append(file_results)

        return "\n".join(results) if results else ""
