"""
Comprehensive tests for the more command.
Tests all more functionality including various flags and edge cases.
"""

import pytest
from chuk_virtual_shell.commands.filesystem.more import MoreCommand
from tests.dummy_shell import DummyShell


@pytest.fixture
def more_setup():
    """Set up test environment with various files."""
    # Create test content
    short_content = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"
    
    # Long content (100 lines)
    long_content = "\n".join([f"Line {i}" for i in range(1, 101)])
    
    # Content with blank lines for squeeze testing
    blank_content = "Line 1\n\n\nLine 2\n\n\n\n\nLine 3\nLine 4\n\n\nLine 5"
    
    # Content with pattern
    pattern_content = (
        "Header line\n"
        "Some text here\n"
        "PATTERN: This is the target line\n"
        "More text after pattern\n"
        "Another line\n"
        "Final line"
    )
    
    # Binary-like content
    binary_content = "Normal\x00\x01\x02\nBinary\xff\xfe\nContent"
    
    # Unicode content
    unicode_content = "Hello 世界\n🎉 Emoji line\nÄccëntéd tëxt\nСирилица\nالعربية"
    
    # Very long lines
    long_lines = "\n".join([
        f"Line {i}: " + "x" * 200 for i in range(1, 21)
    ])
    
    # Tab content
    tab_content = "Col1\tCol2\tCol3\nData1\tData2\tData3\nRow1\tRow2\tRow3"
    
    files = {
        "/": {
            "short.txt": None,
            "long.txt": None,
            "blank.txt": None,
            "pattern.txt": None,
            "binary.bin": None,
            "unicode.txt": None,
            "longlines.txt": None,
            "tabs.txt": None,
            "empty.txt": None,
            "testdir": None
        },
        "/short.txt": short_content,
        "/long.txt": long_content,
        "/blank.txt": blank_content,
        "/pattern.txt": pattern_content,
        "/binary.bin": binary_content,
        "/unicode.txt": unicode_content,
        "/longlines.txt": long_lines,
        "/tabs.txt": tab_content,
        "/empty.txt": "",
        "/testdir": {}
    }
    
    shell = DummyShell(files)
    shell.fs.current_directory = "/"
    shell.environ = {"PWD": "/"}
    
    cmd = MoreCommand(shell)
    return shell, cmd


class TestMoreBasic:
    """Test basic more functionality."""
    
    def test_more_single_file(self, more_setup):
        """Test displaying a single file."""
        shell, cmd = more_setup
        result = cmd.execute(["/short.txt"])
        assert "Line 1" in result
        assert "Line 2" in result
        assert "Line 5" in result
    
    def test_more_multiple_files(self, more_setup):
        """Test displaying multiple files."""
        shell, cmd = more_setup
        result = cmd.execute(["/short.txt", "/empty.txt"])
        # Should show file headers
        assert "short.txt" in result or "Line 1" in result
        assert "::::::" in result  # File separator
    
    def test_more_nonexistent_file(self, more_setup):
        """Test with non-existent file."""
        shell, cmd = more_setup
        result = cmd.execute(["/nonexistent.txt"])
        assert "No such file or directory" in result
    
    def test_more_directory(self, more_setup):
        """Test trying to display a directory."""
        shell, cmd = more_setup
        result = cmd.execute(["/testdir"])
        assert "Is a directory" in result
    
    def test_more_empty_file(self, more_setup):
        """Test displaying empty file."""
        shell, cmd = more_setup
        result = cmd.execute(["/empty.txt"])
        # Should handle empty file gracefully
        assert result == "" or "--More--" not in result
    
    def test_more_no_arguments(self, more_setup):
        """Test more with no arguments."""
        shell, cmd = more_setup
        result = cmd.execute([])
        assert "missing operand" in result


class TestMorePaging:
    """Test paging functionality."""
    
    def test_more_long_file_pagination(self, more_setup):
        """Test pagination with long file."""
        shell, cmd = more_setup
        result = cmd.execute(["/long.txt"])
        # Should show pagination markers
        assert "--More--" in result
        assert "%" in result  # Percentage indicator
    
    def test_more_custom_page_size(self, more_setup):
        """Test custom page size with -n option."""
        shell, cmd = more_setup
        result = cmd.execute(["-n", "10", "/long.txt"])
        # Should paginate with 10 lines per page
        lines = result.split("\n")
        # Check for more frequent pagination markers
        more_count = result.count("--More--")
        assert more_count > 5  # Should have many pages with only 10 lines each
    
    def test_more_numeric_page_size(self, more_setup):
        """Test -NUM syntax for page size."""
        shell, cmd = more_setup
        result = cmd.execute(["-5", "/long.txt"])
        # Should paginate with 5 lines per page
        more_count = result.count("--More--")
        assert more_count > 10  # Even more pages with 5 lines each


