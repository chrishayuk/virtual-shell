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
        Run a shell script from a string, supporting heredocs and multi-line control flow

        Args:
            script_content: String containing the script commands

        Returns:
            str: Output from the script execution
        """
        # Split the script into lines
        lines = script_content.splitlines()

        # Process each line, handling control flow and heredocs
        results = []
        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Skip empty lines and comments
            if not line or line.startswith("#"):
                i += 1
                continue

            # Check for control flow statements
            if any(line.startswith(kw + " ") for kw in ["if", "for", "while", "until"]):
                # Process control flow block
                control_result, end_line = self._process_control_flow_block(lines, i)
                if control_result:
                    results.append(control_result)
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

    def _process_control_flow_block(self, lines, start_line):
        """
        Process a control flow block (if/for/while/until)
        
        Args:
            lines: All script lines
            start_line: Index of the line containing control flow keyword
            
        Returns:
            Tuple of (result, end_line)
        """
        first_line = lines[start_line].strip()
        
        # Determine the type of control flow
        if first_line.startswith("if "):
            return self._process_if_block(lines, start_line)
        elif first_line.startswith("for "):
            return self._process_loop_block(lines, start_line, "for", "done")
        elif first_line.startswith("while "):
            return self._process_loop_block(lines, start_line, "while", "done")
        elif first_line.startswith("until "):
            return self._process_loop_block(lines, start_line, "until", "done")
        else:
            # Shouldn't happen, but fallback to single line execution
            result = self.shell.execute(first_line)
            return result if result else "", start_line
    
    def _process_loop_block(self, lines, start_line, loop_type, end_keyword):
        """
        Process a loop block (for/while/until)
        
        Args:
            lines: All script lines
            start_line: Index of the line containing loop keyword
            loop_type: "for", "while", or "until"
            end_keyword: "done"
            
        Returns:
            Tuple of (result, end_line)
        """
        # Collect all lines that make up the loop
        loop_lines = []
        current = start_line
        nesting_level = 0
        
        while current < len(lines):
            line = lines[current].strip()
            
            # Track nesting
            if any(line.startswith(kw + " ") for kw in ["for", "while", "until"]):
                nesting_level += 1
                loop_lines.append(line)
            elif line == end_keyword:
                nesting_level -= 1
                loop_lines.append(line)
                if nesting_level == 0:
                    # Found the matching done
                    # Join lines with proper separators
                    loop_command = self._join_control_flow_lines(loop_lines)
                    result = self.shell.execute(loop_command)
                    return result if result else "", current
            elif line == "do":
                loop_lines.append(line)
            elif line in ["then", "else", "elif", "fi"]:
                loop_lines.append(line)
            else:
                # Regular command - needs semicolon if not a keyword
                if loop_lines and not loop_lines[-1].endswith(";"):
                    # Add semicolon before regular commands
                    if loop_lines[-1] not in ["do", "then", "else"]:
                        loop_lines[-1] += ";"
                loop_lines.append(line)
            
            current += 1
        
        # End keyword not found, execute what we have
        loop_command = self._join_control_flow_lines(loop_lines)
        result = self.shell.execute(loop_command)
        return result if result else "", current - 1
    
    def _join_control_flow_lines(self, lines):
        """
        Join control flow lines with proper syntax.
        
        Args:
            lines: List of lines to join
            
        Returns:
            Single command string
        """
        result = []
        for i, line in enumerate(lines):
            result.append(line)
            # Add semicolon between statements when needed
            if i < len(lines) - 1:
                next_line = lines[i + 1]
                # Add semicolon if current line is a command and next is a keyword or command
                if (not line.endswith(";") and 
                    line not in ["do", "then", "else", "elif"] and
                    not line.startswith("if ") and
                    not line.startswith("for ") and
                    not line.startswith("while ") and
                    not line.startswith("until ")):
                    # This is a regular command, add semicolon if next is not 'do' or 'then'
                    if next_line not in ["do", "then"]:
                        result[-1] += ";"
        
        return " ".join(result)

    def _process_if_block(self, lines, start_line):
        """
        Process if/then/else/fi block

        Args:
            lines: All script lines
            start_line: Index of the line containing 'if'

        Returns:
            Tuple of (result, end_line)
        """
        # Collect all lines that make up the if block
        if_lines = []
        current = start_line
        nesting_level = 0
        
        while current < len(lines):
            line = lines[current].strip()
            
            # Track nesting and add lines
            if line.startswith("if "):
                nesting_level += 1
                if_lines.append(line)
            elif line == "fi":
                nesting_level -= 1
                if_lines.append(line)
                if nesting_level == 0:
                    # Found the matching fi
                    # Join lines with proper syntax
                    if_command = self._join_control_flow_lines(if_lines)
                    result = self.shell.execute(if_command)
                    return result if result else "", current
            elif line in ["then", "else", "elif"]:
                if_lines.append(line)
            else:
                # Regular command
                if if_lines and not if_lines[-1].endswith(";"):
                    if if_lines[-1] not in ["do", "then", "else"]:
                        if_lines[-1] += ";"
                if_lines.append(line)
            
            current += 1
        
        # fi not found, execute what we have
        if_command = self._join_control_flow_lines(if_lines)
        result = self.shell.execute(if_command)
        return result if result else "", current - 1

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
