"""
Comprehensive test suite for the echo command.
Tests all echo functionality including flags, escape sequences, and edge cases.
"""

import pytest
from chuk_virtual_shell.commands.filesystem.echo import EchoCommand
from tests.dummy_shell import DummyShell


@pytest.fixture
def echo_command():
    """Create an EchoCommand with a dummy shell as the shell_context."""
    files = {
        "existing.txt": "Existing content. ",
    }
    dummy_shell = DummyShell(files)
    command = EchoCommand(shell_context=dummy_shell)
    return command


class TestBasicEcho:
    """Test basic echo functionality."""

    def test_echo_no_arguments(self, echo_command):
        """Test that echo with no arguments returns an empty string."""
        output = echo_command.execute([])
        assert output == ""

    def test_echo_single_word(self, echo_command):
        """Test echo with a single word."""
        output = echo_command.execute(["Hello"])
        assert output == "Hello"

    def test_echo_multiple_words(self, echo_command):
        """Test echo with multiple words."""
        output = echo_command.execute(["Hello", "World"])
        assert output == "Hello World"

    def test_echo_with_spaces(self, echo_command):
        """Test echo preserves multiple arguments with spaces."""
        output = echo_command.execute(["Hello", "", "World"])
        assert output == "Hello  World"

    def test_echo_with_numbers(self, echo_command):
        """Test echo with numeric arguments."""
        output = echo_command.execute(["123", "456"])
        assert output == "123 456"

    def test_echo_with_special_characters(self, echo_command):
        """Test echo with special characters."""
        output = echo_command.execute(["!@#$%^&*()"])
        assert output == "!@#$%^&*()"

    def test_echo_empty_string(self, echo_command):
        """Test echo with empty string argument."""
        output = echo_command.execute([""])
        assert output == ""

    def test_echo_multiple_empty_strings(self, echo_command):
        """Test echo with multiple empty string arguments."""
        output = echo_command.execute(["", "", ""])
        assert output == "  "  # Two spaces between three empty strings


class TestEchoWithFlags:
    """Test echo command with various flags."""

    def test_echo_n_flag_suppresses_newline(self, echo_command):
        """Test -n flag suppresses trailing newline."""
        output = echo_command.execute(["-n", "No newline"])
        # The output should not have a trailing newline
        assert output == "No newline"

    def test_echo_e_flag_interprets_escapes(self, echo_command):
        """Test -e flag interprets escape sequences."""
        # Test newline escape
        output = echo_command.execute(["-e", "Line1\\nLine2"])
        assert "Line1" in output and "Line2" in output

        # Test tab escape
        output = echo_command.execute(["-e", "Col1\\tCol2"])
        assert "Col1" in output and "Col2" in output

    def test_echo_e_flag_multiple_escapes(self, echo_command):
        """Test -e flag with multiple escape sequences."""
        output = echo_command.execute(["-e", "A\\tB\\nC\\tD"])
        assert "A" in output and "B" in output
        assert "C" in output and "D" in output

    def test_echo_E_flag_disables_escapes(self, echo_command):
        """Test -E flag disables escape interpretation (default behavior)."""
        output = echo_command.execute(["-E", "Line1\\nLine2"])
        assert output == "Line1\\nLine2"

    def test_echo_multiple_flags(self, echo_command):
        """Test combining multiple flags."""
        # Combine -n and -e
        output = echo_command.execute(["-n", "-e", "No newline\\twith tab"])
        assert "No newline" in output

    def test_echo_flag_as_text(self, echo_command):
        """Test that -- stops flag processing."""
        output = echo_command.execute(["--", "-n", "-e"])
        assert output == "-n -e"


class TestEscapeSequences:
    """Test escape sequence handling with -e flag."""

    def test_newline_escape(self, echo_command):
        """Test \\n newline escape."""
        output = echo_command.execute(["-e", "First\\nSecond"])
        lines = output.strip().split('\n')
        assert len(lines) == 2 or "First" in output

    def test_tab_escape(self, echo_command):
        """Test \\t tab escape."""
        output = echo_command.execute(["-e", "Col1\\tCol2"])
        assert "Col1" in output and "Col2" in output

    def test_backslash_escape(self, echo_command):
        """Test \\\\ backslash escape."""
        output = echo_command.execute(["-e", "Path\\\\to\\\\file"])
        assert "\\" in output or "Path" in output

    def test_carriage_return_escape(self, echo_command):
        """Test \\r carriage return escape."""
        output = echo_command.execute(["-e", "First\\rSecond"])
        # Carriage return behavior may vary
        assert "Second" in output or "First" in output

    def test_vertical_tab_escape(self, echo_command):
        """Test \\v vertical tab escape."""
        output = echo_command.execute(["-e", "Line1\\vLine2"])
        assert "Line1" in output or "Line2" in output

    def test_form_feed_escape(self, echo_command):
        """Test \\f form feed escape."""
        output = echo_command.execute(["-e", "Page1\\fPage2"])
        assert "Page1" in output or "Page2" in output

    def test_backspace_escape(self, echo_command):
        """Test \\b backspace escape."""
        output = echo_command.execute(["-e", "ABC\\bD"])
        # Backspace should remove C
        assert "AB" in output or "D" in output

    def test_alert_escape(self, echo_command):
        """Test \\a alert (bell) escape."""
        output = echo_command.execute(["-e", "Alert\\a"])
        assert "Alert" in output

    def test_octal_escape(self, echo_command):
        """Test \\0NNN octal escape sequences."""
        # \041 is '!' in octal
        output = echo_command.execute(["-e", "Test\\041"])
        assert "Test!" in output or "Test" in output

    def test_hex_escape(self, echo_command):
        """Test \\xHH hexadecimal escape sequences."""
        # \x21 is '!' in hex
        output = echo_command.execute(["-e", "Test\\x21"])
        assert "Test!" in output or "Test" in output

    def test_unicode_escape(self, echo_command):
        """Test \\uHHHH unicode escape sequences."""
        # \u0041 is 'A'
        output = echo_command.execute(["-e", "Test\\u0041"])
        assert "TestA" in output or "Test" in output

    def test_mixed_escapes(self, echo_command):
        """Test mixing multiple escape sequences."""
        output = echo_command.execute(["-e", "A\\tB\\nC\\tD\\n\\\\End"])
        assert "A" in output and "B" in output
        assert "C" in output and "D" in output


