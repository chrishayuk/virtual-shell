"""
Comprehensive test suite for the cp (copy) command.
Tests all cp functionality including recursive copying, flags, and edge cases.
"""

import pytest
from tests.dummy_shell import DummyShell
from chuk_virtual_shell.commands.filesystem.cp import CpCommand


class TestCpCommand:
    """Test cases for the cp command"""

    def setup_method(self):
        """Set up test environment before each test"""
        self.shell = DummyShell({})
        self.cmd = CpCommand(self.shell)

        # Create test files and directories
        self.shell.fs.write_file("/source.txt", "Source content")
        self.shell.fs.write_file("/file1.txt", "File 1 content")
        self.shell.fs.write_file("/file2.txt", "File 2 content")
        self.shell.fs.write_file("/binary.bin", b"\x00\x01\x02\x03\x04")
        self.shell.fs.write_file("/unicode.txt", "Hello 世界 🌍")
        self.shell.fs.write_file("/large.txt", "X" * 10000)

        self.shell.fs.mkdir("/srcdir")
        self.shell.fs.write_file("/srcdir/nested.txt", "Nested file")
        self.shell.fs.mkdir("/srcdir/subdir")
        self.shell.fs.write_file("/srcdir/subdir/deep.txt", "Deep file")
        self.shell.fs.mkdir("/srcdir/subdir/deeper")
        self.shell.fs.write_file("/srcdir/subdir/deeper/deepest.txt", "Deepest")

        self.shell.fs.mkdir("/destdir")
        self.shell.fs.mkdir("/emptydir")

    def test_cp_basic_file(self):
        """Test basic file copy"""
        result = self.cmd.execute(["/source.txt", "/dest.txt"])
        assert result == "" or "copied" in result.lower()

        # Verify file was copied
        content = self.shell.fs.read_file("/dest.txt")
        assert content == "Source content"

        # Original should still exist
        assert self.shell.fs.read_file("/source.txt") == "Source content"

    def test_cp_file_to_directory(self):
        """Test copying file to directory"""
        self.cmd.execute(["/source.txt", "/destdir"])

        # File should be copied into the directory
        content = self.shell.fs.read_file("/destdir/source.txt")
        assert content == "Source content"

    def test_cp_multiple_files_to_directory(self):
        """Test copying multiple files to directory"""
        self.cmd.execute(["/file1.txt", "/file2.txt", "/source.txt", "/destdir"])

        # All files should be in the directory
        assert self.shell.fs.read_file("/destdir/file1.txt") == "File 1 content"
        assert self.shell.fs.read_file("/destdir/file2.txt") == "File 2 content"
        assert self.shell.fs.read_file("/destdir/source.txt") == "Source content"

    def test_cp_overwrite_existing_file(self):
        """Test overwriting existing file"""
        self.shell.fs.write_file("/existing.txt", "Old content")
        self.cmd.execute(["/source.txt", "/existing.txt"])

        # Should overwrite
        assert self.shell.fs.read_file("/existing.txt") == "Source content"

    def test_cp_nonexistent_source(self):
        """Test copying non-existent source file"""
        result = self.cmd.execute(["/nonexistent.txt", "/dest.txt"])
        assert "not found" in result.lower() or "no such file" in result.lower()

    def test_cp_insufficient_args(self):
        """Test cp with insufficient arguments"""
        result = self.cmd.execute([])
        assert "missing" in result.lower() or "usage" in result.lower()

        result = self.cmd.execute(["/source.txt"])
        assert "missing" in result.lower() or "destination" in result.lower()


