"""
Compatibility wrapper for VirtualFileSystem to provide consistent API
"""


class FileSystemCompat:
    """Wrapper to provide compatible filesystem API across different implementations"""

    def __init__(self, fs):
        self.fs = fs
        self._cwd = None
        # Provide provider attribute for compatibility
        self.provider = fs

    # Basic file operations
    def read_file(self, path):
        return self.fs.read_file(path)

    def write_file(self, path, content):
        return self.fs.write_file(path, content)

    def mkdir(self, path):
        return self.fs.mkdir(path)

    def rm(self, path):
        return self.fs.rm(path)

    def rmdir(self, path):
        return self.fs.rmdir(path)

    def touch(self, path):
        return self.fs.touch(path)

    def cp(self, source, dest):
        return self.fs.cp(source, dest)

    def mv(self, source, dest):
        return self.fs.mv(source, dest)

    # Directory operations
    def cd(self, path):
        result = self.fs.cd(path)
        if result:
            self._cwd = self.fs.pwd()
        return result

    def pwd(self):
        return self.fs.pwd()

    @property
    def cwd(self):
        """Current working directory property"""
        if self._cwd is None:
            self._cwd = self.fs.pwd()
        return self._cwd

    def ls(self, path=None):
        return self.fs.ls(path)

    def list_dir(self, path):
        """List directory contents"""
        result = self.fs.ls(path)
        return result if result is not None else []

    def list_directory(self, path):
        """List directory contents (alias for list_dir)"""
        return self.list_dir(path)

    # Path operations
    def resolve_path(self, path):
        return self.fs.resolve_path(path)

    # Existence and type checking
    def exists(self, path):
        """Check if path exists"""
        try:
            info = self.fs.get_node_info(path)
            return info is not None
        except Exception:
            return False

    def is_file(self, path):
        """Check if path is a file"""
        try:
            info = self.fs.get_node_info(path)
            return info is not None and not info.is_dir
        except Exception:
            return False

    def is_dir(self, path):
        """Check if path is a directory"""
        try:
            info = self.fs.get_node_info(path)
            return info is not None and info.is_dir
        except Exception:
            return False

    def get_node_info(self, path):
        """Get node information for a path"""
        return self.fs.get_node_info(path)

    # Search operations
    def find(self, pattern, path=None):
        """Find files matching pattern"""
        if hasattr(self.fs, "find"):
            return self.fs.find(pattern, path)
        return []

    def search(self, pattern, path=None):
        """Search for pattern in files"""
        if hasattr(self.fs, "search"):
            return self.fs.search(pattern, path)
        return []

    # Info methods

    def get_fs_info(self):
        """Get filesystem info"""
        if hasattr(self.fs, "get_fs_info"):
            return self.fs.get_fs_info()
        return {}

    def get_storage_stats(self):
        """Get storage statistics"""
        if hasattr(self.fs, "get_storage_stats"):
            return self.fs.get_storage_stats()
        return {}

    # Provider operations
    def get_provider_name(self):
        """Get provider name"""
        if hasattr(self.fs, "get_provider_name"):
            return self.fs.get_provider_name()
        return "unknown"

    def change_provider(self, provider, **kwargs):
        """Change filesystem provider"""
        if hasattr(self.fs, "change_provider"):
            return self.fs.change_provider(provider, **kwargs)
        return False

    # Security operations
    def is_read_only(self):
        """Check if filesystem is read-only"""
        if hasattr(self.fs, "is_read_only"):
            return self.fs.is_read_only()
        return False

    def set_read_only(self, value):
        """Set read-only mode"""
        if hasattr(self.fs, "set_read_only"):
            return self.fs.set_read_only(value)
        return False
