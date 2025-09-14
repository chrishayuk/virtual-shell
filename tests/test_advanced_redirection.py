"""
Tests for advanced redirection features including stderr, combined output, and here-docs.
"""

import pytest
from chuk_virtual_shell.shell_interpreter import ShellInterpreter
from chuk_virtual_shell.core.redirection import RedirectionParser


class TestRedirectionParser:
    """Test the redirection parser."""

    def test_parse_stdout_redirection(self):
        """Test parsing stdout redirection."""
        parser = RedirectionParser()

        # Basic output redirection
        info = parser.parse("echo hello > output.txt")
        assert info.command == "echo hello"
        assert info.stdout_file == "output.txt"
        assert info.stdout_append is False

        # Append redirection
        info = parser.parse("echo world >> output.txt")
        assert info.command == "echo world"
        assert info.stdout_file == "output.txt"
        assert info.stdout_append is True

    def test_parse_stderr_redirection(self):
        """Test parsing stderr redirection."""
        parser = RedirectionParser()

        # Basic stderr redirection
        info = parser.parse("command 2> errors.txt")
        assert info.command == "command"
        assert info.stderr_file == "errors.txt"
        assert info.stderr_append is False

        # Append stderr
        info = parser.parse("command 2>> errors.txt")
        assert info.command == "command"
        assert info.stderr_file == "errors.txt"
        assert info.stderr_append is True

    def test_parse_stderr_to_stdout(self):
        """Test parsing stderr to stdout redirection."""
        parser = RedirectionParser()

        info = parser.parse("command 2>&1")
        assert info.command == "command"
        assert info.stderr_to_stdout is True
        assert info.stderr_file is None

        # With stdout redirection
        info = parser.parse("command > output.txt 2>&1")
        assert info.command == "command"
        assert info.stdout_file == "output.txt"
        assert info.stderr_to_stdout is True

    def test_parse_combined_redirection(self):
        """Test parsing combined output redirection."""
        parser = RedirectionParser()

        # Combined output
        info = parser.parse("command &> all.txt")
        assert info.command == "command"
        assert info.combined_file == "all.txt"
        assert info.combined_append is False

        # Append combined
        info = parser.parse("command &>> all.txt")
        assert info.command == "command"
        assert info.combined_file == "all.txt"
        assert info.combined_append is True

    def test_parse_input_redirection(self):
        """Test parsing input redirection."""
        parser = RedirectionParser()

        info = parser.parse("cat < input.txt")
        assert info.command == "cat"
        assert info.stdin_file == "input.txt"

    def test_parse_heredoc(self):
        """Test parsing here-document markers."""
        parser = RedirectionParser()

        # Basic heredoc
        info = parser.parse("cat << EOF")
        assert info.command == "cat"
        assert info.heredoc_delimiter == "EOF"
        assert info.heredoc_strip_tabs is False

        # Heredoc with tab stripping
        info = parser.parse("cat <<- DELIMITER")
        assert info.command == "cat"
        assert info.heredoc_delimiter == "DELIMITER"
        assert info.heredoc_strip_tabs is True

    def test_parse_multiple_redirections(self):
        """Test parsing multiple redirections."""
        parser = RedirectionParser()

        # Input and output
        info = parser.parse("sort < input.txt > output.txt")
        assert info.command == "sort"
        assert info.stdin_file == "input.txt"
        assert info.stdout_file == "output.txt"

        # Stdout and stderr
        info = parser.parse("command > out.txt 2> err.txt")
        assert info.command == "command"
        assert info.stdout_file == "out.txt"
        assert info.stderr_file == "err.txt"

        # Complex combination
        info = parser.parse("cmd < in.txt > out.txt 2>&1")
        assert info.command == "cmd"
        assert info.stdin_file == "in.txt"
        assert info.stdout_file == "out.txt"
        assert info.stderr_to_stdout is True

    def test_extract_heredoc_content(self):
        """Test extracting here-document content."""
        parser = RedirectionParser()

        lines = ["cat << EOF", "Line 1", "Line 2", "Line 3", "EOF", "next command"]

        content, end_idx = parser.extract_heredoc_content(lines, 0, "EOF")
        assert content == "Line 1\nLine 2\nLine 3"
        assert end_idx == 4

        # Test with tab stripping
        lines = [
            "cat <<- END",
            "\tIndented line",
            "\t\tDouble indented",
            "END",
        ]

        content, end_idx = parser.extract_heredoc_content(
            lines, 0, "END", strip_tabs=True
        )
        assert content == "Indented line\nDouble indented"
        assert end_idx == 3


@pytest.fixture
def shell():
    """Create a shell instance for testing."""
    shell = ShellInterpreter()
    shell.execute("mkdir -p /tmp")
    return shell


