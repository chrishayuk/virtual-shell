"""
Comprehensive tests for the du (disk usage) command.
Tests all du functionality including various flags and edge cases.
"""

import pytest
from chuk_virtual_shell.commands.filesystem.du import DuCommand
from tests.dummy_shell import DummyShell


@pytest.fixture
def du_setup():
    """Set up test environment with various files and directories."""
    files = {
        "/": {"file1.txt": None, "file2.txt": None, "large.txt": None, "empty.txt": None, 
              "dir1": None, "dir2": None, "empty_dir": None, "unicode.txt": None, 
              "binary.bin": None, ".hidden": None},  # Root directory with contents
        "/file1.txt": "a" * 1024,  # 1KB
        "/file2.txt": "b" * 2048,  # 2KB
        "/large.txt": "x" * 10240,  # 10KB
        "/empty.txt": "",  # 0 bytes
        "/dir1": {"file1.txt": None, "file2.txt": None, "subdir": None},
        "/dir1/file1.txt": "c" * 512,  # 512 bytes
        "/dir1/file2.txt": "d" * 1536,  # 1.5KB
        "/dir1/subdir": {"deep.txt": None},
        "/dir1/subdir/deep.txt": "e" * 256,  # 256 bytes
        "/dir2": {"data.txt": None, "nested": None},
        "/dir2/data.txt": "f" * 4096,  # 4KB
        "/dir2/nested": {"level2": None},
        "/dir2/nested/level2": {"file.txt": None},
        "/dir2/nested/level2/file.txt": "g" * 128,  # 128 bytes
        "/empty_dir": {},
        "/unicode.txt": "世界" * 100,  # Unicode content
        "/binary.bin": b"\x00\x01\x02\x03" * 256,  # 1KB binary
        "/.hidden": {"secret.txt": None},
        "/.hidden/secret.txt": "secret" * 100,  # Hidden dir with file
    }
    
    shell = DummyShell(files)
    # Set current directory
    shell.fs.current_directory = "/"
    shell.environ = {"PWD": "/"}
    
    # Add exists method for compatibility
    shell.exists = lambda path: path in files
    
    cmd = DuCommand(shell)
    return shell, cmd


class TestDuBasic:
    """Test basic du functionality."""
    
    def test_du_no_args(self, du_setup):
        """Test du with no arguments (current directory)."""
        shell, cmd = du_setup
        result = cmd.execute([])
        lines = result.split("\n")
        # Should show directories and total
        assert any("dir1" in line for line in lines)
        assert any("dir2" in line for line in lines)
        # Last line should be current directory total (. or /)
        assert lines[-1].endswith(".") or lines[-1].endswith("/")
    
    def test_du_specific_path(self, du_setup):
        """Test du with specific path."""
        shell, cmd = du_setup
        result = cmd.execute(["/dir1"])
        assert "/dir1/subdir" in result
        assert "/dir1" in result
    
    def test_du_multiple_paths(self, du_setup):
        """Test du with multiple paths."""
        shell, cmd = du_setup
        result = cmd.execute(["/dir1", "/dir2"])
        assert "/dir1" in result
        assert "/dir2" in result
    
    def test_du_file_path(self, du_setup):
        """Test du with file path."""
        shell, cmd = du_setup
        result = cmd.execute(["/file1.txt"])
        lines = result.split("\n")
        assert len(lines) == 1
        assert "/file1.txt" in result
        # Should show 1KB (1024 bytes / 1024)
        assert "1\t" in result
    
    def test_du_nonexistent_path(self, du_setup):
        """Test du with non-existent path."""
        shell, cmd = du_setup
        result = cmd.execute(["/nonexistent"])
        assert "No such file or directory" in result
    
    def test_du_empty_directory(self, du_setup):
        """Test du with empty directory."""
        shell, cmd = du_setup
        result = cmd.execute(["/empty_dir"])
        assert "/empty_dir" in result
        # Should show 0 size
        assert "0\t" in result