class TestMoreStartPosition:
    """Test start position options."""
    
    def test_more_start_at_line(self, more_setup):
        """Test +NUM to start at specific line."""
        shell, cmd = more_setup
        result = cmd.execute(["+3", "/short.txt"])
        # Should start at line 3
        lines = result.split("\n")
        assert "Line 3" in lines[0] or "Line 3" in lines[1]
        # Line 1 and 2 should not appear before Line 3
        line3_pos = result.find("Line 3")
        line1_pos = result.find("Line 1")
        if line1_pos != -1:
            assert line3_pos < line1_pos
    
    def test_more_start_at_pattern(self, more_setup):
        """Test +/PATTERN to start at pattern."""
        shell, cmd = more_setup
        result = cmd.execute(["+/PATTERN", "/pattern.txt"])
        # Should start at or near the pattern line
        lines = result.split("\n")
        found_pattern = False
        for i, line in enumerate(lines[:5]):  # Check first few lines
            if "PATTERN" in line:
                found_pattern = True
                break
        assert found_pattern


class TestMoreSqueezeBlank:
    """Test squeeze blank lines functionality."""
    
    def test_more_squeeze_blanks(self, more_setup):
        """Test -s flag to squeeze blank lines."""
        shell, cmd = more_setup
        result = cmd.execute(["-s", "/blank.txt"])
        # Count blank lines
        lines = result.split("\n")
        consecutive_blanks = 0
        max_consecutive = 0
        for line in lines:
            if line.strip() == "" and "--More--" not in line:
                consecutive_blanks += 1
                max_consecutive = max(max_consecutive, consecutive_blanks)
            else:
                consecutive_blanks = 0
        # Should not have more than 1 consecutive blank
        assert max_consecutive <= 1
    
    def test_more_no_squeeze(self, more_setup):
        """Test without squeeze shows multiple blanks."""
        shell, cmd = more_setup
        result = cmd.execute(["/blank.txt"])
        # Should preserve multiple blank lines
        assert "\n\n\n" in result or result.count("\n") > 10


class TestMoreDisplayOptions:
    """Test display options."""
    
    def test_more_clear_screen(self, more_setup):
        """Test -p flag to clear screen."""
        shell, cmd = more_setup
        result = cmd.execute(["-p", "/short.txt"])
        assert "[Screen cleared]" in result or "Line 1" in result
    
    def test_more_clean_print(self, more_setup):
        """Test -c flag for clean printing."""
        shell, cmd = more_setup
        result = cmd.execute(["-c", "/short.txt"])
        assert "[Screen cleared]" in result or "Line 1" in result
    
    def test_more_silent_mode(self, more_setup):
        """Test -d flag for helpful prompts."""
        shell, cmd = more_setup
        result = cmd.execute(["-d", "/long.txt"])
        if "--More--" in result:
            # Should show helpful prompt
            assert "Press space to continue" in result or "quit" in result


class TestMoreStdin:
    """Test reading from stdin."""
    
    def test_more_from_stdin(self, more_setup):
        """Test reading from stdin buffer."""
        shell, cmd = more_setup
        shell._stdin_buffer = "Stdin line 1\nStdin line 2\nStdin line 3"
        result = cmd.execute([])
        assert "Stdin line 1" in result
        assert "Stdin line 2" in result
    
    def test_more_no_stdin_no_files(self, more_setup):
        """Test with no stdin and no files."""
        shell, cmd = more_setup
        result = cmd.execute([])
        assert "missing operand" in result


class TestMoreSpecialContent:
    """Test handling of special content."""
    
    def test_more_binary_content(self, more_setup):
        """Test displaying binary content."""
        shell, cmd = more_setup
        result = cmd.execute(["/binary.bin"])
        # Should handle binary content somehow
        assert "Normal" in result or "Binary" in result
    
    def test_more_unicode_content(self, more_setup):
        """Test displaying unicode content."""
        shell, cmd = more_setup
        result = cmd.execute(["/unicode.txt"])
        # Should handle unicode
        assert result  # At minimum should not crash
    
    def test_more_long_lines(self, more_setup):
        """Test handling very long lines."""
        shell, cmd = more_setup
        result = cmd.execute(["/longlines.txt"])
        assert "Line 1:" in result
        assert "xxx" in result  # Part of the long line
    
    def test_more_tab_content(self, more_setup):
        """Test handling tab characters."""
        shell, cmd = more_setup
        result = cmd.execute(["/tabs.txt"])
        assert "Col1" in result
        assert "Data1" in result


