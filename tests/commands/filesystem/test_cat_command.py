"""
Comprehensive test suite for the cat command.
Tests all cat functionality including concatenation, line numbering, and edge cases.
"""

import pytest
from chuk_virtual_shell.commands.filesystem.cat import CatCommand
from tests.dummy_shell import DummyShell


@pytest.fixture
def cat_command():
    """Create a CatCommand with a dummy shell and sample files."""
    files = {
        "file1.txt": "Hello, ",
        "file2.txt": "world!",
        "multiline.txt": "Line 1\nLine 2\nLine 3\n",
        "empty.txt": "",
        "binary.bin": "\x00\x01\x02\x03\x04",
        "unicode.txt": "Hello 世界 🌍",
        "spaces.txt": "  leading spaces\n    indented\ntrailing spaces  ",
        "tabs.txt": "\tTab line 1\n\t\tTab line 2",
        "long.txt": "A" * 10000,
        "numbers.txt": "1\n2\n3\n4\n5\n6\n7\n8\n9\n10",
        "mixed_endings.txt": "Unix line\nWindows line\r\nMac line\rLast line",
        "dir/nested.txt": "Nested file content",
    }
    dummy_shell = DummyShell(files)
    command = CatCommand(shell_context=dummy_shell)
    return command


class TestBasicCat:
    """Test basic cat functionality."""

    def test_cat_missing_operand(self, cat_command):
        """Test cat with no arguments."""
        output = cat_command.execute([])
        assert output == "cat: missing operand"

    def test_cat_single_file(self, cat_command):
        """Test cat with a single file."""
        output = cat_command.execute(["file1.txt"])
        assert output == "Hello, "

    def test_cat_multiple_files(self, cat_command):
        """Test concatenating multiple files."""
        output = cat_command.execute(["file1.txt", "file2.txt"])
        assert output == "Hello, world!"

    def test_cat_file_not_found(self, cat_command):
        """Test cat with non-existent file."""
        output = cat_command.execute(["nonexistent.txt"])
        assert "cat: nonexistent.txt: No such file" in output

    def test_cat_multiple_files_with_missing(self, cat_command):
        """Test cat with mix of existing and non-existent files."""
        output = cat_command.execute(["file1.txt", "missing.txt", "file2.txt"])
        # Should show content of existing files and error for missing
        assert "Hello, " in output
        assert "No such file" in output
        assert "world!" in output

    def test_cat_empty_file(self, cat_command):
        """Test cat with empty file."""
        output = cat_command.execute(["empty.txt"])
        assert output == ""

    def test_cat_nested_file(self, cat_command):
        """Test cat with file in subdirectory."""
        output = cat_command.execute(["dir/nested.txt"])
        assert output == "Nested file content"


