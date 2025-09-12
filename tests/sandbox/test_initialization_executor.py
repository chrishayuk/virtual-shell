# tests/sandbox/test_initialization_executor.py
from chuk_virtual_shell.sandbox.loader.initialization_executor import (
    execute_initialization,
    _ensure_directory,
)


# Dummy VirtualFileSystem to simulate mkdir and write_file.
class DummyProvider:
    def __init__(self):
        self.created = []
        self.written = {}

    def mkdir(self, path):
        self.created.append(path)
        return True

    def get_node_info(self, path):
        return None  # Simulate that the directory doesn't exist.


class DummyFS:
    def __init__(self):
        self.provider = DummyProvider()

    def mkdir(self, path):
        return self.provider.mkdir(path)

    def get_node_info(self, path):
        return self.provider.get_node_info(path)

    def write_file(self, path, content):
        self.provider.written[path] = content


def test_execute_initialization():
    fs = DummyFS()
    commands = [
        "mkdir -p /init/dir1",
        "mkdir /init/dir2",
        "echo 'Hello, Test!' > /init/file.txt",
    ]
    execute_initialization(fs, commands)
    # Expect mkdir to be called for "/init/dir2" directly.
    assert "/init/dir2" in fs.provider.created
    # For the echo command, since our DummyFS.write_file was used:
    assert fs.provider.written.get("/init/file.txt") == "Hello, Test!"


def test_ensure_directory():
    fs = DummyFS()

    # We patch get_node_info to always return None (simulate missing directories).
    def fake_get_node_info(path):
        return None

    fs.get_node_info = fake_get_node_info

    _ensure_directory(fs, "/init/dir1/dir2")
    # Expect mkdir to be called for each path component.
    assert "/init" in fs.provider.created
    assert "/init/dir1" in fs.provider.created
    assert "/init/dir1/dir2" in fs.provider.created
