"""
Comprehensive test suite for the ShellInterpreter class.
Tests all core functionality, edge cases, and integration points.
"""

import pytest
import os
import time
from chuk_virtual_shell.shell_interpreter import ShellInterpreter
from chuk_virtual_fs import VirtualFileSystem
from chuk_virtual_shell.filesystem_compat import FileSystemCompat


class TestShellInterpreterCore:
    """Test core shell interpreter functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.shell = ShellInterpreter()

    def test_initialization(self):
        """Test shell initialization with all components."""
        assert self.shell.fs is not None
        assert self.shell.environ is not None
        assert self.shell.env_manager is not None
        assert self.shell.parser is not None
        assert self.shell.expansion is not None
        assert self.shell.executor is not None
        assert self.shell.commands is not None
        assert self.shell.history == []
        assert self.shell.running is True
        assert self.shell.return_code == 0
        assert self.shell.current_user == self.shell.environ.get("USER", "user")

    def test_default_environment(self):
        """Test default environment variables are set."""
        required_vars = ["HOME", "PATH", "USER", "PWD", "SHELL", "OLDPWD"]
        for var in required_vars:
            assert var in self.shell.environ, f"Missing environment variable: {var}"
        
        # Check PATH contains expected directories
        path = self.shell.environ["PATH"]
        assert "/bin" in path
        assert "/usr/bin" in path

    def test_command_loading(self):
        """Test that commands are loaded properly."""
        # Check some essential commands are loaded
        essential_commands = ["echo", "ls", "cd", "pwd", "cat", "grep", "mkdir", "touch"]
        for cmd in essential_commands:
            assert cmd in self.shell.commands, f"Missing command: {cmd}"

    def test_resolve_path(self):
        """Test path resolution."""
        # Test absolute path
        assert self.shell.resolve_path("/test") == "/test"
        
        # Test relative path from root
        self.shell.execute("cd /")
        assert self.shell.resolve_path("test") == "/test"
        
        # Test relative path from subdirectory
        self.shell.execute("mkdir -p /dir/subdir")
        self.shell.execute("cd /dir")
        assert self.shell.resolve_path("subdir") == "/dir/subdir"
        
        # Test . and ..
        assert self.shell.resolve_path(".") == "/dir"
        assert self.shell.resolve_path("..") == "/"
        
        # Test home directory
        home = self.shell.environ["HOME"]
        assert self.shell.resolve_path("~") == home
        assert self.shell.resolve_path("~/test") == f"{home}/test"


class TestCommandExecution:
    """Test command execution and return codes."""

    def setup_method(self):
        """Set up test environment."""
        self.shell = ShellInterpreter()

    def test_simple_commands(self):
        """Test execution of simple commands."""
        # Echo command
        result = self.shell.execute("echo Hello World")
        assert result == "Hello World"
        assert self.shell.return_code == 0
        
        # PWD command
        result = self.shell.execute("pwd")
        assert result == "/"
        assert self.shell.return_code == 0
        
        # Touch and ls
        self.shell.execute("touch test.txt")
        result = self.shell.execute("ls")
        assert "test.txt" in result
        assert self.shell.return_code == 0

    def test_command_not_found(self):
        """Test handling of non-existent commands."""
        result = self.shell.execute("nonexistent_command")
        assert "command not found" in result.lower()
        assert self.shell.return_code != 0

    def test_return_codes(self):
        """Test command return codes."""
        # Test 'true' command (should succeed)
        self.shell.execute("true")
        assert self.shell.return_code == 0
        
        # Test 'false' command (should fail)
        self.shell.execute("false")
        assert self.shell.return_code == 1
        
        # Test command with error
        result = self.shell.execute("cat /nonexistent/file")
        assert self.shell.return_code != 0

    def test_empty_command(self):
        """Test handling of empty commands."""
        result = self.shell.execute("")
        assert result == ""
        assert self.shell.return_code == 0
        
        result = self.shell.execute("   ")
        assert result == ""
        assert self.shell.return_code == 0

    def test_command_with_arguments(self):
        """Test commands with various argument types."""
        # Single argument
        result = self.shell.execute("echo test")
        assert result == "test"
        
        # Multiple arguments
        result = self.shell.execute("echo one two three")
        assert result == "one two three"
        
        # Quoted arguments
        result = self.shell.execute('echo "hello world"')
        assert result == "hello world"
        
        # Mixed quotes
        result = self.shell.execute('''echo "double" 'single' unquoted''')
        assert "double" in result
        assert "single" in result
        assert "unquoted" in result


class TestVariableExpansion:
    """Test environment variable expansion functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.shell = ShellInterpreter()

    def test_simple_expansion(self):
        """Test basic variable expansion."""
        self.shell.execute("export TEST=value")
        result = self.shell.execute("echo $TEST")
        assert result == "value"

    def test_braced_expansion(self):
        """Test ${VAR} style expansion."""
        self.shell.execute("export VAR=test")
        result = self.shell.execute("echo ${VAR}ing")
        assert result == "testing"

    def test_undefined_variable(self):
        """Test expansion of undefined variables."""
        result = self.shell.execute("echo $UNDEFINED")
        assert result == ""

    def test_special_variables(self):
        """Test special shell variables."""
        # $? - last exit status
        self.shell.execute("true")
        result = self.shell.execute("echo $?")
        assert result == "0"
        
        self.shell.execute("false")
        result = self.shell.execute("echo $?")
        assert result == "1"
        
        # $$ - process ID (simulated)
        result = self.shell.execute("echo $$")
        assert result.isdigit()
        
        # $HOME
        result = self.shell.execute("echo $HOME")
        assert result == self.shell.environ["HOME"]
        
        # $PWD
        result = self.shell.execute("echo $PWD")
        assert result == self.shell.environ["PWD"]

    def test_variable_in_strings(self):
        """Test variable expansion in quoted strings."""
        self.shell.execute("export NAME=World")
        
        # Double quotes - should expand
        result = self.shell.execute('echo "Hello $NAME"')
        assert result == "Hello World"
        
        # Single quotes - should not expand
        result = self.shell.execute("echo 'Hello $NAME'")
        assert result == "Hello $NAME"

    def test_multiple_variables(self):
        """Test multiple variable expansions."""
        self.shell.execute("export VAR1=first")
        self.shell.execute("export VAR2=second")
        result = self.shell.execute("echo $VAR1 and $VAR2")
        assert result == "first and second"

    def test_nested_expansion(self):
        """Test nested variable expansion."""
        self.shell.execute("export PREFIX=TEST")
        self.shell.execute("export TEST_VAR=value")
        # Note: Full indirect expansion might not be supported
        result = self.shell.execute("echo $TEST_VAR")
        assert result == "value"


