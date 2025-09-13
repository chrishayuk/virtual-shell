# src/chuk_virtual_shell/commands/text/sed.py
"""
chuk_virtual_shell/commands/text/sed.py - Stream editor for filtering and transforming text
"""

import re
from chuk_virtual_shell.commands.command_base import ShellCommand


class SedCommand(ShellCommand):
    name = "sed"
    help_text = """sed - Stream editor for filtering and transforming text
Usage: sed [OPTIONS] 'SCRIPT' [FILE]...
Options:
  -e SCRIPT    Add script to commands to be executed
  -i           Edit files in place
  -n           Suppress automatic printing
  -E           Use extended regular expressions
Common commands:
  s/old/new/   Substitute first occurrence
  s/old/new/g  Substitute all occurrences
  s/old/new/i  Case-insensitive substitution
  /pattern/d   Delete lines matching pattern
  /pattern/p   Print lines matching pattern
  1d           Delete first line
  $d           Delete last line
  2,5d         Delete lines 2-5"""
    category = "text"

    def execute(self, args):
        if not args:
            return "sed: missing script"

        # Parse options
        options = {"in_place": False, "quiet": False, "extended": False}

        scripts = []
        files = []
        i = 0

        # Parse arguments
        while i < len(args):
            arg = args[i]
            if arg == "-i":
                options["in_place"] = True
            elif arg == "-n":
                options["quiet"] = True
            elif arg == "-E":
                options["extended"] = True
            elif arg == "-e":
                if i + 1 < len(args):
                    scripts.append(args[i + 1])
                    i += 1
                else:
                    return "sed: option requires an argument -- 'e'"
            elif arg.startswith("-"):
                # Check for combined flags like -in
                for char in arg[1:]:
                    if char == "i":
                        options["in_place"] = True
                    elif char == "n":
                        options["quiet"] = True
                    elif char == "E":
                        options["extended"] = True
                    else:
                        return f"sed: invalid option -- '{char}'"
            elif not scripts:
                scripts.append(arg)
            else:
                files.append(arg)
            i += 1

        if not scripts:
            return "sed: missing script"

        # If no files specified, use stdin
        if not files:
            if hasattr(self.shell, "_stdin_buffer") and self.shell._stdin_buffer:
                content = self.shell._stdin_buffer
                result = self._process_content(content, scripts, options)
                return result
            else:
                return "sed: no input files"

        # Process files
        results = []
        for filepath in files:
            content = self.shell.fs.read_file(filepath)
            if content is None:
                return f"sed: {filepath}: No such file or directory"

            # For in-place editing with quiet mode, we need different behavior
            if options["in_place"] and options["quiet"]:
                # Process without quiet mode for the actual file write
                lines = content.splitlines()
                for script in scripts:
                    lines = self._apply_script(lines, script, options)
                # Write the actual modified content
                if lines and isinstance(lines[0], tuple):
                    processed = "\n".join([line for line, _ in lines])
                else:
                    processed = "\n".join(lines)
                self.shell.fs.write_file(filepath, processed)
                # But don't output anything (quiet mode)
            elif options["in_place"]:
                # Normal in-place editing
                processed = self._process_content(content, scripts, options)
                self.shell.fs.write_file(filepath, processed)
            else:
                # Normal output mode
                processed = self._process_content(content, scripts, options)
                results.append(processed)

        return "\n".join(results) if results else ""

    def _process_content(self, content, scripts, options):
        """Process content with sed scripts"""
        lines = content.splitlines()

        for script in scripts:
            lines = self._apply_script(lines, script, options)

        # Handle quiet mode
        if options["quiet"]:
            # Only output explicitly printed lines
            if lines and isinstance(lines[0], tuple):
                return "\n".join([line for line, printed in lines if printed])
            else:
                # If not tuples, nothing was explicitly printed
                return ""
        else:
            # Normal mode - output all lines
            if lines and isinstance(lines[0], tuple):
                return "\n".join([line for line, _ in lines])
            else:
                return "\n".join(lines)

    def _apply_script(self, lines, script, options):
        """Apply a single sed script to lines"""

        # Check for line-addressed substitution: 2s/old/new/ or $s/old/new/
        addr_sub_match = re.match(r"^(\d+|[$])s([/|#])(.*?)\2(.*?)\2([gip]*)$", script)
        if addr_sub_match:
            addr, delimiter, pattern, replacement, flags = addr_sub_match.groups()
            return self._substitute_at_line(
                lines, addr, pattern, replacement, flags, options
            )

        # Parse substitution command: s/pattern/replacement/flags
        sub_match = re.match(r"^s([/|#])(.*?)\1(.*?)\1([gip]*)$", script)
        if sub_match:
            delimiter, pattern, replacement, flags = sub_match.groups()
            return self._substitute(lines, pattern, replacement, flags, options)

        # Parse line addressing first: 1d, $d, 2,5d
        line_match = re.match(r"^(\d+|[$])(?:,(\d+|[$]))?([dp])$", script)
        if line_match:
            start, end, command = line_match.groups()
            return self._line_command(lines, start, end, command, options)

        # Parse pattern delete command: /pattern/d
        if script.endswith("d"):
            addr = script[:-1].strip()
            return self._delete(lines, addr, options)

        # Parse print command: /pattern/p
        if script.endswith("p"):
            addr = script[:-1].strip()
            return self._print(lines, addr, options)

        return lines

    def _substitute_at_line(self, lines, addr, pattern, replacement, flags, options):
        """Apply substitution to specific line(s)"""
        result = []

        # Prepare regex
        re_flags = 0
        if "i" in flags:
            re_flags |= re.IGNORECASE

        if not options["extended"]:
            pattern = re.escape(pattern)
            pattern = (
                pattern.replace(r"\*", "*")
                .replace(r"\.", ".")
                .replace(r"\^", "^")
                .replace(r"\$", "$")
            )

        try:
            compiled = re.compile(pattern, re_flags)
        except re.error:
            return lines

        # Determine which lines to process
        if addr == "$":
            target_lines = {len(lines) - 1} if lines else set()
        else:
            try:
                line_num = int(addr) - 1
                target_lines = {line_num} if 0 <= line_num < len(lines) else set()
            except ValueError:
                return lines

        for i, line in enumerate(lines):
            if isinstance(line, tuple):
                line = line[0]

            if i in target_lines:
                if "g" in flags:
                    new_line = compiled.sub(replacement, line)
                else:
                    new_line = compiled.sub(replacement, line, count=1)
                result.append(new_line)
            else:
                result.append(line)

        return result

    def _substitute(self, lines, pattern, replacement, flags, options):
        """Perform substitution"""
        result = []

        # Prepare regex flags
        re_flags = 0
        if "i" in flags:
            re_flags |= re.IGNORECASE

        if not options["extended"]:
            # Basic regex - escape special characters
            pattern = re.escape(pattern)
            # But unescape the basic regex metacharacters that sed supports
            pattern = (
                pattern.replace(r"\*", "*")
                .replace(r"\.", ".")
                .replace(r"\^", "^")
                .replace(r"\$", "$")
            )

        try:
            compiled = re.compile(pattern, re_flags)
        except re.error:
            return lines

        for line in lines:
            if isinstance(line, tuple):
                line = line[0]

            if "g" in flags:
                # Global replacement
                new_line = compiled.sub(replacement, line)
            else:
                # Single replacement
                new_line = compiled.sub(replacement, line, count=1)

            result.append(new_line)

        return result

    def _delete(self, lines, address, options):
        """Delete lines matching address"""
        if not address:
            # Delete all lines
            return []

        if address.startswith("/") and address.endswith("/"):
            # Pattern address
            pattern = address[1:-1]
            result = []

            re_flags = 0
            if not options["extended"]:
                pattern = re.escape(pattern)

            try:
                compiled = re.compile(pattern, re_flags)
            except re.error:
                return lines

            for line in lines:
                if isinstance(line, tuple):
                    line = line[0]
                if not compiled.search(line):
                    result.append(line)

            return result

        return lines

    def _print(self, lines, address, options):
        """Print lines matching address (for -n mode)"""
        if not address:
            return [(line, True) for line in lines]

        if address.startswith("/") and address.endswith("/"):
            # Pattern address
            pattern = address[1:-1]
            result = []

            re_flags = 0
            if not options["extended"]:
                pattern = re.escape(pattern)

            try:
                compiled = re.compile(pattern, re_flags)
            except re.error:
                return [(line, False) for line in lines]

            for line in lines:
                if isinstance(line, tuple):
                    line = line[0]
                printed = bool(compiled.search(line))
                result.append((line, printed))

            return result

        return [(line, False) for line in lines]

    def _line_command(self, lines, start, end, command, options):
        """Execute line-based commands"""
        result = []

        # Convert addresses to line numbers
        if start == "$":
            start_num = len(lines)
        else:
            start_num = int(start) if start else 1

        if end == "$":
            end_num = len(lines)
        elif end:
            end_num = int(end)
        else:
            end_num = start_num

        for i, line in enumerate(lines, 1):
            if isinstance(line, tuple):
                line = line[0]

            if command == "d":
                # Delete command
                if not (start_num <= i <= end_num):
                    result.append(line)
            elif command == "p":
                # Print command (for -n mode)
                if start_num <= i <= end_num:
                    result.append((line, True))
                else:
                    result.append((line, False))

        return result
