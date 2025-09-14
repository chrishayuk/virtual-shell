"""
Compatibility wrapper for VirtualFileSystem to provide consistent API
"""

import asyncio
import inspect
import threading


class FileSystemCompat:
    """Wrapper to provide compatible filesystem API across different implementations"""

    _executor = None  # Shared thread pool executor
    _loop = None  # Shared event loop
    _loop_thread = None  # Thread running the event loop

    @classmethod
    def _get_or_create_loop(cls):
        """Get or create a shared event loop running in a background thread"""
        if cls._loop is None or not cls._loop.is_running():
            cls._loop = asyncio.new_event_loop()
            cls._loop_thread = threading.Thread(
                target=cls._loop.run_forever, daemon=True
            )
            cls._loop_thread.start()
        return cls._loop

    def __init__(self, fs):
        self.fs = fs
        self._cwd = None
        # Provide provider attribute for compatibility
        self.provider = fs

        # Setup shared event loop
        self._loop = self._get_or_create_loop()

        # Check if we need to initialize the async filesystem
        self._ensure_initialized()

    def _ensure_initialized(self):
        """Ensure async filesystem is initialized if needed"""
        if hasattr(self.fs, "_initialized") and not self.fs._initialized:
            if hasattr(self.fs, "initialize"):
                # Run initialization in the event loop
                future = asyncio.run_coroutine_threadsafe(
                    self.fs.initialize(), self._loop
                )
                try:
                    future.result(timeout=5)
                except Exception:
                    # Initialization failed, but continue anyway
                    pass

    def _sync_wrapper(self, method, *args, **kwargs):
        """Wrap async methods to run synchronously"""
        result = method(*args, **kwargs)
        if inspect.iscoroutine(result):
            # It's an async method, run it in our event loop
            future = asyncio.run_coroutine_threadsafe(result, self._loop)
            try:
                return future.result(timeout=10)
            except Exception as e:
                # If timeout or error, return None or raise
                if "timeout" in str(e).lower():
                    return None
                raise e
        return result

    # Basic file operations
    def read_file(self, path):
        return self._sync_wrapper(self.fs.read_file, path)

    def write_file(self, path, content):
        return self._sync_wrapper(self.fs.write_file, path, content)

    def mkdir(self, path):
        return self._sync_wrapper(self.fs.mkdir, path)

    def rm(self, path):
        return self._sync_wrapper(self.fs.rm, path)

    def rmdir(self, path):
        return self._sync_wrapper(self.fs.rmdir, path)

    def touch(self, path):
        return self._sync_wrapper(self.fs.touch, path)

    def cp(self, source, dest):
        return self._sync_wrapper(self.fs.cp, source, dest)

    def mv(self, source, dest):
        return self._sync_wrapper(self.fs.mv, source, dest)

    # Directory operations
    def cd(self, path):
        result = self._sync_wrapper(self.fs.cd, path)
        if result:
            self._cwd = self._sync_wrapper(self.fs.pwd)
        return result

    def pwd(self):
        return self._sync_wrapper(self.fs.pwd)

    @property
    def cwd(self):
        """Current working directory property"""
        if self._cwd is None:
            self._cwd = self._sync_wrapper(self.fs.pwd)
        return self._cwd

    def ls(self, path=None):
        return self._sync_wrapper(self.fs.ls, path)

    def list_dir(self, path):
        """List directory contents"""
        result = self._sync_wrapper(self.fs.ls, path)
        return result if result is not None else []

    def list_directory(self, path):
        """List directory contents (alias for list_dir)"""
        return self.list_dir(path)

    # Path operations
    def resolve_path(self, path):
        return self._sync_wrapper(self.fs.resolve_path, path)

    # Existence and type checking
    def exists(self, path):
        """Check if path exists"""
        try:
            info = self._sync_wrapper(self.fs.get_node_info, path)
            return info is not None
        except Exception:
            return False

    def is_file(self, path):
        """Check if path is a file"""
        try:
            info = self._sync_wrapper(self.fs.get_node_info, path)
            return info is not None and not info.is_dir
        except Exception:
            return False

    def is_dir(self, path):
        """Check if path is a directory"""
        try:
            info = self._sync_wrapper(self.fs.get_node_info, path)
            return info is not None and info.is_dir
        except Exception:
            return False

    def get_node_info(self, path):
        """Get node information for a path"""
        return self._sync_wrapper(self.fs.get_node_info, path)

    # Search operations
    def find(self, pattern, path=None):
        """Find files matching pattern"""
        if hasattr(self.fs, "find"):
            return self._sync_wrapper(self.fs.find, pattern, path)
        return []

    def search(self, pattern, path=None):
        """Search for pattern in files"""
        if hasattr(self.fs, "search"):
            return self._sync_wrapper(self.fs.search, pattern, path)
        return []

    # Info methods
    def get_fs_info(self):
        """Get filesystem info"""
        if hasattr(self.fs, "get_fs_info"):
            return self._sync_wrapper(self.fs.get_fs_info)
        return {}

    def get_storage_stats(self):
        """Get storage statistics"""
        if hasattr(self.fs, "get_storage_stats"):
            return self._sync_wrapper(self.fs.get_storage_stats)
        return {}

    # Provider operations
    def get_provider_name(self):
        """Get provider name"""
        if hasattr(self.fs, "get_provider_name"):
            return self._sync_wrapper(self.fs.get_provider_name)
        return "unknown"

    def change_provider(self, provider, **kwargs):
        """Change filesystem provider"""
        if hasattr(self.fs, "change_provider"):
            return self._sync_wrapper(self.fs.change_provider, provider, **kwargs)
        return False

    # Security operations
    def is_read_only(self):
        """Check if filesystem is read-only"""
        if hasattr(self.fs, "is_read_only"):
            return self._sync_wrapper(self.fs.is_read_only)
        return False

    def set_read_only(self, value):
        """Set read-only mode"""
        if hasattr(self.fs, "set_read_only"):
            return self._sync_wrapper(self.fs.set_read_only, value)
        return False