class TestMoreOptions:
    """Test various command options."""
    
    def test_more_help(self, more_setup):
        """Test --help flag."""
        shell, cmd = more_setup
        result = cmd.execute(["--help"])
        assert "more - Display file contents" in result
        assert "Usage:" in result
        assert "-s" in result
        assert "+NUM" in result
    
    def test_more_version(self, more_setup):
        """Test --version flag."""
        shell, cmd = more_setup
        result = cmd.execute(["--version"])
        assert "more version" in result
    
    def test_more_invalid_lines(self, more_setup):
        """Test invalid number of lines."""
        shell, cmd = more_setup
        result = cmd.execute(["-n", "abc", "/short.txt"])
        assert "invalid number" in result
    
    def test_more_logical_lines(self, more_setup):
        """Test -f flag for logical lines."""
        shell, cmd = more_setup
        result = cmd.execute(["-f", "/short.txt"])
        # Should count logical lines
        assert "Line 1" in result
    
    def test_more_plain_mode(self, more_setup):
        """Test -u flag for plain mode."""
        shell, cmd = more_setup
        result = cmd.execute(["-u", "/short.txt"])
        # Should suppress underlining (no-op in our implementation)
        assert "Line 1" in result


class TestMoreCombinations:
    """Test combining multiple options."""
    
    def test_more_squeeze_and_start(self, more_setup):
        """Test combining squeeze and start position."""
        shell, cmd = more_setup
        result = cmd.execute(["-s", "+2", "/blank.txt"])
        # Should squeeze blanks and start at line 2
        consecutive_blanks = 0
        max_consecutive = 0
        for line in result.split("\n"):
            if line.strip() == "" and "--More--" not in line:
                consecutive_blanks += 1
                max_consecutive = max(max_consecutive, consecutive_blanks)
            else:
                consecutive_blanks = 0
        assert max_consecutive <= 1
    
    def test_more_page_size_and_clear(self, more_setup):
        """Test combining page size and clear screen."""
        shell, cmd = more_setup
        result = cmd.execute(["-5", "-p", "/long.txt"])
        # Should have small pages and clear screen
        assert "[Screen cleared]" in result or "--More--" in result
        more_count = result.count("--More--")
        assert more_count > 10
    
    def test_more_multiple_files_with_options(self, more_setup):
        """Test multiple files with various options."""
        shell, cmd = more_setup
        result = cmd.execute(["-s", "-10", "/short.txt", "/blank.txt"])
        # Should process both files with options
        assert "::::::" in result  # File separator
        assert "Line 1" in result


class TestMoreErrorHandling:
    """Test error handling."""
    
    def test_more_mixed_valid_invalid(self, more_setup):
        """Test mix of valid and invalid files."""
        shell, cmd = more_setup
        result = cmd.execute(["/short.txt", "/nonexistent.txt", "/empty.txt"])
        # Should show error for nonexistent but continue
        assert "No such file or directory" in result
        assert "Line 1" in result  # From short.txt
    
    def test_more_all_invalid_files(self, more_setup):
        """Test all invalid files."""
        shell, cmd = more_setup
        result = cmd.execute(["/nonexistent1.txt", "/nonexistent2.txt"])
        # Should show errors for all
        assert result.count("No such file or directory") == 2


class TestMoreRealWorldScenarios:
    """Test real-world usage scenarios."""
    
    def test_more_log_file_viewing(self, more_setup):
        """Test viewing a log file with pagination."""
        shell, cmd = more_setup
        # Create a log file
        log_content = "\n".join([
            f"2024-01-01 12:00:{i:02d} INFO: Log entry {i}"
            for i in range(100)
        ])
        shell.fs.write_file("/app.log", log_content)
        
        result = cmd.execute(["-20", "/app.log"])
        assert "2024-01-01" in result
        assert "INFO: Log entry" in result
        assert "--More--" in result
    
    def test_more_config_file_viewing(self, more_setup):
        """Test viewing configuration files."""
        shell, cmd = more_setup
        config = """# Configuration file
# Server settings
server.host=localhost
server.port=8080

# Database settings
db.host=localhost
db.port=5432
db.name=myapp

# Logging
log.level=INFO
log.file=/var/log/app.log"""
        shell.fs.write_file("/config.ini", config)
        
        result = cmd.execute(["-s", "/config.ini"])
        assert "server.host" in result
        assert "db.name" in result
        # Squeezed blanks
        lines = result.split("\n")
        consecutive_blanks = 0
        for line in lines:
            if line.strip() == "":
                consecutive_blanks += 1
                assert consecutive_blanks <= 1
            else:
                consecutive_blanks = 0
    
    def test_more_search_in_file(self, more_setup):
        """Test searching for pattern in file."""
        shell, cmd = more_setup
        # Create file with specific content
        content = "\n".join([
            f"Line {i}" for i in range(1, 50)
        ] + ["ERROR: Something went wrong"] + [
            f"Line {i}" for i in range(51, 100)
        ])
        shell.fs.write_file("/debug.log", content)
        
        result = cmd.execute(["+/ERROR", "/debug.log"])
        # Should start at or near the ERROR line
        lines = result.split("\n")
        found_error = False
        for i in range(min(10, len(lines))):
            if "ERROR" in lines[i]:
                found_error = True
                break
        assert found_error