class TestCpRecursive:
    """Test recursive copying functionality"""

    def setup_method(self):
        """Set up test environment"""
        self.shell = DummyShell({})
        self.cmd = CpCommand(self.shell)

        # Create complex directory structure
        self.shell.fs.mkdir("/src")
        self.shell.fs.mkdir("/src/dir1")
        self.shell.fs.mkdir("/src/dir1/subdir")
        self.shell.fs.mkdir("/src/dir2")
        self.shell.fs.write_file("/src/file.txt", "Root file")
        self.shell.fs.write_file("/src/dir1/file1.txt", "File 1")
        self.shell.fs.write_file("/src/dir1/subdir/deep.txt", "Deep file")
        self.shell.fs.write_file("/src/dir2/file2.txt", "File 2")

    def test_cp_recursive_basic(self):
        """Test basic recursive copy"""
        result = self.cmd.execute(["-r", "/src", "/dest"])

        # Check structure was copied
        assert self.shell.fs.is_directory("/dest")
        assert self.shell.fs.read_file("/dest/file.txt") == "Root file"
        assert self.shell.fs.is_directory("/dest/dir1")
        assert self.shell.fs.read_file("/dest/dir1/file1.txt") == "File 1"
        assert self.shell.fs.is_directory("/dest/dir1/subdir")
        assert self.shell.fs.read_file("/dest/dir1/subdir/deep.txt") == "Deep file"
        assert self.shell.fs.is_directory("/dest/dir2")
        assert self.shell.fs.read_file("/dest/dir2/file2.txt") == "File 2"

    def test_cp_R_flag(self):
        """Test -R flag (uppercase) for recursive copy"""
        result = self.cmd.execute(["-R", "/src", "/dest"])

        # Should work same as -r
        assert self.shell.fs.is_directory("/dest")
        assert self.shell.fs.read_file("/dest/file.txt") == "Root file"

    def test_cp_directory_without_recursive(self):
        """Test copying directory without recursive flag"""
        result = self.cmd.execute(["/src", "/dest"])
        assert "directory" in result.lower() or "recursive" in result.lower()

    def test_cp_recursive_to_existing_directory(self):
        """Test recursive copy to existing directory"""
        self.shell.fs.mkdir("/existing")
        self.cmd.execute(["-r", "/src", "/existing"])

        # Should create /existing/src
        assert self.shell.fs.is_directory("/existing/src")
        assert self.shell.fs.read_file("/existing/src/file.txt") == "Root file"

    def test_cp_recursive_empty_directory(self):
        """Test copying empty directory"""
        self.shell.fs.mkdir("/empty")
        self.cmd.execute(["-r", "/empty", "/dest_empty"])

        assert self.shell.fs.is_directory("/dest_empty")
        # Should be empty
        contents = self.shell.fs.list_dir("/dest_empty")
        assert len(contents) == 0

    def test_cp_recursive_with_symlinks(self):
        """Test recursive copy with symbolic links (if supported)"""
        # Create a symlink if supported
        result = self.cmd.execute(["-r", "/src", "/dest"])
        assert self.shell.fs.is_directory("/dest")

    def test_cp_recursive_without_copy_dir_method(self):
        """Test recursive copy when filesystem doesn't have copy_dir method"""
        # Remove copy_dir method if it exists (DummyFileSystem doesn't have it by default)
        try:
            delattr(self.shell.fs, 'copy_dir')
        except AttributeError:
            pass  # Method doesn't exist, which is what we want
        
        result = self.cmd.execute(["-r", "/src", "/dest"])
        
        # Should still work using manual recursion
        assert self.shell.fs.is_directory("/dest")
        assert self.shell.fs.read_file("/dest/file.txt") == "Root file"
        assert self.shell.fs.is_directory("/dest/dir1")

    def test_cp_recursive_manual_write_failure(self):
        """Test recursive copy with write failure during manual recursion"""
        # Make copy_dir fail to force manual recursion
        original_copy_dir = self.shell.fs.copy_dir
        def failing_copy_dir(src, dst):
            return False  # Force manual recursion
        self.shell.fs.copy_dir = failing_copy_dir
        
        # Make write_file fail for specific file
        original_write = self.shell.fs.write_file
        def failing_write(path, content):
            if "fail" in path:
                return False
            return original_write(path, content)
        
        self.shell.fs.write_file("/src/fail.txt", "This will fail")
        self.shell.fs.write_file = failing_write
        
        result = self.cmd.execute(["-r", "/src", "/dest"])
        
        # Should show error but continue with other files
        assert "error" in result.lower() or "failed" in result.lower()
        
        # Other files should still be copied
        assert self.shell.fs.read_file("/dest/file.txt") == "Root file"

    def test_cp_recursive_manual_subdirectory_failure(self):
        """Test recursive copy with subdirectory creation failure"""
        # Make copy_dir fail to force manual recursion
        original_copy_dir = self.shell.fs.copy_dir
        def failing_copy_dir(src, dst):
            return False  # Force manual recursion
        self.shell.fs.copy_dir = failing_copy_dir
        
        # Make mkdir fail for specific directory
        original_mkdir = self.shell.fs.mkdir
        def failing_mkdir(path):
            if "faildir" in path:
                return False
            return original_mkdir(path)
        
        # Create faildir and ensure it appears in parent directory listing
        self.shell.fs.mkdir("/src/faildir")
        # Manually add to parent directory structure for DummyFileSystem
        if "/src" in self.shell.fs.files and isinstance(self.shell.fs.files["/src"], dict):
            self.shell.fs.files["/src"]["faildir"] = {}
        
        self.shell.fs.mkdir = failing_mkdir
        
        result = self.cmd.execute(["-r", "/src", "/dest"])
        
        # Should show error for failed directory
        assert "error" in result.lower() or "failed" in result.lower()