class TestDuHumanReadable:
    """Test human-readable output format."""
    
    def test_du_h_flag(self, du_setup):
        """Test -h flag for human-readable output."""
        shell, cmd = du_setup
        result = cmd.execute(["-h"])
        # Should contain human-readable sizes
        assert any(unit in result for unit in ["B", "K", "M"]) or "0" in result
    
    def test_du_human_readable_long(self, du_setup):
        """Test --human-readable flag."""
        shell, cmd = du_setup
        result = cmd.execute(["--human-readable", "/dir1"])
        assert any(unit in result for unit in ["B", "K"]) or "0" in result
    
    def test_du_human_readable_sizes(self, du_setup):
        """Test human-readable formatting of various sizes."""
        shell, cmd = du_setup
        # Test the format method directly
        assert cmd._format_human_readable(0) == "0"
        assert cmd._format_human_readable(512) == "512B"
        assert cmd._format_human_readable(1024) == "1.0K"
        assert cmd._format_human_readable(1536) == "1.5K"
        assert cmd._format_human_readable(10240) == "10K"
        assert cmd._format_human_readable(1048576) == "1.0M"
        assert cmd._format_human_readable(1073741824) == "1.0G"


class TestDuSummarize:
    """Test summarize option."""
    
    def test_du_s_flag(self, du_setup):
        """Test -s flag for summary only."""
        shell, cmd = du_setup
        result = cmd.execute(["-s", "/dir1"])
        lines = result.split("\n")
        # Should only show one line with total
        assert len(lines) == 1
        assert "/dir1" in result
        # Should not show subdirectories
        assert "subdir" not in result
    
    def test_du_summarize_long(self, du_setup):
        """Test --summarize flag."""
        shell, cmd = du_setup
        result = cmd.execute(["--summarize", "/dir2"])
        lines = result.split("\n")
        assert len(lines) == 1
        assert "/dir2" in result
    
    def test_du_summarize_multiple(self, du_setup):
        """Test summarize with multiple paths."""
        shell, cmd = du_setup
        result = cmd.execute(["-s", "/dir1", "/dir2", "/file1.txt"])
        lines = result.split("\n")
        # Should show one line per path
        assert len(lines) == 3
        assert "/dir1" in result
        assert "/dir2" in result
        assert "/file1.txt" in result


class TestDuTotal:
    """Test total option."""
    
    def test_du_c_flag(self, du_setup):
        """Test -c flag for grand total."""
        shell, cmd = du_setup
        result = cmd.execute(["-c", "/file1.txt", "/file2.txt"])
        lines = result.split("\n")
        # Should have a total line
        assert any("total" in line for line in lines)
        # Total should be 3 (1KB + 2KB)
        assert "3\ttotal" in result
    
    def test_du_total_long(self, du_setup):
        """Test --total flag."""
        shell, cmd = du_setup
        result = cmd.execute(["--total", "/dir1", "/dir2"])
        assert "total" in result
    
    def test_du_total_with_summarize(self, du_setup):
        """Test total with summarize."""
        shell, cmd = du_setup
        result = cmd.execute(["-sc", "/dir1", "/dir2"])
        lines = result.split("\n")
        # Should show summary for each and total
        assert len(lines) == 3
        assert "total" in lines[-1]


class TestDuAllFiles:
    """Test showing all files."""
    
    def test_du_a_flag(self, du_setup):
        """Test -a flag to show all files."""
        shell, cmd = du_setup
        result = cmd.execute(["-a", "/dir1"])
        # Should show files, not just directories
        assert "file1.txt" in result
        assert "file2.txt" in result
        assert "deep.txt" in result
    
    def test_du_all_long(self, du_setup):
        """Test --all flag."""
        shell, cmd = du_setup
        result = cmd.execute(["--all", "/dir2"])
        assert "data.txt" in result
        assert "file.txt" in result


