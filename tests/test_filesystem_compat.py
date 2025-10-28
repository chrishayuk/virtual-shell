"""
Tests for FileSystemCompat wrapper
"""

from unittest.mock import Mock
from chuk_virtual_shell.filesystem_compat import FileSystemCompat


class TestFileSystemCompat:
    """Test cases for FileSystemCompat wrapper"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_fs = Mock()
        self.compat = FileSystemCompat(self.mock_fs)

    def test_init(self):
        """Test initialization"""
        assert self.compat.fs == self.mock_fs
        assert self.compat._cwd is None
        assert self.compat.provider == self.mock_fs

    def test_read_file_string(self):
        """Test reading file that returns string"""
        self.mock_fs.read_file.return_value = "test content"
        result = self.compat.read_file("/test.txt")
        assert result == "test content"
        self.mock_fs.read_file.assert_called_once_with("/test.txt")

    def test_read_file_bytes_utf8(self):
        """Test reading file that returns bytes (UTF-8)"""
        self.mock_fs.read_file.return_value = b"test content"
        result = self.compat.read_file("/test.txt")
        assert result == "test content"

    def test_read_file_bytes_binary(self):
        """Test reading file that returns binary data (non-UTF-8)"""
        binary_data = b"\x89\x50\x4e\x47"  # PNG header
        self.mock_fs.read_file.return_value = binary_data
        result = self.compat.read_file("/test.png")
        # Should return bytes as-is when decode fails
        assert result == binary_data

    def test_read_file_none(self):
        """Test reading file that doesn't exist"""
        self.mock_fs.read_file.return_value = None
        result = self.compat.read_file("/nonexistent.txt")
        assert result is None

    def test_write_file(self):
        """Test writing file"""
        self.mock_fs.write_file.return_value = True
        result = self.compat.write_file("/test.txt", "content")
        assert result is True
        self.mock_fs.write_file.assert_called_once_with("/test.txt", "content")

    def test_mkdir(self):
        """Test creating directory"""
        self.mock_fs.mkdir.return_value = True
        result = self.compat.mkdir("/testdir")
        assert result is True
        self.mock_fs.mkdir.assert_called_once_with("/testdir")

    def test_rm(self):
        """Test removing file"""
        self.mock_fs.rm.return_value = True
        result = self.compat.rm("/test.txt")
        assert result is True
        self.mock_fs.rm.assert_called_once_with("/test.txt")

    def test_rmdir(self):
        """Test removing directory"""
        self.mock_fs.rmdir.return_value = True
        result = self.compat.rmdir("/testdir")
        assert result is True
        self.mock_fs.rmdir.assert_called_once_with("/testdir")

    def test_touch(self):
        """Test touching file"""
        self.mock_fs.touch.return_value = True
        result = self.compat.touch("/test.txt")
        assert result is True
        self.mock_fs.touch.assert_called_once_with("/test.txt")

    def test_cp(self):
        """Test copying file"""
        self.mock_fs.cp.return_value = True
        result = self.compat.cp("/src.txt", "/dest.txt")
        assert result is True
        self.mock_fs.cp.assert_called_once_with("/src.txt", "/dest.txt")

    def test_mv(self):
        """Test moving file"""
        self.mock_fs.mv.return_value = True
        result = self.compat.mv("/src.txt", "/dest.txt")
        assert result is True
        self.mock_fs.mv.assert_called_once_with("/src.txt", "/dest.txt")

    def test_cd(self):
        """Test changing directory"""
        self.mock_fs.cd.return_value = True
        self.mock_fs.pwd.return_value = "/testdir"
        result = self.compat.cd("/testdir")
        assert result is True
        assert self.compat._cwd == "/testdir"
        self.mock_fs.cd.assert_called_once_with("/testdir")

    def test_pwd(self):
        """Test getting current directory"""
        self.mock_fs.pwd.return_value = "/current"
        result = self.compat.pwd()
        assert result == "/current"

    def test_cwd_property_cached(self):
        """Test cwd property returns cached value"""
        self.compat._cwd = "/cached"
        result = self.compat.cwd
        assert result == "/cached"
        self.mock_fs.pwd.assert_not_called()

    def test_cwd_property_not_cached(self):
        """Test cwd property when not cached"""
        self.mock_fs.pwd.return_value = "/current"
        result = self.compat.cwd
        assert result == "/current"
        assert self.compat._cwd == "/current"
        self.mock_fs.pwd.assert_called_once()

    def test_ls(self):
        """Test listing directory"""
        self.mock_fs.ls.return_value = ["file1.txt", "file2.txt"]
        result = self.compat.ls("/dir")
        assert result == ["file1.txt", "file2.txt"]
        self.mock_fs.ls.assert_called_once_with("/dir")

    def test_list_dir(self):
        """Test list_dir with results"""
        self.mock_fs.ls.return_value = ["file1.txt"]
        result = self.compat.list_dir("/dir")
        assert result == ["file1.txt"]

    def test_list_dir_none(self):
        """Test list_dir returns empty list when None"""
        self.mock_fs.ls.return_value = None
        result = self.compat.list_dir("/dir")
        assert result == []

    def test_list_directory(self):
        """Test list_directory alias"""
        self.mock_fs.ls.return_value = ["file1.txt"]
        result = self.compat.list_directory("/dir")
        assert result == ["file1.txt"]

    def test_resolve_path(self):
        """Test resolving path"""
        self.mock_fs.resolve_path.return_value = "/resolved/path"
        result = self.compat.resolve_path("../path")
        assert result == "/resolved/path"

    def test_exists_true(self):
        """Test exists returns true"""
        mock_info = Mock()
        self.mock_fs.get_node_info.return_value = mock_info
        result = self.compat.exists("/file.txt")
        assert result is True

    def test_exists_false(self):
        """Test exists returns false when exception"""
        self.mock_fs.get_node_info.side_effect = Exception("Not found")
        result = self.compat.exists("/file.txt")
        assert result is False

    def test_is_file_true(self):
        """Test is_file returns true"""
        mock_info = Mock()
        mock_info.is_dir = False
        self.mock_fs.get_node_info.return_value = mock_info
        result = self.compat.is_file("/file.txt")
        assert result is True

    def test_is_file_false_directory(self):
        """Test is_file returns false for directory"""
        mock_info = Mock()
        mock_info.is_dir = True
        self.mock_fs.get_node_info.return_value = mock_info
        result = self.compat.is_file("/dir")
        assert result is False

    def test_is_file_exception(self):
        """Test is_file returns false on exception"""
        self.mock_fs.get_node_info.side_effect = Exception("Error")
        result = self.compat.is_file("/file.txt")
        assert result is False

    def test_is_dir_true(self):
        """Test is_dir returns true"""
        mock_info = Mock()
        mock_info.is_dir = True
        self.mock_fs.get_node_info.return_value = mock_info
        result = self.compat.is_dir("/dir")
        assert result is True

    def test_is_dir_false_file(self):
        """Test is_dir returns false for file"""
        mock_info = Mock()
        mock_info.is_dir = False
        self.mock_fs.get_node_info.return_value = mock_info
        result = self.compat.is_dir("/file.txt")
        assert result is False

    def test_is_dir_exception(self):
        """Test is_dir returns false on exception"""
        self.mock_fs.get_node_info.side_effect = Exception("Error")
        result = self.compat.is_dir("/file.txt")
        assert result is False

    def test_get_node_info(self):
        """Test getting node info"""
        mock_info = Mock()
        self.mock_fs.get_node_info.return_value = mock_info
        result = self.compat.get_node_info("/file.txt")
        assert result == mock_info

    def test_find_with_method(self):
        """Test find when method exists"""
        self.mock_fs.find = Mock(return_value=["file1.txt", "file2.txt"])
        result = self.compat.find("*.txt", "/dir")
        assert result == ["file1.txt", "file2.txt"]
        self.mock_fs.find.assert_called_once_with("*.txt", "/dir")

    def test_find_without_method(self):
        """Test find when method doesn't exist"""
        # Create a new compat with a mock that doesn't have find
        mock_fs_no_find = Mock(spec=["read_file", "write_file"])
        compat_no_find = FileSystemCompat(mock_fs_no_find)
        result = compat_no_find.find("*.txt", "/dir")
        assert result == []

    def test_search_with_method(self):
        """Test search when method exists"""
        self.mock_fs.search = Mock(return_value=[("file.txt", 1, "match")])
        result = self.compat.search("pattern", "/dir")
        assert result == [("file.txt", 1, "match")]
        self.mock_fs.search.assert_called_once_with("pattern", "/dir")

    def test_search_without_method(self):
        """Test search when method doesn't exist"""
        # Create a new compat with a mock that doesn't have search
        mock_fs_no_search = Mock(spec=["read_file", "write_file"])
        compat_no_search = FileSystemCompat(mock_fs_no_search)
        result = compat_no_search.search("pattern", "/dir")
        assert result == []

    def test_get_fs_info_with_method(self):
        """Test get_fs_info when method exists"""
        self.mock_fs.get_fs_info = Mock(return_value={"type": "memory"})
        result = self.compat.get_fs_info()
        assert result == {"type": "memory"}

    def test_get_fs_info_without_method(self):
        """Test get_fs_info when method doesn't exist"""
        mock_fs_no_info = Mock(spec=["read_file", "write_file"])
        compat_no_info = FileSystemCompat(mock_fs_no_info)
        result = compat_no_info.get_fs_info()
        assert result == {}

    def test_get_storage_stats_with_method(self):
        """Test get_storage_stats when method exists"""
        self.mock_fs.get_storage_stats = Mock(return_value={"used": 100, "total": 1000})
        result = self.compat.get_storage_stats()
        assert result == {"used": 100, "total": 1000}

    def test_get_storage_stats_without_method(self):
        """Test get_storage_stats when method doesn't exist"""
        mock_fs_no_stats = Mock(spec=["read_file", "write_file"])
        compat_no_stats = FileSystemCompat(mock_fs_no_stats)
        result = compat_no_stats.get_storage_stats()
        assert result == {}

    def test_get_provider_name_with_method(self):
        """Test get_provider_name when method exists"""
        self.mock_fs.get_provider_name = Mock(return_value="memory")
        result = self.compat.get_provider_name()
        assert result == "memory"

    def test_get_provider_name_without_method(self):
        """Test get_provider_name when method doesn't exist"""
        mock_fs_no_name = Mock(spec=["read_file", "write_file"])
        compat_no_name = FileSystemCompat(mock_fs_no_name)
        result = compat_no_name.get_provider_name()
        assert result == "unknown"

    def test_change_provider_with_method(self):
        """Test change_provider when method exists"""
        self.mock_fs.change_provider = Mock(return_value=True)
        result = self.compat.change_provider("sqlite", db_path="/tmp/test.db")
        assert result is True
        self.mock_fs.change_provider.assert_called_once_with(
            "sqlite", db_path="/tmp/test.db"
        )

    def test_change_provider_without_method(self):
        """Test change_provider when method doesn't exist"""
        mock_fs_no_change = Mock(spec=["read_file", "write_file"])
        compat_no_change = FileSystemCompat(mock_fs_no_change)
        result = compat_no_change.change_provider("sqlite")
        assert result is False

    def test_is_read_only_with_method(self):
        """Test is_read_only when method exists"""
        self.mock_fs.is_read_only = Mock(return_value=True)
        result = self.compat.is_read_only()
        assert result is True

    def test_is_read_only_without_method(self):
        """Test is_read_only when method doesn't exist"""
        mock_fs_no_ro = Mock(spec=["read_file", "write_file"])
        compat_no_ro = FileSystemCompat(mock_fs_no_ro)
        result = compat_no_ro.is_read_only()
        assert result is False

    def test_set_read_only_with_method(self):
        """Test set_read_only when method exists"""
        self.mock_fs.set_read_only = Mock(return_value=True)
        result = self.compat.set_read_only(True)
        assert result is True
        self.mock_fs.set_read_only.assert_called_once_with(True)

    def test_set_read_only_without_method(self):
        """Test set_read_only when method doesn't exist"""
        mock_fs_no_set_ro = Mock(spec=["read_file", "write_file"])
        compat_no_set_ro = FileSystemCompat(mock_fs_no_set_ro)
        result = compat_no_set_ro.set_read_only(True)
        assert result is False
