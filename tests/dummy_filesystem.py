import os

class DummyFileSystem:
    def __init__(self, files):
        """
        Initialize the dummy filesystem with a dictionary.
        'files' is a dictionary where keys represent paths and values are:
          - A dict for directories
          - A string for file contents
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
        # Remove file (not directory)
        if self.exists(path) and self.is_file(path):
            del self.files[path]
            return True
        return False

    def rmdir(self, path):
        if self.exists(path) and self.is_dir(path):
            if self.files[path]:
                return False  # Directory is not empty
            del self.files[path]
            return True
        return False

    def touch(self, path):
        if not self.exists(path):
            self.files[path] = ""
        return True

    def cd(self, path):
        # Assume path is already resolved.
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

    # Alias for is_dir
    isdir = is_dir

    def get_size(self, path):
        """
        Return the size (in bytes) of a file.
        For directories, return 0 (or you might sum contents if needed).
        """
        if self.is_file(path):
            content = self.files[path]
            return len(content)
        return 0

    def resolve_path(self, path):
        """
        Resolve a given path to an absolute path.
        - If the path is "." or empty, return the current directory.
        - If the path is already absolute (starts with '/'), return it.
        - Otherwise, join it with the current directory.
        """
        if not path or path == ".":
            return self.current_directory
        if path.startswith("/"):
            return path
        base = self.current_directory.rstrip("/")
        return f"{base}/{path}"

    def delete_file(self, path):
        if self.exists(path) and self.is_file(path):
            del self.files[path]
            return True
        return False

    def list_dir(self, path):
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

    def get_node_info(self, path):
        """
        Return information about a file or directory at the given path.
        
        Returns a NodeInfo object with path, name, is_dir, and is_file attributes,
        or None if the path doesn't exist.
        """
        if not self.exists(path):
            return None
        
        # Create a NodeInfo object with required attributes
        class NodeInfo:
            def __init__(self, fs, path):
                self.path = path  # Keep the full path
                self.name = os.path.basename(path) or path  # Handle root directory
                self.is_dir = fs.is_dir(path)
                self.is_file = not self.is_dir
                # Include children for directories to support recursion
                self.children = []
                if self.is_dir:
                    self.children = fs.list_dir(path)
        
        # Create the NodeInfo with a reference to the filesystem
        return NodeInfo(self, path)