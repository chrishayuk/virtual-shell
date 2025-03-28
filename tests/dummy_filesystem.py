class DummyFileSystem:
    def __init__(self, files):
        self.files = files
        self.current_directory = "/"  # Default current directory

    def read_file(self, path):
        return self.files.get(path)

    def write_file(self, path, content):
        self.files[path] = content
        return True

    def mkdir(self, path):
        if path in self.files:
            return False
        self.files[path] = {}
        return True

    def rm(self, path):
        if path in self.files:
            del self.files[path]
            return True
        return False

    def rmdir(self, path):
        if path in self.files and isinstance(self.files[path], dict):
            if self.files[path]:
                return False  # Directory is not empty
            del self.files[path]
            return True
        return False

    def touch(self, path):
        if path not in self.files:
            self.files[path] = ""
        return True

    def cd(self, path):
        if path == "/":
            self.current_directory = "/"
            return True
        if path in self.files and isinstance(self.files[path], dict):
            self.current_directory = path
            return True
        return False

    def pwd(self):
        return self.current_directory

    def ls(self, path):
        # If no path is given, list the current directory.
        if path is None:
            path = self.current_directory
        # If the path is a directory (represented as a dict), return its keys.
        if path in self.files and isinstance(self.files[path], dict):
            return list(self.files[path].keys())
        # If the path is a file, return a list containing its name.
        elif path in self.files:
            return [path]
        # Otherwise, return an empty list.
        return []
