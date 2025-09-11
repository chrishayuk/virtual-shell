"""
chuk_virtual_shell/interpreters/bash_interpreter.py - Execute bash scripts in virtual environment
"""

import re
import shlex
import asyncio


class VirtualBashInterpreter:
    """Execute bash scripts within virtual shell context"""

    def __init__(self, shell):
        self.shell = shell
        self.variables = {}
        self.exit_code = 0
        self.functions = {}
        self.aliases = {}

    async def run_script(self, script_path: str) -> str:
        """Execute a .sh script from virtual FS"""

        # Read script from virtual FS
        script_content = self.shell.fs.read_file(script_path)
        if script_content is None:
            return f"bash: {script_path}: No such file or directory"

        return await self.execute_script(script_content)

    async def execute_script(self, script_content: str) -> str:
        """Execute bash script content"""
        lines = script_content.splitlines()
        output = []

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Skip comments and empty lines
            if not line or line.startswith("#"):
                i += 1
                continue

            # Handle line continuation
            while line.endswith("\\") and i + 1 < len(lines):
                line = line[:-1] + " " + lines[i + 1].strip()
                i += 1

            try:
                # Use sync version to avoid nested event loop issues
                result = self.execute_line_sync(line)
                if result:
                    output.append(result)
            except Exception as e:
                return f"Error at line {i + 1}: {e}"

            i += 1

        return "\n".join(output)

    def execute_line_sync(self, line: str) -> str:
        """Synchronous version of execute_line"""

        # Skip complex constructs in sync mode (they need async)
        if any(line.startswith(kw) for kw in ["if ", "for ", "while ", "case "]):
            return ""

        # Expand variables for regular commands
        line = self._expand_variables(line)

        # Handle variable assignment
        if (
            "=" in line
            and not line.startswith("export")
            and not any(op in line for op in ["==", "!=", ">=", "<="])
        ):
            return self._handle_assignment(line)

        # Handle export
        if line.startswith("export "):
            return self._handle_export(line)

        # Handle pipes and redirects
        if any(op in line for op in ["|", ">", "<", ">>", "2>", "&>"]):
            return self._handle_pipeline_sync(line)

        # Handle logical operators
        if "&&" in line or "||" in line:
            return self._handle_logical_operators_sync(line)

        # Execute as simple command
        return self._execute_command_sync(line)

    async def execute_line(self, line: str) -> str:
        """Execute a single bash line"""

        # Don't expand variables yet for control structures
        # They need to handle variable expansion internally

        # Handle for loops (before variable expansion)
        if line.startswith("for "):
            return await self._handle_for_loop(line)

        # Handle if statements (before variable expansion)
        if line.startswith("if "):
            return await self._handle_if(line)

        # Handle while loops (before variable expansion)
        if line.startswith("while "):
            return await self._handle_while_loop(line)

        # Handle case statements (before variable expansion)
        if line.startswith("case "):
            return await self._handle_case(line)

        # Now expand variables for other commands
        line = self._expand_variables(line)

        # Handle variable assignment
        if (
            "=" in line
            and not line.startswith("export")
            and not any(op in line for op in ["==", "!=", ">=", "<="])
        ):
            return self._handle_assignment(line)

        # Handle export
        if line.startswith("export "):
            return self._handle_export(line)

        # Handle function definitions
        if "()" in line and "{" in line:
            return self._handle_function_def(line)

        # Handle pipes and redirects
        if any(op in line for op in ["|", ">", "<", ">>", "2>", "&>"]):
            return await self._handle_pipeline(line)

        # Handle command substitution
        if "`" in line or "$(" in line:
            line = await self._handle_command_substitution(line)

        # Handle logical operators
        if "&&" in line or "||" in line:
            return await self._handle_logical_operators(line)

        # Execute as simple command
        return await self._execute_command(line)

    def _expand_variables(self, text: str) -> str:
        """Expand variables in text"""

        # Special variables
        text = text.replace("$?", str(self.exit_code))
        text = text.replace("$$", str(id(self)))  # Process ID simulation
        text = text.replace("$#", "0")  # Argument count

        # Expand ${VAR} format
        def expand_braces(match):
            var_expr = match.group(1)

            # Handle ${VAR:-default}
            if ":-" in var_expr:
                var_name, default = var_expr.split(":-", 1)
                value = self.variables.get(var_name) or self.shell.environ.get(var_name)
                return value if value else default

            # Handle ${VAR:=default}
            if ":=" in var_expr:
                var_name, default = var_expr.split(":=", 1)
                value = self.variables.get(var_name) or self.shell.environ.get(var_name)
                if not value:
                    self.variables[var_name] = default
                    return default
                return value

            # Simple variable
            return self.variables.get(var_expr, self.shell.environ.get(var_expr, ""))

        text = re.sub(r"\$\{([^}]+)\}", expand_braces, text)

        # Expand $VAR format
        def expand_simple(match):
            var_name = match.group(1)
            return self.variables.get(var_name, self.shell.environ.get(var_name, ""))

        text = re.sub(r"\$([A-Za-z_]\w*)", expand_simple, text)

        return text

    def _handle_assignment(self, line: str) -> str:
        """Handle variable assignment"""
        match = re.match(r"^([A-Za-z_]\w*)=(.*)$", line)
        if match:
            var_name, var_value = match.groups()

            # Remove quotes if present
            if var_value.startswith('"') and var_value.endswith('"'):
                var_value = var_value[1:-1]
            elif var_value.startswith("'") and var_value.endswith("'"):
                var_value = var_value[1:-1]

            self.variables[var_name] = var_value
            return ""
        return ""

    def _handle_export(self, line: str) -> str:
        """Handle export command"""
        export_part = line[7:].strip()

        if "=" in export_part:
            var_name, var_value = export_part.split("=", 1)
            # Remove quotes
            if var_value.startswith('"') and var_value.endswith('"'):
                var_value = var_value[1:-1]
            elif var_value.startswith("'") and var_value.endswith("'"):
                var_value = var_value[1:-1]

            self.shell.environ[var_name] = var_value
            self.variables[var_name] = var_value
        else:
            # Export existing variable
            if export_part in self.variables:
                self.shell.environ[export_part] = self.variables[export_part]

        return ""

    def _handle_pipeline_sync(self, line: str) -> str:
        """Synchronous version of handle pipeline"""
        # Handle pipes first
        if "|" in line:
            commands = line.split("|")
            last_output = ""

            for cmd in commands:
                cmd = cmd.strip()

                # Set stdin buffer for piped commands
                if last_output:
                    self.shell._stdin_buffer = last_output

                last_output = self._execute_command_sync(cmd)

                # Clear stdin buffer
                if hasattr(self.shell, "_stdin_buffer"):
                    delattr(self.shell, "_stdin_buffer")

            return last_output

        # Handle output redirection
        redirect_match = re.match(r"^(.*?)\s*(>>?|2>|&>)\s*(.*)$", line)
        if redirect_match:
            command, operator, filepath = redirect_match.groups()
            filepath = filepath.strip()

            # Execute command
            output = self._execute_command_sync(command)

            # Handle redirection
            if filepath:
                if operator == ">>":
                    # Append
                    existing = self.shell.fs.read_file(filepath) or ""
                    self.shell.fs.write_file(filepath, existing + output + "\n")
                elif operator in [">", "2>", "&>"]:
                    # Overwrite
                    self.shell.fs.write_file(filepath, output)

            return ""

        # Handle input redirection
        if "<" in line:
            parts = line.split("<")
            if len(parts) == 2:
                command, filepath = parts
                filepath = filepath.strip()

                # Read file and set as stdin
                content = self.shell.fs.read_file(filepath)
                if content is not None:
                    self.shell._stdin_buffer = content
                    result = self._execute_command_sync(command.strip())
                    if hasattr(self.shell, "_stdin_buffer"):
                        delattr(self.shell, "_stdin_buffer")
                    return result

        return self._execute_command_sync(line)

    async def _handle_pipeline(self, line: str) -> str:
        """Handle pipes and redirections"""

        # Handle pipes first
        if "|" in line:
            commands = line.split("|")
            last_output = ""

            for cmd in commands:
                cmd = cmd.strip()

                # Set stdin buffer for piped commands
                if last_output:
                    self.shell._stdin_buffer = last_output

                last_output = await self._execute_command(cmd)

                # Clear stdin buffer
                if hasattr(self.shell, "_stdin_buffer"):
                    delattr(self.shell, "_stdin_buffer")

            return last_output

        # Handle output redirection
        redirect_match = re.match(r"^(.*?)\s*(>>?|2>|&>)\s*(.*)$", line)
        if redirect_match:
            command, operator, filepath = redirect_match.groups()
            filepath = filepath.strip()

            # Execute command
            output = await self._execute_command(command)

            # Handle redirection
            if filepath:
                if operator == ">>":
                    # Append
                    existing = self.shell.fs.read_file(filepath) or ""
                    self.shell.fs.write_file(filepath, existing + output + "\n")
                elif operator in [">", "2>", "&>"]:
                    # Overwrite
                    self.shell.fs.write_file(filepath, output)

            return ""

        # Handle input redirection
        if "<" in line:
            parts = line.split("<")
            if len(parts) == 2:
                command, filepath = parts
                filepath = filepath.strip()

                # Read file and set as stdin
                content = self.shell.fs.read_file(filepath)
                if content is not None:
                    self.shell._stdin_buffer = content
                    result = await self._execute_command(command.strip())
                    if hasattr(self.shell, "_stdin_buffer"):
                        delattr(self.shell, "_stdin_buffer")
                    return result

        return await self._execute_command(line)

    async def _handle_command_substitution(self, line: str) -> str:
        """Handle command substitution with `` or $()"""

        # Handle $() format
        def sub_dollar(match):
            cmd = match.group(1)
            result = asyncio.run(self._execute_command(cmd))
            return result.strip()

        line = re.sub(r"\$\(([^)]+)\)", sub_dollar, line)

        # Handle `` format
        def sub_backtick(match):
            cmd = match.group(1)
            result = asyncio.run(self._execute_command(cmd))
            return result.strip()

        line = re.sub(r"`([^`]+)`", sub_backtick, line)

        return line

    def _handle_logical_operators_sync(self, line: str) -> str:
        """Synchronous version of handle logical operators"""
        # Split by && and ||
        parts = re.split(r"(\s*&&\s*|\s*\|\|\s*)", line)

        results = []
        i = 0
        while i < len(parts):
            if i % 2 == 0:  # Command part
                cmd = parts[i].strip()
                if cmd:
                    result = self._execute_command_sync(cmd)
                    if result:
                        results.append(result)

                    # Check operator
                    if i + 1 < len(parts):
                        operator = parts[i + 1].strip()
                        if operator == "&&" and self.exit_code != 0:
                            # Skip next command if previous failed
                            break
                        elif operator == "||" and self.exit_code == 0:
                            # Skip next command if previous succeeded
                            break
            i += 1

        return "\n".join(results)

    async def _handle_logical_operators(self, line: str) -> str:
        """Handle && and || operators"""

        # Split by && and ||
        parts = re.split(r"(\s*&&\s*|\s*\|\|\s*)", line)

        results = []
        i = 0
        while i < len(parts):
            if i % 2 == 0:  # Command part
                cmd = parts[i].strip()
                if cmd:
                    result = await self._execute_command(cmd)
                    if result:
                        results.append(result)

                    # Check operator
                    if i + 1 < len(parts):
                        operator = parts[i + 1].strip()
                        if operator == "&&" and self.exit_code != 0:
                            # Skip next command if previous failed
                            break
                        elif operator == "||" and self.exit_code == 0:
                            # Skip next command if previous succeeded
                            break
            i += 1

        return "\n".join(results)

    def _execute_command_sync(self, command: str) -> str:
        """Synchronous version of execute command"""
        if not command or not command.strip():
            return ""

        command = command.strip()

        # Check if it's an alias
        cmd_parts = shlex.split(command)
        if cmd_parts and cmd_parts[0] in self.aliases:
            command = self.aliases[cmd_parts[0]] + " " + " ".join(cmd_parts[1:])

        # Execute through virtual shell
        try:
            result = self.shell.execute(command)
            self.exit_code = 0
            return result if result else ""
        except Exception as e:
            self.exit_code = 1
            return f"bash: {e}"

    async def _execute_command(self, command: str) -> str:
        """Execute a simple command through the virtual shell"""
        if not command or not command.strip():
            return ""

        command = command.strip()

        # Check if it's an alias
        cmd_parts = shlex.split(command)
        if cmd_parts and cmd_parts[0] in self.aliases:
            command = self.aliases[cmd_parts[0]] + " " + " ".join(cmd_parts[1:])

        # Execute through virtual shell
        try:
            if hasattr(self.shell, "execute_async"):
                result = await self.shell.execute_async(command)
            else:
                result = self.shell.execute(command)

            self.exit_code = 0
            return result if result else ""
        except Exception as e:
            self.exit_code = 1
            return f"bash: {e}"

    async def _handle_if(self, line: str) -> str:
        """Handle if statements (simplified)"""
        # This is a simplified implementation
        # Full bash if statements would require more complex parsing

        # Extract condition
        if_match = re.match(r"if\s+\[(.*?)\];\s*then\s+(.*?)(?:;\s*fi)?$", line)
        if if_match:
            condition, then_part = if_match.groups()

            # Evaluate condition (simplified)
            if await self._evaluate_condition(condition):
                return await self.execute_line(then_part)

        return ""

    async def _handle_for_loop(self, line: str) -> str:
        """Handle for loops (simplified)"""
        # Match: for var in items; do command; done
        for_match = re.match(r"for\s+(\w+)\s+in\s+(.*?);\s*do\s+(.*?);\s*done", line)
        if for_match:
            var_name, items_expr, command = for_match.groups()

            # Parse items
            items = shlex.split(items_expr)

            results = []
            for item in items:
                self.variables[var_name] = item
                # Don't call execute_line since it will expand variables before we set them
                # Instead, expand variables now and execute the command
                expanded_command = self._expand_variables(command)
                result = await self._execute_command(expanded_command)
                if result:
                    results.append(result)

            return "\n".join(results)

        return ""

    async def _handle_while_loop(self, line: str) -> str:
        """Handle while loops (simplified)"""
        # This is a very simplified implementation
        return ""

    async def _handle_case(self, line: str) -> str:
        """Handle case statements (simplified)"""
        # This is a very simplified implementation
        return ""

    def _handle_function_def(self, line: str) -> str:
        """Handle function definitions"""
        # This is a simplified implementation
        return ""

    async def _evaluate_condition(self, condition: str) -> bool:
        """Evaluate a test condition (simplified)"""
        condition = condition.strip()

        # File tests
        if condition.startswith("-f "):
            filepath = condition[3:].strip()
            return self.shell.fs.is_file(filepath)
        elif condition.startswith("-d "):
            dirpath = condition[3:].strip()
            return self.shell.fs.is_dir(dirpath)
        elif condition.startswith("-e "):
            path = condition[3:].strip()
            return self.shell.fs.exists(path)

        # String tests
        if "==" in condition or "=" in condition:
            parts = re.split(r"==|=", condition)
            if len(parts) == 2:
                left = self._expand_variables(parts[0].strip())
                right = self._expand_variables(parts[1].strip())
                # Remove quotes if present
                if left.startswith('"') and left.endswith('"'):
                    left = left[1:-1]
                if right.startswith('"') and right.endswith('"'):
                    right = right[1:-1]
                return left == right

        if "!=" in condition:
            parts = condition.split("!=")
            if len(parts) == 2:
                left = self._expand_variables(parts[0].strip())
                right = self._expand_variables(parts[1].strip())
                # Remove quotes if present
                if left.startswith('"') and left.endswith('"'):
                    left = left[1:-1]
                if right.startswith('"') and right.endswith('"'):
                    right = right[1:-1]
                return left != right

        # Numeric tests
        if (
            "-eq" in condition
            or "-ne" in condition
            or "-gt" in condition
            or "-lt" in condition
        ):
            # Simplified numeric comparison
            return False

        return False