class TestGlobExpansion:
    """Test glob pattern expansion."""

    def setup_method(self):
        """Set up test environment."""
        self.shell = ShellInterpreter()
        # Create test file structure
        self.shell.execute("mkdir -p /test/dir")
        self.shell.execute("touch /test/file1.txt /test/file2.txt /test/file3.log")
        self.shell.execute("touch /test/data.csv /test/readme.md")
        self.shell.execute("touch /test/dir/nested.txt")

    def test_star_glob(self):
        """Test * wildcard expansion."""
        result = self.shell.execute("ls /test/*.txt")
        assert "file1.txt" in result
        assert "file2.txt" in result
        assert "file3.log" not in result
        assert "data.csv" not in result

    def test_question_glob(self):
        """Test ? wildcard expansion."""
        result = self.shell.execute("ls /test/file?.txt")
        assert "file1.txt" in result
        assert "file2.txt" in result
        # file3.log should not match

    def test_multiple_globs(self):
        """Test multiple glob patterns."""
        result = self.shell.execute("ls /test/*.txt /test/*.log")
        assert "file1.txt" in result
        assert "file2.txt" in result
        assert "file3.log" in result

    def test_no_match_glob(self):
        """Test glob with no matches."""
        result = self.shell.execute("ls /test/*.xyz")
        # Should either show the pattern literally or an error
        assert "*.xyz" in result or "not found" in result.lower()

    def test_glob_in_subdirs(self):
        """Test glob patterns with subdirectories."""
        result = self.shell.execute("ls /test/dir/*.txt")
        assert "nested.txt" in result

    def test_glob_with_commands(self):
        """Test glob expansion with various commands."""
        # With rm
        self.shell.execute("rm /test/*.log")
        result = self.shell.execute("ls /test")
        assert "file3.log" not in result
        assert "file1.txt" in result  # Should still exist
        
        # With cp
        self.shell.execute("cp /test/*.txt /test/dir/")
        result = self.shell.execute("ls /test/dir")
        assert "file1.txt" in result
        assert "file2.txt" in result