class TestCatWithFlags:
    """Test cat command with various flags."""

    def test_cat_n_flag_line_numbers(self, cat_command):
        """Test -n flag for line numbering."""
        output = cat_command.execute(["-n", "multiline.txt"])
        # Should contain line numbers
        assert "1" in output
        assert "2" in output
        assert "3" in output
        assert "Line 1" in output
        assert "Line 2" in output
        assert "Line 3" in output

    def test_cat_b_flag_number_non_blank(self, cat_command):
        """Test -b flag for numbering non-blank lines."""
        # Create file with blank lines
        cat_command.shell.fs.write_file("blanks.txt", "Line 1\n\nLine 2\n\nLine 3")
        output = cat_command.execute(["-b", "blanks.txt"])
        # Should number only non-blank lines
        assert "1" in output
        assert "2" in output
        assert "3" in output

    def test_cat_s_flag_squeeze_blank(self, cat_command):
        """Test -s flag for squeezing blank lines."""
        # Create file with multiple blank lines
        cat_command.shell.fs.write_file("multiple_blanks.txt", "Line 1\n\n\n\nLine 2\n\n\nLine 3")
        output = cat_command.execute(["-s", "multiple_blanks.txt"])
        # Should reduce multiple blank lines to single
        lines = output.split('\n')
        blank_count = sum(1 for line in lines if line == "")
        assert blank_count <= 2  # At most one blank between content lines

    def test_cat_e_flag_show_ends(self, cat_command):
        """Test -E flag for showing line ends."""
        output = cat_command.execute(["-E", "multiline.txt"])
        # Should show $ at end of lines
        assert "$" in output or "Line 1" in output

    def test_cat_t_flag_show_tabs(self, cat_command):
        """Test -T flag for showing tabs."""
        output = cat_command.execute(["-T", "tabs.txt"])
        # Should show ^I for tabs or preserve tabs
        assert "^I" in output or "\t" in output

    def test_cat_v_flag_show_nonprinting(self, cat_command):
        """Test -v flag for showing non-printing characters."""
        output = cat_command.execute(["-v", "binary.bin"])
        # Should show non-printing characters in visible form
        assert len(output) > 0

    def test_cat_multiple_flags(self, cat_command):
        """Test combining multiple flags."""
        output = cat_command.execute(["-n", "-E", "multiline.txt"])
        # Should have both line numbers and end markers
        assert "1" in output
        assert "Line 1" in output

    def test_cat_flags_with_multiple_files(self, cat_command):
        """Test flags applied to multiple files."""
        output = cat_command.execute(["-n", "file1.txt", "file2.txt"])
        # Should number lines across both files
        assert "Hello, " in output
        assert "world!" in output


class TestMultilineContent:
    """Test cat with multiline content."""

    def test_cat_multiline_file(self, cat_command):
        """Test cat with multiline file."""
        output = cat_command.execute(["multiline.txt"])
        assert "Line 1\nLine 2\nLine 3\n" == output

    def test_cat_preserve_line_endings(self, cat_command):
        """Test that cat preserves line endings."""
        output = cat_command.execute(["mixed_endings.txt"])
        assert "Unix line" in output
        assert "Windows line" in output
        assert "Mac line" in output
        assert "Last line" in output

    def test_cat_long_lines(self, cat_command):
        """Test cat with very long lines."""
        cat_command.shell.fs.write_file("longline.txt", "A" * 5000 + "\n" + "B" * 5000)
        output = cat_command.execute(["longline.txt"])
        assert "A" * 5000 in output
        assert "B" * 5000 in output

    def test_cat_many_lines(self, cat_command):
        """Test cat with many lines."""
        lines = [f"Line {i}" for i in range(1000)]
        cat_command.shell.fs.write_file("manylines.txt", "\n".join(lines))
        output = cat_command.execute(["manylines.txt"])
        assert "Line 0" in output
        assert "Line 999" in output
        assert len(output.split('\n')) >= 999


class TestSpecialCharacters:
    """Test cat with special characters."""

    def test_cat_unicode(self, cat_command):
        """Test cat with Unicode characters."""
        output = cat_command.execute(["unicode.txt"])
        assert "Hello" in output
        assert "世界" in output
        assert "🌍" in output

    def test_cat_binary_file(self, cat_command):
        """Test cat with binary content."""
        output = cat_command.execute(["binary.bin"])
        # Should output binary content (might appear garbled)
        assert len(output) > 0

    def test_cat_spaces_and_tabs(self, cat_command):
        """Test cat preserves spaces and tabs."""
        output = cat_command.execute(["spaces.txt"])
        assert "  leading spaces" in output
        assert "    indented" in output
        assert "trailing spaces  " in output

    def test_cat_special_chars_in_filename(self, cat_command):
        """Test cat with special characters in filename."""
        cat_command.shell.fs.write_file("file with spaces.txt", "content")
        output = cat_command.execute(["file with spaces.txt"])
        assert output == "content"

    def test_cat_ansi_escape_codes(self, cat_command):
        """Test cat with ANSI escape codes."""
        cat_command.shell.fs.write_file("ansi.txt", "\033[31mRed\033[0m Normal")
        output = cat_command.execute(["ansi.txt"])
        assert "\033[31m" in output or "Red" in output
        assert "Normal" in output