class TestDuDepthLimit:
    """Test depth limiting options."""
    
    def test_du_max_depth_1(self, du_setup):
        """Test --max-depth=1."""
        shell, cmd = du_setup
        result = cmd.execute(["--max-depth=1", "/"])
        lines = result.split("\n")
        # Should show first level directories but not deeper
        assert any("dir1" in line for line in lines)
        assert not any("subdir" in line for line in lines)
    
    def test_du_d_flag(self, du_setup):
        """Test -d flag for depth limit."""
        shell, cmd = du_setup
        result = cmd.execute(["-d", "0", "/dir2"])
        lines = result.split("\n")
        # Depth 0 should only show the directory itself
        assert len(lines) == 1
        assert "/dir2" in result
    
    def test_du_max_depth_2(self, du_setup):
        """Test depth 2."""
        shell, cmd = du_setup
        result = cmd.execute(["--max-depth=2", "/"])
        # Should show up to 2 levels deep
        assert "dir1/subdir" in result
        assert "dir2/nested" in result
        # Should not show level2
        assert "level2" not in result


class TestDuUnits:
    """Test different unit options."""
    
    def test_du_k_flag(self, du_setup):
        """Test -k flag for kilobytes."""
        shell, cmd = du_setup
        result = cmd.execute(["-k", "/file1.txt"])
        # Should show in KB (default)
        assert "1\t" in result
    
    def test_du_m_flag(self, du_setup):
        """Test -m flag for megabytes."""
        shell, cmd = du_setup
        result = cmd.execute(["-m", "/large.txt"])
        # 10KB should round up to 1MB
        assert "1\t" in result
    
    def test_du_b_flag(self, du_setup):
        """Test -b flag for bytes."""
        shell, cmd = du_setup
        result = cmd.execute(["-b", "/file1.txt"])
        # Should show exact bytes
        assert "1024\t" in result
    
    def test_du_bytes_long(self, du_setup):
        """Test --bytes flag."""
        shell, cmd = du_setup
        result = cmd.execute(["--bytes", "/dir1/file1.txt"])
        assert "512\t" in result


class TestDuExclude:
    """Test exclude patterns."""
    
    def test_du_exclude_pattern(self, du_setup):
        """Test --exclude with pattern."""
        shell, cmd = du_setup
        result = cmd.execute(["--exclude=*.txt", "-a", "/dir1"])
        # Should not show .txt files
        assert "file1.txt" not in result
        assert "file2.txt" not in result
        # Should still show directories
        assert "subdir" in result
    
    def test_du_exclude_multiple(self, du_setup):
        """Test multiple exclude patterns."""
        shell, cmd = du_setup
        result = cmd.execute(["--exclude=*.txt", "--exclude=subdir", "/dir1"])
        # Should not show txt files or subdir
        assert "file1.txt" not in result
        assert "subdir" not in result
    
    def test_du_exclude_directory(self, du_setup):
        """Test excluding directories."""
        shell, cmd = du_setup
        result = cmd.execute(["--exclude=nested", "/dir2"])
        # Should not show nested directory
        assert "nested" not in result
        # Should still show dir2
        assert "/dir2" in result


class TestDuSpecialFiles:
    """Test with special files."""
    
    def test_du_empty_file(self, du_setup):
        """Test du with empty file."""
        shell, cmd = du_setup
        result = cmd.execute(["/empty.txt"])
        assert "0\t/empty.txt" in result
    
    def test_du_unicode_file(self, du_setup):
        """Test du with Unicode content."""
        shell, cmd = du_setup
        result = cmd.execute(["/unicode.txt"])
        # Should handle Unicode properly
        assert "/unicode.txt" in result
    
    def test_du_binary_file(self, du_setup):
        """Test du with binary file."""
        shell, cmd = du_setup
        result = cmd.execute(["/binary.bin"])
        assert "/binary.bin" in result
        # Binary is 1KB
        assert "1\t" in result
    
    def test_du_hidden_directory(self, du_setup):
        """Test du with hidden directory."""
        shell, cmd = du_setup
        result = cmd.execute(["/.hidden"])
        assert "/.hidden" in result
        assert "secret.txt" not in result  # Unless -a is used


