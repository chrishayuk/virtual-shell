"""
Comprehensive tests for the df (disk free) command.
Tests all df functionality including various flags and edge cases.
"""

import pytest
from tests.dummy_shell import DummyShell
from chuk_virtual_shell.commands.filesystem.df import DfCommand


@pytest.fixture
def df_setup():
    """Set up test environment with various files and directories."""
    files = {
        "/": {},  # Root directory
        "/small.txt": "x" * 512,  # 512 bytes
        "/medium.txt": "y" * 5120,  # 5KB
        "/large.txt": "z" * 51200,  # 50KB
        "/huge.txt": "a" * 1048576,  # 1MB
        "/dir1": {},  # Directory
        "/dir1/file1.txt": "content1" * 100,
        "/dir1/file2.txt": "content2" * 200,
        "/dir2": {},  # Directory
        "/dir2/nested": {},  # Nested directory
        "/dir2/nested/deep.txt": "deep content",
        "/empty.txt": "",
        "/binary.bin": b"\x00\x01\x02\x03" * 256,
    }
    shell = DummyShell(files)
    cmd = DfCommand(shell)
    
    # Mock storage stats for testing
    def mock_storage_stats():
        total_size = sum(len(content) if isinstance(content, (str, bytes)) else 0 
                        for content in files.values())
        return {
            "provider_name": "testfs",
            "fs_type": "vfs",
            "max_total_size": 104857600,  # 100MB
            "total_size_bytes": total_size,
            "max_files": 10000,
            "file_count": len(files),
        }
    
    shell.fs.get_storage_stats = mock_storage_stats
    return shell, cmd


class TestDfBasic:
    """Test basic df functionality."""
    
    def test_df_no_args(self, df_setup):
        """Test df with no arguments."""
        shell, cmd = df_setup
        result = cmd.execute([])
        assert "Filesystem" in result
        assert "1K-blocks" in result
        assert "Used" in result
        assert "Available" in result
        assert "Use%" in result
        assert "Mounted on" in result
        assert "/" in result
        assert "testfs" in result
    
    def test_df_help(self, df_setup):
        """Test df help flag."""
        shell, cmd = df_setup
        result = cmd.execute(["--help"])
        assert "df - Display disk free space" in result
        assert "Usage:" in result
        assert "-h, --human-readable" in result
        assert "-i, --inodes" in result
        assert "-P, --portability" in result
    
    def test_df_specific_path(self, df_setup):
        """Test df with specific path."""
        shell, cmd = df_setup
        result = cmd.execute(["/dir1"])
        assert "Filesystem" in result
        assert "/dir1" in result
        assert "testfs" in result
    
    def test_df_multiple_paths(self, df_setup):
        """Test df with multiple paths."""
        shell, cmd = df_setup
        result = cmd.execute(["/", "/dir1", "/dir2"])
        lines = result.split("\n")
        # Header + 3 data lines
        assert len(lines) >= 4
        assert "/" in result
        assert "/dir1" in result
        assert "/dir2" in result
    
    def test_df_nonexistent_path(self, df_setup):
        """Test df with non-existent path."""
        shell, cmd = df_setup
        result = cmd.execute(["/nonexistent"])
        assert "No such file or directory" in result
    
    def test_df_file_path(self, df_setup):
        """Test df with file path (should show filesystem of that file)."""
        shell, cmd = df_setup
        result = cmd.execute(["/small.txt"])
        assert "Filesystem" in result
        assert "/" in result  # Should show root filesystem