class TestCommandSubstitution:
    """Test command substitution functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.shell = ShellInterpreter()

    def test_dollar_paren_substitution(self):
        """Test $(command) substitution."""
        self.shell.execute("cd /home")
        result = self.shell.execute("echo Current: $(pwd)")
        assert "Current: /home" in result

    def test_backtick_substitution(self):
        """Test `command` substitution."""
        self.shell.execute("echo test > /file.txt")
        result = self.shell.execute("echo Content: `cat /file.txt`")
        assert "Content: test" in result

    def test_nested_substitution(self):
        """Test nested command substitutions."""
        self.shell.execute("echo 3 > /count.txt")
        self.shell.execute("touch /f1.txt /f2.txt /f3.txt")
        result = self.shell.execute("echo Files: $(ls /*.txt | wc -l)")
        assert "Files: 4" in result or "Files: 4" in result.strip()

    def test_substitution_with_pipes(self):
        """Test command substitution with pipes."""
        self.shell.execute("echo -e 'one\\ntwo\\nthree' > /lines.txt")
        result = self.shell.execute("echo Lines with 'e': $(cat /lines.txt | grep e | wc -l)")
        assert "2" in result  # 'one' and 'three' contain 'e'

    def test_substitution_in_variables(self):
        """Test command substitution in variable assignment."""
        self.shell.execute("export COUNT=$(ls / | wc -l)")
        result = self.shell.execute("echo $COUNT")
        assert result.strip().isdigit()


class TestPipesAndRedirection:
    """Test pipe and I/O redirection functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.shell = ShellInterpreter()

    def test_simple_pipe(self):
        """Test simple pipe between two commands."""
        self.shell.execute("echo -e 'apple\\nbanana\\ncherry' > /fruits.txt")
        result = self.shell.execute("cat /fruits.txt | grep a")
        assert "apple" in result
        assert "banana" in result
        # cherry should not appear (no 'a' in cherry)

    def test_multiple_pipes(self):
        """Test chaining multiple pipes."""
        self.shell.execute("echo -e 'one\\ntwo\\nthree\\nfour' > /numbers.txt")
        result = self.shell.execute("cat /numbers.txt | grep o | wc -l")
        assert "3" in result.strip()  # one, two, four contain 'o'

    def test_output_redirection(self):
        """Test > output redirection."""
        self.shell.execute("echo test > /out.txt")
        result = self.shell.execute("cat /out.txt")
        assert result.strip() == "test"
        
        # Overwrite test
        self.shell.execute("echo new > /out.txt")
        result = self.shell.execute("cat /out.txt")
        assert result.strip() == "new"
        assert "test" not in result

    def test_append_redirection(self):
        """Test >> append redirection."""
        self.shell.execute("echo first > /append.txt")
        self.shell.execute("echo second >> /append.txt")
        result = self.shell.execute("cat /append.txt")
        assert "first" in result
        assert "second" in result

    def test_input_redirection(self):
        """Test < input redirection."""
        self.shell.execute("echo 'search term' > /input.txt")
        result = self.shell.execute("grep search < /input.txt")
        assert "search term" in result

    def test_combined_redirections(self):
        """Test combinations of pipes and redirections."""
        # Pipe to file
        self.shell.execute("echo -e 'a\\nb\\nc' | grep b > /result.txt")
        result = self.shell.execute("cat /result.txt")
        assert "b" in result
        
        # File to pipe to file
        self.shell.execute("echo -e 'x\\ny\\nz' > /source.txt")
        self.shell.execute("cat /source.txt | grep y > /dest.txt")
        result = self.shell.execute("cat /dest.txt")
        assert "y" in result

    def test_stderr_redirection(self):
        """Test stderr redirection."""
        # Command that produces an error
        result = self.shell.execute("cat /nonexistent 2> /error.txt")
        error_content = self.shell.fs.read_file("/error.txt")
        assert "not found" in error_content.lower() or "error" in error_content.lower()