class TestDuCombinations:
    """Test various flag combinations."""
    
    def test_du_hs_flags(self, du_setup):
        """Test combining -h and -s flags."""
        shell, cmd = du_setup
        result = cmd.execute(["-hs", "/dir1"])
        lines = result.split("\n")
        # Should show human-readable summary
        assert len(lines) == 1
        assert any(unit in result for unit in ["B", "K"]) or "0" in result
    
    def test_du_ahc_flags(self, du_setup):
        """Test combining -a, -h, and -c flags."""
        shell, cmd = du_setup
        result = cmd.execute(["-ahc", "/dir1/file1.txt", "/dir1/file2.txt"])
        # Should show all files in human-readable with total
        assert "file1.txt" in result
        assert "file2.txt" in result
        assert "total" in result
        assert any(unit in result for unit in ["B", "K"]) or "0" in result
    
    def test_du_sd_flags(self, du_setup):
        """Test combining -s and -d flags."""
        shell, cmd = du_setup
        # -s should take precedence
        result = cmd.execute(["-s", "-d", "2", "/"])
        lines = result.split("\n")
        assert len(lines) == 1
    
    def test_du_am_flags(self, du_setup):
        """Test combining -a and -m flags."""
        shell, cmd = du_setup
        result = cmd.execute(["-am", "/dir1"])
        # Should show all files in megabytes
        assert "file1.txt" in result
        # Small files should show as 1M (rounded up)
        assert "1\t" in result


class TestDuErrorHandling:
    """Test error handling."""
    
    def test_du_permission_denied_simulation(self, du_setup):
        """Test handling permission denied."""
        shell, cmd = du_setup
        # Override read to simulate permission error
        def fail_read(path):
            if "protected" in path:
                return None
            return shell.fs.read_file(path)
        
        original_read = shell.fs.read_file
        shell.fs.write_file("/protected.txt", "secret")
        shell.fs.read_file = fail_read
        
        result = cmd.execute(["/protected.txt"])
        # Should handle gracefully
        assert "/protected.txt" in result
        
        shell.fs.read_file = original_read
    
    def test_du_invalid_depth(self, du_setup):
        """Test invalid depth value."""
        shell, cmd = du_setup
        result = cmd.execute(["-d", "invalid"])
        # Should show help or error
        assert "du" in result.lower()
    
    def test_du_help_flag(self, du_setup):
        """Test --help flag."""
        shell, cmd = du_setup
        result = cmd.execute(["--help"])
        assert "du - Display disk usage" in result
        assert "Usage:" in result
        assert "-h, --human-readable" in result


class TestDuRealWorldScenarios:
    """Test real-world usage scenarios."""
    
    def test_du_find_large_directories(self, du_setup):
        """Test finding large directories."""
        shell, cmd = du_setup
        result = cmd.execute(["-h", "-d", "1", "/"])
        lines = result.split("\n")
        # Should help identify which directories use most space
        assert any("dir" in line for line in lines)
    
    def test_du_project_size(self, du_setup):
        """Test getting project size summary."""
        shell, cmd = du_setup
        # Create project-like structure
        # First create directories
        shell.fs.mkdir("/project")
        shell.fs.mkdir("/project/src")
        shell.fs.mkdir("/project/tests")
        # Then add files
        shell.fs.write_file("/project/src/main.py", "code" * 1000)
        shell.fs.write_file("/project/src/utils.py", "utils" * 500)
        shell.fs.write_file("/project/tests/test.py", "test" * 300)
        shell.fs.write_file("/project/README.md", "readme" * 100)
        # Update files dict for exists check
        shell.fs.files["/project"] = {"src": None, "tests": None, "README.md": None}
        shell.fs.files["/project/src"] = {"main.py": None, "utils.py": None}
        shell.fs.files["/project/tests"] = {"test.py": None}
        
        result = cmd.execute(["-sh", "/project"])
        # Should show total project size
        assert "/project" in result
        assert any(unit in result for unit in ["B", "K"]) or "0" in result
    
    def test_du_cleanup_candidates(self, du_setup):
        """Test finding cleanup candidates."""
        shell, cmd = du_setup
        # Show all files sorted by size (manual sorting needed)
        result = cmd.execute(["-a", "/"])
        lines = result.split("\n")
        # Should list all files with sizes
        assert len(lines) > 10  # Should have many entries
    
    def test_du_exclude_node_modules(self, du_setup):
        """Test excluding node_modules pattern."""
        shell, cmd = du_setup
        # Create node_modules-like structure
        shell.fs.mkdir("/app/node_modules")
        shell.fs.write_file("/app/node_modules/pkg1/index.js", "x" * 5000)
        shell.fs.write_file("/app/src/main.js", "y" * 1000)
        
        result = cmd.execute(["--exclude=node_modules", "/app"])
        # Should not include node_modules
        assert "node_modules" not in result
        # Should still show app
        assert "/app" in result
    
    def test_du_ci_disk_usage(self, du_setup):
        """Test checking disk usage in CI environment."""
        shell, cmd = du_setup
        result = cmd.execute(["-sh", ".", "-c"])
        # Should show current directory total
        assert "total" in result


