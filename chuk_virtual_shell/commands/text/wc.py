# src/chuk_virtual_shell/commands/text/wc.py
"""
chuk_virtual_shell/commands/text/wc.py - Word, line, character, and byte count
"""

from chuk_virtual_shell.commands.command_base import ShellCommand


class WcCommand(ShellCommand):
    name = "wc"
    help_text = """wc - Word, line, character, and byte count
Usage: wc [OPTIONS] [FILE]...
Options:
  -l        Print line count
  -w        Print word count
  -c        Print byte count
  -m        Print character count
  -L        Print length of longest line
Default: Print lines, words, and bytes"""
    category = "text"

    def execute(self, args):
        # Parse options
        options = {
            "lines": False,
            "words": False,
            "bytes": False,
            "chars": False,
            "max_line": False,
        }

        files = []
        i = 0
        has_options = False

        # Parse arguments
        while i < len(args):
            arg = args[i]
            if arg.startswith("-"):
                has_options = True
                for char in arg[1:]:
                    if char == "l":
                        options["lines"] = True
                    elif char == "w":
                        options["words"] = True
                    elif char == "c":
                        options["bytes"] = True
                    elif char == "m":
                        options["chars"] = True
                    elif char == "L":
                        options["max_line"] = True
            else:
                files.append(arg)
            i += 1

        # If no options specified, default to lines, words, bytes
        if not has_options:
            options["lines"] = True
            options["words"] = True
            options["bytes"] = True

        # Process input
        if not files:
            # Use stdin if available
            if hasattr(self.shell, "_stdin_buffer") and self.shell._stdin_buffer:
                content = self.shell._stdin_buffer
                counts = self._count_content(content, options)
                return self._format_output([counts], [""], options, False)
            else:
                return self._format_output([(0, 0, 0, 0, 0)], [""], options, False)

        # Process files
        all_counts = []
        filenames = []

        for filepath in files:
            content = self.shell.fs.read_file(filepath)
            if content is None:
                return f"wc: {filepath}: No such file or directory"

            counts = self._count_content(content, options)
            all_counts.append(counts)
            filenames.append(filepath)

        return self._format_output(all_counts, filenames, options, len(files) > 1)

    def _count_content(self, content, options):
        """Count lines, words, bytes, chars, and max line length"""
        if not content:
            return (0, 0, 0, 0, 0)

        lines = content.splitlines()
        line_count = len(lines)

        # Count words
        word_count = 0
        for line in lines:
            word_count += len(line.split())

        # Count bytes
        byte_count = len(content.encode("utf-8"))

        # Count characters
        char_count = len(content)

        # Find longest line
        max_line_length = 0
        for line in lines:
            line_length = len(line)
            if line_length > max_line_length:
                max_line_length = line_length

        return (line_count, word_count, byte_count, char_count, max_line_length)

    def _format_output(self, counts_list, filenames, options, show_total):
        """Format output based on options"""
        results = []

        # Calculate totals if needed
        total_lines = 0
        total_words = 0
        total_bytes = 0
        total_chars = 0
        max_of_max = 0

        for counts in counts_list:
            total_lines += counts[0]
            total_words += counts[1]
            total_bytes += counts[2]
            total_chars += counts[3]
            if counts[4] > max_of_max:
                max_of_max = counts[4]

        # Format each file's counts
        for i, counts in enumerate(counts_list):
            parts = []

            if options["lines"]:
                parts.append(f"{counts[0]:8d}")
            if options["words"]:
                parts.append(f"{counts[1]:8d}")
            if options["bytes"]:
                parts.append(f"{counts[2]:8d}")
            if options["chars"] and not options["bytes"]:
                parts.append(f"{counts[3]:8d}")
            if options["max_line"]:
                parts.append(f"{counts[4]:8d}")

            # Add filename if provided
            line = " ".join(parts)
            if filenames[i]:
                line += f" {filenames[i]}"

            results.append(line.strip())

        # Add total line if multiple files
        if show_total:
            parts = []

            if options["lines"]:
                parts.append(f"{total_lines:8d}")
            if options["words"]:
                parts.append(f"{total_words:8d}")
            if options["bytes"]:
                parts.append(f"{total_bytes:8d}")
            if options["chars"] and not options["bytes"]:
                parts.append(f"{total_chars:8d}")
            if options["max_line"]:
                parts.append(f"{max_of_max:8d}")

            line = " ".join(parts) + " total"
            results.append(line.strip())

        return "\n".join(results)
