"""
Test cases for the true and false commands.
"""

import pytest
from chuk_virtual_shell.shell_interpreter import ShellInterpreter


class TestBooleanCommands:
    """Test the true and false command functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.shell = ShellInterpreter()

    def test_true_command(self):
        """Test that true always returns success."""
        result = self.shell.execute("true")
        assert result == ""
        assert self.shell.return_code == 0
        
        # Test with arguments (should be ignored)
        result = self.shell.execute("true arg1 arg2")
        assert result == ""
        assert self.shell.return_code == 0

    def test_false_command(self):
        """Test that false always returns failure."""
        result = self.shell.execute("false")
        assert result == ""
        assert self.shell.return_code == 1
        
        # Test with arguments (should be ignored)
        result = self.shell.execute("false arg1 arg2")
        assert result == ""
        assert self.shell.return_code == 1

    def test_true_with_logical_operators(self):
        """Test true command with && and || operators."""
        # true && command should execute command
        result = self.shell.execute("true && echo success")
        assert "success" in result
        
        # true || command should not execute command
        result = self.shell.execute("true || echo failure")
        assert "failure" not in result

    def test_false_with_logical_operators(self):
        """Test false command with && and || operators."""
        # false && command should not execute command
        result = self.shell.execute("false && echo success")
        assert "success" not in result
        
        # false || command should execute command
        result = self.shell.execute("false || echo failure")
        assert "failure" in result

    def test_chained_operations(self):
        """Test chaining true and false with other commands."""
        # Complex chain
        result = self.shell.execute("true && echo first && false || echo second")
        assert "first" in result
        assert "second" in result
        
        result = self.shell.execute("false || true && echo success")
        assert "success" in result