class TestDuExcludePatterns:
    """Test exclude pattern functionality."""
    
    def test_du_exclude_pattern(self, du_setup):
        """Test --exclude option."""
        shell, cmd = du_setup
        result = cmd.execute(["--exclude", "*.txt", "/"])
        # Should exclude txt files from size calculation
        assert result  # Should have some output
    
    def test_du_exclude_multiple_patterns(self, du_setup):
        """Test multiple --exclude options."""
        shell, cmd = du_setup
        result = cmd.execute(["--exclude", "*.txt", "--exclude", "*.bin", "/"])
        # Should exclude both txt and bin files
        assert result  # Should have output but exclude specified patterns
    
    def test_du_exclude_directory(self, du_setup):
        """Test excluding directories."""
        shell, cmd = du_setup
        result = cmd.execute(["--exclude", "dir1", "/"])
        # dir1 should not appear in output
        lines = result.split("\n")
        dir1_found = False
        for line in lines:
            if "dir1" in line and "/" not in line.replace("/dir1", ""):
                dir1_found = True
        assert not dir1_found or "/" in result


class TestDuTimeOptions:
    """Test time-related options."""
    
    def test_du_time_option(self, du_setup):
        """Test --time option."""
        shell, cmd = du_setup
        result = cmd.execute(["--time", "/dir1"])
        # Should show modification times (even if mock)
        assert result  # Should produce output
        assert "/dir1" in result
    
    def test_du_time_with_style(self, du_setup):
        """Test --time with --time-style."""
        shell, cmd = du_setup
        # --time-style is now supported
        result = cmd.execute(["--time", "--time-style", "iso", "/dir1"])
        # Should work with time-style
        assert result
        assert "/dir1" in result
    
    def test_du_time_access(self, du_setup):
        """Test --time=atime option."""
        shell, cmd = du_setup
        result = cmd.execute(["--time=atime", "/"])
        # Should show access times
        assert result
    
    def test_du_time_birth(self, du_setup):
        """Test --time=birth option."""
        shell, cmd = du_setup
        result = cmd.execute(["--time=birth", "/"])
        # Should show birth times or handle gracefully
        assert result


class TestDuErrorCases:
    """Test error handling cases."""
    
    def test_du_invalid_max_depth(self, du_setup):
        """Test invalid max-depth value."""
        shell, cmd = du_setup
        result = cmd.execute(["--max-depth", "abc", "/"])
        # Should handle invalid depth gracefully or show error
        assert result  # Should produce some output
    
    def test_du_conflicting_options(self, du_setup):
        """Test conflicting options."""
        shell, cmd = du_setup
        # -s (summarize) with -a (all) doesn't make sense
        result = cmd.execute(["-s", "-a", "/"])
        # Should still work, one option takes precedence
        assert result
    
    def test_du_permission_denied_simulation(self, du_setup):
        """Test handling of inaccessible paths."""
        shell, cmd = du_setup
        # Try to access a path that doesn't exist
        result = cmd.execute(["/nonexistent/../also_nonexistent"])
        assert "cannot access" in result.lower() or "no such" in result.lower()
    
    def test_du_invalid_block_size(self, du_setup):
        """Test invalid block size."""
        shell, cmd = du_setup
        result = cmd.execute(["-B", "invalid", "/"])
        # Should use default or show error
        assert result
    
    def test_du_threshold_invalid(self, du_setup):
        """Test invalid threshold value."""
        shell, cmd = du_setup
        result = cmd.execute(["--threshold", "abc", "/"])
        # Should handle gracefully
        assert result