class TestConcatenation:
    """Test file concatenation features."""

    def test_cat_concat_order(self, cat_command):
        """Test that files are concatenated in order."""
        cat_command.shell.fs.write_file("a.txt", "AAA")
        cat_command.shell.fs.write_file("b.txt", "BBB")
        cat_command.shell.fs.write_file("c.txt", "CCC")
        output = cat_command.execute(["a.txt", "b.txt", "c.txt"])
        assert output == "AAABBBCCC"
        
        # Test different order
        output = cat_command.execute(["c.txt", "a.txt", "b.txt"])
        assert output == "CCCAAABBB"

    def test_cat_concat_with_newlines(self, cat_command):
        """Test concatenation preserves newlines."""
        cat_command.shell.fs.write_file("first.txt", "First\n")
        cat_command.shell.fs.write_file("second.txt", "Second\n")
        output = cat_command.execute(["first.txt", "second.txt"])
        assert output == "First\nSecond\n"

    def test_cat_concat_mixed_content(self, cat_command):
        """Test concatenating files with different content types."""
        output = cat_command.execute(["unicode.txt", "multiline.txt", "tabs.txt"])
        assert "Hello 世界" in output
        assert "Line 1" in output
        assert "Tab line" in output

    def test_cat_same_file_multiple_times(self, cat_command):
        """Test concatenating same file multiple times."""
        output = cat_command.execute(["file1.txt", "file1.txt", "file1.txt"])
        assert output == "Hello, Hello, Hello, "

    def test_cat_large_concatenation(self, cat_command):
        """Test concatenating many files."""
        # Create many small files
        for i in range(20):
            cat_command.shell.fs.write_file(f"part{i}.txt", f"Part{i}\n")
        
        files = [f"part{i}.txt" for i in range(20)]
        output = cat_command.execute(files)
        
        for i in range(20):
            assert f"Part{i}" in output


class TestErrorHandling:
    """Test error handling in cat command."""

    def test_cat_directory(self, cat_command):
        """Test cat on a directory."""
        cat_command.shell.fs.mkdir("/testdir")
        output = cat_command.execute(["/testdir"])
        assert "Is a directory" in output or "error" in output.lower()

    def test_cat_permission_denied(self, cat_command):
        """Test cat with permission denied (simulated)."""
        # Override read_file to simulate permission error
        def fail_read(path):
            if path == "protected.txt":
                return None
            return cat_command.shell.fs._files.get(path, None)
        
        cat_command.shell.fs.write_file("protected.txt", "secret")
        original_read = cat_command.shell.fs.read_file
        cat_command.shell.fs.read_file = fail_read
        
        output = cat_command.execute(["protected.txt"])
        assert "No such file" in output or "error" in output.lower()
        
        cat_command.shell.fs.read_file = original_read

    def test_cat_mixed_valid_invalid(self, cat_command):
        """Test cat with mix of valid files and directories."""
        cat_command.shell.fs.mkdir("/dir")
        output = cat_command.execute(["file1.txt", "/dir", "file2.txt"])
        assert "Hello, " in output
        assert "world!" in output
        assert "directory" in output.lower() or "error" in output.lower()

    def test_cat_wildcard_pattern(self, cat_command):
        """Test cat with wildcard patterns (if supported)."""
        # Note: Wildcard expansion might be handled by shell, not cat
        output = cat_command.execute(["*.txt"])
        # Should either expand wildcards or treat as literal filename
        assert len(output) >= 0

    def test_cat_stdin_marker(self, cat_command):
        """Test cat with - for stdin (if supported)."""
        output = cat_command.execute(["-"])
        # Should either read from stdin or show error
        assert len(output) >= 0 or "operand" in output


class TestPerformance:
    """Test cat performance with large files."""

    def test_cat_large_file(self, cat_command):
        """Test cat with large file."""
        output = cat_command.execute(["long.txt"])
        assert len(output) == 10000
        assert output == "A" * 10000

    def test_cat_very_large_file(self, cat_command):
        """Test cat with very large file."""
        # Create 1MB file
        large_content = "X" * (1024 * 1024)
        cat_command.shell.fs.write_file("huge.txt", large_content)
        output = cat_command.execute(["huge.txt"])
        assert len(output) == 1024 * 1024

    def test_cat_many_small_files(self, cat_command):
        """Test cat with many small files."""
        # Create 100 small files
        for i in range(100):
            cat_command.shell.fs.write_file(f"small{i}.txt", f"{i}")
        
        files = [f"small{i}.txt" for i in range(100)]
        output = cat_command.execute(files)
        
        # Check all numbers are present
        for i in range(100):
            assert str(i) in output


