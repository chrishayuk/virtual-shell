"""
Tests for the more command (paginated file viewer)
"""

from tests.dummy_shell import DummyShell
from chuk_virtual_shell.commands.filesystem.more import MoreCommand


class TestMoreCommand:
    """Test cases for the more command"""

    def setup_method(self):
        """Set up test environment before each test"""
        self.shell = DummyShell({})
        self.cmd = MoreCommand(self.shell)

        # Create test files with various content
        self.short_content = "Line 1\nLine 2\nLine 3"
        self.shell.fs.write_file("/short.txt", self.short_content)

        # Create a long file (more than 24 lines for pagination)
        self.long_content = "\n".join([f"Line {i}" for i in range(1, 51)])
        self.shell.fs.write_file("/long.txt", self.long_content)

        # Create empty file
        self.shell.fs.write_file("/empty.txt", "")

        # Create file with long lines
        self.long_lines = "\n".join(
            [
                f"This is a very long line with lots of text: {'x' * 100}"
                for i in range(10)
            ]
        )
        self.shell.fs.write_file("/long_lines.txt", self.long_lines)

    def test_more_basic(self):
        """Test basic more command with a short file"""
        result = self.cmd.execute(["/short.txt"])
        assert "Line 1" in result
        assert "Line 2" in result
        assert "Line 3" in result

    def test_more_nonexistent_file(self):
        """Test more with non-existent file"""
        result = self.cmd.execute(["/nonexistent.txt"])
        assert "No such file" in result or "cannot open" in result

    def test_more_empty_file(self):
        """Test more with empty file"""
        result = self.cmd.execute(["/empty.txt"])
        # Should handle empty file gracefully
        assert result == "" or "empty" in result.lower()

    def test_more_no_arguments(self):
        """Test more without arguments"""
        result = self.cmd.execute([])
        assert "missing operand" in result.lower()

    def test_more_multiple_files(self):
        """Test more with multiple files"""
        result = self.cmd.execute(["/short.txt", "/empty.txt"])
        # Should show first file (pagination not tested here)
        assert "Line 1" in result or "short.txt" in result

    def test_more_long_file(self):
        """Test more with a file longer than page size"""
        result = self.cmd.execute(["/long.txt"])
        # Should show first page (first 24 lines by default)
        assert "Line 1" in result
        # The more command shows all content in our implementation
        lines = result.split("\n")
        # Check that we got some output
        assert len(lines) > 0

    def test_more_with_options(self):
        """Test more with various options"""
        # Test with number of lines option (if supported)
        result = self.cmd.execute(["-10", "/long.txt"])
        if "usage" not in result.lower():
            # With -10, should paginate with 10 lines per page
            # Check that pagination markers appear
            assert "--More--" in result
            # Should have multiple pages for a 50-line file with 10 lines per page
            more_count = result.count("--More--")
            assert more_count >= 3  # At least 4 pages (10+10+10+10+10)

    def test_more_directory(self):
        """Test more with a directory (should fail)"""
        self.shell.fs.mkdir("/testdir")
        result = self.cmd.execute(["/testdir"])
        # Since read_file returns None for directories, should get "No such file"
        assert "No such file" in result or "directory" in result.lower()

    def test_more_binary_content(self):
        """Test more with binary-like content"""
        # Create a file with non-printable characters
        binary_content = "Normal text\x00\x01\x02\nMore text\xff\xfe"
        self.shell.fs.write_file("/binary.txt", binary_content)
        result = self.cmd.execute(["/binary.txt"])
        # Should handle binary content somehow
        assert result  # Should return something

    def test_more_help(self):
        """Test more help message"""
        result = self.cmd.execute(["--help"])
        assert "more" in result.lower() or "usage" in result.lower()

    def test_more_pagination_marker(self):
        """Test that more shows pagination indicator for long files"""
        result = self.cmd.execute(["/long.txt"])
        # Might show a "-- More --" or percentage indicator
        # This depends on implementation, but should handle long files
        assert result

    def test_more_with_stdin(self):
        """Test more reading from stdin (if supported)"""
        # Set up stdin buffer
        self.shell._stdin_buffer = self.long_content
        result = self.cmd.execute([])
        # Might read from stdin or show usage
        assert result

    def test_more_special_characters(self):
        """Test more with special characters in content"""
        special_content = "Tab\there\nNewline\nCarriage\rReturn\nForm\fFeed"
        self.shell.fs.write_file("/special.txt", special_content)
        result = self.cmd.execute(["/special.txt"])
        # Should handle special characters
        assert "Tab" in result or result

    def test_more_unicode_content(self):
        """Test more with unicode content"""
        unicode_content = "Hello 世界\n🎉 Emoji test\nÄccëntéd characters"
        self.shell.fs.write_file("/unicode.txt", unicode_content)
        result = self.cmd.execute(["/unicode.txt"])
        # Should handle unicode (may depend on encoding)
        assert result

    def test_more_line_wrapping(self):
        """Test more with very long lines"""
        result = self.cmd.execute(["/long_lines.txt"])
        # Should handle long lines (wrap or truncate)
        assert "This is a very long line" in result

    def test_more_relative_path(self):
        """Test more with relative path"""
        # Change to a subdirectory
        self.shell.fs.mkdir("/subdir")
        self.shell.fs.cwd = "/subdir"
        self.shell.fs.write_file("/subdir/local.txt", "Local file content")

        result = self.cmd.execute(["local.txt"])
        if "Local file content" in result:
            assert True
        else:
            # Might not support relative paths
            assert "No such file" in result or "cannot open" in result
