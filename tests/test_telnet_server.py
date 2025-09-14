"""
tests/test_telnet_server.py
"""

import pytest
from unittest.mock import Mock, patch

# virtual shell imports
from chuk_virtual_shell.telnet_server import TelnetConnection


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

    # Create a connection with a mock shell interpreter
    with patch("chuk_virtual_shell.telnet_server.ShellInterpreter") as MockShell:
        # Configure the mock shell
        mock_shell = MockShell.return_value
        mock_shell.running = True  # Initially running
        mock_fs = Mock()
        mock_fs.get_provider_name.return_value = "MemoryStorageProvider"
        mock_shell.fs = mock_fs

        # Make sure execute("exit") sets running to False and returns "Goodbye!"
        def mock_execute(cmd):
            if cmd == "exit":
                mock_shell.running = False
                return "Goodbye!"
            return None

        mock_shell.execute.side_effect = mock_execute

        # Set up the prompt method
        mock_shell.prompt.return_value = "user@pyodide:/$ "

        # Create the connection
        connection = TelnetConnection(fake_reader, fake_writer)

        # Run the connection handler
        await connection.handle()

    # Check that the writer was closed.
    assert fake_writer.closed is True

    # Join all written output into a single string for inspection.
    output = "".join(fake_writer.written)

    # The output should contain:
    # - The welcome message.
    # - At least one prompt (e.g. "user@pyodide:/...$ ").
    # - The output of executing "exit" (typically "Goodbye!").
    assert "Welcome to PyodideShell" in output
    assert "user@pyodide:/" in output  # Check for prompt format
    assert "Goodbye!" in output
