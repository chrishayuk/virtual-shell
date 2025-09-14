"""
Edge case tests for mv command to reach 80% coverage
"""

from tests.dummy_shell import DummyShell
from chuk_virtual_shell.commands.filesystem.mv import MvCommand
from unittest.mock import MagicMock


class TestMvEdgeCases:
    """Edge case tests for mv command"""

    def setup_method(self):
        """Set up test environment"""
        self.shell = DummyShell({})
        self.cmd = MvCommand(self.shell)

    def test_is_directory_with_isdir_method(self):
        """Test _is_directory using isdir method"""
        # Create mock fs with only isdir method
        mock_fs = MagicMock()
        del mock_fs.get_node_info
        del mock_fs.is_dir
        mock_fs.isdir.return_value = True

        original_fs = self.shell.fs
        self.shell.fs = mock_fs

        assert self.cmd._is_directory("/test")
        mock_fs.isdir.assert_called_with("/test")

        self.shell.fs = original_fs

    def test_is_directory_with_ls_method(self):
        """Test _is_directory using ls method as fallback"""
        # Create mock fs with only ls method
        mock_fs = MagicMock()
        del mock_fs.get_node_info
        del mock_fs.is_dir
        del mock_fs.isdir
        mock_fs.ls.return_value = ["file1", "file2"]

        original_fs = self.shell.fs
        self.shell.fs = mock_fs

        assert self.cmd._is_directory("/test")
        mock_fs.ls.assert_called_with("/test")

        # Test when ls raises exception (not a dir)
        mock_fs.ls.side_effect = Exception("Not a directory")
        assert not self.cmd._is_directory("/notdir")

        self.shell.fs = original_fs

    def test_file_exists_with_shell_exists(self):
        """Test _file_exists using shell.exists method"""
        # Create mock with shell.exists
        mock_shell = MagicMock()
        mock_shell.exists.return_value = True
        mock_fs = MagicMock()
        del mock_fs.get_node_info
        del mock_fs.exists
        mock_shell.fs = mock_fs

        cmd = MvCommand(mock_shell)
        assert cmd._file_exists("/test")
        mock_shell.exists.assert_called_with("/test")

    def test_file_exists_with_read_file_fallback(self):
        """Test _file_exists using read_file as last resort"""
        # Create mock fs with only read_file
        mock_fs = MagicMock()
        del mock_fs.get_node_info
        del mock_fs.exists
        mock_fs.read_file.return_value = "content"

        mock_shell = MagicMock()
        del mock_shell.exists
        mock_shell.fs = mock_fs

        cmd = MvCommand(mock_shell)
        assert cmd._file_exists("/test")
        mock_fs.read_file.assert_called_with("/test")

        # Test when read_file returns None (doesn't exist)
        mock_fs.read_file.return_value = None
        assert not cmd._file_exists("/notexist")

    def test_remove_file_with_delete_node(self):
        """Test _remove_file using delete_node method"""
        # Create mock fs with only delete_node
        mock_fs = MagicMock()
        del mock_fs.rm
        del mock_fs.delete_file
        mock_fs.delete_node.return_value = True

        original_fs = self.shell.fs
        self.shell.fs = mock_fs

        assert self.cmd._remove_file("/test")
        mock_fs.delete_node.assert_called_with("/test")

        self.shell.fs = original_fs
