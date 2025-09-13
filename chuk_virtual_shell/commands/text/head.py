# src/chuk_virtual_shell/commands/text/head.py
"""
chuk_virtual_shell/commands/text/head.py - Display first lines of files
"""

from chuk_virtual_shell.commands.command_base import ShellCommand


class HeadCommand(ShellCommand):
    name = "head"
    help_text = """head - Display first lines of files
Usage: head [OPTIONS] [FILE]...
Options:
  -n NUM    Display first NUM lines (default: 10)
  -c NUM    Display first NUM bytes
  -q        Never print headers with file names
  -v        Always print headers with file names"""
    category = "text"

    def execute(self, args):
        # Parse options
        options = {"lines": 10, "bytes": None, "quiet": False, "verbose": False}

        files = []
        i = 0

        # Parse arguments
        while i < len(args):
            arg = args[i]
            if arg == "-n":
                if i + 1 < len(args):
                    try:
                        options["lines"] = int(args[i + 1])
                        i += 1
                    except ValueError:
                        return f"head: invalid number of lines: '{args[i + 1]}'"
                else:
                    return "head: option requires an argument -- 'n'"
            elif arg.startswith("-n"):
                # Handle -n10 format
                try:
                    options["lines"] = int(arg[2:])
                except ValueError:
                    return f"head: invalid number of lines: '{arg[2:]}'"
            elif arg == "-c":
                if i + 1 < len(args):
                    try:
                        options["bytes"] = int(args[i + 1])
                        i += 1
                    except ValueError:
                        return f"head: invalid number of bytes: '{args[i + 1]}'"
                else:
                    return "head: option requires an argument -- 'c'"
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
                results.append(f"head: {filepath}: No such file or directory")
                continue

            # Add header if needed
            if show_headers:
                if i > 0:
                    results.append("")  # Empty line between files
                results.append(f"==> {filepath} <==")

            processed = self._process_content(content, options)
            if processed:
                results.append(processed)

        return "\n".join(results)

    def _process_content(self, content, options):
        """Process content according to options"""
        if options["bytes"] is not None:
            # Return first N bytes
            return content[: options["bytes"]]
        else:
            # Return first N lines
            lines = content.splitlines()
            return "\n".join(lines[: options["lines"]])