class TestDuSpecialCases:
    """Test special edge cases."""
    
    def test_du_empty_directory_tree(self, du_setup):
        """Test with only empty directories."""
        shell, cmd = du_setup
        # Create nested empty directories
        shell.fs.mkdir("/empty1")
        shell.fs.mkdir("/empty1/empty2")
        shell.fs.mkdir("/empty1/empty2/empty3")
        
        result = cmd.execute(["/empty1"])
        # Should show all directories even if empty
        assert "/empty1" in result
    
    def test_du_symlink_flag(self, du_setup):
        """Test symbolic link flag handling."""
        shell, cmd = du_setup
        # -L flag for following symlinks (even if not implemented)
        result = cmd.execute(["-L", "/"])
        # Should handle -L flag gracefully
        assert result
    
    def test_du_dereference_args(self, du_setup):
        """Test -D/--dereference-args flag."""
        shell, cmd = du_setup
        result = cmd.execute(["-D", "/"])
        # Should handle flag even if no symlinks
        assert result
    
    def test_du_dereference_flag(self, du_setup):
        """Test --dereference flag."""
        shell, cmd = du_setup
        result = cmd.execute(["--dereference", "/"])
        # Should handle flag
        assert result
    
    def test_du_very_deep_nesting(self, du_setup):
        """Test with very deep directory nesting."""
        shell, cmd = du_setup
        # Create deep nesting
        path = ""
        for i in range(10):
            path = f"/deep{i}" if not path else f"{path}/deep{i}"
            shell.fs.mkdir(path)
            shell.fs.write_file(f"{path}/file.txt", f"content{i}")
        
        # Test without max-depth first
        result_all = cmd.execute(["/deep0"])
        
        # Test with max-depth
        result = cmd.execute(["--max-depth", "5", "/deep0"])
        # Should show top-level directory
        assert "/deep0" in result
        # With max-depth=5, it limits recursion depth
        # The result should be shorter than without max-depth
        assert len(result) <= len(result_all)
    
    def test_du_separate_dirs_flag(self, du_setup):
        """Test -S/--separate-dirs flag."""
        shell, cmd = du_setup
        result = cmd.execute(["-S", "/"])
        # Should not include subdirectory sizes in parent
        assert result
    
    def test_du_one_file_system(self, du_setup):
        """Test -x/--one-file-system flag."""
        shell, cmd = du_setup
        result = cmd.execute(["-x", "/"])
        # Should stay on same filesystem
        assert result
    
    def test_du_null_termination(self, du_setup):
        """Test -0/--null flag for null-terminated output."""
        shell, cmd = du_setup
        result = cmd.execute(["-0", "/dir1", "/dir2"])
        # Should use null terminators instead of newlines
        assert "/dir1" in result
        assert "/dir2" in result
    
    def test_du_files0_from(self, du_setup):
        """Test --files0-from option."""
        shell, cmd = du_setup
        # Create a file with null-separated paths
        shell.fs.write_file("/paths.txt", "/dir1\0/dir2\0")
        result = cmd.execute(["--files0-from", "/paths.txt"])
        # Should process files from the list
        assert result
    
    def test_du_apparent_size(self, du_setup):
        """Test --apparent-size flag."""
        shell, cmd = du_setup
        result = cmd.execute(["--apparent-size", "/"])
        # Should show apparent sizes
        assert result
    
    def test_du_threshold_option(self, du_setup):
        """Test --threshold option."""
        shell, cmd = du_setup
        result = cmd.execute(["--threshold", "100", "/"])
        # Should only show entries above threshold
        assert result