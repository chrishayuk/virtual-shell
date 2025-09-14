# src/chuk_virtual_shell/commands/text/diff.py
"""
chuk_virtual_shell/commands/text/diff.py - Compare files line by line
"""

import difflib
from chuk_virtual_shell.commands.command_base import ShellCommand


class DiffCommand(ShellCommand):
    name = "diff"
    help_text = """diff - Compare files line by line
Usage: diff [OPTIONS] FILE1 FILE2
Options:
  -u, --unified     Output unified diff format (default)
  -c, --context     Output context diff format
  -n, --normal      Output normal diff format
  -i, --ignore-case Ignore case differences
  -w, --ignore-all-space  Ignore all white space
  -b, --ignore-space-change  Ignore changes in amount of white space
  -B, --ignore-blank-lines  Ignore blank lines
  -q, --brief       Report only whether files differ
  --side-by-side    Output in two columns
  
Examples:
  diff file1.txt file2.txt      # Show differences
  diff -u old.txt new.txt       # Unified diff format
  diff -i file1 file2           # Case-insensitive comparison
  diff -q file1 file2           # Just check if different"""
    category = "text"

    def execute(self, args):
        if len(args) < 2:
            return "diff: missing operand\nTry 'diff --help' for more information."

        # Parse options
        context = False
        normal = False
        ignore_case = False
        ignore_all_space = False
        ignore_space_change = False
        ignore_blank_lines = False
        brief = False
        side_by_side = False
        files = []

        i = 0
        while i < len(args):
            arg = args[i]
            if arg in ["-u", "--unified"]:
                context = False
                normal = False
            elif arg in ["-c", "--context"]:
                context = True
                normal = False
            elif arg in ["-n", "--normal"]:
                normal = True
                context = False
            elif arg in ["-i", "--ignore-case"]:
                ignore_case = True
            elif arg in ["-w", "--ignore-all-space"]:
                ignore_all_space = True
            elif arg in ["-b", "--ignore-space-change"]:
                ignore_space_change = True
            elif arg in ["-B", "--ignore-blank-lines"]:
                ignore_blank_lines = True
            elif arg in ["-q", "--brief"]:
                brief = True
            elif arg == "--side-by-side":
                side_by_side = True
            elif not arg.startswith("-"):
                files.append(arg)
            i += 1

        if len(files) < 2:
            return "diff: missing operand\nTry 'diff --help' for more information."

        file1_path = files[0]
        file2_path = files[1]

        # Read files
        content1 = self.shell.fs.read_file(file1_path)
        if content1 is None:
            return f"diff: {file1_path}: No such file or directory"

        content2 = self.shell.fs.read_file(file2_path)
        if content2 is None:
            return f"diff: {file2_path}: No such file or directory"

        # Process content based on options
        lines1 = self._process_lines(
            content1,
            ignore_case,
            ignore_all_space,
            ignore_space_change,
            ignore_blank_lines,
        )
        lines2 = self._process_lines(
            content2,
            ignore_case,
            ignore_all_space,
            ignore_space_change,
            ignore_blank_lines,
        )

        # If files are identical
        if lines1 == lines2:
            if brief:
                return ""  # No output for identical files in brief mode
            return ""  # No output for identical files

        # If brief mode, just report that files differ
        if brief:
            return f"Files {file1_path} and {file2_path} differ"

        # Generate diff based on format
        if side_by_side:
            return self._side_by_side_diff(lines1, lines2, file1_path, file2_path)
        elif context:
            return self._context_diff(lines1, lines2, file1_path, file2_path)
        elif normal:
            return self._normal_diff(lines1, lines2)
        else:  # unified (default)
            return self._unified_diff(lines1, lines2, file1_path, file2_path)

    def _process_lines(
        self,
        content,
        ignore_case,
        ignore_all_space,
        ignore_space_change,
        ignore_blank_lines,
    ):
        """Process lines based on options"""
        lines = content.splitlines() if content else []

        processed = []
        for line in lines:
            # Apply transformations
            if ignore_case:
                line = line.lower()
            if ignore_all_space:
                line = "".join(line.split())
            elif ignore_space_change:
                line = " ".join(line.split())

            # Skip blank lines if requested
            if ignore_blank_lines and not line.strip():
                continue

            processed.append(line)

        return processed

    def _unified_diff(self, lines1, lines2, file1, file2):
        """Generate unified diff format"""
        diff = difflib.unified_diff(
            lines1, lines2, fromfile=file1, tofile=file2, lineterm=""
        )
        return "\n".join(diff)

    def _context_diff(self, lines1, lines2, file1, file2):
        """Generate context diff format"""
        diff = difflib.context_diff(
            lines1, lines2, fromfile=file1, tofile=file2, lineterm=""
        )
        return "\n".join(diff)

    def _normal_diff(self, lines1, lines2):
        """Generate normal diff format"""
        differ = difflib.Differ()
        diff = differ.compare(lines1, lines2)

        result = []
        line1_num = 0
        line2_num = 0
        changes = []

        for line in diff:
            if line.startswith("  "):  # Common line
                if changes:
                    result.append(self._format_normal_changes(changes))
                    changes = []
                line1_num += 1
                line2_num += 1
            elif line.startswith("- "):  # Line only in first file
                changes.append(("d", line1_num + 1, line[2:]))
                line1_num += 1
            elif line.startswith("+ "):  # Line only in second file
                changes.append(("a", line2_num + 1, line[2:]))
                line2_num += 1
            elif line.startswith("? "):  # Hint about changes
                continue

        if changes:
            result.append(self._format_normal_changes(changes))

        return "\n".join(result)

    def _format_normal_changes(self, changes):
        """Format changes for normal diff output"""
        if not changes:
            return ""

        # Group consecutive changes
        deletes = [c for c in changes if c[0] == "d"]
        adds = [c for c in changes if c[0] == "a"]

        output = []

        if deletes and adds:
            # Change operation
            d_start = deletes[0][1]
            d_end = deletes[-1][1]
            a_start = adds[0][1]
            a_end = adds[-1][1]

            if d_start == d_end:
                output.append(
                    f"{d_start}c{a_start},{a_end}"
                    if a_start != a_end
                    else f"{d_start}c{a_start}"
                )
            else:
                output.append(
                    f"{d_start},{d_end}c{a_start},{a_end}"
                    if a_start != a_end
                    else f"{d_start},{d_end}c{a_start}"
                )

            for d in deletes:
                output.append(f"< {d[2]}")
            output.append("---")
            for a in adds:
                output.append(f"> {a[2]}")
        elif deletes:
            # Delete operation
            d_start = deletes[0][1]
            d_end = deletes[-1][1]

            if d_start == d_end:
                output.append(f"{d_start}d{d_start - 1}")
            else:
                output.append(f"{d_start},{d_end}d{d_start - 1}")

            for d in deletes:
                output.append(f"< {d[2]}")
        elif adds:
            # Add operation
            a_start = adds[0][1]
            a_end = adds[-1][1]

            if a_start == a_end:
                output.append(f"{a_start - 1}a{a_start}")
            else:
                output.append(f"{a_start - 1}a{a_start},{a_end}")

            for a in adds:
                output.append(f"> {a[2]}")

        return "\n".join(output)

    def _side_by_side_diff(self, lines1, lines2, file1, file2):
        """Generate side-by-side diff format"""
        # Use difflib to get the differences
        differ = difflib.Differ()
        diff = list(differ.compare(lines1, lines2))

        output = []
        max_width = 40  # Width for each column

        # Header
        output.append(f"{file1:<{max_width}} | {file2}")
        output.append("-" * (max_width * 2 + 3))

        i = 0
        while i < len(diff):
            line = diff[i]
            if line.startswith("  "):  # Common line
                text = line[2:][: max_width - 1]
                output.append(f"{text:<{max_width}} | {text}")
            elif line.startswith("- "):  # Line only in first file
                text1 = line[2:][: max_width - 1]
                # Check if next line is an addition (change)
                if i + 1 < len(diff) and diff[i + 1].startswith("+ "):
                    text2 = diff[i + 1][2:][: max_width - 1]
                    output.append(f"{text1:<{max_width}} < {text2}")
                    i += 1  # Skip the next line
                else:
                    output.append(f"{text1:<{max_width}} <")
            elif line.startswith("+ "):  # Line only in second file
                text2 = line[2:][: max_width - 1]
                output.append(f"{'':<{max_width}} > {text2}")
            elif line.startswith("? "):  # Skip hint lines
                pass
            i += 1

        return "\n".join(output)
