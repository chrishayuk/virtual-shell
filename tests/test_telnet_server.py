"""
tests/virtual_server/test_telnet_server.py
"""
import asyncio
import pytest
from virtual_shell.telnet_server import TelnetServer

# Fake stream reader that returns preset lines.
class FakeStreamReader:
    def __init__(self, lines):
        # Each element in lines should be bytes.
        self.lines = lines

    async def readline(self):
        # Pop and return the first line; return empty bytes when done.
        if self.lines:
            return self.lines.pop(0)
        return b""

# Fake stream writer that records written data.
class FakeStreamWriter:
    def __init__(self):
        self.written = []
        self.closed = False

    def get_extra_info(self, key):
        # For 'peername', return a dummy address.
        if key == "peername":
            return ("127.0.0.1", 12345)
        return None

    def write(self, data):
        # Record decoded data.
        self.written.append(data.decode())

    async def drain(self):
        pass

    def close(self):
        self.closed = True

    async def wait_closed(self):
        pass

@pytest.mark.asyncio
async def test_telnet_server_handle_client_exit():
    # Prepare fake reader:
    # Simulate a client sending "exit" followed by end-of-stream.
    fake_reader = FakeStreamReader([b"exit\n", b""])
    fake_writer = FakeStreamWriter()

    # Instantiate the TelnetServer.
    server = TelnetServer()

    # Before handling the client, capture the expected welcome message.
    # The VirtualFileSystem is initialized with /etc/motd.
    expected_welcome = server.fs.read_file("/etc/motd")
    # expected_welcome should be something like:
    # "Welcome to PyodideShell - A Virtual Filesystem in the Browser!\n"
    
    # Run the client handler.
    await server.handle_client(fake_reader, fake_writer)

    # Check that the writer was closed.
    assert fake_writer.closed is True

    # Join all written output into a single string for inspection.
    output = "".join(fake_writer.written)

    # The output should contain:
    # - The welcome message.
    # - At least one prompt (which is based on the shell's environment, e.g. "user@pyodide:/...$ ")
    # - The output of executing "exit" (typically "Goodbye!").
    assert expected_welcome in output
    assert "Goodbye!" in output
    # Also, verify that after "exit" the shell stops sending further prompts.
    # Since our fake reader sends only one
