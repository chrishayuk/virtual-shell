import os

class DummyFileSystem:
    def __init__(self, files):
        """
        Initialize the dummy filesystem with a dictionary.
        'files' is a dictionary where:
            - keys represent paths (as strings)
            - values are either:
                - dict for directories
                - string for file contents
        """
        self.files = files
        self.current_directory = "/"  # Default current directory

    def read_file(self, path):
        return self.files.get(path)

    def write_file(self, path, content):
        self.files[path] = content
        return True

    def mkdir(self, path):
        if self.exists(path):
            return False
        self.files[path] = {}
        return True

    def rm(self, path):
        # Remove a file (not a directory).
        if self.exists(path) and self.is_file(path):
            del self.files[path]
            return True
        return False

    def rmdir(self, path):
        if self.exists(path) and self.is_dir(path):
            # Remove directory only if empty.
            if self.files[path]:
                return False
            del self.files[path]
            return True
        return False

    def touch(self, path):
        if not self.exists(path):
            self.files[path] = ""
        return True

    def cd(self, path):
        # For simplicity, assume that 'path' is already resolved.
        if path == "/":
            self.current_directory = "/"
            return True
        if self.exists(path) and self.is_dir(path):
            self.current_directory = path
            return True
        return False

    def pwd(self):
        return self.current_directory

    def ls(self, path):
        # If no path is provided, use the current directory.
        if path is None:
            path = self.current_directory
        if self.exists(path) and self.is_dir(path):
            return list(self.files[path].keys())
        elif self.exists(path):
            return [os.path.basename(path)]
        return []

    def exists(self, path):
        return path in self.files

    def is_file(self, path):
        return self.exists(path) and not isinstance(self.files[path], dict)

    def is_dir(self, path):
        return self.exists(path) and isinstance(self.files[path], dict)

    # Alias to support commands using "isdir" instead of "is_dir".
    isdir = is_dir

    def resolve_path(self, path):
        """
        Resolve a given path to an absolute path.
        If 'path' is already absolute (starts with '/'), return it.
        Otherwise, join it with the current directory.
        """
        if not path:
            return self.current_directory
        if path.startswith("/"):
            return path
        base = self.current_directory.rstrip("/")
        return f"{base}/{path}"

    def delete_file(self, path):
        """
        Delete a file from the filesystem.
        Returns True if deletion was successful.
        """
        if self.exists(path) and self.is_file(path):
            del self.files[path]
            return True
        return False

    def list_dir(self, path):
        """
        List directory entries for the given path.
        Returns a list of names if the path is a directory; otherwise, returns an empty list.
        """
        if self.exists(path) and self.is_dir(path):
            return list(self.files[path].keys())
        return []

    def walk(self, path):
        """
        A basic implementation of os.walk.
        Yields tuples: (current_path, list_of_subdirectories, list_of_files).
        """
        if self.exists(path) and self.is_dir(path):
            entries = self.files[path]
            subdirs = [name for name, val in entries.items() if isinstance(val, dict)]
            files = [name for name, val in entries.items() if not isinstance(val, dict)]
            yield (path, subdirs, files)
            for sub in subdirs:
                sub_path = path.rstrip("/") + "/" + sub if path != "/" else "/" + sub
                yield from self.walk(sub_path)
        else:
            yield (path, [], [])