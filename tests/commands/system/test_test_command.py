"""
Test cases for the test/[ command.
"""

import pytest
from chuk_virtual_shell.shell_interpreter import ShellInterpreter


class TestTestCommand:
    """Test the test/[ command functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.shell = ShellInterpreter()
        # Create test files and directories
        self.shell.execute("mkdir -p /test/dir")
        self.shell.execute("echo 'content' > /test/file.txt")
        self.shell.execute("touch /test/empty.txt")

    def test_file_exists(self):
        """Test -e flag for file existence."""
        # Test with test command
        self.shell.execute("test -e /test/file.txt")
        assert self.shell.return_code == 0
        
        self.shell.execute("test -e /nonexistent")
        assert self.shell.return_code == 1
        
        # Test with [ ] syntax
        self.shell.execute("[ -e /test/file.txt ]")
        assert self.shell.return_code == 0
        
        self.shell.execute("[ -e /nonexistent ]")
        assert self.shell.return_code == 1

    def test_is_file(self):
        """Test -f flag for regular file."""
        self.shell.execute("test -f /test/file.txt")
        assert self.shell.return_code == 0
        
        self.shell.execute("test -f /test/dir")
        assert self.shell.return_code == 1
        
        self.shell.execute("test -f /nonexistent")
        assert self.shell.return_code == 1

    def test_is_directory(self):
        """Test -d flag for directory."""
        self.shell.execute("test -d /test/dir")
        assert self.shell.return_code == 0
        
        self.shell.execute("test -d /test/file.txt")
        assert self.shell.return_code == 1
        
        self.shell.execute("test -d /nonexistent")
        assert self.shell.return_code == 1

    def test_file_has_size(self):
        """Test -s flag for file with size > 0."""
        self.shell.execute("test -s /test/file.txt")
        assert self.shell.return_code == 0
        
        self.shell.execute("test -s /test/empty.txt")
        assert self.shell.return_code == 1
        
        self.shell.execute("test -s /nonexistent")
        assert self.shell.return_code == 1

    def test_string_empty(self):
        """Test -z flag for empty string."""
        self.shell.execute("test -z ''")
        assert self.shell.return_code == 0
        
        self.shell.execute("test -z 'hello'")
        assert self.shell.return_code == 1

    def test_string_not_empty(self):
        """Test -n flag for non-empty string."""
        self.shell.execute("test -n 'hello'")
        assert self.shell.return_code == 0
        
        self.shell.execute("test -n ''")
        assert self.shell.return_code == 1

    def test_string_equality(self):
        """Test string equality with =."""
        self.shell.execute("test 'hello' = 'hello'")
        assert self.shell.return_code == 0
        
        self.shell.execute("test 'hello' = 'world'")
        assert self.shell.return_code == 1
        
        # Test with [ ] syntax
        self.shell.execute("[ 'hello' = 'hello' ]")
        assert self.shell.return_code == 0

    def test_string_inequality(self):
        """Test string inequality with !=."""
        self.shell.execute("test 'hello' != 'world'")
        assert self.shell.return_code == 0
        
        self.shell.execute("test 'hello' != 'hello'")
        assert self.shell.return_code == 1

    def test_numeric_equality(self):
        """Test numeric equality with -eq."""
        self.shell.execute("test 5 -eq 5")
        assert self.shell.return_code == 0
        
        self.shell.execute("test 5 -eq 10")
        assert self.shell.return_code == 1

    def test_numeric_inequality(self):
        """Test numeric inequality with -ne."""
        self.shell.execute("test 5 -ne 10")
        assert self.shell.return_code == 0
        
        self.shell.execute("test 5 -ne 5")
        assert self.shell.return_code == 1

    def test_numeric_less_than(self):
        """Test numeric less than with -lt."""
        self.shell.execute("test 5 -lt 10")
        assert self.shell.return_code == 0
        
        self.shell.execute("test 10 -lt 5")
        assert self.shell.return_code == 1
        
        self.shell.execute("test 5 -lt 5")
        assert self.shell.return_code == 1

    def test_numeric_greater_than(self):
        """Test numeric greater than with -gt."""
        self.shell.execute("test 10 -gt 5")
        assert self.shell.return_code == 0
        
        self.shell.execute("test 5 -gt 10")
        assert self.shell.return_code == 1
        
        self.shell.execute("test 5 -gt 5")
        assert self.shell.return_code == 1

    def test_negation(self):
        """Test negation with !."""
        self.shell.execute("test ! -e /nonexistent")
        assert self.shell.return_code == 0
        
        self.shell.execute("test ! -e /test/file.txt")
        assert self.shell.return_code == 1

    def test_single_argument(self):
        """Test single argument (non-empty string test)."""
        self.shell.execute("test hello")
        assert self.shell.return_code == 0
        
        self.shell.execute("test ''")
        assert self.shell.return_code == 1

    def test_bracket_command_syntax(self):
        """Test that [ command requires closing ]."""
        # Valid syntax
        self.shell.execute("[ -e /test/file.txt ]")
        assert self.shell.return_code == 0
        
        # The actual [ command implementation should handle missing ]
        # but for now we just test the valid case