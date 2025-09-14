# src/chuk_virtual_shell/commands/text/awk.py
"""
chuk_virtual_shell/commands/text/awk.py - Pattern scanning and processing language
"""

import re
from chuk_virtual_shell.commands.command_base import ShellCommand


class AwkCommand(ShellCommand):
    name = "awk"
    help_text = """awk - Pattern scanning and processing language
Usage: awk [OPTIONS] 'PROGRAM' [FILE]...
Options:
  -F fs        Field separator (default: space/tab)
  -v var=val   Set variable
Common patterns:
  '{print}'           Print all lines
  '{print $1}'        Print first field
  '{print $1,$3}'     Print fields 1 and 3
  '{print NF}'        Print number of fields
  '{print NR}'        Print line number
  '/pattern/'         Lines matching pattern
  '$1=="value"'       Field 1 equals value
  'NR==1'            First line only
  'BEGIN{...}'        Execute before processing
  'END{...}'          Execute after processing
  '{sum+=$1} END{print sum}'  Sum column"""
    category = "text"

    def execute(self, args):
        if not args:
            return "awk: missing program"

        # Parse options
        field_separator = None
        variables = {}
        program = None
        files = []
        i = 0

        # Parse arguments
        while i < len(args):
            arg = args[i]
            if arg == "-F":
                if i + 1 < len(args):
                    field_separator = args[i + 1]
                    i += 1
                else:
                    return "awk: option requires an argument -- 'F'"
            elif arg.startswith("-F"):
                # Handle -F with value attached (e.g., -F, or -F:)
                field_separator = arg[2:]  # Everything after -F
            elif arg == "-v":
                if i + 1 < len(args):
                    var_assignment = args[i + 1]
                    if "=" in var_assignment:
                        var_name, var_value = var_assignment.split("=", 1)
                        variables[var_name] = var_value
                    i += 1
                else:
                    return "awk: option requires an argument -- 'v'"
            elif not program:
                # The first non-option argument is the program
                # AWK programs typically start with { or / or contain these characters
                program = arg
            else:
                # All remaining arguments are files
                files.append(arg)
            i += 1

        if not program:
            return "awk: missing program"

        # Default field separator
        if field_separator is None:
            field_separator = r"[ \t]+"

        # If no files specified, use stdin
        if not files:
            if hasattr(self.shell, "_stdin_buffer") and self.shell._stdin_buffer:
                content = self.shell._stdin_buffer
                return self._process_content(
                    content, program, field_separator, variables
                )
            elif "BEGIN" in program or "END" in program:
                # Allow BEGIN/END only programs without input
                return self._process_content("", program, field_separator, variables)
            else:
                return "awk: no input files"

        # Process files
        all_lines = []
        for filepath in files:
            content = self.shell.fs.read_file(filepath)
            if content is None:
                return f"awk: {filepath}: No such file or directory"
            all_lines.extend(content.splitlines())

        return self._process_content(
            "\n".join(all_lines), program, field_separator, variables
        )

    def _process_content(self, content, program, field_separator, variables):
        """Process content with awk program"""
        lines = content.splitlines() if content else []
        output = []

        # Parse program into BEGIN, main, and END sections
        begin_code = ""
        end_code = ""
        main_pattern = ""
        main_action = ""

        # Extract BEGIN block with proper brace matching
        begin_match = re.search(r"BEGIN\s*{", program)
        if begin_match:
            start = begin_match.end() - 1  # Position of opening brace
            brace_count = 0
            end = start
            for i in range(start, len(program)):
                if program[i] == "{":
                    brace_count += 1
                elif program[i] == "}":
                    brace_count -= 1
                    if brace_count == 0:
                        end = i
                        break
            begin_code = program[start + 1 : end]
            program = program[: begin_match.start()] + program[end + 1 :]
            program = program.strip()

        # Extract END block with proper brace matching
        end_match = re.search(r"END\s*{", program)
        if end_match:
            start = end_match.end() - 1  # Position of opening brace
            brace_count = 0
            end = start
            for i in range(start, len(program)):
                if program[i] == "{":
                    brace_count += 1
                elif program[i] == "}":
                    brace_count -= 1
                    if brace_count == 0:
                        end = i
                        break
            end_code = program[start + 1 : end]
            program = program[: end_match.start()] + program[end + 1 :]
            program = program.strip()

        # Parse main program
        if program:
            # Check for pattern{action} format
            pattern_action = re.match(
                r'^(/[^/]+/|\$\d+[=!<>]+["\']?[^"\']*["\']?|NR[=!<>]+\d+)?\s*{([^}]*)}',
                program,
            )
            if pattern_action:
                main_pattern = pattern_action.group(1) or ""
                main_action = pattern_action.group(2)
            elif program.startswith("{") and program.endswith("}"):
                main_action = program[1:-1]
            elif program.startswith("/") and program.endswith("/"):
                main_pattern = program
                main_action = "print"
            else:
                # Assume it's just an action
                main_action = program

        # Initialize AWK variables
        awk_vars = {
            "NF": 0,  # Number of fields
            "NR": 0,  # Number of records (lines)
            "FS": field_separator,  # Field separator
            "OFS": " ",  # Output field separator
            "sum": 0,  # Common variable for summing
            "count": 0,  # Common variable for counting
        }
        awk_vars.update(variables)

        # Execute BEGIN block
        if begin_code:
            # Check if BEGIN block contains for-in loop
            if "for(" in begin_code or "for (" in begin_code:
                self._execute_for_in_loop(begin_code, {}, awk_vars, output)
            else:
                self._execute_action(begin_code, {}, awk_vars, output)

        # Process each line
        for line_num, line in enumerate(lines, 1):
            awk_vars["NR"] = line_num

            # Split line into fields
            if field_separator == r"[ \t]+" or field_separator == " ":
                fields = line.split()
            else:
                try:
                    fields = re.split(field_separator, line)
                except re.error:
                    # If regex fails, fall back to string split
                    fields = line.split(field_separator)

            # AWK fields are 1-indexed, $0 is the whole line
            field_vars = {"0": line}
            for i, field in enumerate(fields, 1):
                field_vars[str(i)] = field

            awk_vars["NF"] = len(fields)

            # Check if pattern matches
            if not main_pattern or self._match_pattern(
                main_pattern, line, field_vars, awk_vars
            ):
                if main_action:
                    self._execute_action(main_action, field_vars, awk_vars, output)

        # Execute END block
        if end_code:
            # Handle for-in loops in END block
            if "for(" in end_code or "for (" in end_code:
                self._execute_for_in_loop(end_code, {}, awk_vars, output)
            else:
                self._execute_action(end_code, {}, awk_vars, output)

        return "\n".join(output)

    def _execute_for_in_loop(self, code, fields, variables, output):
        """Execute for-in loop for associative arrays"""
        import re

        # First, we need to execute any statements before the for loop
        # This includes array assignments
        statements = code.split(";")

        for statement in statements:
            statement = statement.strip()
            if not statement:
                continue

            # Check if this is a for-in loop
            if "for(" in statement or "for (" in statement:
                # Parse for(var in array) { actions }
                for_pattern = r"for\s*\(\s*(\w+)\s+in\s+(\w+)\s*\)\s*(.+)"
                match = re.search(for_pattern, statement)

                if match:
                    loop_var = match.group(1)
                    array_name = match.group(2)
                    rest = match.group(3).strip()

                    # Extract loop body
                    if rest.startswith("{"):
                        # Find matching closing brace
                        brace_count = 0
                        loop_body = ""
                        for i, char in enumerate(rest):
                            if char == "{":
                                brace_count += 1
                            elif char == "}":
                                brace_count -= 1
                                if brace_count == 0:
                                    loop_body = rest[1:i].strip()
                                    break
                    else:
                        # Single statement without braces
                        loop_body = rest

                    # Check if the array exists in variables
                    if array_name in variables and isinstance(
                        variables[array_name], dict
                    ):
                        # Iterate over the associative array
                        for key in variables[array_name]:
                            # Set the loop variable
                            variables[loop_var] = key

                            # Execute the loop body
                            self._execute_action(loop_body, fields, variables, output)
            else:
                # Execute non-loop statement (like array assignments)
                self._execute_action(statement, fields, variables, output)

    def _match_pattern(self, pattern, line, fields, variables):
        """Check if pattern matches the current line"""
        if not pattern:
            return True

        # Regular expression pattern
        if pattern.startswith("/") and pattern.endswith("/"):
            regex = pattern[1:-1]
            return bool(re.search(regex, line))

        # Field comparison: $1=="value"
        field_match = re.match(r'\$(\d+)\s*([=!<>]+)\s*["\']?([^"\']*)["\']?', pattern)
        if field_match:
            field_num, operator, value = field_match.groups()
            field_value = fields.get(field_num, "")

            if operator == "==":
                return field_value == value
            elif operator == "!=":
                return field_value != value
            elif operator == ">":
                try:
                    return float(field_value) > float(value)
                except ValueError:
                    return field_value > value
            elif operator == "<":
                try:
                    return float(field_value) < float(value)
                except ValueError:
                    return field_value < value

        # Line number comparison: NR==1
        nr_match = re.match(r"NR\s*([=!<>]+)\s*(\d+)", pattern)
        if nr_match:
            operator, value = nr_match.groups()
            nr = variables["NR"]
            value = int(value)

            if operator == "==":
                return nr == value
            elif operator == "!=":
                return nr != value
            elif operator == ">":
                return nr > value
            elif operator == "<":
                return nr < value

        return False

    def _execute_action(self, action, fields, variables, output):
        """Execute an AWK action"""
        action = action.strip()

        # Handle multiple statements separated by semicolon
        if ";" in action:
            statements = action.split(";")
            for statement in statements:
                self._execute_action(statement.strip(), fields, variables, output)
            return

        # Handle printf statements
        if action.startswith("printf"):
            printf_args = action[6:].strip()

            # Parse printf arguments
            import re

            # Find the format string and arguments
            if printf_args.startswith('"'):
                # Extract format string handling escaped quotes
                i = 1
                end_quote = -1
                while i < len(printf_args):
                    if printf_args[i] == "\\" and i + 1 < len(printf_args):
                        i += 2  # Skip escaped character
                    elif printf_args[i] == '"':
                        end_quote = i
                        break
                    else:
                        i += 1

                if end_quote == -1:
                    # No closing quote found, treat whole thing as format string
                    format_str = printf_args[1:]
                    remaining = ""
                else:
                    format_str = printf_args[1:end_quote]
                    remaining = printf_args[end_quote + 1 :].strip()

                # Handle escaped quotes in format string
                # Handle bash-style single quote escaping '\''
                format_str = format_str.replace("'\\''", "'")
                format_str = format_str.replace("\\'", "'")
                format_str = format_str.replace('\\"', '"')

                # Parse arguments after format string
                args = []
                if remaining.startswith(","):
                    remaining = remaining[1:].strip()
                    # Split arguments by comma
                    parts = remaining.split(",")
                    for part in parts:
                        part = part.strip()
                        # Evaluate each argument
                        if part.startswith("$"):
                            # Field reference
                            field_num = part[1:]
                            if field_num.isdigit():
                                args.append(fields.get(field_num, ""))
                        elif part.startswith('"') and part.endswith('"'):
                            # String literal
                            args.append(part[1:-1])
                        elif part in variables:
                            # Variable reference
                            args.append(variables[part])
                        else:
                            # Try to evaluate as number or expression
                            try:
                                args.append(eval(part, {"__builtins__": {}}, variables))
                            except Exception:
                                args.append(part)

                # Format the output
                try:
                    # Handle different format specifiers
                    formatted = format_str

                    # Simple replacement for common formats
                    import re

                    format_specs = re.findall(
                        r"%[-+0 #]*\*?(?:\d+|\*)?(?:\.(?:\d+|\*))?[hlL]?[diouxXeEfFgGcrsa%]",
                        format_str,
                    )

                    for i, spec in enumerate(format_specs):
                        if i < len(args):
                            arg = args[i]
                            if spec == "%s":
                                formatted = formatted.replace(spec, str(arg), 1)
                            elif spec == "%d" or spec == "%i":
                                formatted = formatted.replace(
                                    spec, str(int(float(str(arg)))), 1
                                )
                            elif spec == "%f":
                                formatted = formatted.replace(spec, str(float(arg)), 1)
                            elif spec.startswith("%") and "f" in spec:
                                # Handle precision formats like %.2f
                                match = re.match(r"%(\d*\.?\d*)f", spec)
                                if match:
                                    precision = match.group(1)
                                    if "." in precision:
                                        dec_places = int(precision.split(".")[1])
                                        formatted = formatted.replace(
                                            spec, f"{float(arg):.{dec_places}f}", 1
                                        )
                                    else:
                                        formatted = formatted.replace(
                                            spec, str(float(arg)), 1
                                        )
                            elif spec.startswith("%") and "d" in spec:
                                # Handle width formats like %3d
                                match = re.match(r"%(\d+)d", spec)
                                if match:
                                    width = int(match.group(1))
                                    formatted = formatted.replace(
                                        spec, str(int(float(str(arg)))).rjust(width), 1
                                    )
                            else:
                                formatted = formatted.replace(spec, str(arg), 1)

                    # Don't add newline for printf (unlike print)
                    output.append(formatted)
                except Exception:
                    output.append(format_str % tuple(args) if args else format_str)
            return

        # Handle print statements
        elif action.startswith("print"):
            print_args = action[5:].strip()

            if not print_args:
                # Print whole line
                if "0" in fields:
                    output.append(fields["0"])
                else:
                    output.append("")
            else:
                # Parse print arguments
                result = []

                # Handle string literals and expressions
                import re

                # Parse print arguments more intelligently
                # Handle space-separated items with string literals properly
                parts = []
                current = ""
                in_quotes = False
                i = 0

                while i < len(print_args):
                    char = print_args[i]

                    if char == '"':
                        # Start or end of string literal
                        if not in_quotes:
                            # Starting a string literal
                            if current.strip():
                                # Save any accumulated non-quoted content
                                parts.append(current.strip())
                                current = ""
                            in_quotes = True
                            current = '"'
                        else:
                            # Ending a string literal
                            current += '"'
                            parts.append(current)
                            current = ""
                            in_quotes = False
                    elif char == " " and not in_quotes:
                        # Space outside quotes - separator
                        if current.strip():
                            parts.append(current.strip())
                            current = ""
                    elif char == "," and not in_quotes:
                        # Comma separator (for compatibility)
                        if current.strip():
                            parts.append(current.strip())
                            current = ""
                    else:
                        current += char

                    i += 1

                # Add any remaining content
                if current.strip():
                    parts.append(current.strip())

                list(re.findall(r'"([^"]*)"', print_args)) if '"' in print_args else []

                for part in parts:
                    part = part.strip()

                    # String literal
                    if part.startswith('"') and part.endswith('"'):
                        result.append(part[1:-1])
                    # Field reference: $1, $2, etc.
                    elif part.startswith("$"):
                        field_num = part[1:]
                        if field_num.isdigit():
                            result.append(fields.get(field_num, ""))
                    # Number literal
                    elif part.replace(".", "").replace("-", "").isdigit():
                        result.append(part)
                    # Expression with operators
                    elif any(op in part for op in ["+", "-", "*", "/", "%"]):
                        # Simple expression evaluation
                        try:
                            # Replace variables with their values
                            expr = part
                            for var, val in variables.items():
                                expr = expr.replace(var, str(val))
                            # Safely evaluate the expression
                            if "/" in expr and "count" in variables:
                                # Handle division operations
                                value = eval(expr, {"__builtins__": {}}, variables)
                            else:
                                value = eval(expr, {"__builtins__": {}}, {})
                            result.append(str(value))
                        except Exception:
                            # If evaluation fails, try to output the expression literally
                            result.append(part)
                    # Array element reference: array[key]
                    elif "[" in part and "]" in part:
                        import re

                        array_match = re.match(r"(\w+)\[([^\]]+)\]", part)
                        if array_match:
                            array_name = array_match.group(1)
                            key = array_match.group(2).strip()

                            # Process key
                            if key.startswith('"') and key.endswith('"'):
                                key = key[1:-1]
                            elif key in variables:
                                key = str(variables[key])

                            # Get value from array
                            if array_name in variables and isinstance(
                                variables[array_name], dict
                            ):
                                if key in variables[array_name]:
                                    result.append(str(variables[array_name][key]))
                                else:
                                    result.append("")
                            else:
                                result.append("")
                    # Variable reference: NF, NR, sum
                    elif part in variables:
                        val = variables[part]
                        if isinstance(val, dict):
                            # Don't print dict directly
                            pass
                        else:
                            result.append(str(val))

                output.append(variables.get("OFS", " ").join(result))

        # Handle variable operations
        elif "++" in action:
            # Variable increment: count++
            var_name = action.replace("++", "").strip()
            variables[var_name] = variables.get(var_name, 0) + 1
        elif "+=" in action:
            # Check for array increment like array[key]+=$1
            if "[" in action and "]" in action:
                import re

                array_match = re.match(r"(\w+)\[([^\]]+)\]\s*\+=\s*(.+)", action)
                if array_match:
                    array_name = array_match.group(1)
                    key = array_match.group(2).strip()
                    expr = array_match.group(3).strip()

                    # Process key
                    if key.startswith('"') and key.endswith('"'):
                        key = key[1:-1]
                    elif key.startswith("$"):
                        field_num = key[1:]
                        if field_num.isdigit():
                            key = fields.get(field_num, "")

                    # Initialize array if needed
                    if array_name not in variables:
                        variables[array_name] = {}
                    if not isinstance(variables[array_name], dict):
                        variables[array_name] = {}

                    # Evaluate expression
                    value = 0
                    if expr.startswith("$"):
                        field_num = expr[1:]
                        if field_num.isdigit():
                            try:
                                value = float(fields.get(field_num, "0"))
                            except ValueError:
                                value = 0
                    else:
                        try:
                            value = float(expr)
                        except ValueError:
                            value = 0

                    # Increment the array element
                    if key not in variables[array_name]:
                        variables[array_name][key] = 0
                    variables[array_name][key] = (
                        variables[array_name].get(key, 0) + value
                    )
                    return

            # Regular variable increment: sum+=$1
            var_name, expr = action.split("+=", 1)
            var_name = var_name.strip()
            expr = expr.strip()

            # Evaluate expression
            if expr.startswith("$"):
                field_num = expr[1:]
                if field_num.isdigit():
                    value = fields.get(field_num, "0")
                    try:
                        variables[var_name] = variables.get(var_name, 0) + float(value)
                    except ValueError:
                        pass

        # Handle simple variable assignment
        elif "=" in action and not any(op in action for op in ["==", "!=", ">=", "<="]):
            # Check for array assignment like array[key]=value
            if "[" in action and "]" in action:
                import re

                array_match = re.match(r"(\w+)\[([^\]]+)\]\s*=\s*(.+)", action)
                if array_match:
                    array_name = array_match.group(1)
                    key = array_match.group(2).strip()
                    value = array_match.group(3).strip()

                    # Remove quotes from key if present
                    if key.startswith('"') and key.endswith('"'):
                        key = key[1:-1]
                    elif key.startswith("$"):
                        # Field reference as key
                        field_num = key[1:]
                        if field_num.isdigit():
                            key = fields.get(field_num, "")

                    # Initialize array if it doesn't exist
                    if array_name not in variables:
                        variables[array_name] = {}
                    if not isinstance(variables[array_name], dict):
                        variables[array_name] = {}

                    # Process value
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif any(op in value for op in ["+", "-", "*", "/", "%"]):
                        # Evaluate arithmetic expression
                        try:
                            expr = value
                            for i in range(20):
                                field_ref = f"${i}"
                                if field_ref in expr:
                                    expr = expr.replace(
                                        field_ref, str(fields.get(str(i), 0))
                                    )
                            for var, val in variables.items():
                                if not isinstance(val, dict):
                                    expr = expr.replace(var, str(val))
                            value = eval(expr, {"__builtins__": {}}, {})
                        except Exception:
                            pass

                    # Store in associative array
                    variables[array_name][key] = value
                    return

            # Regular variable assignment
            var_name, value = action.split("=", 1)
            var_name = var_name.strip()
            value = value.strip()

            # Remove quotes if present
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            # Evaluate arithmetic expressions
            elif any(op in value for op in ["+", "-", "*", "/", "%"]):
                try:
                    # Replace field references with their values
                    expr = value
                    for i in range(20):  # Support up to $20
                        field_ref = f"${i}"
                        if field_ref in expr:
                            expr = expr.replace(field_ref, str(fields.get(str(i), 0)))
                    # Replace variables with their values
                    for var, val in variables.items():
                        expr = expr.replace(var, str(val))
                    # Evaluate the expression
                    value = eval(expr, {"__builtins__": {}}, {})
                except Exception:
                    pass  # Keep original value if evaluation fails

            variables[var_name] = value