class TestCommandChaining:
    """Test command chaining operators."""

    def setup_method(self):
        """Set up test environment."""
        self.shell = ShellInterpreter()

    def test_and_operator(self):
        """Test && operator."""
        # Both succeed
        result = self.shell.execute("echo first && echo second")
        assert "first" in result
        assert "second" in result
        
        # First fails
        result = self.shell.execute("false && echo should_not_appear")
        assert "should_not_appear" not in result
        
        # First succeeds, second fails
        result = self.shell.execute("true && false")
        assert self.shell.return_code != 0

    def test_or_operator(self):
        """Test || operator."""
        # First succeeds
        result = self.shell.execute("echo success || echo fallback")
        assert "success" in result
        assert "fallback" not in result
        
        # First fails
        result = self.shell.execute("false || echo fallback")
        assert "fallback" in result
        
        # Both fail
        self.shell.execute("false || false")
        assert self.shell.return_code != 0

    def test_semicolon_separator(self):
        """Test ; command separator."""
        result = self.shell.execute("echo one; echo two; echo three")
        assert "one" in result
        assert "two" in result
        assert "three" in result
        
        # With failed command
        result = self.shell.execute("echo before; false; echo after")
        assert "before" in result
        assert "after" in result

    def test_mixed_operators(self):
        """Test combinations of operators."""
        result = self.shell.execute("echo start && echo middle || echo fallback; echo end")
        assert "start" in result
        assert "middle" in result
        assert "fallback" not in result
        assert "end" in result
        
        result = self.shell.execute("false && echo skip || echo shown; echo always")
        assert "skip" not in result
        assert "shown" in result
        assert "always" in result

    def test_operators_with_pipes(self):
        """Test operators combined with pipes."""
        self.shell.execute("echo 'test' > /test.txt")
        result = self.shell.execute("cat /test.txt | grep test && echo found || echo not_found")
        assert "test" in result
        assert "found" in result
        assert "not_found" not in result


class TestAliases:
    """Test alias functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.shell = ShellInterpreter()

    def test_create_alias(self):
        """Test creating aliases."""
        self.shell.execute('alias ll="ls -la"')
        assert "ll" in self.shell.aliases
        assert self.shell.aliases["ll"] == "ls -la"

    def test_use_alias(self):
        """Test using aliases."""
        self.shell.execute('alias ll="ls -la"')
        self.shell.execute("touch /test.txt")
        result = self.shell.execute("ll /")
        assert "test.txt" in result

    def test_list_aliases(self):
        """Test listing all aliases."""
        self.shell.execute('alias l="ls"')
        self.shell.execute('alias ll="ls -la"')
        result = self.shell.execute("alias")
        assert "l=" in result or "l =" in result
        assert "ll=" in result or "ll =" in result

    def test_unalias(self):
        """Test removing aliases."""
        self.shell.execute('alias test="echo test"')
        assert "test" in self.shell.aliases
        self.shell.execute("unalias test")
        assert "test" not in self.shell.aliases

    def test_alias_expansion(self):
        """Test alias expansion in commands."""
        self.shell.execute('alias greet="echo Hello"')
        result = self.shell.execute("greet World")
        assert "Hello World" in result

    def test_nested_aliases(self):
        """Test aliases that reference other aliases."""
        self.shell.execute('alias l="ls"')
        self.shell.execute('alias ll="l -la"')
        self.shell.execute("touch /file.txt")
        result = self.shell.execute("ll /")
        assert "file.txt" in result


class TestWorkingDirectory:
    """Test working directory management."""

    def setup_method(self):
        """Set up test environment."""
        self.shell = ShellInterpreter()

    def test_initial_directory(self):
        """Test initial working directory."""
        result = self.shell.execute("pwd")
        assert result.strip() == "/"

    def test_cd_absolute(self):
        """Test cd with absolute paths."""
        self.shell.execute("mkdir -p /test/subdir")
        self.shell.execute("cd /test")
        result = self.shell.execute("pwd")
        assert result.strip() == "/test"
        
        self.shell.execute("cd /test/subdir")
        result = self.shell.execute("pwd")
        assert result.strip() == "/test/subdir"

    def test_cd_relative(self):
        """Test cd with relative paths."""
        self.shell.execute("mkdir -p /a/b/c")
        self.shell.execute("cd /a")
        self.shell.execute("cd b")
        result = self.shell.execute("pwd")
        assert result.strip() == "/a/b"
        
        self.shell.execute("cd c")
        result = self.shell.execute("pwd")
        assert result.strip() == "/a/b/c"

    def test_cd_parent(self):
        """Test cd with .. (parent directory)."""
        self.shell.execute("mkdir -p /one/two/three")
        self.shell.execute("cd /one/two/three")
        self.shell.execute("cd ..")
        result = self.shell.execute("pwd")
        assert result.strip() == "/one/two"
        
        self.shell.execute("cd ../..")
        result = self.shell.execute("pwd")
        assert result.strip() == "/"

    def test_cd_home(self):
        """Test cd to home directory."""
        home = self.shell.environ["HOME"]
        self.shell.execute("cd /tmp")
        self.shell.execute("cd ~")
        result = self.shell.execute("pwd")
        assert result.strip() == home
        
        self.shell.execute("cd")  # cd with no args should go home
        result = self.shell.execute("pwd")
        assert result.strip() == home

    def test_cd_oldpwd(self):
        """Test cd - (previous directory)."""
        self.shell.execute("mkdir -p /first /second")
        self.shell.execute("cd /first")
        self.shell.execute("cd /second")
        self.shell.execute("cd -")
        result = self.shell.execute("pwd")
        assert result.strip() == "/first"

    def test_pwd_update(self):
        """Test that PWD environment variable is updated."""
        self.shell.execute("mkdir /testdir")
        self.shell.execute("cd /testdir")
        assert self.shell.environ["PWD"] == "/testdir"
        result = self.shell.execute("echo $PWD")
        assert result.strip() == "/testdir"


class TestCommandHistory:
    """Test command history functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.shell = ShellInterpreter()

    def test_history_recording(self):
        """Test that commands are recorded in history."""
        commands = ["echo first", "echo second", "echo third"]
        for cmd in commands:
            self.shell.execute(cmd)
        
        for cmd in commands:
            assert cmd in self.shell.history

    def test_history_command(self):
        """Test the history command."""
        self.shell.execute("echo one")
        self.shell.execute("echo two")
        self.shell.execute("echo three")
        
        result = self.shell.execute("history")
        assert "echo one" in result
        assert "echo two" in result
        assert "echo three" in result

    def test_history_limit(self):
        """Test history with limit."""
        for i in range(10):
            self.shell.execute(f"echo {i}")
        
        result = self.shell.execute("history 3")
        lines = result.strip().split('\n')
        assert len(lines) <= 3

    def test_history_search(self):
        """Test history search."""
        self.shell.execute("echo test")
        self.shell.execute("ls /")
        self.shell.execute("echo another")
        
        result = self.shell.execute("history echo")
        assert "echo test" in result
        assert "echo another" in result
        assert "ls" not in result


