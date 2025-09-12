"""Tests for .shellrc loading functionality."""

import logging
from chuk_virtual_shell.shell_interpreter import ShellInterpreter
from chuk_virtual_fs import VirtualFileSystem
from chuk_virtual_shell.filesystem_compat import FileSystemCompat


class TestShellRCLoading:
    """Test cases for .shellrc file loading."""

    def test_shellrc_not_found(self, caplog):
        """Test that missing .shellrc doesn't cause errors."""
        with caplog.at_level(logging.DEBUG):
            shell = ShellInterpreter()

        # Should not have any errors, just debug messages
        assert shell.aliases == {}
        assert shell.enable_timing is False

    def test_shellrc_loads_from_home(self):
        """Test that .shellrc loads from home directory."""
        # Create filesystem with .shellrc
        raw_fs = VirtualFileSystem()
        fs = FileSystemCompat(raw_fs)

        # Create .shellrc before shell initialization
        fs.mkdir("/home")
        fs.mkdir("/home/user")
        shellrc_content = """# Test shellrc
export TEST_VAR=test_value
alias ll="ls -la"
alias test="echo test"
timings -e
"""
        fs.write_file("/home/user/.shellrc", shellrc_content)

        # Create shell and manually initialize with the filesystem
        shell = ShellInterpreter()
        shell.fs = fs
        shell._setup_default_environment()
        shell._load_commands()
        shell.aliases = {}
        shell.enable_timing = False
        shell.command_timing = {}
        shell._load_shellrc()

        # Check that settings were applied
        assert shell.environ.get("TEST_VAR") == "test_value"
        assert shell.aliases["ll"] == "ls -la"
        assert shell.aliases["test"] == "echo test"
        assert shell.enable_timing is True

    def test_shellrc_loads_from_root_fallback(self):
        """Test that .shellrc loads from root if not in home."""
        raw_fs = VirtualFileSystem()
        fs = FileSystemCompat(raw_fs)

        # Create .shellrc in root
        shellrc_content = """alias root="echo root"
export ROOT_VAR=root_value"""
        fs.write_file("/.shellrc", shellrc_content)

        # Create shell
        shell = ShellInterpreter()
        shell.fs = fs
        shell._setup_default_environment()
        shell._load_commands()
        shell.aliases = {}
        shell._load_shellrc()

        assert shell.aliases["root"] == "echo root"
        assert shell.environ.get("ROOT_VAR") == "root_value"

    def test_shellrc_skips_comments_and_empty_lines(self):
        """Test that comments and empty lines are ignored."""
        raw_fs = VirtualFileSystem()
        fs = FileSystemCompat(raw_fs)

        fs.mkdir("/home")
        fs.mkdir("/home/user")
        shellrc_content = """# This is a comment
# Another comment

alias test="echo test"

# More comments
   # Indented comment
"""
        fs.write_file("/home/user/.shellrc", shellrc_content)

        shell = ShellInterpreter()
        shell.fs = fs
        shell._setup_default_environment()
        shell._load_commands()
        shell.aliases = {}
        shell._load_shellrc()

        # Only the alias should be set
        assert len(shell.aliases) == 1
        assert shell.aliases["test"] == "echo test"

    def test_shellrc_error_handling(self, caplog):
        """Test that errors in .shellrc are handled gracefully."""
        raw_fs = VirtualFileSystem()
        fs = FileSystemCompat(raw_fs)

        fs.mkdir("/home")
        fs.mkdir("/home/user")
        # Create .shellrc with invalid command
        shellrc_content = """alias good="echo good"
invalid_command_that_doesnt_exist
alias another="echo another"
"""
        fs.write_file("/home/user/.shellrc", shellrc_content)

        with caplog.at_level(logging.WARNING):
            shell = ShellInterpreter()
            shell.fs = fs
            shell._setup_default_environment()
            shell._load_commands()
            shell.aliases = {}
            shell._load_shellrc()

        # Good aliases should still be set
        assert shell.aliases["good"] == "echo good"
        assert shell.aliases["another"] == "echo another"

        # Check if there was any warning logged (might vary based on implementation)
        # The invalid command should trigger some warning/error
        warning_records = [r for r in caplog.records if r.levelname == "WARNING"]
        # Should have at least a warning about creating home directory or executing shellrc line
        assert len(warning_records) > 0

    def test_shellrc_complex_configuration(self):
        """Test loading complex .shellrc with multiple settings."""
        raw_fs = VirtualFileSystem()
        fs = FileSystemCompat(raw_fs)

        fs.mkdir("/home")
        fs.mkdir("/home/user")
        shellrc_content = """# Complex .shellrc configuration

# Environment variables
export EDITOR=nano
export PAGER=less
export MY_PATH=/usr/local/bin:/usr/bin:/bin

# Aliases
alias ll="ls -la"
alias la="ls -a"
alias l="ls -CF"
alias ..="cd .."
alias ...="cd ../.."
alias grep="grep --color=auto"
alias rm="rm -i"
alias cp="cp -i"
alias mv="mv -i"

# Enable command timing
timings -e

# Create some test files
mkdir -p /tmp/test
touch /tmp/test/file1.txt
echo "test content" > /tmp/test/file2.txt
"""
        fs.write_file("/home/user/.shellrc", shellrc_content)

        shell = ShellInterpreter()
        shell.fs = fs
        shell._setup_default_environment()
        shell._load_commands()
        shell.aliases = {}
        shell.enable_timing = False
        shell.command_timing = {}
        shell._load_shellrc()

        # Check environment variables
        assert shell.environ.get("EDITOR") == "nano"
        assert shell.environ.get("PAGER") == "less"
        assert shell.environ.get("MY_PATH") == "/usr/local/bin:/usr/bin:/bin"

        # Check aliases
        assert shell.aliases["ll"] == "ls -la"
        assert shell.aliases["la"] == "ls -a"
        assert shell.aliases[".."] == "cd .."
        assert shell.aliases["grep"] == "grep --color=auto"
        assert shell.aliases["rm"] == "rm -i"

        # Check timing is enabled
        assert shell.enable_timing is True

        # Check that files were created
        assert fs.exists("/tmp/test")
        assert fs.exists("/tmp/test/file1.txt")
        assert fs.exists("/tmp/test/file2.txt")
        assert fs.read_file("/tmp/test/file2.txt").strip() == "test content"

    def test_shellrc_alias_with_quotes(self):
        """Test that aliases with quotes are handled correctly."""
        raw_fs = VirtualFileSystem()
        fs = FileSystemCompat(raw_fs)

        fs.mkdir("/home")
        fs.mkdir("/home/user")
        shellrc_content = """alias single='echo "single quotes"'
alias double="echo 'double quotes'"
alias mixed='grep "pattern" file.txt'
"""
        fs.write_file("/home/user/.shellrc", shellrc_content)

        shell = ShellInterpreter()
        shell.fs = fs
        shell._setup_default_environment()
        shell._load_commands()
        shell.aliases = {}
        shell._load_shellrc()

        assert shell.aliases["single"] == 'echo "single quotes"'
        assert shell.aliases["double"] == "echo 'double quotes'"
        assert shell.aliases["mixed"] == 'grep "pattern" file.txt'

    def test_shellrc_only_first_file_loaded(self):
        """Test that only the first .shellrc found is loaded."""
        raw_fs = VirtualFileSystem()
        fs = FileSystemCompat(raw_fs)

        # Create both home and root .shellrc
        fs.mkdir("/home")
        fs.mkdir("/home/user")
        fs.write_file("/home/user/.shellrc", 'alias home="echo home"')
        fs.write_file("/.shellrc", 'alias root="echo root"')

        shell = ShellInterpreter()
        shell.fs = fs
        shell._setup_default_environment()
        shell._load_commands()
        shell.aliases = {}
        shell._load_shellrc()

        # Only home .shellrc should be loaded
        assert shell.aliases.get("home") == "echo home"
        assert "root" not in shell.aliases

    def test_shellrc_command_execution_order(self):
        """Test that .shellrc commands are executed in order."""
        raw_fs = VirtualFileSystem()
        fs = FileSystemCompat(raw_fs)

        fs.mkdir("/home")
        fs.mkdir("/home/user")
        shellrc_content = """export VAR1=first
export VAR2=$VAR1_second
export VAR1=changed
alias test="echo $VAR1"
"""
        fs.write_file("/home/user/.shellrc", shellrc_content)

        shell = ShellInterpreter()
        shell.fs = fs
        shell._setup_default_environment()
        shell._load_commands()
        shell.aliases = {}
        shell._load_shellrc()

        # VAR1 should be changed
        assert shell.environ.get("VAR1") == "changed"
        # VAR2 should be empty string since $VAR1_second variable doesn't exist
        # (bash behavior: looking for variable named VAR1_second, not VAR1 + "_second")
        assert shell.environ.get("VAR2") == ""
        # Alias should have the literal string with variable
        assert shell.aliases["test"] == "echo $VAR1"
