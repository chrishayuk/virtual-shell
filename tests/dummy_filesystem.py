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

    @property
    def cwd(self):
        """Alias for current_directory for compatibility"""
        return self.current_directory

    @cwd.setter
    def cwd(self, path):
        """Set current working directory"""
        self.current_directory = path

    def chdir(self, path):
        """Alias for cd for compatibility"""
        return self.cd(path)

    def read_file(self, path):
        content = self.files.get(path)
        # Don't return dict (directory) content as file content
        if isinstance(content, dict):
            return None
        return content

    def write_file(self, path, content):
        # Store the file with the exact path as key
        self.files[path] = content

        # Also update the parent directory's structure if it exists
        # This ensures the file appears in directory listings
        if "/" in path:
            parent_path = "/".join(path.split("/")[:-1])
            filename = path.split("/")[-1]

            # If parent is root, handle specially
            if parent_path == "":
                parent_path = "/"

            # If parent directory exists and is a dict, add the file reference
            if parent_path in self.files and isinstance(self.files[parent_path], dict):
                self.files[parent_path][filename] = content

        return True

    def mkdir(self, path):
        # Resolve path to absolute path first
        resolved_path = self.resolve_path(path)
        
        if self.exists(resolved_path):
            return False
        
        # Create parent directories if they don't exist
        parts = [p for p in resolved_path.split("/") if p]  # Remove empty parts
        current_path = ""
        
        for part in parts:
            current_path = current_path + "/" + part if current_path else "/" + part
            if current_path == "/":
                continue
                
            if not self.exists(current_path):
                self.files[current_path] = {}
        
        return True

    def rm(self, path):
        # Remove file (not directory)
        if self.exists(path) and self.is_file(path):
            del self.files[path]

            # Also remove from parent directory's structure if it exists
            if "/" in path:
                parent_path = "/".join(path.split("/")[:-1])
                filename = path.split("/")[-1]

                # If parent is root, handle specially
                if parent_path == "":
                    parent_path = "/"

                # If parent directory exists and is a dict, remove the file reference
                if parent_path in self.files and isinstance(
                    self.files[parent_path], dict
                ):
                    if filename in self.files[parent_path]:
                        del self.files[parent_path][filename]

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
            # Use portable path operations
            basename = path.split("/")[-1] if "/" in path else path
            return [basename]
        return []

    def exists(self, path):
        return path in self.files

    def is_file(self, path):
        return self.exists(path) and not isinstance(self.files[path], dict)

    def is_dir(self, path):
        return self.exists(path) and isinstance(self.files[path], dict)

    # Aliases for compatibility
    isdir = is_dir
    is_directory = is_dir

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
                # Use portable path operations
                self.name = (
                    path.split("/")[-1] if "/" in path else path or path
                )  # Handle root directory
                self.is_dir = fs.is_dir(path)
                self.is_file = not self.is_dir
                # Include children for directories to support recursion
                self.children = []
                if self.is_dir:
                    self.children = fs.list_dir(path)

        # Create the NodeInfo with a reference to the filesystem
        return NodeInfo(self, path)

    def get_storage_stats(self):
        """
        Return storage statistics for the filesystem.
        """
        total_files = 0
        total_size = 0

        def count_files(d):
            nonlocal total_files, total_size
            for key, value in d.items():
                if isinstance(value, dict):
                    total_files += 1  # Count directory
                    count_files(value)
                else:
                    total_files += 1  # Count file
                    total_size += len(value) if value else 0

        count_files(self.files)

        return {
            "provider_name": "DummyFS",
            "max_total_size": 1000000000,  # 1GB dummy limit
            "total_size_bytes": total_size,
            "max_files": 10000,  # 10k files dummy limit
            "file_count": total_files,
        }

    def copy_file(self, src, dst):
        """Copy a file from src to dst"""
        if self.is_file(src):
            content = self.read_file(src)
            self.write_file(dst, content)
            return True
        return False

    def copy_dir(self, src, dst):
        """Recursively copy a directory from src to dst"""
        if not self.is_dir(src):
            return False

        # Create destination directory with proper structure
        if not self.exists(dst):
            self.files[dst] = {}

        # Get the source directory structure
        src_dir = self.files[src]

        # If it's a nested dict structure, copy it properly
        if isinstance(src_dir, dict):
            # Copy nested structure
            for key, value in src_dir.items():
                if isinstance(value, dict):
                    # It's a subdirectory in nested format - shouldn't happen in our test setup
                    continue
                else:
                    # It's a file in nested format
                    dst_file_path = f"{dst}/{key}" if dst != "/" else f"/{key}"
                    self.files[dst_file_path] = value

        # Also handle flat file paths that start with src
        for path in list(self.files.keys()):
            if path.startswith(src + "/"):
                # Get relative path from src
                relative = path[len(src) + 1 :]
                dst_path = f"{dst}/{relative}" if dst != "/" else f"/{relative}"

                if self.is_dir(path):
                    if not self.exists(dst_path):
                        self.files[dst_path] = {}
                else:
                    # Copy file content
                    self.files[dst_path] = self.files[path]

        return True