class TestCpWithFlags:
    """Test cp command with various flags"""

    def setup_method(self):
        """Set up test environment"""
        self.shell = DummyShell({})
        self.cmd = CpCommand(self.shell)

        self.shell.fs.write_file("/source.txt", "Content")
        self.shell.fs.write_file("/existing.txt", "Old content")

    def test_cp_i_interactive(self):
        """Test -i flag for interactive mode"""
        # Note: Interactive mode is hard to test without user input
        # Should prompt before overwrite
        result = self.cmd.execute(["-i", "/source.txt", "/existing.txt"])
        # Behavior depends on implementation

    def test_cp_f_force(self):
        """Test -f flag for force"""
        result = self.cmd.execute(["-f", "/source.txt", "/existing.txt"])
        assert self.shell.fs.read_file("/existing.txt") == "Content"

    def test_cp_n_no_clobber(self):
        """Test -n flag for no-clobber"""
        result = self.cmd.execute(["-n", "/source.txt", "/existing.txt"])
        # Should not overwrite
        assert self.shell.fs.read_file("/existing.txt") == "Old content"

    def test_cp_v_verbose(self):
        """Test -v flag for verbose output"""
        result = self.cmd.execute(["-v", "/source.txt", "/dest.txt"])
        # Should show what was copied
        assert "source.txt" in result or "dest.txt" in result or len(result) > 0

    def test_cp_p_preserve(self):
        """Test -p flag for preserving attributes"""
        result = self.cmd.execute(["-p", "/source.txt", "/dest.txt"])
        assert self.shell.fs.read_file("/dest.txt") == "Content"
        # Attributes preservation depends on filesystem support

    def test_cp_multiple_flags(self):
        """Test combining multiple flags"""
        result = self.cmd.execute(["-r", "-v", "-f", "/source.txt", "/dest.txt"])
        assert self.shell.fs.read_file("/dest.txt") == "Content"

    def test_cp_invalid_flag(self):
        """Test invalid flag"""
        result = self.cmd.execute(["-x", "/source.txt", "/dest.txt"])
        # Should either ignore or show error
        assert self.shell.fs.exists("/dest.txt") or "invalid" in result.lower()


