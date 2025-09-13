# src/chuk_virtual_shell/core/control_flow_ececutor.py
"""
Control flow implementation for shell interpreter with proper tokenization.
This module provides robust parsing and execution of shell control structures.
Designed to work with existing TestCommand implementation.
"""

import shlex
import re
from typing import List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum


class TokenType(Enum):
    """Token types for shell parsing."""
    KEYWORD = "keyword"
    COMMAND = "command"
    OPERATOR = "operator"
    SEPARATOR = "separator"
    STRING = "string"
    VARIABLE = "variable"
    REDIRECT = "redirect"


@dataclass
class Token:
    """Represents a parsed token."""
    type: TokenType
    value: str
    position: int = 0


class ShellTokenizer:
    """Tokenizer for shell command parsing."""
    
    KEYWORDS = {
        'if', 'then', 'elif', 'else', 'fi',
        'for', 'in', 'do', 'done',
        'while', 'until',
        'case', 'esac',
        'function', 'return',
        'break', 'continue'
    }
    
    OPERATORS = {
        '&&', '||', '|', ';', '&',
        '>', '>>', '<', '<<',
        '$(', '`'
    }
    
    def __init__(self):
        self.tokens = []
        self.current_pos = 0
        
    def tokenize(self, text: str) -> List[Token]:
        """
        Tokenize shell command text into structured tokens.
        
        Args:
            text: Shell command text to tokenize
            
        Returns:
            List of Token objects
        """
        self.tokens = []
        self.current_pos = 0
        
        # First pass: split while preserving quotes and operators
        raw_tokens = self._initial_tokenize(text)
        
        # Second pass: classify tokens
        classified_tokens = []
        for raw_token in raw_tokens:
            token_type = self._classify_token(raw_token)
            classified_tokens.append(Token(token_type, raw_token, self.current_pos))
            self.current_pos += len(raw_token) + 1
            
        return classified_tokens
    
    def _initial_tokenize(self, text: str) -> List[str]:
        """
        Initial tokenization preserving quotes and special characters.
        """
        tokens = []
        current = []
        in_single = False
        in_double = False
        escaped = False
        i = 0
        
        while i < len(text):
            char = text[i]
            
            if escaped:
                current.append(char)
                escaped = False
                i += 1
                continue
                
            if char == '\\' and not in_single:
                current.append(char)
                escaped = True
                i += 1
                continue
            
            # Handle quotes
            if char == "'" and not in_double:
                if in_single:
                    # End of single quote
                    current.append(char)
                    tokens.append(''.join(current))
                    current = []
                    in_single = False
                else:
                    # Start of single quote
                    if current:
                        tokens.append(''.join(current))
                        current = []
                    current.append(char)
                    in_single = True
                i += 1
                continue
                
            if char == '"' and not in_single:
                if in_double:
                    # End of double quote
                    current.append(char)
                    tokens.append(''.join(current))
                    current = []
                    in_double = False
                else:
                    # Start of double quote
                    if current:
                        tokens.append(''.join(current))
                        current = []
                    current.append(char)
                    in_double = True
                i += 1
                continue
            
            # Inside quotes, just accumulate
            if in_single or in_double:
                current.append(char)
                i += 1
                continue
            
            # Handle operators and separators
            if char in ' \t\n':
                if current:
                    tokens.append(''.join(current))
                    current = []
                i += 1
                continue
            
            # Check for arithmetic expansion $((
            if i + 2 < len(text) and text[i:i+3] == '$((':
                # Find the matching ))
                end = text.find('))', i + 3)
                if end != -1:
                    if current:
                        tokens.append(''.join(current))
                        current = []
                    # Keep the entire arithmetic expression as one token
                    tokens.append(text[i:end+2])
                    i = end + 2
                    continue
            
            # Check for multi-character operators
            if i + 1 < len(text):
                two_char = text[i:i+2]
                if two_char in ['&&', '||', '>>', '<<', '$(']:
                    if current:
                        tokens.append(''.join(current))
                        current = []
                    tokens.append(two_char)
                    i += 2
                    continue
            
            # Check for single-character operators
            if char in ';|<>&':
                if current:
                    tokens.append(''.join(current))
                    current = []
                tokens.append(char)
                i += 1
                continue
            
            # Regular character
            current.append(char)
            i += 1
        
        if current:
            tokens.append(''.join(current))
            
        return tokens
    
    def _classify_token(self, token: str) -> TokenType:
        """Classify a token by its type."""
        if token in self.KEYWORDS:
            return TokenType.KEYWORD
        elif token in ['&&', '||', '|', '&']:
            return TokenType.OPERATOR
        elif token in [';', '\n']:
            return TokenType.SEPARATOR
        elif token in ['>', '>>', '<', '<<']:
            return TokenType.REDIRECT
        elif token.startswith('$') or token.startswith('`'):
            return TokenType.VARIABLE
        else:
            return TokenType.COMMAND


