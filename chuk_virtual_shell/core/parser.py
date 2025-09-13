# chuk_virtual_shell/core/parser.py
"""
chuk_virtual_shell/core/parser.py - Command line parsing utilities

Handles parsing of command lines, checking for quotes, and splitting
commands into components.
"""

import shlex
from typing import Tuple, Optional, List, Dict


class CommandParser:
    """Handles command line parsing and analysis."""
    
    @staticmethod
    def parse_command(cmd_line: str) -> Tuple[Optional[str], List[str]]:
        """
        Parse a command line into the command name and arguments.
        
        Args:
            cmd_line: Raw command line string
            
        Returns:
            Tuple of (command_name, arguments_list) or (None, []) if empty
        """
        if not cmd_line or not cmd_line.strip():
            return None, []
        
        try:
            parts = shlex.split(cmd_line.strip())
        except ValueError:
            # Fallback to simple split if shlex fails (e.g., unclosed quotes)
            parts = cmd_line.strip().split()
        
        if not parts:
            return None, []
        
        return parts[0], parts[1:]
    
    @staticmethod
    def is_quoted(text: str, position: int) -> bool:
        """
        Check if a position in text is within quotes.
        
        Args:
            text: Text to check
            position: Position to check
            
        Returns:
            True if position is within quotes, False otherwise
        """
        in_single = False
        in_double = False
        escaped = False
        
        for i, char in enumerate(text):
            if i >= position:
                return in_single or in_double
            
            if escaped:
                escaped = False
                continue
            
            if char == "\\":
                escaped = True
            elif char == '"' and not in_single:
                in_double = not in_double
            elif char == "'" and not in_double:
                in_single = not in_single
        
        return False
    
    @staticmethod
    def contains_quoted_operator(cmd_line: str) -> bool:
        """
        Check if logical operators or semicolons are within quotes.
        
        Args:
            cmd_line: Command line to check
            
        Returns:
            True if any operators are quoted, False otherwise
        """
        parser = CommandParser()
        for op in ["&&", "||", ";"]:
            if op in cmd_line:
                idx = cmd_line.index(op)
                if parser.is_quoted(cmd_line, idx):
                    return True
        return False
    
    @staticmethod
    def parse_redirection(cmd_line: str) -> Dict:
        """
        Parse input/output redirection from command line.
        
        Args:
            cmd_line: Command line possibly containing redirection
            
        Returns:
            Dictionary with:
                - 'command': The command without redirection
                - 'input': Input file path or None
                - 'output': Output file path or None
                - 'append': Boolean indicating append mode
        """
        result = {
            'command': cmd_line,
            'input': None,
            'output': None,
            'append': False
        }
        
        parser = CommandParser()
        
        # First, handle input redirection (<)
        if "<" in cmd_line:
            pos = cmd_line.index("<")
            if not parser.is_quoted(cmd_line, pos):
                # Split command and input file
                cmd_part = cmd_line[:pos].strip()
                input_part = cmd_line[pos + 1:].strip()
                
                # Check if there's also output redirection after input
                if ">>" in input_part:
                    pos2 = input_part.index(">>")
                    if not parser.is_quoted(input_part, pos2):
                        result['input'] = input_part[:pos2].strip()
                        result['output'] = input_part[pos2 + 2:].strip()
                        result['append'] = True
                elif ">" in input_part:
                    pos2 = input_part.index(">")
                    if not parser.is_quoted(input_part, pos2):
                        result['input'] = input_part[:pos2].strip()
                        result['output'] = input_part[pos2 + 1:].strip()
                        result['append'] = False
                else:
                    result['input'] = input_part
                
                # Parse the input file (might be quoted)
                if result['input']:
                    try:
                        parts = shlex.split(result['input'])
                        if parts:
                            result['input'] = parts[0]
                            result['command'] = cmd_part
                    except ValueError:
                        result['input'] = None
                
                # Parse output file if present
                if result['output']:
                    try:
                        parts = shlex.split(result['output'])
                        if parts:
                            result['output'] = parts[0]
                    except ValueError:
                        result['output'] = None
        
        # If no input redirection, check for output redirection only
        if not result['input']:
            # Look for >> first (append mode)
            if ">>" in result['command']:
                pos = result['command'].index(">>")
                if not parser.is_quoted(result['command'], pos):
                    cmd_part = result['command'][:pos].strip()
                    redirect_part = result['command'][pos + 2:].strip()
                    if redirect_part:
                        try:
                            parts = shlex.split(redirect_part)
                            if parts:
                                result['output'] = parts[0]
                                result['append'] = True
                                result['command'] = cmd_part
                        except ValueError:
                            pass
            # Look for > (overwrite mode)
            elif ">" in result['command']:
                pos = result['command'].index(">")
                if not parser.is_quoted(result['command'], pos):
                    cmd_part = result['command'][:pos].strip()
                    redirect_part = result['command'][pos + 1:].strip()
                    if redirect_part:
                        try:
                            parts = shlex.split(redirect_part)
                            if parts:
                                result['output'] = parts[0]
                                result['append'] = False
                                result['command'] = cmd_part
                        except ValueError:
                            pass
        
        return result
    
    @staticmethod
    def parse_pipeline_redirection(cmd_line: str) -> Dict:
        """
        Parse redirection for pipelines.
        
        Args:
            cmd_line: Pipeline command line
            
        Returns:
            Dictionary with:
                - 'pipeline': The pipeline without redirection
                - 'input': Input file for first command or None
                - 'output': Output file for last command or None
                - 'append': Boolean indicating append mode
        """
        result = {
            'pipeline': cmd_line,
            'input': None,
            'output': None,
            'append': False
        }
        
        parser = CommandParser()
        
        # Check for input redirection in the first command
        if "<" in cmd_line:
            # Find the first pipe
            pipe_pos = cmd_line.index("|") if "|" in cmd_line else len(cmd_line)
            first_cmd = cmd_line[:pipe_pos]
            
            if "<" in first_cmd:
                pos = first_cmd.index("<")
                if not parser.is_quoted(first_cmd, pos):
                    # Extract input file
                    before_input = first_cmd[:pos].strip()
                    after_input = first_cmd[pos + 1:].strip()
                    
                    try:
                        parts = shlex.split(after_input)
                        if parts:
                            result['input'] = parts[0]
                            # Reconstruct command line without input redirection
                            if pipe_pos < len(cmd_line):
                                result['pipeline'] = before_input + cmd_line[pipe_pos:]
                            else:
                                result['pipeline'] = before_input
                    except ValueError:
                        pass
        
        # Look for output redirection in the whole pipeline
        if ">>" in result['pipeline']:
            pos = result['pipeline'].rfind(">>")  # Find last occurrence
            if not parser.is_quoted(result['pipeline'], pos):
                pipeline_part = result['pipeline'][:pos].strip()
                redirect_part = result['pipeline'][pos + 2:].strip()
                if redirect_part:
                    try:
                        parts = shlex.split(redirect_part)
                        if parts:
                            result['output'] = parts[0]
                            result['append'] = True
                            result['pipeline'] = pipeline_part
                    except ValueError:
                        pass
        elif ">" in result['pipeline']:
            pos = result['pipeline'].rfind(">")  # Find last occurrence
            if not parser.is_quoted(result['pipeline'], pos):
                pipeline_part = result['pipeline'][:pos].strip()
                redirect_part = result['pipeline'][pos + 1:].strip()
                if redirect_part:
                    try:
                        parts = shlex.split(redirect_part)
                        if parts:
                            result['output'] = parts[0]
                            result['append'] = False
                            result['pipeline'] = pipeline_part
                    except ValueError:
                        pass
        
        return result
    
    @staticmethod
    def split_by_operators(cmd_line: str) -> List[Tuple[str, str]]:
        """
        Split command line by logical operators while preserving them.
        
        Args:
            cmd_line: Command line with operators
            
        Returns:
            List of tuples (command, operator) where operator may be empty
        """
        import re
        
        # Split by operators while preserving them
        parts = re.split(r'(&&|\|\||;)', cmd_line)
        
        result = []
        for i in range(0, len(parts), 2):
            command = parts[i].strip()
            operator = parts[i + 1].strip() if i + 1 < len(parts) else ""
            if command:  # Skip empty commands
                result.append((command, operator))
        
        return result