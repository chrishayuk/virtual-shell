# src/chuk_virtual_shell/commands/text/uniq.py
"""
chuk_virtual_shell/commands/text/uniq.py - Report or omit repeated lines
"""

from chuk_virtual_shell.commands.command_base import ShellCommand


class UniqCommand(ShellCommand):
    name = "uniq"
    help_text = """uniq - Report or omit repeated lines
Usage: uniq [OPTIONS] [INPUT [OUTPUT]]
Options:
  -c        Count occurrences
  -d        Only print duplicate lines
  -u        Only print unique lines
  -i        Ignore case
  -f NUM    Skip NUM fields
  -s NUM    Skip NUM characters
  -w NUM    Compare at most NUM characters"""
    category = "text"

    def execute(self, args):
        # Parse options
        options = {
            "count": False,
            "duplicates_only": False,
            "unique_only": False,
            "ignore_case": False,
            "skip_fields": 0,
            "skip_chars": 0,
            "max_chars": None,
        }

        files = []
        i = 0

        # Parse arguments
        while i < len(args):
            arg = args[i]
            if arg == "-c":
                options["count"] = True
            elif arg == "-d":
                options["duplicates_only"] = True
            elif arg == "-u":
                options["unique_only"] = True
            elif arg == "-i":
                options["ignore_case"] = True
            elif arg == "-f":
                if i + 1 < len(args):
                    try:
                        options["skip_fields"] = int(args[i + 1])
                        i += 1
                    except ValueError:
                        return (
                            f"uniq: invalid number of fields to skip: '{args[i + 1]}'"
                        )
                else:
                    return "uniq: option requires an argument -- 'f'"
            elif arg == "-s":
                if i + 1 < len(args):
                    try:
                        options["skip_chars"] = int(args[i + 1])
                        i += 1
                    except ValueError:
                        return f"uniq: invalid number of characters to skip: '{args[i + 1]}'"
                else:
                    return "uniq: option requires an argument -- 's'"
            elif arg == "-w":
                if i + 1 < len(args):
                    try:
                        options["max_chars"] = int(args[i + 1])
                        i += 1
                    except ValueError:
                        return f"uniq: invalid number of characters to compare: '{args[i + 1]}'"
                else:
                    return "uniq: option requires an argument -- 'w'"
            elif arg.startswith("-"):
                # Handle combined options
                for char in arg[1:]:
                    if char == "c":
                        options["count"] = True
                    elif char == "d":
                        options["duplicates_only"] = True
                    elif char == "u":
                        options["unique_only"] = True
                    elif char == "i":
                        options["ignore_case"] = True
            else:
                files.append(arg)
            i += 1

        # Get input content
        if not files:
            # Use stdin if available
            if hasattr(self.shell, "_stdin_buffer") and self.shell._stdin_buffer:
                content = self.shell._stdin_buffer
            else:
                return ""
        else:
            # Read from first file
            input_file = files[0]
            content = self.shell.fs.read_file(input_file)
            if content is None:
                return f"uniq: {input_file}: No such file or directory"

        # Process the content
        result = self._process_uniq(content, options)

        # Handle output file if specified
        if len(files) > 1:
            output_file = files[1]
            self.shell.fs.write_file(output_file, result)
            return ""

        return result

    def _process_uniq(self, content, options):
        """Process content for unique/duplicate lines"""
        if not content:
            return ""

        lines = content.splitlines()
        if not lines:
            return ""

        result = []
        prev_line = None
        prev_compare = None
        count = 0

        for line in lines:
            # Prepare line for comparison
            compare_line = self._prepare_for_comparison(line, options)

            if prev_compare is None:
                # First line
                prev_line = line
                prev_compare = compare_line
                count = 1
            elif compare_line == prev_compare:
                # Duplicate of previous line
                count += 1
            else:
                # Different from previous line
                self._output_line(result, prev_line, count, options)
                prev_line = line
                prev_compare = compare_line
                count = 1

        # Output the last line
        if prev_line is not None:
            self._output_line(result, prev_line, count, options)

        return "\n".join(result)

    def _prepare_for_comparison(self, line, options):
        """Prepare a line for comparison based on options"""
        # Skip fields if requested
        if options["skip_fields"] > 0:
            fields = line.split()
            if options["skip_fields"] < len(fields):
                line = " ".join(fields[options["skip_fields"] :])
            else:
                line = ""

        # Skip characters if requested
        if options["skip_chars"] > 0:
            if options["skip_chars"] < len(line):
                line = line[options["skip_chars"] :]
            else:
                line = ""

        # Limit comparison to max_chars
        if options["max_chars"] is not None:
            line = line[: options["max_chars"]]

        # Handle case-insensitive comparison
        if options["ignore_case"]:
            line = line.lower()

        return line

    def _output_line(self, result, line, count, options):
        """Output a line based on options and count"""
        # Check if we should output this line
        if options["duplicates_only"] and count == 1:
            return
        if options["unique_only"] and count > 1:
            return

        # Format output
        if options["count"]:
            result.append(f"   {count:4d} {line}")
        else:
            result.append(line)