class ControlFlowExecutor:
    """Executes control flow structures for the shell."""
    
    def __init__(self, shell):
        """
        Initialize the control flow executor.
        
        Args:
            shell: The ShellInterpreter instance
        """
        self.shell = shell
        self.tokenizer = ShellTokenizer()
        
    def execute_control_flow(self, cmd_line: str) -> str:
        """
        Main entry point for control flow execution.
        
        Args:
            cmd_line: The control flow command line
            
        Returns:
            Output from execution
        """
        # Tokenize the command
        tokens = self.tokenizer.tokenize(cmd_line)
        
        if not tokens:
            return ""
        
        # Check first keyword to determine structure type
        first_keyword = None
        for token in tokens:
            if token.type == TokenType.KEYWORD:
                first_keyword = token.value
                break
        
        if first_keyword == 'if':
            return self._execute_if_statement(tokens)
        elif first_keyword == 'for':
            return self._execute_for_loop(tokens)
        elif first_keyword == 'while':
            return self._execute_while_loop(tokens)
        elif first_keyword == 'until':
            return self._execute_until_loop(tokens)
        else:
            return f"{first_keyword}: control structure not implemented"
    
    def _execute_if_statement(self, tokens: List[Token]) -> str:
        """
        Execute if/then/elif/else/fi statement.
        
        Args:
            tokens: Tokenized command
            
        Returns:
            Output from executed branch
        """
        # Parse the if statement structure
        structure = self._parse_if_structure(tokens)
        
        if not structure:
            return "if: syntax error"
        
        # Execute conditions and find which branch to run
        for branch in structure['branches']:
            if branch['type'] == 'else':
                # Else branch always executes if we reach it
                return self._execute_commands(branch['commands'])
            else:
                # Execute condition
                condition_result = self._execute_condition(branch['condition'])
                if condition_result:  # Condition succeeded (exit code 0)
                    return self._execute_commands(branch['commands'])
        
        return ""
    
    def _parse_if_structure(self, tokens: List[Token]) -> Optional[dict]:
        """
        Parse if statement into structured format.
        
        Returns dict with:
        {
            'branches': [
                {'type': 'if', 'condition': [...], 'commands': [...]},
                {'type': 'elif', 'condition': [...], 'commands': [...]},
                {'type': 'else', 'commands': [...]}
            ]
        }
        """
        structure = {'branches': []}
        current_branch = None
        current_section = None  # 'condition' or 'commands'
        
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            if token.type == TokenType.KEYWORD:
                if token.value == 'if':
                    current_branch = {'type': 'if', 'condition': [], 'commands': []}
                    current_section = 'condition'
                    
                elif token.value == 'then':
                    if current_branch and current_section == 'condition':
                        current_section = 'commands'
                    else:
                        return None  # Syntax error
                        
                elif token.value == 'elif':
                    # Save current branch and start new one
                    if current_branch:
                        structure['branches'].append(current_branch)
                    current_branch = {'type': 'elif', 'condition': [], 'commands': []}
                    current_section = 'condition'
                    
                elif token.value == 'else':
                    # Save current branch and start else branch
                    if current_branch:
                        structure['branches'].append(current_branch)
                    current_branch = {'type': 'else', 'commands': []}
                    current_section = 'commands'
                    
                elif token.value == 'fi':
                    # End of if statement
                    if current_branch:
                        structure['branches'].append(current_branch)
                    break
                    
                else:
                    # Other keyword in condition or command
                    if current_section == 'condition':
                        current_branch['condition'].append(token)
                    elif current_section == 'commands':
                        current_branch['commands'].append(token)
                        
            elif token.type == TokenType.SEPARATOR and token.value == ';':
                # Separator can end condition or separate commands
                if current_section == 'commands':
                    # Keep separators in commands for proper splitting
                    current_branch['commands'].append(token)
                
            else:
                # Regular token (command, operator, etc.)
                if current_section == 'condition' and current_branch:
                    current_branch['condition'].append(token)
                elif current_section == 'commands' and current_branch:
                    current_branch['commands'].append(token)
            
            i += 1
        
        return structure if structure['branches'] else None
    
    def _execute_condition(self, condition_tokens: List[Token]) -> bool:
        """
        Execute a condition and return success/failure.
        Uses the existing test command implementation.
        
        Args:
            condition_tokens: Tokens making up the condition
            
        Returns:
            True if condition succeeded (exit code 0), False otherwise
        """
        if not condition_tokens:
            return False
        
        # Reconstruct command from tokens
        cmd_parts = []
        for token in condition_tokens:
            cmd_parts.append(token.value)
        
        condition_cmd = ' '.join(cmd_parts)
        
        # Execute the condition command
        # The test command or [ command will set the return code
        self.shell.execute(condition_cmd)
        
        # Check return code
        return self.shell.return_code == 0
    
    def _execute_commands(self, command_tokens: List[Token]) -> str:
        """
        Execute a list of command tokens.
        
        Args:
            command_tokens: Tokens making up the commands
            
        Returns:
            Combined output from commands
        """
        if not command_tokens:
            return ""
        
        # Group tokens into individual commands
        # Need to be careful with control flow statements that contain semicolons
        commands = []
        current_cmd = []
        depth = 0  # Track control flow depth
        
        for token in command_tokens:
            if token.type == TokenType.KEYWORD and token.value in ['if', 'for', 'while', 'until']:
                depth += 1
                current_cmd.append(token)
            elif token.type == TokenType.KEYWORD and token.value in ['fi', 'done']:
                current_cmd.append(token)
                depth -= 1
                # If we're back at depth 0, this command is complete
                if depth == 0 and current_cmd:
                    commands.append(current_cmd)
                    current_cmd = []
            elif token.type == TokenType.SEPARATOR and depth == 0:
                # Only split on separators when not inside control flow
                if current_cmd:
                    commands.append(current_cmd)
                    current_cmd = []
            else:
                current_cmd.append(token)
        
        if current_cmd:
            commands.append(current_cmd)
        
        # Execute each command
        results = []
        for cmd_tokens in commands:
            # Check for break/continue keywords
            if cmd_tokens and len(cmd_tokens) == 1 and cmd_tokens[0].type == TokenType.KEYWORD:
                if cmd_tokens[0].value == 'break':
                    self.shell._break_loop = True
                    self.shell.return_code = 0
                    break
                elif cmd_tokens[0].value == 'continue':
                    self.shell._continue_loop = True
                    self.shell.return_code = 0
                    continue
            
            # Reconstruct command string
            cmd_parts = [t.value for t in cmd_tokens]
            cmd = ' '.join(cmd_parts)
            
            # Execute command through shell (which will handle nested control flow)
            output = self.shell.execute(cmd)
            if output:
                results.append(output)
            
            # Check if break or continue was set by nested control flow
            if hasattr(self.shell, '_break_loop') and self.shell._break_loop:
                break
            if hasattr(self.shell, '_continue_loop') and self.shell._continue_loop:
                break  # Exit command loop to continue outer loop
        
        return '\n'.join(results)
    
    def _execute_for_loop(self, tokens: List[Token]) -> str:
        """
        Execute for loop: for var in items; do commands; done
        
        Args:
            tokens: Tokenized command
            
        Returns:
            Output from loop execution
        """
        # Parse the for loop structure
        structure = self._parse_for_structure(tokens)
        
        if not structure:
            return "for: syntax error"
        
        var_name = structure['variable']
        items = structure['items']
        commands = structure['commands']
        
        # Expand items (variables and globs)
        expanded_items = self._expand_items(items)
        
        # Execute loop
        results = []
        # Save previous value if it exists
        prev_value = self.shell.environ.get(var_name)
        
        for item in expanded_items:
            # Set loop variable
            self.shell.environ[var_name] = item
            
            # Reset continue flag
            if hasattr(self.shell, '_continue_loop'):
                self.shell._continue_loop = False
            
            # Execute commands
            output = self._execute_commands(commands)
            if output:
                results.append(output)
            
            # Check for continue (skip to next iteration)
            if hasattr(self.shell, '_continue_loop') and self.shell._continue_loop:
                self.shell._continue_loop = False
                continue
            
            # Check for break
            if hasattr(self.shell, '_break_loop') and self.shell._break_loop:
                self.shell._break_loop = False
                break
        
        # Restore previous value or clean up loop variable
        if prev_value is not None:
            self.shell.environ[var_name] = prev_value
        elif var_name in self.shell.environ:
            del self.shell.environ[var_name]
        
        return '\n'.join(results)
    
    def _parse_for_structure(self, tokens: List[Token]) -> Optional[dict]:
        """
        Parse for loop into structured format.
        
        Returns dict with:
        {
            'variable': 'var_name',
            'items': [...],
            'commands': [...]
        }
        """
        structure = {}
        section = None  # 'var', 'items', 'commands'
        depth = 0  # Track nested for/done pairs
        
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            if token.type == TokenType.KEYWORD:
                if token.value == 'for':
                    if depth == 0 and section is None:
                        # This is our main for loop
                        section = 'var'
                    else:
                        # This is a nested for loop, part of commands
                        if section == 'commands':
                            structure['commands'].append(token)
                        depth += 1
                elif token.value == 'in' and depth == 0:
                    section = 'items'
                    structure['items'] = []
                elif token.value == 'do':
                    if depth == 0 and section == 'items':
                        # This is our main do
                        section = 'commands'
                        structure['commands'] = []
                    else:
                        # Part of nested structure
                        if section == 'commands':
                            structure['commands'].append(token)
                elif token.value == 'done':
                    if depth == 0:
                        # End of our main loop
                        break
                    else:
                        # End of nested loop
                        depth -= 1
                        if section == 'commands':
                            structure['commands'].append(token)
                else:
                    # Other keyword inside commands
                    if section == 'commands':
                        structure['commands'].append(token)
            else:
                if section == 'var' and 'variable' not in structure:
                    structure['variable'] = token.value
                elif section == 'items':
                    if token.type != TokenType.SEPARATOR:
                        structure['items'].append(token)
                elif section == 'commands':
                    structure['commands'].append(token)
            
            i += 1
        
        # Validate structure
        if 'variable' in structure and 'items' in structure and 'commands' in structure:
            return structure
        return None
    
    def _expand_items(self, item_tokens: List[Token]) -> List[str]:
        """
        Expand item tokens (variables, globs, etc.) into actual items.
        
        Args:
            item_tokens: Tokens representing items
            
        Returns:
            List of expanded item strings
        """
        # Reconstruct items string
        items_str = ' '.join(t.value for t in item_tokens)
        
        # Expand variables
        items_str = self.shell._expand_variables(items_str)
        
        # Expand globs
        items_str = self.shell._expand_globs(items_str)
        
        # Split into individual items
        try:
            items = shlex.split(items_str)
        except ValueError:
            items = items_str.split()
        
        return items
    
    def _execute_while_loop(self, tokens: List[Token]) -> str:
        """
        Execute while loop: while condition; do commands; done
        
        Args:
            tokens: Tokenized command
            
        Returns:
            Output from loop execution
        """
        # Parse structure
        structure = self._parse_while_structure(tokens, 'while')
        
        if not structure:
            return "while: syntax error"
        
        condition = structure['condition']
        commands = structure['commands']
        
        # Execute loop
        results = []
        max_iterations = 10000
        iteration = 0
        
        while iteration < max_iterations:
            # Check condition
            if not self._execute_condition(condition):
                break
            
            # Execute commands
            output = self._execute_commands(commands)
            if output:
                results.append(output)
            
            # Check for break
            if hasattr(self.shell, '_break_loop') and self.shell._break_loop:
                self.shell._break_loop = False
                break
            
            iteration += 1
        
        if iteration >= max_iterations:
            return "while: maximum iterations exceeded\n" + '\n'.join(results)
        
        return '\n'.join(results)
    
    def _execute_until_loop(self, tokens: List[Token]) -> str:
        """
        Execute until loop: until condition; do commands; done
        
        Args:
            tokens: Tokenized command
            
        Returns:
            Output from loop execution
        """
        # Parse structure
        structure = self._parse_while_structure(tokens, 'until')
        
        if not structure:
            return "until: syntax error"
        
        condition = structure['condition']
        commands = structure['commands']
        
        # Execute loop (opposite of while)
        results = []
        max_iterations = 10000
        iteration = 0
        
        while iteration < max_iterations:
            # Check condition (opposite of while)
            if self._execute_condition(condition):
                break
            
            # Execute commands
            output = self._execute_commands(commands)
            if output:
                results.append(output)
            
            # Check for break
            if hasattr(self.shell, '_break_loop') and self.shell._break_loop:
                self.shell._break_loop = False
                break
            
            iteration += 1
        
        if iteration >= max_iterations:
            return "until: maximum iterations exceeded\n" + '\n'.join(results)
        
        return '\n'.join(results)
    
    def _parse_while_structure(self, tokens: List[Token], loop_type: str) -> Optional[dict]:
        """
        Parse while/until loop into structured format.
        
        Args:
            tokens: Tokenized command
            loop_type: 'while' or 'until'
            
        Returns dict with:
        {
            'condition': [...],
            'commands': [...]
        }
        """
        structure = {}
        section = None  # 'condition' or 'commands'
        
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            if token.type == TokenType.KEYWORD:
                if token.value == loop_type:
                    section = 'condition'
                    structure['condition'] = []
                elif token.value == 'do':
                    section = 'commands'
                    structure['commands'] = []
                elif token.value == 'done':
                    break
                else:
                    # Keyword inside condition or commands
                    if section == 'condition':
                        structure['condition'].append(token)
                    elif section == 'commands':
                        structure['commands'].append(token)
            elif token.type != TokenType.SEPARATOR or section != 'condition':
                # Add to current section (skip separators in condition)
                if section == 'condition':
                    structure['condition'].append(token)
                elif section == 'commands':
                    structure['commands'].append(token)
            
            i += 1
        
        # Validate structure
        if 'condition' in structure and 'commands' in structure:
            return structure
        return None