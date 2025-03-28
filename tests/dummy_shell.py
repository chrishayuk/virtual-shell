from tests.dummy_filesystem import DummyFileSystem

class DummyShell:
    def __init__(self, files):
        self.fs = DummyFileSystem(files)
        self.environ = {}          # Environment variables (e.g., HOME, PWD)
        self.current_user = "testuser"
        self.initial_state = {}    # Optional: for state comparison in tests

    def read_file(self, path):
        return self.fs.read_file(path)
    
    def resolve_path(self, path):
        return self.fs.resolve_path(path)
    
    def user_exists(self, target):
        # For testing, assume the current user always exists.
        return target == self.current_user
    
    def group_exists(self, target):
        # For testing, assume a single group "staff".
        return target == "staff"