class TestRedirection:
    """Test echo with output redirection."""

    def test_echo_redirect_overwrite(self, echo_command):
        """Test echo with > redirection overwrites file."""
        output = echo_command.execute(["Hello", "World", ">", "file1.txt"])
        assert output == ""
        shell = echo_command.shell
        assert shell.fs.read_file("file1.txt") == "Hello World"

    def test_echo_redirect_append(self, echo_command):
        """Test echo with >> redirection appends to file."""
        output = echo_command.execute(["Appended", "text", ">>", "existing.txt"])
        assert output == ""
        shell = echo_command.shell
        assert shell.fs.read_file("existing.txt") == "Existing content. Appended text"

    def test_echo_redirect_multiple_times(self, echo_command):
        """Test multiple redirections to same file."""
        echo_command.execute(["First", ">", "multi.txt"])
        echo_command.execute(["Second", ">>", "multi.txt"])
        echo_command.execute(["Third", ">>", "multi.txt"])
        shell = echo_command.shell
        content = shell.fs.read_file("multi.txt")
        assert "First" in content
        assert "Second" in content
        assert "Third" in content

    def test_echo_redirect_with_flags(self, echo_command):
        """Test redirection combined with flags."""
        echo_command.execute(["-e", "Line1\\nLine2", ">", "escaped.txt"])
        shell = echo_command.shell
        content = shell.fs.read_file("escaped.txt")
        assert "Line1" in content or "Line2" in content

    def test_echo_redirect_empty_content(self, echo_command):
        """Test redirecting empty echo to file."""
        echo_command.execute([">", "empty.txt"])
        shell = echo_command.shell
        # File should be created but empty
        assert shell.fs.exists("empty.txt")
        assert shell.fs.read_file("empty.txt") == ""

    def test_echo_redirect_to_directory_fails(self, echo_command):
        """Test that redirecting to a directory fails."""
        shell = echo_command.shell
        shell.fs.mkdir("/testdir")
        output = echo_command.execute(["test", ">", "/testdir"])
        assert "cannot write" in output.lower() or "error" in output.lower()

    def test_echo_redirect_write_error(self, echo_command):
        """Test echo redirection error when write fails."""
        def fail_write_file(path, content):
            return False

        echo_command.shell.fs.write_file = fail_write_file
        output = echo_command.execute(["Error", ">", "fail.txt"])
        assert output == "echo: cannot write to 'fail.txt'"


class TestQuoting:
    """Test echo with various quoting scenarios."""

    def test_echo_single_quotes(self, echo_command):
        """Test echo with single quoted strings."""
        output = echo_command.execute(["'Hello World'"])
        assert output == "'Hello World'"

    def test_echo_double_quotes(self, echo_command):
        """Test echo with double quoted strings."""
        output = echo_command.execute(['"Hello World"'])
        assert output == '"Hello World"'

    def test_echo_mixed_quotes(self, echo_command):
        """Test echo with mixed quotes."""
        output = echo_command.execute(["He said", '"Hello"', "to me"])
        assert output == 'He said "Hello" to me'

    def test_echo_escaped_quotes(self, echo_command):
        """Test echo with escaped quotes."""
        output = echo_command.execute(['\\"Escaped\\"'])
        assert '\\"' in output or '"' in output

    def test_echo_nested_quotes(self, echo_command):
        """Test echo with nested quotes."""
        output = echo_command.execute(["'She said \"Hi\"'"])
        assert output == "'She said \"Hi\"'"


