# chuk_virtual_shell/core/executor.py
"""
chuk_virtual_shell/core/executor.py - Command execution engine

Handles command execution, pipelines, redirection, and operators.
"""

import re
import time
import logging
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from chuk_virtual_shell.shell_interpreter import ShellInterpreter

logger = logging.getLogger(__name__)


class CommandExecutor:
    """Handles command execution, pipelines, and redirection."""
    
    def __init__(self, shell: 'ShellInterpreter'):
        self.shell = shell
        
        # Lazy imports to avoid circular dependencies
        self._parser = None
        self._expansion = None
    
    @property
    def parser(self):
        """Lazy load parser to avoid circular imports."""
        if self._parser is None:
            from chuk_virtual_shell.core.parser import CommandParser
            self._parser = CommandParser()
        return self._parser
    
    @property
    def expansion(self):
        """Lazy load expansion handler to avoid circular imports."""
        if self._expansion is None:
            from chuk_virtual_shell.core.expansion import ExpansionHandler
            self._expansion = ExpansionHandler(self.shell)
        return self._expansion
    
    def execute_line(self, cmd_line: str) -> str:
        """
        Main execution entry point for a command line.
        
        Args:
            cmd_line: Full command line to execute
            
        Returns:
            Command output or error message
        """
        cmd_line = cmd_line.strip()
        if not cmd_line:
            return ""
        
        # Handle exit command
        if cmd_line == "exit":
            self.shell.running = False
            return "Goodbye!"
        
        # Check for control flow
        if self._is_control_flow(cmd_line):
            return self.shell._control_flow_executor.execute_control_flow(cmd_line)
        
        # Check for logical operators (&&, ||, ;)
        if self._has_operators(cmd_line):
            return self._execute_with_operators(cmd_line)
        
        # Check for pipes
        if "|" in cmd_line and not self.parser.is_quoted(cmd_line, cmd_line.index("|")):
            return self._execute_pipeline(cmd_line)
        
        # Simple command with possible redirection
        return self._execute_single(cmd_line)
    
    def execute_without_substitution(self, cmd_line: str) -> str:
        """
        Execute without command substitution (for recursion prevention).
        Still applies variable and glob expansion.
        
        Args:
            cmd_line: Command to execute
            
        Returns:
            Command output
        """
        cmd_line = cmd_line.strip()
        if not cmd_line:
            return ""
        
        # Apply expansions except command substitution
        cmd_line = self.expansion.expand_variables(cmd_line)
        cmd_line = self.expansion.expand_arithmetic(cmd_line)
        cmd_line = self.expansion.expand_globs(cmd_line)
        cmd_line = self.expansion.expand_tilde(cmd_line)
        
        # Check for pipes
        if "|" in cmd_line and not self.parser.is_quoted(cmd_line, cmd_line.index("|")):
            return self._execute_pipeline_no_substitution(cmd_line)
        
        # Parse redirection
        redirect_info = self.parser.parse_redirection(cmd_line)
        cmd_line = redirect_info['command']
        
        # Handle input redirection
        if redirect_info['input']:
            content = self.shell.fs.read_file(redirect_info['input'])
            if content is None:
                return f"{redirect_info['input']}: No such file or directory"
            self.shell._stdin_buffer = content
        
        # Parse and execute command
        cmd, args = self.parser.parse_command(cmd_line)
        if not cmd:
            return ""
        
        if cmd in self.shell.commands:
            try:
                result = self.shell.commands[cmd].run(args)
                if cmd == "cd":
                    self.shell.environ["PWD"] = self.shell.fs.pwd()
                
                if hasattr(self.shell, "_stdin_buffer"):
                    del self.shell._stdin_buffer
                
                # Handle output redirection
                if redirect_info['output']:
                    self._write_redirect(redirect_info['output'], result, redirect_info['append'])
                    return ""
                
                return result
            except Exception as e:
                return f"Error executing command: {e}"
        else:
            return f"{cmd}: command not found"
    
    def _is_control_flow(self, cmd_line: str) -> bool:
        """Check if command is a control flow structure."""
        parts = cmd_line.split(None, 1)
        if not parts:
            return False
        return parts[0] in ["if", "for", "while", "until", "case", "function"]
    
    def _has_operators(self, cmd_line: str) -> bool:
        """Check if command has logical operators."""
        return any(op in cmd_line for op in ["&&", "||", ";"]) and \
               not self.parser.contains_quoted_operator(cmd_line)
    
    def _execute_with_operators(self, cmd_line: str) -> str:
        """
        Execute command line with logical operators (&&, ||) and semicolon separator.
        
        Args:
            cmd_line: Command line with operators
            
        Returns:
            Combined output from commands
        """
        parts = self.parser.split_by_operators(cmd_line)
        results = []
        skip_next = False
        
        for i, (command, operator) in enumerate(parts):
            if not skip_next:
                # Execute the individual command
                result = self._execute_single(command)
                
                # Store the result if there's output
                if result:
                    results.append(result)
                
                # Check operator to determine flow
                if operator == "&&":
                    # Continue only if command succeeded (return code 0)
                    skip_next = self.shell.return_code != 0
                elif operator == "||":
                    # Continue only if command failed (return code != 0)
                    skip_next = self.shell.return_code == 0
                elif operator == ";":
                    # Always continue with semicolon
                    skip_next = False
            else:
                skip_next = False
        
        return "\n".join(results)
    
    def _execute_pipeline(self, cmd_line: str) -> str:
        """
        Execute a pipeline of commands connected by pipes.
        
        Args:
            cmd_line: Pipeline command line
            
        Returns:
            Output from the last command in the pipeline
        """
        # Apply expansions to whole pipeline
        cmd_line = self.expansion.expand_all(cmd_line)
        
        # Parse for redirection
        pipeline_info = self.parser.parse_pipeline_redirection(cmd_line)
        cmd_line = pipeline_info['pipeline']
        
        # Execute pipeline
        commands = cmd_line.split("|")
        result = ""
        
        for i, cmd_str in enumerate(commands):
            cmd_str = cmd_str.strip()
            if not cmd_str:
                continue
            
            cmd, args = self.parser.parse_command(cmd_str)
            if not cmd:
                continue
            
            if cmd not in self.shell.commands:
                return f"{cmd}: command not found"
            
            try:
                # Handle stdin
                if i == 0 and pipeline_info['input']:
                    # Read input file for the first command
                    content = self.shell.fs.read_file(pipeline_info['input'])
                    if content is None:
                        return f"{pipeline_info['input']}: No such file or directory"
                    self.shell._stdin_buffer = content
                elif i > 0 and result:
                    # Store the previous command's output as stdin for this command
                    self.shell._stdin_buffer = result
                
                # Execute command
                result = self.shell.commands[cmd].run(args)
                
                # Clear stdin buffer
                if hasattr(self.shell, "_stdin_buffer"):
                    del self.shell._stdin_buffer
                
                # Check if the command returned an error
                if result and (
                    result.startswith(f"{cmd}: ")
                    and ("No such file" in result or "error" in result.lower())
                ):
                    # Error occurred, stop pipeline and return error
                    return result
                    
            except Exception as e:
                logger.error(f"Error executing command '{cmd}' in pipeline: {e}")
                return f"Error executing command in pipeline: {e}"
        
        # Handle output redirection
        if pipeline_info['output']:
            self._write_redirect(pipeline_info['output'], result, pipeline_info['append'])
            return ""
        
        return result
    
    def _execute_pipeline_no_substitution(self, cmd_line: str) -> str:
        """Execute pipeline without command substitution."""
        # Similar to _execute_pipeline but without expansion
        commands = cmd_line.split("|")
        result = ""
        
        for i, cmd_str in enumerate(commands):
            cmd_str = cmd_str.strip()
            if not cmd_str:
                continue
            
            cmd, args = self.parser.parse_command(cmd_str)
            if not cmd:
                continue
            
            if cmd not in self.shell.commands:
                return f"{cmd}: command not found"
            
            try:
                if i > 0 and result:
                    self.shell._stdin_buffer = result
                
                result = self.shell.commands[cmd].run(args)
                
                if hasattr(self.shell, "_stdin_buffer"):
                    del self.shell._stdin_buffer
                    
            except Exception as e:
                return f"Error executing command in pipeline: {e}"
        
        return result
    
    def _execute_single(self, cmd_line: str) -> str:
        """
        Execute a single command with expansions.
        
        Args:
            cmd_line: Single command (no operators)
            
        Returns:
            Command output
        """
        # Apply expansions
        cmd_line = self.expansion.expand_all(cmd_line)
        
        # Check for pipes after expansion
        if "|" in cmd_line and not self.parser.is_quoted(cmd_line, cmd_line.index("|")):
            return self._execute_pipeline(cmd_line)
        
        return self._execute_simple(cmd_line)
    
    def _execute_simple(self, cmd_line: str) -> str:
        """
        Execute a simple command with possible redirection.
        
        Args:
            cmd_line: Command with possible redirection
            
        Returns:
            Command output
        """
        # Check for variable assignment (VAR=value)
        if '=' in cmd_line and not ' ' in cmd_line.split('=')[0]:
            # Simple variable assignment without spaces before =
            parts = cmd_line.split('=', 1)
            if parts[0] and parts[0][0].isalpha() or parts[0][0] == '_':
                # Valid variable name
                var_name = parts[0].strip()
                var_value = parts[1].strip() if len(parts) > 1 else ""
                # Remove quotes if present
                if var_value and var_value[0] in '"\'':
                    var_value = var_value.strip(var_value[0])
                self.shell.environ[var_name] = var_value
                self.shell.return_code = 0
                return ""
        
        # Parse redirection
        redirect_info = self.parser.parse_redirection(cmd_line)
        cmd_line = redirect_info['command']
        
        # Handle input redirection
        if redirect_info['input']:
            content = self.shell.fs.read_file(redirect_info['input'])
            if content is None:
                self.shell.return_code = 1
                return f"bash: {redirect_info['input']}: No such file or directory"
            self.shell._stdin_buffer = content
        
        # Parse and execute command
        cmd, args = self.parser.parse_command(cmd_line)
        if not cmd:
            return ""
        
        if cmd in self.shell.commands:
            try:
                # Track command timing if enabled
                start_time = time.time() if self.shell.enable_timing else None
                
                # Execute command
                # Reset return code before execution
                self.shell.return_code = 0
                result = self.shell.commands[cmd].run(args)
                # The command may have set a specific return code (e.g., false sets it to 1)
                # If it didn't, return_code will still be 0 (success)
                
                # Record timing statistics
                if self.shell.enable_timing and start_time:
                    self._record_timing(cmd, time.time() - start_time)
                
                # Update PWD for cd command
                if cmd == "cd":
                    self.shell.environ["PWD"] = self.shell.fs.pwd()
                
                # Clear stdin buffer
                if hasattr(self.shell, "_stdin_buffer"):
                    del self.shell._stdin_buffer
                
                # Handle output redirection
                if redirect_info['output']:
                    self._write_redirect(redirect_info['output'], result, redirect_info['append'])
                    return ""
                
                return result
                
            except Exception as e:
                logger.error(f"Error executing command '{cmd}': {e}")
                self.shell.return_code = 1
                return f"Error executing command: {e}"
        else:
            self.shell.return_code = 127  # Command not found
            return f"{cmd}: command not found"
    
    def _write_redirect(self, filename: str, content: str, append: bool) -> None:
        """
        Write or append content to file.
        
        Args:
            filename: File to write to
            content: Content to write
            append: Whether to append or overwrite
        """
        if append:
            # Append to file
            existing = self.shell.fs.read_file(filename) or ""
            if existing and not existing.endswith("\n"):
                content = existing + "\n" + content
            elif existing:
                content = existing + content
        
        self.shell.fs.write_file(filename, content)
    
    def _record_timing(self, cmd: str, elapsed: float) -> None:
        """
        Record command timing statistics.
        
        Args:
            cmd: Command name
            elapsed: Elapsed time in seconds
        """
        if cmd not in self.shell.command_timing:
            self.shell.command_timing[cmd] = {
                "count": 0,
                "total_time": 0.0,
                "min_time": float("inf"),
                "max_time": 0.0,
            }
        
        stats = self.shell.command_timing[cmd]
        stats["count"] += 1
        stats["total_time"] += elapsed
        stats["min_time"] = min(stats["min_time"], elapsed)
        stats["max_time"] = max(stats["max_time"], elapsed)