class TestCommandTiming:
    """Test command timing functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.shell = ShellInterpreter()

    def test_enable_timing(self):
        """Test enabling command timing."""
        self.shell.execute("timings -e")
        assert self.shell.enable_timing is True

    def test_disable_timing(self):
        """Test disabling command timing."""
        self.shell.execute("timings -e")
        self.shell.execute("timings -d")
        assert self.shell.enable_timing is False

    def test_timing_statistics(self):
        """Test timing statistics collection."""
        self.shell.execute("timings -e")
        self.shell.execute("echo test")
        self.shell.execute("ls /")
        self.shell.execute("pwd")
        self.shell.execute("echo test")  # Run echo twice
        
        result = self.shell.execute("timings")
        # Should show timing stats
        assert "echo" in result or "Command" in result

    def test_timing_clear(self):
        """Test clearing timing statistics."""
        self.shell.execute("timings -e")
        self.shell.execute("echo test")
        self.shell.execute("timings -c")
        assert len(self.shell.command_timing) == 0


class TestShellrcLoading:
    """Test .shellrc file loading."""

    def setup_method(self):
        """Set up test environment."""
        # Create a shell without automatic shellrc loading
        self.shell = ShellInterpreter()

    def test_shellrc_loading(self):
        """Test loading .shellrc on initialization."""
        # Create .shellrc
        shellrc_content = """export TEST_RC=loaded
alias rctest="echo RC Test"
timings -e"""
        
        self.shell.fs.write_file("/home/user/.shellrc", shellrc_content)
        
        # Create new shell to trigger loading
        new_shell = ShellInterpreter()
        
        # Check environment variable
        assert new_shell.environ.get("TEST_RC") == "loaded"
        
        # Check alias
        assert "rctest" in new_shell.aliases
        
        # Check timing enabled
        assert new_shell.enable_timing is True

    def test_shellrc_with_errors(self):
        """Test .shellrc with invalid commands."""
        shellrc_content = """export VALID=yes
