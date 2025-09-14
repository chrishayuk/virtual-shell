# src/chuk_virtual_shell/commands/text/tail.py
"""
chuk_virtual_shell/commands/text/tail.py - Display last lines of files
"""

from chuk_virtual_shell.commands.command_base import ShellCommand


class TailCommand(ShellCommand):
    name = "tail"
    help_text = """tail - Display last lines of files
Usage: tail [OPTIONS] [FILE]...
Options:
  -n NUM    Display last NUM lines (default: 10)
  -c NUM    Display last NUM bytes
  -f        Follow file (not fully supported in virtual FS)
  -q        Never print headers with file names
  -v        Always print headers with file names"""
    category = "text"

    def execute(self, args):
        # Parse options
        options = {
            "lines": 10,
            "bytes": None,
            "follow": False,
            "quiet": False,
            "verbose": False,
        }

        files = []
        i = 0

        # Parse arguments
        while i < len(args):
            arg = args[i]
            if arg == "-n":
                if i + 1 < len(args):
                    try:
                        # Handle +N format (from Nth line onwards)
                        if args[i + 1].startswith("+"):
                            options["from_line"] = int(args[i + 1][1:])
                            options["lines"] = None
                        else:
                            options["lines"] = int(args[i + 1])
                        i += 1
                    except ValueError:
                        return f"tail: invalid number of lines: '{args[i + 1]}'"
                else:
                    return "tail: option requires an argument -- 'n'"
            elif arg.startswith("-n"):
                # Handle -n10 format
                try:
                    value = arg[2:]
                    if value.startswith("+"):
                        options["from_line"] = int(value[1:])
                        options["lines"] = None
                    else:
                        options["lines"] = int(value)
                except ValueError:
                    return f"tail: invalid number of lines: '{arg[2:]}'"
            elif arg == "-c":
                if i + 1 < len(args):
                    try:
                        options["bytes"] = int(args[i + 1])
                        i += 1
                    except ValueError:
                        return f"tail: invalid number of bytes: '{args[i + 1]}'"
                else:
                    return "tail: option requires an argument -- 'c'"
            elif arg == "-f":
                options["follow"] = True
            elif arg == "-q":
                options["quiet"] = True
            elif arg == "-v":
                options["verbose"] = True
            elif arg.startswith("-") and len(arg) > 1 and arg[1:].isdigit():
                # Handle -10 format (legacy)
                try:
                    options["lines"] = int(arg[1:])
                except ValueError:
                    files.append(arg)
            elif not arg.startswith("-"):
                files.append(arg)
            i += 1

        # If no files specified, use stdin
        if not files:
            if hasattr(self.shell, "_stdin_buffer") and self.shell._stdin_buffer:
                content = self.shell._stdin_buffer
                return self._process_content(content, options)
            else:
                return ""

        # Process files
        results = []
        show_headers = options["verbose"] or (len(files) > 1 and not options["quiet"])

        for i, filepath in enumerate(files):
            content = self.shell.fs.read_file(filepath)
            if content is None:
                results.append(f"tail: {filepath}: No such file or directory")
                continue

            # Add header if needed
            if show_headers:
                if i > 0:
                    results.append("")  # Empty line between files
                results.append(f"==> {filepath} <==")

            processed = self._process_content(content, options)
            if processed:
                results.append(processed)

            # Note: -f (follow) mode not fully implemented for virtual FS
            if options["follow"]:
                results.append(
                    "tail: follow mode not fully supported in virtual filesystem"
                )

        return "\n".join(results)

    def _process_content(self, content, options):
        """Process content according to options"""
        if options["bytes"] is not None:
            # Return last N bytes
            if options["bytes"] > 0:
                return content[-options["bytes"] :]
            else:
                return ""
        elif "from_line" in options and options.get("from_line"):
            # Return from Nth line onwards
            lines = content.splitlines()
            from_line = options["from_line"] - 1  # Convert to 0-based
            if from_line < len(lines):
                return "\n".join(lines[from_line:])
            else:
                return ""
        else:
            # Return last N lines
            lines = content.splitlines()
            if options["lines"] and options["lines"] > 0:
                return "\n".join(lines[-options["lines"] :])
            else:
                return ""
