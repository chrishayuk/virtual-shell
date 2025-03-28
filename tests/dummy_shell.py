from tests.dummy_filesystem import DummyFileSystem

class NodeInfo:
    """Simple class to mimic node info returned by a real filesystem."""
    def __init__(self, name, is_dir, parent_path=""):
        self.name = name
        self.is_dir = is_dir
        self.parent_path = parent_path
        
    def get_path(self):
        """Get the full path of this node."""
        if not self.parent_path or self.parent_path == "/":
            return "/" + self.name if self.name else "/"
        return f"{self.parent_path}/{self.name}"

class DummyShell:
    def __init__(self, files):
        self.fs = DummyFileSystem(files)
        self.environ = {}          # Environment variables (e.g., HOME, PWD)
        self.current_user = "testuser"
        self.initial_state = {}    # Optional state snapshot for testing

    def read_file(self, path):
        return self.fs.read_file(path)
    
    def resolve_path(self, path):
        return self.fs.resolve_path(path)
    
    def user_exists(self, target):
        return target == self.current_user
    
    def group_exists(self, target):
        return target == "staff"
        
    def get_node_info(self, path):
        """Get node information for the specified path."""
        # Check if the path exists in the filesystem
        if not self.fs.exists(path):
            return None
            
        # Extract the name component from the path
        name = path.rstrip('/').split('/')[-1] if path != "/" else ""
        parent_path = '/'.join(path.rstrip('/').split('/')[:-1]) or "/"
        
        # Determine if it's a directory
        is_dir = self.fs.is_dir(path)
        
        # Return a NodeInfo object
        return NodeInfo(name, is_dir, parent_path)
    
    def get_user_home(self, user):
        """Get the home directory for a user."""
        if user == self.current_user:
            return self.environ.get("HOME", f"/home/{user}")
        return None