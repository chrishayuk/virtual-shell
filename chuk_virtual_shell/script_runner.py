"""
chuk_virtual_shell/script_runner.py - Execute shell scripts in PyodideShell
"""


class ScriptRunner:
    """Utility class for running shell scripts"""

    def __init__(self, shell):
        """
        Initialize the script runner

        Args:
            shell: The shell interpreter instance
        """
        self.shell = shell

    def run_script(self, script_path):
        """
        Run a shell script from a file path

        Args:
            script_path: Path to the script file

        Returns:
            str: Output from the script execution
        """
        # Read script content
        script_content = self.shell.fs.read_file(script_path)

        if script_content is None:
            return f"script: cannot open '{script_path}': No such file"

        return self.run_script_content(script_content)

    def run_script_content(self, script_content):
        """
        Run a shell script from a string, supporting heredocs

        Args:
            script_content: String containing the script commands

        Returns:
            str: Output from the script execution
        """
        # Split the script into lines
        lines = script_content.splitlines()

        # Process each line, handling heredocs
        results = []
        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Skip empty lines and comments
            if not line or line.startswith("#"):
                i += 1
                continue

            # Check for if statement
            if line.startswith("if "):
                # Process if/else/fi block
                if_result, end_line = self._process_if_block(lines, i)
                if if_result:
                    results.append(if_result)
                i = end_line + 1
            # Check for heredoc
            elif "<<" in line:
                # Parse heredoc
                heredoc_result = self._process_heredoc(lines, i)
                if heredoc_result:
                    command, content, end_line = heredoc_result
                    # Execute the command with the heredoc content
                    result = self._execute_with_heredoc(command, content)
                    if result:
                        results.append(result)
                    i = end_line + 1
                else:
                    # Not a valid heredoc, execute normally
                    result = self.shell.execute(line)
                    if result:
                        results.append(result)
                    i += 1
            else:
                # Execute the command normally
                result = self.shell.execute(line)
                if result:
                    results.append(result)
                i += 1

            # Stop execution if the shell is no longer running
            if not self.shell.running:
                break

        # Return the combined results
        return "\n".join(results)

    def _process_heredoc(self, lines, start_line):
        """
        Process a heredoc starting at the given line

        Args:
            lines: All script lines
            start_line: Index of the line containing <<

        Returns:
            Tuple of (command, content, end_line) or None if not a valid heredoc
        """
        line = lines[start_line]

        # Parse the heredoc syntax: command << DELIMITER
        import re

        match = re.match(r"^(.*?)<<\s*(\S+)\s*$", line)
        if not match:
            return None

        command = match.group(1).strip()
        delimiter = match.group(2)

        # Collect lines until we find the delimiter
        content_lines = []
        current_line = start_line + 1

        while current_line < len(lines):
            if lines[current_line].strip() == delimiter:
                # Found the end delimiter
                content = "\n".join(content_lines)
                return (command, content, current_line)
            else:
                content_lines.append(lines[current_line])
            current_line += 1

        # Delimiter not found
        return None

    def _process_if_block(self, lines, start_line):
        """
        Process if/then/else/fi block

        Args:
            lines: All script lines
            start_line: Index of the line containing 'if'

        Returns:
            Tuple of (result, end_line)
        """
        # Parse if condition
        if_line = lines[start_line].strip()

        # Extract condition (simple support for [ ] test conditions)
        condition = if_line[3:].strip()  # Remove 'if '

        # Find then, else, and fi
        then_line = -1
        else_line = -1
        fi_line = -1
        current = start_line + 1
        nesting_level = 0

        while current < len(lines):
            line = lines[current].strip()

            # Track nested if statements
            if line.startswith("if "):
                nesting_level += 1
            elif line == "fi":
                if nesting_level == 0:
                    fi_line = current
                    break
                else:
                    nesting_level -= 1
            elif nesting_level == 0:
                if line == "then":
                    then_line = current
                elif line == "else":
                    else_line = current

            current += 1

        if fi_line == -1:
            # Missing fi, treat as single line if
            return "", start_line

        # Evaluate condition
        condition_result = self._evaluate_condition(condition)

        # Execute appropriate block
        result_lines = []
        if condition_result:
            # Execute then block
            if then_line != -1:
                start = then_line + 1
                end = else_line if else_line != -1 else fi_line
                for i in range(start, end):
                    line = lines[i].strip()
                    if line and not line.startswith("#"):
                        res = self.shell.execute(line)
                        if res:
                            result_lines.append(res)
        else:
            # Execute else block if it exists
            if else_line != -1:
                start = else_line + 1
                end = fi_line
                for i in range(start, end):
                    line = lines[i].strip()
                    if line and not line.startswith("#"):
                        res = self.shell.execute(line)
                        if res:
                            result_lines.append(res)

        return "\n".join(result_lines), fi_line

    def _evaluate_condition(self, condition):
        """
        Evaluate a shell condition

        Supports:
        - [ -f file ] - file exists
        - [ -d dir ] - directory exists
        - [ -s file ] - file exists and is not empty
        - [ -z string ] - string is empty
        - [ -n string ] - string is not empty
        - [ string1 = string2 ] - strings are equal
        - [ string1 != string2 ] - strings are not equal
        - [ num1 -eq num2 ] - numbers are equal
        - [ num1 -ne num2 ] - numbers are not equal
        - [ num1 -gt num2 ] - num1 > num2
        - [ num1 -lt num2 ] - num1 < num2
        - [ num1 -ge num2 ] - num1 >= num2
        - [ num1 -le num2 ] - num1 <= num2
        """
        # Remove 'then' if it's at the end
        if condition.endswith("then"):
            condition = condition[:-4].strip()

        # Simple implementation for [ ] test conditions
        if condition.startswith("[") and condition.endswith("]"):
            condition = condition[1:-1].strip()

            # File tests
            if condition.startswith("-f "):
                filepath = condition[3:].strip()
                return self.shell.fs.is_file(filepath)
            elif condition.startswith("-d "):
                dirpath = condition[3:].strip()
                return self.shell.fs.is_dir(dirpath)
            elif condition.startswith("-s "):
                filepath = condition[3:].strip()
                content = self.shell.fs.read_file(filepath)
                return content is not None and len(content) > 0
            elif condition.startswith("-z "):
                string = condition[3:].strip().strip('"')
                return len(string) == 0
            elif condition.startswith("-n "):
                string = condition[3:].strip().strip('"')
                return len(string) > 0

            # String comparisons
            if " = " in condition:
                left, right = condition.split(" = ", 1)
                return left.strip().strip('"') == right.strip().strip('"')
            elif " != " in condition:
                left, right = condition.split(" != ", 1)
                return left.strip().strip('"') != right.strip().strip('"')

            # Numeric comparisons
            numeric_ops = {
                " -eq ": "==",
                " -ne ": "!=",
                " -gt ": ">",
                " -lt ": "<",
                " -ge ": ">=",
                " -le ": "<=",
            }

            for op, py_op in numeric_ops.items():
                if op in condition:
                    left, right = condition.split(op, 1)
                    try:
                        left_val = int(left.strip())
                        right_val = int(right.strip())
                        return eval(f"{left_val} {py_op} {right_val}")
                    except ValueError:
                        return False

        # For other conditions, treat as command and check exit status
        # For simplicity, we'll return True if command executes successfully
        result = self.shell.execute(condition)
        return (
            result is not None
            and "error" not in result.lower()
            and "not found" not in result.lower()
        )

    def _execute_with_heredoc(self, command, content):
        """
        Execute a command with heredoc content

        Args:
            command: The command to execute (e.g., "cat > file.txt")
            content: The heredoc content

        Returns:
            str: Result of the command execution
        """
        # Handle cat > file or cat >> file
        if command.startswith("cat"):
            parts = command.split()
            if len(parts) >= 3 and parts[1] in [">", ">>"]:
                filename = parts[2]
                if parts[1] == ">":
                    # Overwrite file
                    self.shell.fs.write_file(filename, content)
                else:
                    # Append to file
                    existing = self.shell.fs.read_file(filename) or ""
                    if existing and not existing.endswith("\n"):
                        content = existing + "\n" + content
                    else:
                        content = existing + content
                    self.shell.fs.write_file(filename, content)
                return ""
            else:
                # Just cat, output the content
                return content

        # For other commands, we could pipe the content as stdin
        # For now, just execute the command
        return self.shell.execute(command)
