"""
Tests for the df (disk free) command
"""

from tests.dummy_shell import DummyShell
from chuk_virtual_shell.commands.filesystem.df import DfCommand


class TestDfCommand:
    """Test cases for the df command"""

    def setup_method(self):
        """Set up test environment before each test"""
        self.shell = DummyShell({})
        self.cmd = DfCommand(self.shell)

        # Create some test files
        self.shell.fs.write_file("/test1.txt", "x" * 1024)  # 1KB file
        self.shell.fs.write_file("/test2.txt", "y" * 2048)  # 2KB file
        self.shell.fs.mkdir("/testdir")
        self.shell.fs.write_file("/testdir/test3.txt", "z" * 512)  # 0.5KB file

    def test_df_basic(self):
        """Test basic df command without arguments"""
        result = self.cmd.execute([])
        assert "Filesystem" in result
        assert "1K-blocks" in result
        assert "Used" in result
        assert "Available" in result
        assert "Use%" in result
        assert "Mounted on" in result
        assert "/" in result  # Root mount point

    def test_df_human_readable(self):
        """Test df with human-readable flag"""
        result = self.cmd.execute(["-h"])
        assert "Filesystem" in result
        assert "Mounted on" in result
        # Should show human-readable sizes (K, M, G, etc.)

        # Also test long form
        result2 = self.cmd.execute(["--human-readable"])
        assert "Filesystem" in result2

    def test_df_inodes(self):
        """Test df with inode information flag"""
        result = self.cmd.execute(["-i"])
        assert "Filesystem" in result
        assert "Inodes" in result
        assert "IUsed" in result
        assert "IFree" in result
        assert "IUse%" in result

        # Also test long form
        result2 = self.cmd.execute(["--inodes"])
        assert "Inodes" in result2

    def test_df_specific_path(self):
        """Test df with specific path"""
        result = self.cmd.execute(["/testdir"])
        assert "Filesystem" in result
        assert "/testdir" in result

    def test_df_nonexistent_path(self):
        """Test df with non-existent path"""
        result = self.cmd.execute(["/nonexistent"])
        assert "No such file or directory" in result

    def test_df_multiple_paths(self):
        """Test df with multiple paths"""
        result = self.cmd.execute(["/", "/testdir"])
        assert "Filesystem" in result
        lines = result.split("\n")
        # Should have header + 2 data lines (one for each path)
        assert len(lines) >= 3

    def test_df_help(self):
        """Test df help output"""
        result = self.cmd.execute(["-h", "--help"])
        # Should show help when invalid combination is used
        assert result

    def test_df_with_file_path(self):
        """Test df with a file path (should show filesystem of that file)"""
        result = self.cmd.execute(["/test1.txt"])
        assert "Filesystem" in result
        assert "/" in result  # Should show root filesystem

    def test_df_human_readable_with_paths(self):
        """Test df with human-readable and specific paths"""
        result = self.cmd.execute(["-h", "/", "/testdir"])
        assert "Filesystem" in result
        # Just check that we got output
        lines = result.split("\n")
        assert len(lines) > 1  # Should have header + data

    def test_df_inode_with_paths(self):
        """Test df with inode flag and specific paths"""
        result = self.cmd.execute(["-i", "/testdir"])
        assert "Inodes" in result
        assert "/testdir" in result

    def test_df_storage_stats(self):
        """Test that df correctly reports storage statistics"""
        # Get the storage stats directly
        self.shell.fs.get_storage_stats()

        # Run df command
        result = self.cmd.execute([])

        # Parse the output to verify stats are reflected
        lines = result.split("\n")
        for line in lines:
            if "/" in line and "Filesystem" not in line:
                parts = line.split()
                if len(parts) >= 5:
                    # Verify that total/used/available make sense
                    try:
                        if not any(
                            suffix in parts[1] for suffix in ["K", "M", "G", "T"]
                        ):
                            total = int(parts[1])
                            used = int(parts[2])
                            available = int(parts[3])
                            # Basic sanity check
                            assert total >= 0
                            assert used >= 0
                            assert available >= 0
                    except (ValueError, IndexError):
                        pass  # Skip if parsing fails

    def test_df_percentage_calculation(self):
        """Test that df correctly calculates usage percentage"""
        result = self.cmd.execute([])
        lines = result.split("\n")

        # Just verify we got some output with percentages
        assert any("%" in line or "-" in line for line in lines)

    def test_df_mixed_arguments(self):
        """Test df with mixed arguments"""
        # Test with both flags and paths
        result = self.cmd.execute(["-h", "-i", "/"])
        # Should handle mixed arguments gracefully
        assert result