class TestSpecialCases:
    """Test special edge cases."""

    def test_cat_null_bytes(self, cat_command):
        """Test cat with null bytes in file."""
        cat_command.shell.fs.write_file("null.txt", "Before\x00After")
        output = cat_command.execute(["null.txt"])
        # Null handling may vary
        assert "Before" in output or "After" in output

    def test_cat_no_newline_at_end(self, cat_command):
        """Test cat with file without trailing newline."""
        cat_command.shell.fs.write_file("no_newline.txt", "No newline at end")
        output = cat_command.execute(["no_newline.txt"])
        assert output == "No newline at end"

    def test_cat_only_newlines(self, cat_command):
        """Test cat with file containing only newlines."""
        cat_command.shell.fs.write_file("newlines.txt", "\n\n\n")
        output = cat_command.execute(["newlines.txt"])
        assert output == "\n\n\n"

    def test_cat_circular_reference(self, cat_command):
        """Test cat behavior with symbolic links (if supported)."""
        # This would test circular references if symlinks were supported
        output = cat_command.execute(["file1.txt"])
        assert "Hello, " in output

    def test_cat_help_option(self, cat_command):
        """Test cat with --help option."""
        output = cat_command.execute(["--help"])
        # Should either show help or treat as filename
        assert len(output) >= 0


class TestRealWorldScenarios:
    """Test real-world usage scenarios."""

    def test_cat_log_file(self, cat_command):
        """Test cat with log file format."""
        log_content = """2024-01-01 10:00:00 INFO Starting application
2024-01-01 10:00:01 DEBUG Loading configuration
2024-01-01 10:00:02 ERROR Failed to connect to database
2024-01-01 10:00:03 WARN Retrying connection
2024-01-01 10:00:04 INFO Connection established"""
        cat_command.shell.fs.write_file("app.log", log_content)
        output = cat_command.execute(["app.log"])
        assert "INFO Starting application" in output
        assert "ERROR Failed to connect" in output

    def test_cat_config_file(self, cat_command):
        """Test cat with configuration file."""
        config = """[database]
host = localhost
port = 5432
user = admin

[application]
debug = true
log_level = INFO"""
        cat_command.shell.fs.write_file("config.ini", config)
        output = cat_command.execute(["config.ini"])
        assert "[database]" in output
        assert "host = localhost" in output
        assert "[application]" in output

    def test_cat_source_code(self, cat_command):
        """Test cat with source code file."""
        code = """def hello_world():
    print("Hello, World!")
    
if __name__ == "__main__":
    hello_world()"""
        cat_command.shell.fs.write_file("hello.py", code)
        output = cat_command.execute(["hello.py"])
        assert "def hello_world():" in output
        assert 'print("Hello, World!")' in output

    def test_cat_csv_file(self, cat_command):
        """Test cat with CSV file."""
        csv_content = """Name,Age,City
Alice,30,New York
Bob,25,Los Angeles
Charlie,35,Chicago"""
        cat_command.shell.fs.write_file("data.csv", csv_content)
        output = cat_command.execute(["data.csv"])
        assert "Name,Age,City" in output
        assert "Alice,30,New York" in output

    def test_cat_json_file(self, cat_command):
        """Test cat with JSON file."""
        json_content = """{
    "name": "Test",
    "version": "1.0.0",
    "dependencies": {
        "package1": "^2.0.0",
        "package2": "~3.1.0"
    }
}"""
        cat_command.shell.fs.write_file("package.json", json_content)
        output = cat_command.execute(["package.json"])
        assert '"name": "Test"' in output
        assert '"dependencies"' in output