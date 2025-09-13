"""
Test cases for the main ShellInterpreter class.
Tests the overall shell interpreter functionality and integration.
"""

import pytest
from chuk_virtual_shell.shell_interpreter import ShellInterpreter
from chuk_virtual_fs import VirtualFileSystem
from chuk_virtual_shell.filesystem_compat import FileSystemCompat


class TestShellInterpreter:
    """Test the main ShellInterpreter class."""

    def test_basic_initialization(self):
        """Test basic shell initialization."""
        shell = ShellInterpreter()
        
        # Check core components are initialized
        assert shell.fs is not None
        assert shell.environ is not None
        assert shell.commands is not None
        assert shell.history is not None
        assert shell.running is True
        assert shell.return_code == 0
        
        # Check environment variables
        assert "HOME" in shell.environ
        assert "PATH" in shell.environ
        assert "USER" in shell.environ
        assert "PWD" in shell.environ

    def test_command_execution(self):
        """Test basic command execution."""
        shell = ShellInterpreter()
        
        # Test echo command
        result = shell.execute("echo Hello World")
        assert "Hello World" in result
        
        # Test pwd command
        result = shell.execute("pwd")
        assert "/" in result
        
        # Test ls command
        shell.execute("touch /test.txt")
        result = shell.execute("ls /")
        assert "test.txt" in result

    def test_return_codes(self):
        """Test command return codes."""
        shell = ShellInterpreter()
        
        # Successful command
        shell.execute("true")
        assert shell.return_code == 0
        
        # Failed command
        shell.execute("false")
        assert shell.return_code == 1
        
        # Command not found
        result = shell.execute("nonexistent_command")
        assert "command not found" in result.lower()

    def test_environment_variables(self):
        """Test environment variable handling."""
        shell = ShellInterpreter()
        
        # Set variable
        shell.execute("export TEST_VAR=test_value")
        assert shell.environ.get("TEST_VAR") == "test_value"
        
        # Use variable
        result = shell.execute("echo $TEST_VAR")
        assert "test_value" in result
        
        # Variable expansion in strings
        result = shell.execute('echo "Value is $TEST_VAR"')
        assert "Value is test_value" in result

    def test_command_history(self):
        """Test command history tracking."""
        shell = ShellInterpreter()
        
        # Execute some commands
        shell.execute("echo first")
        shell.execute("echo second")
        shell.execute("echo third")
        
        # Check history
        assert len(shell.history) >= 3
        assert "echo first" in shell.history
        assert "echo second" in shell.history
        assert "echo third" in shell.history

    def test_aliases(self):
        """Test alias functionality."""
        shell = ShellInterpreter()
        
        # Create alias
        shell.execute('alias ll="ls -la"')
        assert "ll" in shell.aliases
        assert shell.aliases["ll"] == "ls -la"
        
        # Use alias
        shell.execute("touch /test.txt")
        result = shell.execute("ll /")
        assert "test.txt" in result

    def test_pipes(self):
        """Test pipe functionality."""
        shell = ShellInterpreter()
        
        # Create test data
        shell.execute('echo -e "apple\\nbanana\\ncherry" > /fruits.txt')
        
        # Test single pipe
        result = shell.execute("cat /fruits.txt | grep a")
        assert "apple" in result
        assert "banana" in result
        assert "cherry" not in result or result.count("apple") > 0
        
        # Test multiple pipes
        result = shell.execute("cat /fruits.txt | grep a | wc -l")
        assert "2" in result.strip()

    def test_redirections(self):
        """Test I/O redirections."""
        shell = ShellInterpreter()
        
        # Output redirection
        shell.execute("echo test > /output.txt")
        result = shell.execute("cat /output.txt")
        assert "test" in result
        
        # Append redirection
        shell.execute("echo more >> /output.txt")
        result = shell.execute("cat /output.txt")
        assert "test" in result
        assert "more" in result
        
        # Input redirection
        shell.execute('echo "input data" > /input.txt')
        result = shell.execute("grep input < /input.txt")
        assert "input data" in result

    def test_command_chaining(self):
        """Test command chaining operators."""
        shell = ShellInterpreter()
        
        # AND operator (&&)
        result = shell.execute("true && echo success")
        assert "success" in result
        
        result = shell.execute("false && echo should_not_appear")
        assert "should_not_appear" not in result
        
        # OR operator (||)
        result = shell.execute("false || echo fallback")
        assert "fallback" in result
        
        result = shell.execute("true || echo should_not_appear")
        assert "should_not_appear" not in result
        
        # Semicolon separator
        result = shell.execute("echo first; echo second")
        assert "first" in result
        assert "second" in result

    def test_globbing(self):
        """Test glob pattern expansion."""
        shell = ShellInterpreter()
        
        # Create test files
        shell.execute("mkdir -p /test")
        shell.execute("touch /test/file1.txt /test/file2.txt /test/data.log")
        
        # Test star glob
        result = shell.execute("ls /test/*.txt")
        assert "file1.txt" in result
        assert "file2.txt" in result
        assert "data.log" not in result
        
        # Test question mark glob
        result = shell.execute("ls /test/file?.txt")
        assert "file1.txt" in result
        assert "file2.txt" in result

    def test_command_substitution(self):
        """Test command substitution."""
        shell = ShellInterpreter()
        
        # Test $() syntax
        shell.execute("mkdir /testdir")
        shell.execute("cd /testdir")
        result = shell.execute("echo Current dir: $(pwd)")
        assert "Current dir: /testdir" in result
        
        # Test backtick syntax
        result = shell.execute("echo Files: `ls / | wc -l`")
        assert "Files:" in result
        
        # Test nested substitution
        shell.execute("echo 5 > /number.txt")
        result = shell.execute("echo Value is $(cat /number.txt)")
        assert "Value is 5" in result

    def test_working_directory(self):
        """Test working directory management."""
        shell = ShellInterpreter()
        
        # Check initial directory
        result = shell.execute("pwd")
        assert result.strip() == "/"
        
        # Change directory
        shell.execute("mkdir -p /test/subdir")
        shell.execute("cd /test")
        result = shell.execute("pwd")
        assert result.strip() == "/test"
        
        # Relative path
        shell.execute("cd subdir")
        result = shell.execute("pwd")
        assert result.strip() == "/test/subdir"
        
        # Parent directory
        shell.execute("cd ..")
        result = shell.execute("pwd")
        assert result.strip() == "/test"
        
        # Home directory
        shell.execute("cd ~")
        result = shell.execute("pwd")
        assert shell.environ["HOME"] in result

    def test_special_variables(self):
        """Test special shell variables."""
        shell = ShellInterpreter()
        
        # $? - last command exit status
        shell.execute("true")
        result = shell.execute("echo $?")
        assert "0" in result
        
        shell.execute("false")
        result = shell.execute("echo $?")
        assert "1" in result
        
        # $$ - shell PID (simulated)
        result = shell.execute("echo $$")
        assert result.strip().isdigit()

    def test_filesystem_operations(self):
        """Test filesystem operations through shell."""
        shell = ShellInterpreter()
        
        # Create directory structure
        shell.execute("mkdir -p /project/src/components")
        shell.execute("mkdir -p /project/tests")
        
        # Create files
        shell.execute("echo 'import React' > /project/src/index.js")
        shell.execute("touch /project/README.md")
        
        # Copy files
        shell.execute("cp /project/src/index.js /project/src/index.backup.js")
        result = shell.execute("ls /project/src")
        assert "index.js" in result
        assert "index.backup.js" in result
        
        # Move files
        shell.execute("mv /project/README.md /project/README.txt")
        result = shell.execute("ls /project")
        assert "README.txt" in result
        assert "README.md" not in result
        
        # Remove files
        shell.execute("rm /project/src/index.backup.js")
        result = shell.execute("ls /project/src")
        assert "index.backup.js" not in result

    def test_command_timing(self):
        """Test command timing functionality."""
        shell = ShellInterpreter()
        
        # Enable timing
        shell.execute("timings -e")
        assert shell.enable_timing is True
        
        # Execute some commands
        shell.execute("echo test")
        shell.execute("ls /")
        shell.execute("pwd")
        
        # Check timing statistics
        result = shell.execute("timings")
        assert "echo" in result or "Command" in result
        
        # Disable timing
        shell.execute("timings -d")
        assert shell.enable_timing is False

    def test_error_handling(self):
        """Test error handling in shell."""
        shell = ShellInterpreter()
        
        # Command not found
        result = shell.execute("nonexistent_command")
        assert "command not found" in result.lower()
        
        # File not found
        result = shell.execute("cat /nonexistent/file.txt")
        assert "not found" in result.lower() or "error" in result.lower()
        
        # Directory operations on files
        result = shell.execute("touch /file.txt && cd /file.txt")
        assert "not a directory" in result.lower() or "error" in result.lower()