# src/chuk_virtual_shell/commands/text/patch.py
"""
chuk_virtual_shell/commands/text/patch.py - Apply diff patches to files
"""

import re
from chuk_virtual_shell.commands.command_base import ShellCommand


class PatchCommand(ShellCommand):
    name = "patch"
    help_text = """patch - Apply a diff file to an original
Usage: patch [OPTIONS] [ORIGINAL] < PATCHFILE
       patch [OPTIONS] -i PATCHFILE [ORIGINAL]
Options:
  -i FILE      Read patch from FILE instead of stdin
  -p NUM       Strip NUM leading components from file paths (default: 0)
  -R, --reverse  Reverse the patch
  -b           Make backup files
  -o FILE      Output to FILE instead of patching in place
  --dry-run    Print the results without modifying files
  
Examples:
  patch < changes.patch         # Apply patch from file
  patch -i changes.patch file.txt   # Apply specific patch
  patch -R < changes.patch      # Reverse a patch
  patch --dry-run < test.patch  # Test patch without applying"""
    category = "text"

    def execute(self, args):
        # Parse options
        patch_file = None
        original_file = None
        strip_level = 0
        reverse = False
        backup = False
        output_file = None
        dry_run = False
        use_stdin = True

        i = 0
        while i < len(args):
            arg = args[i]
            if arg == "-i":
                if i + 1 < len(args):
                    patch_file = args[i + 1]
                    use_stdin = False
                    i += 1
                else:
                    return "patch: option requires an argument -- 'i'"
            elif arg == "-p":
                if i + 1 < len(args):
                    try:
                        strip_level = int(args[i + 1])
                        i += 1
                    except ValueError:
                        return f"patch: invalid strip level '{args[i + 1]}'"
                else:
                    return "patch: option requires an argument -- 'p'"
            elif arg in ["-R", "--reverse"]:
                reverse = True
            elif arg == "-b":
                backup = True
            elif arg == "-o":
                if i + 1 < len(args):
                    output_file = args[i + 1]
                    i += 1
                else:
                    return "patch: option requires an argument -- 'o'"
            elif arg == "--dry-run":
                dry_run = True
            elif not arg.startswith("-"):
                if not original_file:
                    original_file = arg
            i += 1

        # Get patch content
        if use_stdin:
            if hasattr(self.shell, "_stdin_buffer") and self.shell._stdin_buffer:
                patch_content = self.shell._stdin_buffer
            else:
                return "patch: no patch input"
        else:
            if not patch_file:
                return "patch: no patch file specified"
            patch_content = self.shell.fs.read_file(patch_file)
            if patch_content is None:
                return f"patch: {patch_file}: No such file or directory"

        # Parse the patch
        patch_type, patches = self._parse_patch(patch_content)

        if not patches:
            return "patch: no valid patches found"

        # Apply patches
        results = []
        for patch_info in patches:
            file_to_patch = patch_info["file"]

            # Strip path components if requested
            if strip_level > 0:
                parts = file_to_patch.split("/")
                if len(parts) > strip_level:
                    file_to_patch = "/".join(parts[strip_level:])

            # Use original file if specified and only one patch
            if original_file and len(patches) == 1:
                file_to_patch = original_file

            # Read the file to patch
            original_content = self.shell.fs.read_file(file_to_patch)
            if original_content is None:
                # For new files (created from /dev/null), start with empty content
                if patch_info.get("old_file") == "/dev/null":
                    original_content = ""
                else:
                    results.append(f"patch: {file_to_patch}: No such file or directory")
                    continue

            # Apply the patch
            if patch_type == "unified":
                patched_content = self._apply_unified_patch(
                    original_content, patch_info, reverse
                )
            elif patch_type == "normal":
                patched_content = self._apply_normal_patch(
                    original_content, patch_info, reverse
                )
            else:
                results.append("patch: unsupported patch format")
                continue

            if patched_content is None:
                results.append(f"patch: failed to apply patch to {file_to_patch}")
                continue

            # Handle output
            if dry_run:
                results.append(f"checking file {file_to_patch}")
                results.append(
                    f"Hunk #1 succeeded (file {file_to_patch} would be patched)"
                )
            else:
                # Backup if requested
                if backup and not output_file:
                    backup_name = f"{file_to_patch}.orig"
                    self.shell.fs.write_file(backup_name, original_content)

                # Write the result
                if output_file:
                    self.shell.fs.write_file(output_file, patched_content)
                    results.append(f"patching file {file_to_patch} to {output_file}")
                else:
                    self.shell.fs.write_file(file_to_patch, patched_content)
                    results.append(f"patching file {file_to_patch}")

        return "\n".join(results) if results else "patch: no changes made"

    def _parse_patch(self, content):
        """Parse patch content and determine type"""
        lines = content.splitlines()
        patches = []
        current_patch = None
        patch_type = None

        i = 0
        while i < len(lines):
            line = lines[i]

            # Unified diff format
            if line.startswith("--- "):
                patch_type = "unified"
                # Start new patch
                file1 = line[4:].split("\t")[0].strip()
                if i + 1 < len(lines) and lines[i + 1].startswith("+++ "):
                    file2 = lines[i + 1][4:].split("\t")[0].strip()
                    i += 1

                    # Parse hunks
                    hunks = []
                    i += 1
                    while i < len(lines):
                        if lines[i].startswith("@@"):
                            # Parse hunk header
                            hunk = self._parse_unified_hunk(lines, i)
                            if hunk:
                                hunks.append(hunk)
                                i = hunk["end_line"]
                        elif lines[i].startswith("--- "):
                            # New patch starting
                            i -= 1
                            break
                        i += 1

                    patches.append(
                        {
                            "file": file2 if file2 != "/dev/null" else file1,
                            "old_file": file1,
                            "new_file": file2 if file2 != "/dev/null" else None,
                            "hunks": hunks,
                        }
                    )

            # Normal diff format
            elif re.match(r"^\d+[acd]\d+", line):
                patch_type = "normal"
                # Parse normal diff
                change = self._parse_normal_change(lines, i)
                if change:
                    if not current_patch:
                        current_patch = {"file": "unknown", "changes": []}
                    current_patch["changes"].append(change)
                    i = change["end_line"]

            i += 1

        if current_patch:
            patches.append(current_patch)

        return patch_type, patches

    def _parse_unified_hunk(self, lines, start):
        """Parse a unified diff hunk"""
        hunk_header = lines[start]
        match = re.match(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", hunk_header)
        if not match:
            return None

        old_start = int(match.group(1))
        old_count = int(match.group(2)) if match.group(2) else 1
        new_start = int(match.group(3))
        new_count = int(match.group(4)) if match.group(4) else 1

        hunk_lines = []
        i = start + 1

        while i < len(lines):
            line = lines[i]
            if line.startswith("@@") or line.startswith("--- "):
                break
            if line.startswith((" ", "-", "+")):
                hunk_lines.append(line)
            elif line.startswith("\\"):
                # "\ No newline at end of file" - ignore
                pass
            else:
                break
            i += 1

        return {
            "old_start": old_start,
            "old_count": old_count,
            "new_start": new_start,
            "new_count": new_count,
            "lines": hunk_lines,
            "end_line": i - 1,
        }

    def _parse_normal_change(self, lines, start):
        """Parse a normal diff change"""
        change_line = lines[start]
        match = re.match(r"^(\d+)(?:,(\d+))?([acd])(\d+)(?:,(\d+))?", change_line)
        if not match:
            return None

        old_start = int(match.group(1))
        old_end = int(match.group(2)) if match.group(2) else old_start
        operation = match.group(3)
        new_start = int(match.group(4))
        new_end = int(match.group(5)) if match.group(5) else new_start

        old_lines = []
        new_lines = []
        i = start + 1

        # Parse the change content
        if operation in ["c", "d"]:
            # Read old lines
            while i < len(lines) and lines[i].startswith("< "):
                old_lines.append(lines[i][2:])
                i += 1

        if operation == "c" and i < len(lines) and lines[i] == "---":
            i += 1

        if operation in ["c", "a"]:
            # Read new lines
            while i < len(lines) and lines[i].startswith("> "):
                new_lines.append(lines[i][2:])
                i += 1

        return {
            "old_start": old_start,
            "old_end": old_end,
            "operation": operation,
            "new_start": new_start,
            "new_end": new_end,
            "old_lines": old_lines,
            "new_lines": new_lines,
            "end_line": i - 1,
        }

    def _apply_unified_patch(self, content, patch_info, reverse):
        """Apply a unified diff patch"""
        lines = content.splitlines() if content else []

        # Apply hunks in reverse order to maintain line numbers
        for hunk in reversed(patch_info["hunks"]):
            if reverse:
                # Swap old and new for reverse
                old_start = hunk["new_start"]
                old_count = hunk["new_count"]
                new_lines = []

                for line in hunk["lines"]:
                    if line.startswith("+"):
                        # Remove additions (they become deletions)
                        pass
                    elif line.startswith("-"):
                        # Add deletions (they become additions)
                        new_lines.append(line[1:])
                    else:
                        # Context lines
                        new_lines.append(line[1:])
            else:
                old_start = hunk["old_start"]
                old_count = hunk["old_count"]
                new_lines = []

                for line in hunk["lines"]:
                    if line.startswith("-"):
                        # Skip deletions
                        pass
                    elif line.startswith("+"):
                        # Add additions
                        new_lines.append(line[1:])
                    else:
                        # Context lines
                        new_lines.append(line[1:])

            # Apply the hunk
            # Adjust for 1-based line numbers
            start_idx = old_start - 1
            end_idx = start_idx + old_count

            # Replace the lines
            lines[start_idx:end_idx] = new_lines

        return "\n".join(lines)

    def _apply_normal_patch(self, content, patch_info, reverse):
        """Apply a normal diff patch"""
        lines = content.splitlines() if content else []

        # Apply changes in reverse order
        for change in reversed(patch_info.get("changes", [])):
            operation = change["operation"]

            if reverse:
                # Reverse the operation
                if operation == "a":
                    operation = "d"
                elif operation == "d":
                    operation = "a"

                change["new_lines"]
                new_lines = change["old_lines"]
                start = change["new_start"]
                end = change["new_end"]
            else:
                change["old_lines"]
                new_lines = change["new_lines"]
                start = change["old_start"]
                end = change["old_end"]

            # Apply the change
            if operation == "d":
                # Delete lines
                del lines[start - 1 : end]
            elif operation == "a":
                # Add lines
                for i, line in enumerate(new_lines):
                    lines.insert(start + i, line)
            elif operation == "c":
                # Change lines
                lines[start - 1 : end] = new_lines

        return "\n".join(lines)
