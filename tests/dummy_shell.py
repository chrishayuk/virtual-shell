"""
tests/chuk_virtual_shell/dummy_shell.py
"""
from tests.dummy_filesystem import DummyFileSystem
class DummyShell:
    def __init__(self, files):
        self.fs = DummyFileSystem(files)