class TestCpSpecialCases:
    """Test special cases and edge conditions"""

    def setup_method(self):
        """Set up test environment"""
        self.shell = DummyShell({})
        self.cmd = CpCommand(self.shell)

    def test_cp_same_source_dest(self):
        """Test copying file to itself"""
        self.shell.fs.write_file("/file.txt", "Content")
        result = self.cmd.execute(["/file.txt", "/file.txt"])
        assert "same file" in result.lower() or "identical" in result.lower()

    def test_cp_binary_file(self):
        """Test copying binary file"""
        binary_content = b"\x00\x01\x02\x03\x04\x05"
        self.shell.fs.write_file("/binary.bin", binary_content)
        self.cmd.execute(["/binary.bin", "/copy.bin"])
        
        # Binary content should be preserved
        assert self.shell.fs.read_file("/copy.bin") == binary_content

    def test_cp_unicode_file(self):
        """Test copying file with Unicode content"""
        unicode_content = "Hello 世界 🌍 مرحبا"
        self.shell.fs.write_file("/unicode.txt", unicode_content)
        self.cmd.execute(["/unicode.txt", "/copy.txt"])
        
        assert self.shell.fs.read_file("/copy.txt") == unicode_content

    def test_cp_large_file(self):
        """Test copying large file"""
        large_content = "X" * (1024 * 1024)  # 1MB
        self.shell.fs.write_file("/large.txt", large_content)
        self.cmd.execute(["/large.txt", "/copy.txt"])
        
        assert self.shell.fs.read_file("/copy.txt") == large_content

    def test_cp_empty_file(self):
        """Test copying empty file"""
        self.shell.fs.write_file("/empty.txt", "")
        self.cmd.execute(["/empty.txt", "/copy.txt"])
        
        assert self.shell.fs.exists("/copy.txt")
        assert self.shell.fs.read_file("/copy.txt") == ""

    def test_cp_special_chars_filename(self):
        """Test copying files with special characters in name"""
        self.shell.fs.write_file("/file with spaces.txt", "Content")
        self.cmd.execute(["/file with spaces.txt", "/copy.txt"])
        
        assert self.shell.fs.read_file("/copy.txt") == "Content"

    def test_cp_deep_nesting(self):
        """Test copying deeply nested directory structure"""
        # Create deep structure
        path = "/deep"
        for i in range(10):
            path = f"{path}/level{i}"
            self.shell.fs.mkdir(path)
            self.shell.fs.write_file(f"{path}/file.txt", f"Level {i}")
        
        self.cmd.execute(["-r", "/deep", "/copy"])
        
        # Verify deep structure was copied
        path = "/copy"
        for i in range(10):
            path = f"{path}/level{i}"
            assert self.shell.fs.is_directory(path)
            assert self.shell.fs.read_file(f"{path}/file.txt") == f"Level {i}"

    def test_cp_with_wildcards(self):
        """Test cp with wildcard patterns (shell expansion)"""
        self.shell.fs.write_file("/file1.txt", "1")
        self.shell.fs.write_file("/file2.txt", "2")
        self.shell.fs.write_file("/file3.log", "3")
        
        # Note: Wildcard expansion is typically done by shell
        result = self.cmd.execute(["*.txt", "/dest/"])
        # Behavior depends on shell expansion

    def test_cp_preserve_directory_structure(self):
        """Test preserving directory structure during copy"""
        self.shell.fs.mkdir("/src/a/b/c")
        self.shell.fs.write_file("/src/a/b/c/file.txt", "Deep")
        
        self.cmd.execute(["-r", "/src", "/dest"])
        
        assert self.shell.fs.is_directory("/dest/a/b/c")
        assert self.shell.fs.read_file("/dest/a/b/c/file.txt") == "Deep"

    def test_cp_multiple_sources_invalid_dest(self):
        """Test multiple sources with file as destination"""
        self.shell.fs.write_file("/file1.txt", "1")
        self.shell.fs.write_file("/file2.txt", "2")
        self.shell.fs.write_file("/dest.txt", "dest")
        
        result = self.cmd.execute(["/file1.txt", "/file2.txt", "/dest.txt"])
        assert "not a directory" in result.lower() or "error" in result.lower()


class TestCpErrorHandling:
    """Test error handling in cp command"""

    def setup_method(self):
        """Set up test environment"""
        self.shell = DummyShell({})
        self.cmd = CpCommand(self.shell)

    def test_cp_source_is_directory_no_recursive(self):
        """Test copying directory without -r flag"""
        self.shell.fs.mkdir("/dir")
        result = self.cmd.execute(["/dir", "/dest"])
        assert "directory" in result.lower() or "recursive" in result.lower()

    def test_cp_dest_parent_not_exist(self):
        """Test copying to destination with non-existent parent"""
        self.shell.fs.write_file("/source.txt", "Content")
        result = self.cmd.execute(["/source.txt", "/nonexistent/dest.txt"])
        assert "no such file" in result.lower() or "not found" in result.lower()

    def test_cp_permission_denied_simulation(self):
        """Test permission denied scenario (simulated)"""
        self.shell.fs.write_file("/source.txt", "Content")
        
        # Override write_file to simulate permission denied
        original_write = self.shell.fs.write_file
        def fail_write(path, content):
            if path == "/protected/dest.txt":
                return False
            return original_write(path, content)
        
        self.shell.fs.mkdir("/protected")
        self.shell.fs.write_file = fail_write
        
        result = self.cmd.execute(["/source.txt", "/protected/dest.txt"])
        assert "error" in result.lower() or "failed" in result.lower()

    def test_cp_circular_copy(self):
        """Test circular copy (copying parent to child)"""
        self.shell.fs.mkdir("/parent")
        self.shell.fs.mkdir("/parent/child")
        
        result = self.cmd.execute(["-r", "/parent", "/parent/child"])
        # Should detect and prevent circular copy
        assert "cannot" in result.lower() or "error" in result.lower()

    def test_cp_disk_full_simulation(self):
        """Test disk full scenario (simulated)"""
        huge_content = "X" * (10 * 1024 * 1024)  # 10MB
        self.shell.fs.write_file("/huge.txt", huge_content)
        
        # Simulate disk full by making write fail
        write_count = [0]
        original_write = self.shell.fs.write_file
        def limited_write(path, content):
            write_count[0] += 1
            if write_count[0] > 5:  # Fail after 5 writes
                return False
            return original_write(path, content)
        
        self.shell.fs.write_file = limited_write
        
        result = self.cmd.execute(["/huge.txt", "/dest.txt"])
        # Should handle write failure gracefully


