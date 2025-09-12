"""
Test ls command with FileSystemCompat.provider fix
"""

from unittest.mock import Mock
from chuk_virtual_shell.filesystem_compat import FileSystemCompat


class TestFileSystemCompatProviderFix:
    """Test FileSystemCompat provider attribute fix"""

    def test_filesystem_compat_has_provider_attribute(self):
        """Test that FileSystemCompat has provider attribute pointing to wrapped fs"""
        mock_fs = Mock()
        fs_compat = FileSystemCompat(mock_fs)

        # Should have provider attribute
        assert hasattr(fs_compat, "provider")
        # Provider should point to the wrapped filesystem
        assert fs_compat.provider is mock_fs

    def test_filesystem_compat_delegates_get_node_info(self):
        """Test that FileSystemCompat properly delegates get_node_info"""
        mock_fs = Mock()
        mock_info = Mock()
        mock_fs.get_node_info.return_value = mock_info

        fs_compat = FileSystemCompat(mock_fs)

        result = fs_compat.get_node_info("/test/path")

        # Should delegate to wrapped filesystem
        mock_fs.get_node_info.assert_called_once_with("/test/path")
        assert result is mock_info

    def test_filesystem_compat_provider_used_for_node_info(self):
        """Test that code can access node info via fs.provider.get_node_info"""
        mock_fs = Mock()
        mock_info = Mock()
        mock_info.is_dir = False
        mock_info.name = "test.txt"
        mock_info.size = 100
        mock_fs.get_node_info.return_value = mock_info

        fs_compat = FileSystemCompat(mock_fs)

        # This is the pattern that was failing in ls -l command
        # It was trying to access self.fs.provider.get_node_info
        provider = fs_compat.provider
        info = provider.get_node_info("/test/file.txt")

        assert info is mock_info
        assert info.name == "test.txt"
        assert info.size == 100

    def test_ls_command_pattern_with_filesystem_compat(self):
        """Test the specific pattern used by ls command works with FileSystemCompat"""
        mock_fs = Mock()

        # Setup filesystem mock
        mock_fs.pwd.return_value = "/tmp"
        mock_fs.ls.return_value = ["file1.txt", "file2.txt"]
        mock_fs.resolve_path.side_effect = lambda x: x

        # Setup node info mock
        def get_node_info(path):
            if "file1" in path:
                return Mock(
                    is_dir=False,
                    name="file1.txt",
                    size=100,
                    permissions="rw-r--r--",
                    modified="2024-01-01",
                )
            elif "file2" in path:
                return Mock(
                    is_dir=False,
                    name="file2.txt",
                    size=200,
                    permissions="rw-r--r--",
                    modified="2024-01-02",
                )
            else:
                return Mock(
                    is_dir=True,
                    name="tmp",
                    size=4096,
                    permissions="rwxr-xr-x",
                    modified="2024-01-01",
                )

        mock_fs.get_node_info.side_effect = get_node_info

        # Create FileSystemCompat wrapper
        fs_compat = FileSystemCompat(mock_fs)

        # Simulate ls command access pattern
        files = fs_compat.ls("/tmp")
        assert files == ["file1.txt", "file2.txt"]

        # Access via provider (this was the failing pattern)
        for file in files:
            info = fs_compat.provider.get_node_info(f"/tmp/{file}")
            assert info is not None
            assert hasattr(info, "name")
            assert hasattr(info, "size")

    def test_filesystem_compat_all_delegated_methods(self):
        """Test that all FileSystemCompat methods properly delegate"""
        mock_fs = Mock()
        fs_compat = FileSystemCompat(mock_fs)

        # Test read_file delegation
        mock_fs.read_file.return_value = "content"
        assert fs_compat.read_file("/test") == "content"
        mock_fs.read_file.assert_called_with("/test")

        # Test write_file delegation
        fs_compat.write_file("/test", "data")
        mock_fs.write_file.assert_called_with("/test", "data")

        # Test mkdir delegation
        fs_compat.mkdir("/newdir")
        mock_fs.mkdir.assert_called_with("/newdir")

        # Test ls delegation
        mock_fs.ls.return_value = ["file1", "file2"]
        result = fs_compat.ls("/dir")
        assert result == ["file1", "file2"]
        mock_fs.ls.assert_called_with("/dir")

        # Test pwd delegation
        mock_fs.pwd.return_value = "/current"
        assert fs_compat.pwd() == "/current"

        # Test resolve_path delegation
        mock_fs.resolve_path.return_value = "/resolved"
        assert fs_compat.resolve_path("relative") == "/resolved"
        mock_fs.resolve_path.assert_called_with("relative")

    def test_filesystem_compat_exists_methods(self):
        """Test FileSystemCompat existence checking methods"""
        mock_fs = Mock()
        fs_compat = FileSystemCompat(mock_fs)

        # Test exists method
        mock_fs.get_node_info.return_value = Mock()
        assert fs_compat.exists("/test")

        mock_fs.get_node_info.side_effect = Exception("Not found")
        assert not fs_compat.exists("/notfound")

        # Test is_file method
        mock_fs.get_node_info.side_effect = None
        mock_fs.get_node_info.return_value = Mock(is_dir=False)
        assert fs_compat.is_file("/file")

        mock_fs.get_node_info.return_value = Mock(is_dir=True)
        assert not fs_compat.is_file("/dir")

        # Test is_dir method
        mock_fs.get_node_info.return_value = Mock(is_dir=True)
        assert fs_compat.is_dir("/dir")

        mock_fs.get_node_info.return_value = Mock(is_dir=False)
        assert not fs_compat.is_dir("/file")
