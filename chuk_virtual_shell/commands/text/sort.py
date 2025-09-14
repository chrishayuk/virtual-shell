# src/chuk_virtual_shell/commands/text/sort.py
"""
chuk_virtual_shell/commands/text/sort.py - Sort lines of text files
"""

from chuk_virtual_shell.commands.command_base import ShellCommand


class SortCommand(ShellCommand):
    name = "sort"
    help_text = """sort - Sort lines of text files
Usage: sort [OPTIONS] [FILE]...
Options:
  -r        Reverse order
  -n        Numeric sort
  -u        Unique (remove duplicates)
  -k NUM    Sort by field NUM (1-based)
  -t SEP    Field separator
  -f        Ignore case (fold)
  -b        Ignore leading blanks"""
    category = "text"

    def execute(self, args):
        # Parse options
        options = {
            "reverse": False,
            "numeric": False,
            "unique": False,
            "field": None,
            "separator": None,
            "ignore_case": False,
            "ignore_blanks": False,
        }

        files = []
        i = 0

        # Parse arguments
        while i < len(args):
            arg = args[i]
            if arg == "-r":
                options["reverse"] = True
            elif arg == "-n":
                options["numeric"] = True
            elif arg == "-u":
                options["unique"] = True
            elif arg == "-f":
                options["ignore_case"] = True
            elif arg == "-b":
                options["ignore_blanks"] = True
            elif arg == "-k":
                if i + 1 < len(args):
                    try:
                        options["field"] = int(args[i + 1]) - 1  # Convert to 0-based
                        i += 1
                    except ValueError:
                        return f"sort: invalid field number: '{args[i + 1]}'"
                else:
                    return "sort: option requires an argument -- 'k'"
            elif arg == "-t":
                if i + 1 < len(args):
                    options["separator"] = args[i + 1]
                    i += 1
                else:
                    return "sort: option requires an argument -- 't'"
            elif arg.startswith("-"):
                # Handle combined options like -rn
                for char in arg[1:]:
                    if char == "r":
                        options["reverse"] = True
                    elif char == "n":
                        options["numeric"] = True
                    elif char == "u":
                        options["unique"] = True
                    elif char == "f":
                        options["ignore_case"] = True
                    elif char == "b":
                        options["ignore_blanks"] = True
            else:
                files.append(arg)
            i += 1

        # Collect all lines from input
        all_lines = []

        if not files:
            # Use stdin if available
            if hasattr(self.shell, "_stdin_buffer") and self.shell._stdin_buffer:
                all_lines.extend(self.shell._stdin_buffer.splitlines())
            else:
                return ""
        else:
            # Read from files
            for filepath in files:
                content = self.shell.fs.read_file(filepath)
                if content is None:
                    return f"sort: {filepath}: No such file or directory"
                all_lines.extend(content.splitlines())

        # Sort the lines
        sorted_lines = self._sort_lines(all_lines, options)

        return "\n".join(sorted_lines)

    def _sort_lines(self, lines, options):
        """Sort lines according to options"""
        if not lines:
            return []

        # Prepare key function for sorting
        def sort_key(line):
            # Handle blank line trimming
            if options["ignore_blanks"]:
                line = line.lstrip()

            # Handle field-based sorting
            if options["field"] is not None:
                separator = options["separator"] or r"[ \t]+"

                # Split line into fields
                if options["separator"]:
                    fields = line.split(separator)
                else:
                    fields = line.split()

                # Get the specified field (or empty if not enough fields)
                if options["field"] < len(fields):
                    value = fields[options["field"]]
                else:
                    value = ""
            else:
                value = line

            # Handle case-insensitive sorting
            if options["ignore_case"]:
                value = value.lower()

            # Handle numeric sorting
            if options["numeric"]:
                # Extract numeric part
                import re

                match = re.match(r"^[+-]?(\d+\.?\d*)", value.strip())
                if match:
                    try:
                        return float(match.group(0))
                    except ValueError:
                        return 0
                return 0

            return value

        # Sort the lines
        sorted_lines = sorted(lines, key=sort_key, reverse=options["reverse"])

        # Remove duplicates if requested
        if options["unique"]:
            seen = set()
            unique_lines = []
            for line in sorted_lines:
                if line not in seen:
                    seen.add(line)
                    unique_lines.append(line)
            sorted_lines = unique_lines

        return sorted_lines