class TestDfHumanReadable:
    """Test human-readable output format."""
    
    def test_df_h_flag(self, df_setup):
        """Test -h flag for human-readable output."""
        shell, cmd = df_setup
        result = cmd.execute(["-h"])
        assert "Filesystem" in result
        # Should contain human-readable sizes
        lines = result.split("\n")
        for line in lines[1:]:  # Skip header
            if line and "testfs" in line:
                # Should have units like K, M, G
                assert any(unit in line for unit in ["B", "K", "M", "G"]) or "0" in line
    
    def test_df_human_readable_long(self, df_setup):
        """Test --human-readable flag."""
        shell, cmd = df_setup
        result = cmd.execute(["--human-readable"])
        assert "Filesystem" in result
    
    def test_df_human_readable_sizes(self, df_setup):
        """Test that human-readable formats sizes correctly."""
        shell, cmd = df_setup
        # Test the format_size method directly
        assert cmd._format_size(0) == "0"
        assert cmd._format_size(512) == "512B"
        assert cmd._format_size(1024) == "1.00K"  # Should be 1.00K based on implementation
        assert cmd._format_size(1536) == "1.50K"  # Should be 1.50K
        assert cmd._format_size(1048576) == "1.00M"  # Should be 1.00M
        assert cmd._format_size(1073741824) == "1.00G"  # Should be 1.00G
        assert cmd._format_size(1099511627776) == "1.00T"  # Should be 1.00T


class TestDfInodes:
    """Test inode display functionality."""
    
    def test_df_i_flag(self, df_setup):
        """Test -i flag for inode information."""
        shell, cmd = df_setup
        result = cmd.execute(["-i"])
        assert "Filesystem" in result
        assert "Inodes" in result
        assert "IUsed" in result
        assert "IFree" in result
        assert "IUse%" in result
    
    def test_df_inodes_long(self, df_setup):
        """Test --inodes flag."""
        shell, cmd = df_setup
        result = cmd.execute(["--inodes"])
        assert "Inodes" in result
    
    def test_df_inodes_with_path(self, df_setup):
        """Test inodes display with specific path."""
        shell, cmd = df_setup
        result = cmd.execute(["-i", "/dir1"])
        assert "Inodes" in result
        assert "/dir1" in result
    
    def test_df_inodes_calculation(self, df_setup):
        """Test that inode percentages are calculated correctly."""
        shell, cmd = df_setup
        result = cmd.execute(["-i"])
        lines = result.split("\n")
        for line in lines[1:]:  # Skip header
            if line and "testfs" in line:
                # Should have percentage
                assert "%" in line or "-" in line


class TestDfBlockSize:
    """Test block size options."""
    
    def test_df_k_flag(self, df_setup):
        """Test -k flag for 1K blocks."""
        shell, cmd = df_setup
        result = cmd.execute(["-k"])
        assert "1K-blocks" in result
    
    def test_df_block_size_flag(self, df_setup):
        """Test -B flag with various block sizes."""
        shell, cmd = df_setup
        
        # Test with 512 byte blocks
        result = cmd.execute(["-B", "512"])
        assert "512-blocks" in result
        
        # Test with 1K blocks
        result = cmd.execute(["-B", "1K"])
        assert "1K-blocks" in result
        
        # Test with 1M blocks
        result = cmd.execute(["-B", "1M"])
        assert "1M-blocks" in result
    
    def test_df_invalid_block_size(self, df_setup):
        """Test invalid block size."""
        shell, cmd = df_setup
        result = cmd.execute(["-B", "invalid"])
        assert "invalid block size" in result


class TestDfPortability:
    """Test POSIX portability mode."""
    
    def test_df_P_flag(self, df_setup):
        """Test -P flag for POSIX output."""
        shell, cmd = df_setup
        result = cmd.execute(["-P"])
        assert "512-blocks" in result  # POSIX uses 512-byte blocks
        assert "Capacity" in result  # POSIX uses "Capacity" instead of "Use%"
    
    def test_df_portability_long(self, df_setup):
        """Test --portability flag."""
        shell, cmd = df_setup
        result = cmd.execute(["--portability"])
        assert "512-blocks" in result


