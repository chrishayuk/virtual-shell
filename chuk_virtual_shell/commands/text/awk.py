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
            if arg == '-F':
                if i + 1 < len(args):
                    field_separator = args[i + 1]
                    i += 1
                else:
                    return "awk: option requires an argument -- 'F'"
            elif arg == '-v':
                if i + 1 < len(args):
                    var_assignment = args[i + 1]
                    if '=' in var_assignment:
                        var_name, var_value = var_assignment.split('=', 1)
                        variables[var_name] = var_value
                    i += 1
                else:
                    return "awk: option requires an argument -- 'v'"
            elif not program:
                program = arg
            else:
                files.append(arg)
            i += 1
        
        if not program:
            return "awk: missing program"
        
        # Default field separator
        if field_separator is None:
            field_separator = r'[ \t]+'
        
        # If no files specified, use stdin
        if not files:
            if hasattr(self.shell, '_stdin_buffer') and self.shell._stdin_buffer:
                content = self.shell._stdin_buffer
                return self._process_content(content, program, field_separator, variables)
            else:
                return "awk: no input files"
        
        # Process files
        all_lines = []
        for filepath in files:
            content = self.shell.fs.read_file(filepath)
            if content is None:
                return f"awk: {filepath}: No such file or directory"
            all_lines.extend(content.splitlines())
        
        return self._process_content('\n'.join(all_lines), program, field_separator, variables)
    
    def _process_content(self, content, program, field_separator, variables):
        """Process content with awk program"""
        lines = content.splitlines() if content else []
        output = []
        
        # Parse program into BEGIN, main, and END sections
        begin_code = ""
        end_code = ""
        main_pattern = ""
        main_action = ""
        
        # Extract BEGIN block
        begin_match = re.search(r'BEGIN\s*{([^}]*)}', program)
        if begin_match:
            begin_code = begin_match.group(1)
            program = program.replace(begin_match.group(0), '').strip()
        
        # Extract END block
        end_match = re.search(r'END\s*{([^}]*)}', program)
        if end_match:
            end_code = end_match.group(1)
            program = program.replace(end_match.group(0), '').strip()
        
        # Parse main program
        if program:
            # Check for pattern{action} format
            pattern_action = re.match(r'^(/[^/]+/|\$\d+[=!<>]+["\']?[^"\']*["\']?|NR[=!<>]+\d+)?\s*{([^}]*)}', program)
            if pattern_action:
                main_pattern = pattern_action.group(1) or ""
                main_action = pattern_action.group(2)
            elif program.startswith('{') and program.endswith('}'):
                main_action = program[1:-1]
            elif program.startswith('/') and program.endswith('/'):
                main_pattern = program
                main_action = "print"
            else:
                # Assume it's just an action
                main_action = program
        
        # Initialize AWK variables
        awk_vars = {
            'NF': 0,  # Number of fields
            'NR': 0,  # Number of records (lines)
            'FS': field_separator,  # Field separator
            'OFS': ' ',  # Output field separator
            'sum': 0,  # Common variable for summing
        }
        awk_vars.update(variables)
        
        # Execute BEGIN block
        if begin_code:
            self._execute_action(begin_code, [], awk_vars, output)
        
        # Process each line
        for line_num, line in enumerate(lines, 1):
            awk_vars['NR'] = line_num
            
            # Split line into fields
            if field_separator == ' ':
                fields = line.split()
            else:
                fields = re.split(field_separator, line)
            
            # AWK fields are 1-indexed, $0 is the whole line
            field_vars = {'0': line}
            for i, field in enumerate(fields, 1):
                field_vars[str(i)] = field
            
            awk_vars['NF'] = len(fields)
            
            # Check if pattern matches
            if self._match_pattern(main_pattern, line, field_vars, awk_vars):
                if main_action:
                    self._execute_action(main_action, field_vars, awk_vars, output)
        
        # Execute END block
        if end_code:
            self._execute_action(end_code, {}, awk_vars, output)
        
        return '\n'.join(output)
    
    def _match_pattern(self, pattern, line, fields, variables):
        """Check if pattern matches the current line"""
        if not pattern:
            return True
        
        # Regular expression pattern
        if pattern.startswith('/') and pattern.endswith('/'):
            regex = pattern[1:-1]
            return bool(re.search(regex, line))
        
        # Field comparison: $1=="value"
        field_match = re.match(r'\$(\d+)\s*([=!<>]+)\s*["\']?([^"\']*)["\']?', pattern)
        if field_match:
            field_num, operator, value = field_match.groups()
            field_value = fields.get(field_num, '')
            
            if operator == '==':
                return field_value == value
            elif operator == '!=':
                return field_value != value
            elif operator == '>':
                try:
                    return float(field_value) > float(value)
                except ValueError:
                    return field_value > value
            elif operator == '<':
                try:
                    return float(field_value) < float(value)
                except ValueError:
                    return field_value < value
        
        # Line number comparison: NR==1
        nr_match = re.match(r'NR\s*([=!<>]+)\s*(\d+)', pattern)
        if nr_match:
            operator, value = nr_match.groups()
            nr = variables['NR']
            value = int(value)
            
            if operator == '==':
                return nr == value
            elif operator == '!=':
                return nr != value
            elif operator == '>':
                return nr > value
            elif operator == '<':
                return nr < value
        
        return False
    
    def _execute_action(self, action, fields, variables, output):
        """Execute an AWK action"""
        action = action.strip()
        
        # Handle print statements
        if action.startswith('print'):
            print_args = action[5:].strip()
            
            if not print_args:
                # Print whole line
                if '0' in fields:
                    output.append(fields['0'])
            else:
                # Parse print arguments
                result = []
                
                # Split by comma (field separator in output)
                parts = print_args.split(',')
                
                for part in parts:
                    part = part.strip()
                    
                    # Field reference: $1, $2, etc.
                    if part.startswith('$'):
                        field_num = part[1:]
                        if field_num.isdigit():
                            result.append(fields.get(field_num, ''))
                    # String literal
                    elif part.startswith('"') and part.endswith('"'):
                        result.append(part[1:-1])
                    # Number literal
                    elif part.replace('.', '').replace('-', '').isdigit():
                        result.append(part)
                    # Expression with operators
                    elif any(op in part for op in ['+', '-', '*', '/', '%']):
                        # Simple expression evaluation
                        try:
                            # Replace variables with their values
                            expr = part
                            for var, val in variables.items():
                                expr = expr.replace(var, str(val))
                            # Safely evaluate the expression
                            value = eval(expr, {"__builtins__": {}}, {})
                            result.append(str(value))
                        except:
                            result.append(part)
                    # Variable reference: NF, NR, sum
                    elif part in variables:
                        result.append(str(variables[part]))
                
                output.append(variables.get('OFS', ' ').join(result))
        
        # Handle variable operations
        elif '+=' in action:
            # Variable increment: sum+=$1
            var_name, expr = action.split('+=', 1)
            var_name = var_name.strip()
            expr = expr.strip()
            
            # Evaluate expression
            if expr.startswith('$'):
                field_num = expr[1:]
                if field_num.isdigit():
                    value = fields.get(field_num, '0')
                    try:
                        variables[var_name] = variables.get(var_name, 0) + float(value)
                    except ValueError:
                        pass
        
        # Handle simple variable assignment
        elif '=' in action and not any(op in action for op in ['==', '!=', '>=', '<=']):
            var_name, value = action.split('=', 1)
            var_name = var_name.strip()
            value = value.strip()
            
            # Remove quotes if present
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            
            variables[var_name] = value