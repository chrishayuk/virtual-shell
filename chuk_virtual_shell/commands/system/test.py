# src/chuk_virtual_shell/commands/system/test.py
"""
Test command - evaluates conditional expressions.

Provides the 'test' and '[' commands for evaluating conditional expressions
used in shell scripts and if statements.
"""

from chuk_virtual_shell.commands.command_base import ShellCommand


class TestCommand(ShellCommand):
    """
    Test command for evaluating conditional expressions.
    
    Supports file tests, string comparisons, and numeric comparisons.
    """
    
    name = "test"
    help_text = "test - Evaluate conditional expressions"
    category = "system"

    def __init__(self, shell):
        """Initialize the test command."""
        super().__init__(shell)

    def execute(self, args):
        """
        Execute the test command.
        
        Args:
            args: List of arguments forming the conditional expression
            
        Returns:
            Empty string (sets return code to 0 for true, 1 for false)
        """
        # Handle [ ] syntax - the closing ] is required
        if args and args[-1] == "]":
            args = args[:-1]  # Remove the closing bracket
        
        if not args:
            self.shell.return_code = 1
            return ""
        
        # Evaluate the expression
        result = self._evaluate_expression(args)
        self.shell.return_code = 0 if result else 1
        return ""
    
    def _evaluate_expression(self, args):
        """
        Evaluate a test expression.
        
        Args:
            args: List of arguments forming the expression
            
        Returns:
            bool: True if expression is true, False otherwise
        """
        # Handle negation
        if args[0] == "!":
            return not self._evaluate_expression(args[1:])
        
        # Single argument tests
        if len(args) == 1:
            # Non-empty string test
            return bool(args[0])
        
        # File test operators (unary)
        if len(args) == 2:
            operator = args[0]
            path = args[1]
            
            if operator == "-e" or operator == "-a":
                # File exists
                return self.shell.fs.exists(path)
            elif operator == "-f":
                # Is regular file
                return self.shell.fs.is_file(path)
            elif operator == "-d":
                # Is directory
                return self.shell.fs.is_dir(path)
            elif operator == "-s":
                # File exists and has size > 0
                if not self.shell.fs.exists(path):
                    return False
                if self.shell.fs.is_file(path):
                    content = self.shell.fs.read_file(path)
                    return content is not None and len(content) > 0
                return False
            elif operator == "-r":
                # File is readable (always true in virtual FS)
                return self.shell.fs.exists(path)
            elif operator == "-w":
                # File is writable (always true in virtual FS)
                return self.shell.fs.exists(path)
            elif operator == "-x":
                # File is executable (check if it's a command)
                import os
                basename = os.path.basename(path)
                return basename in self.shell.commands
            elif operator == "-z":
                # String is empty
                return len(path) == 0
            elif operator == "-n":
                # String is not empty
                return len(path) > 0
        
        # Binary operators
        if len(args) >= 3:
            left = args[0]
            operator = args[1]
            right = args[2] if len(args) > 2 else ""
            
            # String comparisons
            if operator == "=":
                return left == right
            elif operator == "!=":
                return left != right
            elif operator == "<":
                return left < right
            elif operator == ">":
                return left > right
            
            # Numeric comparisons
            elif operator == "-eq":
                try:
                    return int(left) == int(right)
                except (ValueError, TypeError):
                    return False
            elif operator == "-ne":
                try:
                    return int(left) != int(right)
                except (ValueError, TypeError):
                    return True
            elif operator == "-lt":
                try:
                    return int(left) < int(right)
                except (ValueError, TypeError):
                    return False
            elif operator == "-le":
                try:
                    return int(left) <= int(right)
                except (ValueError, TypeError):
                    return False
            elif operator == "-gt":
                try:
                    return int(left) > int(right)
                except (ValueError, TypeError):
                    return False
            elif operator == "-ge":
                try:
                    return int(left) >= int(right)
                except (ValueError, TypeError):
                    return False
            
            # Logical operators (handle multiple arguments)
            elif operator == "-a" or operator == "-and":
                # Logical AND
                left_result = self._evaluate_expression([left])
                if not left_result:
                    return False
                return self._evaluate_expression(args[2:])
            elif operator == "-o" or operator == "-or":
                # Logical OR
                left_result = self._evaluate_expression([left])
                if left_result:
                    return True
                return self._evaluate_expression(args[2:])
        
        # Default: non-empty string test
        return bool(args[0]) if args else False


class BracketCommand(TestCommand):
    """
    [ command - alias for test command.
    
    Requires closing bracket ] as last argument.
    """
    
    name = "["
    help_text = "[ - Evaluate conditional expressions (requires closing ])"
    category = "system"
    
    def __init__(self, shell):
        """Initialize the [ command."""
        ShellCommand.__init__(self, shell)