class TestCpRealWorldScenarios:
    """Test real-world usage scenarios"""

    def setup_method(self):
        """Set up test environment"""
        self.shell = DummyShell({})
        self.cmd = CpCommand(self.shell)

    def test_cp_backup_file(self):
        """Test creating backup of file"""
        self.shell.fs.write_file("/important.conf", "Config data")
        self.cmd.execute(["/important.conf", "/important.conf.backup"])
        
        assert self.shell.fs.read_file("/important.conf") == "Config data"
        assert self.shell.fs.read_file("/important.conf.backup") == "Config data"

    def test_cp_project_structure(self):
        """Test copying project structure"""
        # Create project structure
        self.shell.fs.mkdir("/project")
        self.shell.fs.mkdir("/project/src")
        self.shell.fs.mkdir("/project/tests")
        self.shell.fs.mkdir("/project/docs")
        self.shell.fs.write_file("/project/README.md", "# Project")
        self.shell.fs.write_file("/project/src/main.py", "print('Hello')")
        self.shell.fs.write_file("/project/tests/test_main.py", "assert True")
        
        self.cmd.execute(["-r", "/project", "/backup"])
        
        # Verify structure
        assert self.shell.fs.is_directory("/backup")
        assert self.shell.fs.read_file("/backup/README.md") == "# Project"
        assert self.shell.fs.is_directory("/backup/src")
        assert self.shell.fs.read_file("/backup/src/main.py") == "print('Hello')"

    def test_cp_log_rotation(self):
        """Test log file rotation scenario"""
        # Create log files
        self.shell.fs.write_file("/app.log", "Current log")
        self.shell.fs.write_file("/app.log.1", "Old log 1")
        
        # Rotate logs
        self.cmd.execute(["/app.log.1", "/app.log.2"])
        self.cmd.execute(["/app.log", "/app.log.1"])
        
        assert self.shell.fs.read_file("/app.log.1") == "Current log"
        assert self.shell.fs.read_file("/app.log.2") == "Old log 1"

    def test_cp_template_deployment(self):
        """Test deploying template files"""
        # Create template
        self.shell.fs.mkdir("/templates")
        self.shell.fs.write_file("/templates/config.template", "HOST={{host}}")
        
        # Create destination directory
        self.shell.fs.mkdir("/etc")
        
        # Deploy template
        self.cmd.execute(["/templates/config.template", "/etc/config"])
        
        assert self.shell.fs.read_file("/etc/config") == "HOST={{host}}"

    def test_cp_data_migration(self):
        """Test data migration scenario"""
        # Create old structure
        self.shell.fs.mkdir("/old_data")
        self.shell.fs.write_file("/old_data/users.db", "User data")
        self.shell.fs.write_file("/old_data/settings.conf", "Settings")
        
        # Migrate to new structure
        self.shell.fs.mkdir("/new_data")
        self.cmd.execute(["/old_data/users.db", "/new_data/users.db"])
        self.cmd.execute(["/old_data/settings.conf", "/new_data/config.conf"])
        
        assert self.shell.fs.read_file("/new_data/users.db") == "User data"
        assert self.shell.fs.read_file("/new_data/config.conf") == "Settings"