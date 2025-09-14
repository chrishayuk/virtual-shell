"""
chuk_virtual_shell/commands/filesystem/echo.py - Echo arguments command with full flag support
"""

import re
from chuk_virtual_shell.commands.command_base import ShellCommand


class EchoCommand(ShellCommand):
    name = "echo"
    help_text = """echo - Echo arguments
Usage: echo [-neE] [--help] [text] [> file | >> file]
Options:
  -n        Do not output trailing newline
  -e        Enable interpretation of backslash escapes
  -E        Disable interpretation of backslash escapes (default)
  --help    Display this help and exit"""
    category = "file"

    def execute(self, args):
        if not args:
            return ""

        # Handle --help
        if "--help" in args:
            return self.help_text

        # Parse flags
        suppress_newline = False
        enable_escapes = False
        arg_start = 0
        
        # Process flags at the beginning
        for i, arg in enumerate(args):
            if arg == '--':
                # Stop processing flags, everything after -- is text
                arg_start = i + 1
                break
            elif not arg.startswith('-'):
                # First non-flag argument
                arg_start = i
                break
            
            # Handle combined flags like -ne or individual flags
            if arg.startswith('-') and len(arg) > 1:
                for flag in arg[1:]:
                    if flag == 'n':
                        suppress_newline = True
                    elif flag == 'e':
                        enable_escapes = True
                    elif flag == 'E':
                        enable_escapes = False
                    # Ignore unknown flags silently (like real echo)
        else:
            # All arguments were flags
            arg_start = len(args)

        # Get the remaining arguments (text to echo)
        text_args = args[arg_start:]
        
        # Handle redirection
        output = ""
        redirection = None
        redirect_mode = None

        if ">" in text_args:
            redirect_index = text_args.index(">")
            output = " ".join(text_args[:redirect_index])
            redirect_mode = ">"
            if redirect_index + 1 < len(text_args):
                redirection = text_args[redirect_index + 1]

        elif ">>" in text_args:
            redirect_index = text_args.index(">>")
            output = " ".join(text_args[:redirect_index])
            redirect_mode = ">>"
            if redirect_index + 1 < len(text_args):
                redirection = text_args[redirect_index + 1]

        else:
            output = " ".join(text_args)

        # Process escape sequences if -e flag is set
        if enable_escapes:
            output = self._process_escape_sequences(output)

        # Handle redirection
        if redirection:
            # Check if trying to redirect to a directory
            if self.shell.fs.is_directory(redirection):
                return f"echo: cannot write to '{redirection}': Is a directory"
            
            if redirect_mode == ">>":
                # Append mode
                current = self.shell.fs.read_file(redirection) or ""
                final_output = current + output
            else:
                # Overwrite mode
                final_output = output
            
            if not self.shell.fs.write_file(redirection, final_output):
                return f"echo: cannot write to '{redirection}'"
            return ""

        # Return output (don't add newlines for compatibility with existing tests)
        return output

    def _process_escape_sequences(self, text):
        """Process backslash escape sequences when -e flag is enabled."""
        # Define escape sequence mappings
        escape_map = {
            '\\n': '\n',    # newline
            '\\t': '\t',    # tab
            '\\r': '\r',    # carriage return
            '\\b': '\b',    # backspace
            '\\f': '\f',    # form feed
            '\\v': '\v',    # vertical tab
            '\\a': '\a',    # alert (bell)
            '\\\\': '\\',   # backslash
            '\\"': '"',     # double quote
            "\\'": "'",     # single quote
        }
        
        # Replace basic escape sequences
        for escape, replacement in escape_map.items():
            text = text.replace(escape, replacement)
        
        # Handle octal escape sequences (\0NNN, \NNN)
        def replace_octal(match):
            octal_str = match.group(1)
            try:
                # Convert octal to character
                char_code = int(octal_str, 8)
                if 0 <= char_code <= 255:
                    return chr(char_code)
                else:
                    return match.group(0)  # Return original if out of range
            except ValueError:
                return match.group(0)  # Return original if invalid

        # Match \0NNN (up to 3 octal digits after \0)
        text = re.sub(r'\\0([0-7]{1,3})', replace_octal, text)
        # Match \NNN (up to 3 octal digits, but not starting with 0)
        text = re.sub(r'\\([1-7][0-7]{0,2})', replace_octal, text)
        
        # Handle hexadecimal escape sequences (\xHH)
        def replace_hex(match):
            hex_str = match.group(1)
            try:
                char_code = int(hex_str, 16)
                if 0 <= char_code <= 255:
                    return chr(char_code)
                else:
                    return match.group(0)  # Return original if out of range
            except ValueError:
                return match.group(0)  # Return original if invalid

        text = re.sub(r'\\x([0-9a-fA-F]{1,2})', replace_hex, text)
        
        # Handle Unicode escape sequences (\uHHHH, \UHHHHHHHH)
        def replace_unicode(match):
            hex_str = match.group(1)
            try:
                char_code = int(hex_str, 16)
                return chr(char_code)
            except (ValueError, OverflowError):
                return match.group(0)  # Return original if invalid

        # \uHHHH (4 hex digits)
        text = re.sub(r'\\u([0-9a-fA-F]{4})', replace_unicode, text)
        # \UHHHHHHHH (8 hex digits)
        text = re.sub(r'\\U([0-9a-fA-F]{8})', replace_unicode, text)
        
        return text