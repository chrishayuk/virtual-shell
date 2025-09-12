"""
Extended tests for the mv command to improve coverage
"""

from tests.dummy_shell import DummyShell
from chuk_virtual_shell.commands.filesystem.mv import MvCommand


class TestMvExtended:
    """Extended test cases for the mv command"""

    def setup_method(self):
        """Set up test environment before each test"""
        self.shell = DummyShell({})
        self.cmd = MvCommand(self.shell)

        # Create test files and directories
        self.shell.fs.write_file("/file1.txt", "Content 1")
        self.shell.fs.write_file("/file2.txt", "Content 2")
        self.shell.fs.mkdir("/destdir")
        self.shell.fs.write_file("/destdir/existing.txt", "Existing")

    def test_mv_no_arguments(self):
        """Test mv without arguments"""
        result = self.cmd.execute([])
        assert "missing operand" in result

    def test_mv_one_argument(self):
        """Test mv with only one argument"""
        result = self.cmd.execute(["/file1.txt"])
        assert "missing operand" in result

    def test_mv_multiple_files_to_non_directory(self):
        """Test moving multiple files to non-directory"""
        result = self.cmd.execute(["/file1.txt", "/file2.txt", "/notadir.txt"])
        assert "not a directory" in result

    def test_mv_nonexistent_source(self):
        """Test moving non-existent file"""
        result = self.cmd.execute(["/nonexistent.txt", "/dest.txt"])
        assert "No such file or directory" in result

    def test_mv_file_read_error(self):
        """Test when source file cannot be read"""
        # Create a directory (can't read as file)
        self.shell.fs.mkdir("/srcdir")
        result = self.cmd.execute(["/srcdir", "/dest"])
        assert "Permission denied" in result or "cannot read" in result

    def test_mv_write_failure(self):
        """Test when destination cannot be written"""
        # Mock write_file to fail
        original_write = self.shell.fs.write_file
        self.shell.fs.write_file = lambda p, c: (
            False if p == "/dest.txt" else original_write(p, c)
        )

        result = self.cmd.execute(["/file1.txt", "/dest.txt"])
        assert "failed to write" in result

    def test_mv_remove_failure(self):
        """Test when source cannot be removed after copy"""
        # Mock rm to fail
        self.shell.fs.rm = lambda p: False

        result = self.cmd.execute(["/file1.txt", "/newfile.txt"])
        assert "failed to remove original" in result

    def test_mv_successful_rename(self):
        """Test successful file rename"""
        result = self.cmd.execute(["/file1.txt", "/renamed.txt"])
        assert result == ""
        assert self.shell.fs.read_file("/renamed.txt") == "Content 1"
        assert not self.shell.fs.exists("/file1.txt")

    def test_mv_to_directory(self):
        """Test moving file to directory"""
        result = self.cmd.execute(["/file1.txt", "/destdir"])
        assert result == ""
        assert self.shell.fs.read_file("/destdir/file1.txt") == "Content 1"
        assert not self.shell.fs.exists("/file1.txt")

    def test_mv_multiple_to_directory(self):
        """Test moving multiple files to directory"""
        result = self.cmd.execute(["/file1.txt", "/file2.txt", "/destdir"])
        assert result == ""
        assert self.shell.fs.read_file("/destdir/file1.txt") == "Content 1"
        assert self.shell.fs.read_file("/destdir/file2.txt") == "Content 2"

    def test_is_directory_variations(self):
        """Test _is_directory with different filesystem APIs"""
        # Test with existing is_dir method (default)
        assert self.cmd._is_directory("/destdir")
        assert not self.cmd._is_directory("/file1.txt")
        assert not self.cmd._is_directory("/nonexistent")

    def test_is_directory_with_exception(self):
        """Test _is_directory exception handling"""
        # Mock get_node_info to raise exception
        original_get_node_info = self.shell.fs.get_node_info
        self.shell.fs.get_node_info = lambda p: (_ for _ in ()).throw(
            Exception("Test error")
        )

        result = self.cmd._is_directory("/any")
        assert result is False

        # Restore
        self.shell.fs.get_node_info = original_get_node_info

    def test_file_exists_variations(self):
        """Test _file_exists with different filesystem APIs"""
        # Test with default methods
        assert self.cmd._file_exists("/file1.txt")
        assert not self.cmd._file_exists("/nonexistent")

    def test_file_exists_with_exception(self):
        """Test _file_exists exception handling"""
        # Mock to raise exception
        original_get_node_info = self.shell.fs.get_node_info
        self.shell.fs.get_node_info = lambda p: (_ for _ in ()).throw(
            Exception("Test error")
        )

        result = self.cmd._file_exists("/any")
        assert result is False

        # Restore
        self.shell.fs.get_node_info = original_get_node_info

    def test_remove_file_variations(self):
        """Test _remove_file with different filesystem APIs"""
        # Test with rm (default)
        self.shell.fs.write_file("/temp.txt", "temp")
        assert self.cmd._remove_file("/temp.txt")
        assert not self.shell.fs.exists("/temp.txt")

    def test_remove_file_with_delete_file(self):
        """Test _remove_file using delete_file method"""
        # Create a filesystem that only has delete_file
        from unittest.mock import MagicMock

        mock_fs = MagicMock()
        mock_fs.delete_file.return_value = True
        # Ensure rm is not there
        del mock_fs.rm

        original_fs = self.shell.fs
        self.shell.fs = mock_fs

        assert self.cmd._remove_file("/temp2.txt")
        mock_fs.delete_file.assert_called_with("/temp2.txt")

        # Restore
        self.shell.fs = original_fs

    def test_remove_file_no_methods(self):
        """Test _remove_file when no removal methods available"""

        # Create mock filesystem with no removal methods
        class MinimalFS:
            pass

        original_fs = self.shell.fs
        self.shell.fs = MinimalFS()

        result = self.cmd._remove_file("/any")
        assert result is False

        # Restore
        self.shell.fs = original_fs

    def test_remove_file_with_exception(self):
        """Test _remove_file exception handling"""
        # Mock rm to raise exception
        original_rm = self.shell.fs.rm
        self.shell.fs.rm = lambda p: (_ for _ in ()).throw(Exception("Test error"))

        result = self.cmd._remove_file("/any")
        assert result is False

        # Restore
        self.shell.fs.rm = original_rm