class TestStderrRedirection:
    """Test stderr redirection functionality."""

    def test_stderr_to_file(self, shell):
        """Test redirecting stderr to a file."""
        # Try to list non-existent directory
        result = shell.execute("ls /nonexistent 2> /tmp/errors.txt")

        # Check that error was written to file
        errors = shell.fs.read_file("/tmp/errors.txt")
        assert "No such file or directory" in errors or "not found" in errors

        # Stdout should be empty
        assert result == ""

    def test_stderr_append(self, shell):
        """Test appending stderr to a file."""
        # Create initial error file
        shell.execute("ls /nonexistent1 2> /tmp/errors.txt")

        # Append more errors
        shell.execute("ls /nonexistent2 2>> /tmp/errors.txt")

        errors = shell.fs.read_file("/tmp/errors.txt")
        assert "nonexistent1" in errors
        assert "nonexistent2" in errors

    def test_stderr_to_stdout(self, shell):
        """Test redirecting stderr to stdout."""
        # Redirect both to same output
        result = shell.execute("ls /nonexistent 2>&1")

        # Error should appear in result
        assert "No such file or directory" in result or "not found" in result

    def test_combined_redirection(self, shell):
        """Test combined stdout and stderr redirection."""
        # Create test scenario with both output and errors
        shell.execute("echo 'test data' > /tmp/test.txt")

        # Command that produces both stdout and stderr - use a command that naturally produces both
        # Since we don't support subshells, we'll test with ls on a mixed scenario
        shell.execute("mkdir -p /tmp/testdir")
        shell.execute("touch /tmp/testdir/file1.txt")

        # This will list file1.txt (stdout) and error on nonexistent (stderr)
        shell.execute("ls /tmp/testdir/file1.txt /nonexistent &> /tmp/combined.txt")

        combined = shell.fs.read_file("/tmp/combined.txt")
        assert combined is not None
        # Should have the successful listing
        assert "file1.txt" in combined
        # And the error
        assert "nonexistent" in combined

    @pytest.mark.skip(reason="Stderr redirection in pipelines not yet supported")
    def test_stderr_in_pipeline(self, shell):
        """Test stderr handling in pipelines."""
        # Pipeline where middle command fails
        shell.execute("echo hello | ls /nonexistent 2> /tmp/err.txt | cat")

        # Check error was captured
        errors = shell.fs.read_file("/tmp/err.txt")
        assert "No such file or directory" in errors or "not found" in errors


class TestHereDocuments:
    """Test here-document functionality."""

    @pytest.mark.skip(reason="Here-docs not yet integrated with shell")
    def test_simple_heredoc(self, shell):
        """Test a simple here-document."""
        # This would need special handling in the shell
        script = """cat << EOF
Line 1
Line 2
Line 3
EOF"""

        result = shell.execute(script)
        assert "Line 1" in result
        assert "Line 2" in result
        assert "Line 3" in result

    @pytest.mark.skip(reason="Here-docs not yet integrated with shell")
    def test_heredoc_with_redirection(self, shell):
        """Test here-document with output redirection."""
        script = """cat > /tmp/heredoc.txt << END
First line
Second line
Third line
END"""

        shell.execute(script)
        content = shell.fs.read_file("/tmp/heredoc.txt")
        assert content == "First line\nSecond line\nThird line"

    @pytest.mark.skip(reason="Here-docs not yet integrated with shell")
    def test_heredoc_tab_stripping(self, shell):
        """Test here-document with tab stripping."""
        script = """cat <<- EOF
\tIndented line
\t\tDouble indent
\tAnother indent
EOF"""

        result = shell.execute(script)
        assert result == "Indented line\nDouble indent\nAnother indent"


class TestAdvancedRedirectionScenarios:
    """Test complex redirection scenarios."""

    def test_redirect_stderr_only(self, shell):
        """Test redirecting only stderr while keeping stdout."""
        # Create a scenario that produces both stdout and stderr without subshells
        shell.execute("mkdir -p /tmp/testdir")
        shell.execute("touch /tmp/testdir/exists.txt")

        # List two paths - one exists (stdout), one doesn't (stderr)
        result = shell.execute(
            "ls /tmp/testdir/exists.txt /nonexistent 2> /tmp/err.txt"
        )

        # Stdout should be in result
        assert "exists.txt" in result

        # Stderr should be in file
        errors = shell.fs.read_file("/tmp/err.txt")
        assert "nonexistent" in errors

    @pytest.mark.skip(reason="Advanced features not yet integrated")
    def test_swap_stdout_stderr(self, shell):
        """Test swapping stdout and stderr."""
        # This is a complex redirection: 3>&1 1>&2 2>&3
        # Would need file descriptor support
        pass

    def test_discard_stderr(self, shell):
        """Test discarding stderr completely."""
        # Create /dev/null in our virtual filesystem
        shell.execute("mkdir -p /dev")
        shell.execute("touch /dev/null")

        # Redirect stderr to /dev/null
        result = shell.execute("ls /nonexistent 2> /dev/null")

        # Should not see error in output
        assert "No such file or directory" not in result
        assert result == ""

    @pytest.mark.skip(reason="Advanced features not yet integrated")
    def test_tee_like_behavior(self, shell):
        """Test tee-like behavior with process substitution."""
        # This would need process substitution: tee >(cmd1) >(cmd2)
        pass


class TestRedirectionErrorHandling:
    """Test error handling in redirections."""

    def test_invalid_input_file(self, shell):
        """Test redirection from non-existent file."""
        result = shell.execute("cat < /nonexistent.txt")
        assert "No such file" in result or "not found" in result

    def test_permission_denied_output(self, shell):
        """Test output redirection to protected location."""
        # Try to write to root (should fail in virtual FS)
        # This depends on filesystem permission implementation
        pass

    def test_malformed_redirection(self, shell):
        """Test handling of malformed redirections."""
        # Missing filename after >
        result = shell.execute("echo hello >")
        # Should handle gracefully
        assert "hello" in result or "error" in result.lower()
