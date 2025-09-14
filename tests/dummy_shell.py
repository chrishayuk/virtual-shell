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
        self.environ = {}  # Environment variables (e.g., HOME, PWD)
        self.current_user = "testuser"
        self.initial_state = {}  # Optional state snapshot for testing

    def read_file(self, path):
        return self.fs.read_file(path)

    def create_file(self, path, content):
        """Create a file with the given content."""
        return self.fs.write_file(path, content)

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
        name = path.rstrip("/").split("/")[-1] if path != "/" else ""
        parent_path = "/".join(path.rstrip("/").split("/")[:-1]) or "/"

        # Determine if it's a directory
        is_dir = self.fs.is_dir(path)

        # Return a NodeInfo object
        return NodeInfo(name, is_dir, parent_path)

    def get_user_home(self, user):
        """Get the home directory for a user."""
        if user == self.current_user:
            return self.environ.get("HOME", f"/home/{user}")
        return None

    def execute(self, command):
        """Execute a command (simplified for testing)."""
        # Simple command execution for testing
        if command.startswith("echo "):
            # Return the text after echo, handling quotes properly
            text = command[5:].strip()
            # Remove outer quotes if present
            if (text.startswith('"') and text.endswith('"')) or (
                text.startswith("'") and text.endswith("'")
            ):
                text = text[1:-1]
            return text
        elif command == "pwd":
            return self.fs.pwd()
        elif command.startswith("cat"):
            # Handle cat with arguments
            if len(command) > 3 and command[3:4] in [" ", "\t"]:
                filename = command[4:].strip()
                return self.fs.read_file(filename) or f"cat: {filename}: No such file"
            # Handle cat without arguments (reads from stdin)
            elif command == "cat":
                if hasattr(self, "_stdin_buffer") and self._stdin_buffer:
                    result = self._stdin_buffer
                    self._stdin_buffer = None
                    return result
                return "cat: missing operand"
        elif command == "whoami":
            return self.current_user
        else:
            # Return a simple response for unknown commands
            return f"Command executed: {command}"
