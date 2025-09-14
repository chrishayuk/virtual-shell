"""Tests for the which command."""

import pytest
from chuk_virtual_shell.shell_interpreter import ShellInterpreter
from chuk_virtual_shell.commands.system.which import WhichCommand


@pytest.fixture
def shell():
    """Create a shell instance for testing."""
    return ShellInterpreter()


class TestWhichCommand:
    """Test cases for the which command."""

    def test_which_builtin_command(self, shell):
        """Test finding a built-in command."""
        which_cmd = WhichCommand(shell)

        # Add some commands to the shell
        shell.commands = {"ls": "dummy", "cd": "dummy", "pwd": "dummy"}

        result = which_cmd.execute(["ls"])
        assert result == "ls: shell built-in command"

    def test_which_multiple_commands(self, shell):
        """Test finding multiple commands."""
        which_cmd = WhichCommand(shell)
        shell.commands = {"ls": "dummy", "cd": "dummy", "pwd": "dummy"}

        result = which_cmd.execute(["ls", "cd", "pwd"])
        assert "ls: shell built-in command" in result
        assert "cd: shell built-in command" in result
        assert "pwd: shell built-in command" in result

    def test_which_command_not_found(self, shell):
        """Test when command is not found."""
        which_cmd = WhichCommand(shell)
        shell.commands = {}

        result = which_cmd.execute(["nonexistent"])
        assert "nonexistent not found" in result

    def test_which_path_search(self, shell):
        """Test searching in PATH."""
        which_cmd = WhichCommand(shell)
        shell.commands = {}
        shell.environ["PATH"] = "/usr/bin:/bin"

        # Create executable in PATH
        shell.fs.mkdir("/usr")
        shell.fs.mkdir("/usr/bin")
        shell.fs.touch("/usr/bin/python")

        result = which_cmd.execute(["python"])
        assert "/usr/bin/python" in result

    def test_which_all_flag(self, shell):
        """Test -a flag to show all matches."""
        which_cmd = WhichCommand(shell)
        shell.commands = {"python": "dummy"}
        shell.environ["PATH"] = "/usr/bin:/bin:/usr/local/bin"

        # Create multiple python executables
        shell.fs.mkdir("/usr")
        shell.fs.mkdir("/usr/bin")
        shell.fs.mkdir("/usr/local")
        shell.fs.mkdir("/usr/local/bin")
        shell.fs.mkdir("/bin")
        shell.fs.touch("/usr/bin/python")
        shell.fs.touch("/usr/local/bin/python")

        result = which_cmd.execute(["-a", "python"])
        assert "python: shell built-in command" in result
        assert "/usr/bin/python" in result
        assert "/usr/local/bin/python" in result

    def test_which_no_arguments(self, shell):
        """Test with no arguments."""
        which_cmd = WhichCommand(shell)

        result = which_cmd.execute([])
        assert "no command specified" in result

    def test_which_invalid_option(self, shell):
        """Test with invalid option."""
        which_cmd = WhichCommand(shell)

        result = which_cmd.execute(["-x", "ls"])
        assert "invalid option" in result

    def test_which_builtin_precedence(self, shell):
        """Test that built-in commands take precedence over PATH."""
        which_cmd = WhichCommand(shell)
        shell.commands = {"ls": "dummy"}
        shell.environ["PATH"] = "/bin"

        # Create ls in PATH
        shell.fs.mkdir("/bin")
        shell.fs.touch("/bin/ls")

        # Without -a, should only show built-in
        result = which_cmd.execute(["ls"])
        assert result == "ls: shell built-in command"

        # With -a, should show both
        result = which_cmd.execute(["-a", "ls"])
        assert "ls: shell built-in command" in result
        assert "/bin/ls" in result

    def test_which_multiple_paths(self, shell):
        """Test searching multiple directories in PATH."""
        which_cmd = WhichCommand(shell)
        shell.commands = {}
        shell.environ["PATH"] = "/usr/bin:/bin:/usr/local/bin"

        # Create commands in different directories
        shell.fs.mkdir("/usr")
        shell.fs.mkdir("/usr/bin")
        shell.fs.mkdir("/bin")
        shell.fs.mkdir("/usr/local")
        shell.fs.mkdir("/usr/local/bin")

        shell.fs.touch("/usr/bin/gcc")
        shell.fs.touch("/bin/sh")
        shell.fs.touch("/usr/local/bin/node")

        # Test each command
        assert "/usr/bin/gcc" in which_cmd.execute(["gcc"])
        assert "/bin/sh" in which_cmd.execute(["sh"])
        assert "/usr/local/bin/node" in which_cmd.execute(["node"])

    def test_which_nonexecutable_files(self, shell):
        """Test that directories are not returned as commands."""
        which_cmd = WhichCommand(shell)
        shell.commands = {}
        shell.environ["PATH"] = "/bin"

        # Create a directory with the same name as a command
        shell.fs.mkdir("/bin")
        shell.fs.mkdir("/bin/ls")  # This is a directory, not a file

        result = which_cmd.execute(["ls"])
        assert "ls not found" in result