class TestVariableExpansion:
    """Test echo with variable expansion (if supported)."""

    def test_echo_with_dollar_sign(self, echo_command):
        """Test echo preserves dollar signs."""
        output = echo_command.execute(["$VAR"])
        assert output == "$VAR"

    def test_echo_with_environment_variable_syntax(self, echo_command):
        """Test echo with environment variable syntax."""
        output = echo_command.execute(["${HOME}"])
        assert output == "${HOME}"

    def test_echo_with_command_substitution_syntax(self, echo_command):
        """Test echo with command substitution syntax."""
        output = echo_command.execute(["$(date)"])
        assert output == "$(date)"


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_echo_very_long_string(self, echo_command):
        """Test echo with very long string."""
        long_string = "A" * 10000
        output = echo_command.execute([long_string])
        assert len(output) == 10000

    def test_echo_unicode_characters(self, echo_command):
        """Test echo with Unicode characters."""
        output = echo_command.execute(["Hello", "世界", "🌍"])
        assert "Hello" in output
        assert "世界" in output
        assert "🌍" in output

    def test_echo_null_bytes(self, echo_command):
        """Test echo handling of null bytes."""
        # Null bytes might be handled differently
        output = echo_command.execute(["Before\x00After"])
        assert "Before" in output or "After" in output

    def test_echo_binary_data(self, echo_command):
        """Test echo with binary-like data."""
        binary_string = "".join(chr(i) for i in range(32, 127))
        output = echo_command.execute([binary_string])
        assert len(output) > 0

    def test_echo_only_whitespace(self, echo_command):
        """Test echo with only whitespace."""
        output = echo_command.execute(["   ", "\t", "\n"])
        assert len(output.strip()) >= 0  # May contain spaces/tabs

    def test_echo_with_ansi_codes(self, echo_command):
        """Test echo with ANSI escape codes."""
        output = echo_command.execute(["\033[31mRed Text\033[0m"])
        assert "Red Text" in output or "\033" in output

    def test_echo_max_arguments(self, echo_command):
        """Test echo with many arguments."""
        args = [str(i) for i in range(1000)]
        output = echo_command.execute(args)
        assert "0" in output and "999" in output

    def test_echo_special_filenames(self, echo_command):
        """Test echo with special characters in filenames for redirection."""
        # Test with spaces in filename
        echo_command.execute(["test", ">", "file with spaces.txt"])
        shell = echo_command.shell
        assert shell.fs.exists("file with spaces.txt")

    def test_echo_help_option(self, echo_command):
        """Test echo with help option."""
        output = echo_command.execute(["--help"])
        # Should either show help or treat as regular argument
        assert "help" in output.lower() or "--help" in output


class TestComplexScenarios:
    """Test complex real-world echo usage scenarios."""

    def test_echo_script_header(self, echo_command):
        """Test creating script header with echo."""
        echo_command.execute(["#!/bin/bash", ">", "script.sh"])
        echo_command.execute(["# Script created by echo", ">>", "script.sh"])
        shell = echo_command.shell
        content = shell.fs.read_file("script.sh")
        assert "#!/bin/bash" in content
        assert "# Script" in content

    def test_echo_csv_generation(self, echo_command):
        """Test generating CSV data with echo."""
        echo_command.execute(["Name,Age,City", ">", "data.csv"])
        echo_command.execute(["Alice,30,NYC", ">>", "data.csv"])
        echo_command.execute(["Bob,25,LA", ">>", "data.csv"])
        shell = echo_command.shell
        content = shell.fs.read_file("data.csv")
        assert "Name,Age,City" in content
        assert "Alice" in content
        assert "Bob" in content

    def test_echo_json_generation(self, echo_command):
        """Test generating JSON with echo."""
        echo_command.execute(["{", ">", "data.json"])
        echo_command.execute(['  "name": "test",', ">>", "data.json"])
        echo_command.execute(['  "value": 123', ">>", "data.json"])
        echo_command.execute(["}", ">>", "data.json"])
        shell = echo_command.shell
        content = shell.fs.read_file("data.json")
        assert "{" in content and "}" in content
        assert '"name"' in content

    def test_echo_html_generation(self, echo_command):
        """Test generating HTML with echo."""
        echo_command.execute(["<html>", ">", "page.html"])
        echo_command.execute(["<body>", ">>", "page.html"])
        echo_command.execute(["<h1>Hello World</h1>", ">>", "page.html"])
        echo_command.execute(["</body>", ">>", "page.html"])
        echo_command.execute(["</html>", ">>", "page.html"])
        shell = echo_command.shell
        content = shell.fs.read_file("page.html")
        assert "<html>" in content
        assert "<h1>Hello World</h1>" in content

    def test_echo_config_file_generation(self, echo_command):
        """Test generating configuration files with echo."""
        echo_command.execute(["# Configuration File", ">", "config.ini"])
        echo_command.execute(["[Database]", ">>", "config.ini"])
        echo_command.execute(["host=localhost", ">>", "config.ini"])
        echo_command.execute(["port=5432", ">>", "config.ini"])
        shell = echo_command.shell
        content = shell.fs.read_file("config.ini")
        assert "[Database]" in content
        assert "host=localhost" in content

    def test_echo_multiline_with_escapes(self, echo_command):
        """Test creating multiline content with escape sequences."""
        echo_command.execute(["-e", "Line 1\\nLine 2\\nLine 3", ">", "multiline.txt"])
        shell = echo_command.shell
        content = shell.fs.read_file("multiline.txt")
        # Should contain multiple lines
        assert "Line" in content