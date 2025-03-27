"""
tests/virtual_shell/dummy_shell.py
"""
from tests.filesystem.dummy_filesystem import DummyFileSystem

class DummyShell:
    def __init__(self, files):
        self.fs = DummyFileSystem(files)