invalid_command
alias valid="echo valid" """
        
        self.shell.fs.write_file("/home/user/.shellrc", shellrc_content)
        
        # Should not crash on invalid commands
        new_shell = ShellInterpreter()
        assert new_shell.environ.get("VALID") == "yes"
        assert "valid" in new_shell.aliases


class TestErrorHandling:
    """Test error handling and edge cases."""

    def setup_method(self):
        """Set up test environment."""
        self.shell = ShellInterpreter()

    def test_malformed_commands(self):
        """Test handling of malformed commands."""
        # Unclosed quotes
        result = self.shell.execute('echo "unclosed')
        # Should handle gracefully
        assert "unclosed" in result or "error" in result.lower()
        
        # Empty pipes
        result = self.shell.execute("echo test |")
        # Should handle gracefully
        
        # Invalid redirections
        result = self.shell.execute("echo test >")
        # Should handle gracefully

    def test_permission_errors(self):
        """Test handling of permission-like errors."""
        # Try to cd to a file
        self.shell.execute("touch /file.txt")
        result = self.shell.execute("cd /file.txt")
        assert "not a directory" in result.lower() or "error" in result.lower()

    def test_recursive_substitution(self):
        """Test protection against infinite recursion."""
        # This should not hang
        result = self.shell.execute("echo $(echo $(echo test))")
        assert "test" in result

    def test_large_output(self):
        """Test handling of large command output."""
        # Create many files
        for i in range(100):
            self.shell.execute(f"touch /file{i}.txt")
        
        # Should handle large ls output
        result = self.shell.execute("ls /")
        assert "file0.txt" in result
        assert "file99.txt" in result

    def test_special_characters(self):
        """Test handling of special characters."""
        # Filenames with spaces
        self.shell.execute('touch "/file with spaces.txt"')
        result = self.shell.execute("ls /")
        assert "file with spaces.txt" in result
        
        # Special characters in echo
        result = self.shell.execute('echo "!@#$%^&*()"')
        assert "!@#$%^&*()" in result


class TestIntegration:
    """Integration tests for complex scenarios."""

    def setup_method(self):
        """Set up test environment."""
        self.shell = ShellInterpreter()

    def test_complex_pipeline(self):
        """Test complex command pipeline."""
        # Create test data
        self.shell.execute("mkdir -p /data")
        for i in range(10):
            self.shell.execute(f"echo 'Line {i}' > /data/file{i}.txt")
        
        # Complex pipeline
        result = self.shell.execute("ls /data | grep file | head -5 | wc -l")
        assert "5" in result.strip()

    def test_script_like_execution(self):
        """Test executing multiple related commands."""
        commands = [
            "mkdir -p /project/src",
            "cd /project",
            "echo '# My Project' > README.md",
            "cd src",
            "echo 'print(\"Hello\")' > main.py",
            "cd ..",
            "ls -la"
        ]
        
        for cmd in commands:
            self.shell.execute(cmd)
        
        # Verify final state
        assert self.shell.environ["PWD"] == "/project"
        assert self.shell.fs.exists("/project/README.md")
        assert self.shell.fs.exists("/project/src/main.py")

    def test_environment_preservation(self):
        """Test that environment changes persist."""
        self.shell.execute("export VAR1=value1")
        self.shell.execute("export VAR2=value2")
        self.shell.execute("cd /home")
        self.shell.execute('alias myls="ls -la"')
        
        # All changes should persist
        assert self.shell.environ["VAR1"] == "value1"
        assert self.shell.environ["VAR2"] == "value2"
        assert self.shell.environ["PWD"] == "/home"
        assert "myls" in self.shell.aliases

    def test_real_world_scenario(self):
        """Test a real-world usage scenario."""
        # Simulate creating a Python project
        self.shell.execute("mkdir -p /myapp/src /myapp/tests")
        self.shell.execute("cd /myapp")
        self.shell.execute("echo '# MyApp' > README.md")
        self.shell.execute("echo 'def main(): pass' > src/main.py")
        self.shell.execute("echo 'def test(): pass' > tests/test_main.py")
        
        # Check project structure
        result = self.shell.execute("find . -type f")
        assert "./README.md" in result
        assert "./src/main.py" in result
        assert "./tests/test_main.py" in result
        
        # Use grep to find functions
        result = self.shell.execute("grep -r 'def' .")
        assert "main" in result
        assert "test" in result