class TestDfType:
    """Test filesystem type options."""
    
    def test_df_T_flag(self, df_setup):
        """Test -T flag to print filesystem type."""
        shell, cmd = df_setup
        result = cmd.execute(["-T"])
        assert "Type" in result
        lines = result.split("\n")
        for line in lines[1:]:  # Skip header
            if line and "testfs" in line:
                assert "vfs" in line  # Should show fs type
    
    def test_df_print_type_long(self, df_setup):
        """Test --print-type flag."""
        shell, cmd = df_setup
        result = cmd.execute(["--print-type"])
        assert "Type" in result
    
    def test_df_type_filter(self, df_setup):
        """Test -t flag to filter by type."""
        shell, cmd = df_setup
        
        # Should show vfs filesystems
        result = cmd.execute(["-t", "vfs"])
        assert "testfs" in result
        
        # Should not show anything for different type
        result = cmd.execute(["-t", "ext4"])
        lines = result.split("\n")
        # Only header should be present
        assert len([l for l in lines if l and "testfs" in l]) == 0
    
    def test_df_exclude_type(self, df_setup):
        """Test -x flag to exclude by type."""
        shell, cmd = df_setup
        
        # Should exclude vfs filesystems
        result = cmd.execute(["-x", "vfs"])
        lines = result.split("\n")
        # Should not show vfs filesystems
        assert len([l for l in lines if l and "testfs" in l]) == 0
        
        # Should show when excluding different type
        result = cmd.execute(["-x", "ext4"])
        assert "testfs" in result


class TestDfTotal:
    """Test total line functionality."""
    
    def test_df_total_flag(self, df_setup):
        """Test --total flag."""
        shell, cmd = df_setup
        result = cmd.execute(["--total", "/", "/dir1"])
        lines = result.split("\n")
        # Should have a total line
        assert any("total" in line for line in lines)
    
    def test_df_total_calculation(self, df_setup):
        """Test that totals are calculated correctly."""
        shell, cmd = df_setup
        result = cmd.execute(["--total"])
        lines = result.split("\n")
        total_line = [l for l in lines if "total" in l]
        assert len(total_line) > 0
        # Total line should have percentage
        assert "%" in total_line[0] or "-" in total_line[0]
    
    def test_df_total_with_human_readable(self, df_setup):
        """Test total with human-readable format."""
        shell, cmd = df_setup
        result = cmd.execute(["--total", "-h"])
        lines = result.split("\n")
        total_line = [l for l in lines if "total" in l]
        assert len(total_line) > 0


class TestDfCombinations:
    """Test various flag combinations."""
    
    def test_df_hi_flags(self, df_setup):
        """Test combining -h and -i flags."""
        shell, cmd = df_setup
        result = cmd.execute(["-h", "-i"])
        # -i should take precedence
        assert "Inodes" in result
    
    def test_df_hT_flags(self, df_setup):
        """Test combining -h and -T flags."""
        shell, cmd = df_setup
        result = cmd.execute(["-h", "-T"])
        assert "Type" in result
        # Should have human-readable sizes
        lines = result.split("\n")
        for line in lines[1:]:
            if line and "testfs" in line:
                assert "vfs" in line
    
    def test_df_PT_flags(self, df_setup):
        """Test combining -P and -T flags."""
        shell, cmd = df_setup
        result = cmd.execute(["-P", "-T"])
        assert "512-blocks" in result
        assert "Type" in result
    
    def test_df_all_flags(self, df_setup):
        """Test -a flag (include all filesystems)."""
        shell, cmd = df_setup
        result = cmd.execute(["-a"])
        assert "Filesystem" in result
        # Should include all filesystems (in our case, just the one)
        assert "testfs" in result


class TestDfEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_df_empty_filesystem(self, df_setup):
        """Test df with empty filesystem."""
        shell, cmd = df_setup
        # Mock empty filesystem
        def mock_empty_stats():
            return {
                "provider_name": "emptyfs",
                "fs_type": "vfs",
                "max_total_size": 104857600,
                "total_size_bytes": 0,
                "max_files": 10000,
                "file_count": 0,
            }
        shell.fs.get_storage_stats = mock_empty_stats
        
        result = cmd.execute([])
        assert "emptyfs" in result
        # Should show 0% usage
        assert "0%" in result or "-" in result
    
    def test_df_full_filesystem(self, df_setup):
        """Test df with full filesystem."""
        shell, cmd = df_setup
        # Mock full filesystem
        def mock_full_stats():
            return {
                "provider_name": "fullfs",
                "fs_type": "vfs",
                "max_total_size": 104857600,
                "total_size_bytes": 104857600,
                "max_files": 10000,
                "file_count": 10000,
            }
        shell.fs.get_storage_stats = mock_full_stats
        
        result = cmd.execute([])
        assert "fullfs" in result
        # Should show 100% usage
        assert "100%" in result
    
    def test_df_zero_size_filesystem(self, df_setup):
        """Test df with zero-size filesystem."""
        shell, cmd = df_setup
        # Mock zero-size filesystem
        def mock_zero_stats():
            return {
                "provider_name": "zerofs",
                "fs_type": "vfs",
                "max_total_size": 0,
                "total_size_bytes": 0,
                "max_files": 0,
                "file_count": 0,
            }
        shell.fs.get_storage_stats = mock_zero_stats
        
        result = cmd.execute([])
        assert "zerofs" in result
        # Should handle division by zero gracefully
        assert "-" in result or "0" in result
    
    def test_df_mixed_valid_invalid_paths(self, df_setup):
        """Test df with mix of valid and invalid paths."""
        shell, cmd = df_setup
        result = cmd.execute(["/", "/nonexistent", "/dir1"])
        assert "/" in result
        assert "/dir1" in result
        assert "No such file or directory" in result
    
    def test_df_very_large_sizes(self, df_setup):
        """Test df with very large filesystem sizes."""
        shell, cmd = df_setup
        # Mock very large filesystem
        def mock_large_stats():
            return {
                "provider_name": "largefs",
                "fs_type": "vfs",
                "max_total_size": 1099511627776000,  # 1PB
                "total_size_bytes": 549755813888000,  # 500TB
                "max_files": 1000000000,
                "file_count": 500000000,
            }
        shell.fs.get_storage_stats = mock_large_stats
        
        result = cmd.execute(["-h"])
        assert "largefs" in result
        # Should handle large sizes with appropriate units
        assert any(unit in result for unit in ["T", "P", "E"])


class TestDfRealWorldScenarios:
    """Test real-world usage scenarios."""
    
    def test_df_monitoring_script(self, df_setup):
        """Test df usage in monitoring script scenario."""
        shell, cmd = df_setup
        
        # Check multiple paths
        result = cmd.execute(["-h", "/", "/dir1", "/dir2"])
        lines = result.split("\n")
        assert len(lines) >= 4  # Header + data lines
        
        # Parse output for monitoring
        for line in lines[1:]:
            if line and "testfs" in line:
                parts = line.split()
                # Should be able to parse percentage
                percent_str = [p for p in parts if "%" in p]
                assert len(percent_str) > 0
    
    def test_df_disk_usage_report(self, df_setup):
        """Test df for disk usage reporting."""
        shell, cmd = df_setup
        
        # Generate report with type and human-readable
        result = cmd.execute(["-hT", "--total"])
        assert "Type" in result
        assert "total" in result
        
        # Should be formatted for readability
        lines = result.split("\n")
        assert all(len(line) < 120 for line in lines)  # Reasonable line length
    
    def test_df_inode_exhaustion_check(self, df_setup):
        """Test df for checking inode exhaustion."""
        shell, cmd = df_setup
        
        # Mock high inode usage
        def mock_inode_exhaustion():
            return {
                "provider_name": "busyfs",
                "fs_type": "vfs",
                "max_total_size": 104857600,
                "total_size_bytes": 10485760,  # Only 10% space used
                "max_files": 1000,
                "file_count": 950,  # 95% inodes used
            }
        shell.fs.get_storage_stats = mock_inode_exhaustion
        
        result = cmd.execute(["-i"])
        assert "95%" in result  # High inode usage
    
    def test_df_ci_cd_pipeline(self, df_setup):
        """Test df usage in CI/CD pipeline."""
        shell, cmd = df_setup
        
        # Check available space before deployment
        result = cmd.execute(["-B", "1M"])  # Use MB for easy parsing
        assert "1M-blocks" in result
        
        # Parse to check available space
        lines = result.split("\n")
        for line in lines[1:]:
            if line and "testfs" in line:
                parts = line.split()
                # Should have numeric values for parsing
                assert any(p.isdigit() for p in parts)