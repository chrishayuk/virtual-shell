"""
chuk_virtual_shell/commands/filesystem/cat.py - Display file contents command
"""

from chuk_virtual_shell.commands.command_base import ShellCommand


class CatCommand(ShellCommand):
    name = "cat"
    help_text = """cat - Display file contents
Usage: cat [OPTION]... [FILE]...
Options:
  -n        Number all output lines
  -b        Number non-blank output lines
  -s        Squeeze multiple adjacent blank lines
  -E        Display $ at end of each line
  -T        Display TAB characters as ^I
  -v        Display non-printing characters
  --help    Display this help and exit"""
    category = "file"

    def execute(self, args):
        # Parse options
        number_lines = False
        number_nonblank = False
        squeeze_blank = False
        show_ends = False
        show_tabs = False
        show_nonprinting = False
        
        files = []
        i = 0
        while i < len(args):
            arg = args[i]
            if arg.startswith("-") and arg != "-":
                if arg == "--help":
                    return self.help_text
                elif arg == "--":
                    # End of options
                    files.extend(args[i+1:])
                    break
                else:
                    # Process flags (can be combined like -nE)
                    for flag in arg[1:]:
                        if flag == "n":
                            number_lines = True
                        elif flag == "b":
                            number_nonblank = True
                            number_lines = False  # -b overrides -n
                        elif flag == "s":
                            squeeze_blank = True
                        elif flag == "E":
                            show_ends = True
                        elif flag == "T":
                            show_tabs = True
                        elif flag == "v":
                            show_nonprinting = True
                        else:
                            return f"cat: invalid option -- '{flag}'"
            else:
                files.append(arg)
            i += 1

        # Check if we have stdin input (from input redirection or pipe)
        if not files:
            # If no arguments, read from stdin if available
            if hasattr(self.shell, "_stdin_buffer") and self.shell._stdin_buffer:
                content = self.shell._stdin_buffer
                # Clear the buffer after use
                self.shell._stdin_buffer = None
                return self._process_content(content, number_lines, number_nonblank, 
                                            squeeze_blank, show_ends, show_tabs, 
                                            show_nonprinting)
            return "cat: missing operand"

        result = []
        errors = []
        line_number = 1
        nonblank_number = 1
        
        for path in files:
            # Check if path is a directory
            if self.shell.fs.is_dir(path):
                errors.append(f"cat: {path}: Is a directory")
                continue
                
            content = self.shell.fs.read_file(path)
            if content is None:
                errors.append(f"cat: {path}: No such file or directory")
                continue
            
            # Process content with flags
            processed = self._process_content_with_state(
                content, number_lines, number_nonblank, squeeze_blank,
                show_ends, show_tabs, show_nonprinting,
                line_number, nonblank_number
            )
            result.append(processed[0])
            line_number = processed[1]
            nonblank_number = processed[2]

        # Combine results and errors
        output = "".join(result)
        if errors:
            if output:
                # If we have both content and errors, show content first then errors
                return output + "\n".join(errors)
            else:
                # Only errors
                return "\n".join(errors)
        return output
    
    def _process_content(self, content, number_lines, number_nonblank, 
                         squeeze_blank, show_ends, show_tabs, show_nonprinting):
        """Process content with flags (for stdin)"""
        result, _, _ = self._process_content_with_state(
            content, number_lines, number_nonblank, squeeze_blank,
            show_ends, show_tabs, show_nonprinting, 1, 1
        )
        return result
    
    def _process_content_with_state(self, content, number_lines, number_nonblank,
                                   squeeze_blank, show_ends, show_tabs, 
                                   show_nonprinting, line_num, nonblank_num):
        """Process content with flags and maintain line numbering state"""
        if not any([number_lines, number_nonblank, squeeze_blank, 
                   show_ends, show_tabs, show_nonprinting]):
            return content, line_num, nonblank_num
        
        lines = content.split('\n')
        result_lines = []
        prev_blank = False
        
        for i, line in enumerate(lines):
            is_blank = line.strip() == ""
            
            # Handle squeeze blank
            if squeeze_blank and is_blank and prev_blank:
                continue
            
            # Process line content
            processed_line = line
            
            # Show tabs
            if show_tabs:
                processed_line = processed_line.replace('\t', '^I')
            
            # Show non-printing characters
            if show_nonprinting:
                processed_line = self._make_visible(processed_line)
            
            # Add line number
            if number_lines:
                processed_line = f"     {line_num}\t{processed_line}"
                line_num += 1
            elif number_nonblank and not is_blank:
                processed_line = f"     {nonblank_num}\t{processed_line}"
                nonblank_num += 1
            
            # Show ends
            if show_ends:
                processed_line = processed_line + "$"
            
            result_lines.append(processed_line)
            prev_blank = is_blank
        
        # Join lines back together
        result = '\n'.join(result_lines)
        if content.endswith('\n') and not result.endswith('\n'):
            result += '\n'
        
        return result, line_num, nonblank_num
    
    def _make_visible(self, text):
        """Make non-printing characters visible"""
        result = []
        for char in text:
            if char == '\t':
                result.append('^I')
            elif char == '\n':
                result.append(char)
            elif ord(char) < 32:
                # Control characters
                result.append(f'^{chr(ord(char) + 64)}')
            elif ord(char) == 127:
                result.append('^?')
            elif ord(char) > 127:
                # High-bit characters
                result.append(f'M-{chr(ord(char) - 128)}')
            else:
                result.append(char)
        return ''.join(result)
