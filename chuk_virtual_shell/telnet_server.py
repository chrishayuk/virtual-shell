"""
chuk_virtual_shell/telnet_server.py - Telnet server for PyodideShell
"""

import asyncio
from typing import Set

from chuk_virtual_shell.shell_interpreter import ShellInterpreter


class TelnetConnection:
    """Class representing a telnet connection"""

    def __init__(self, reader, writer, fs_provider=None, fs_provider_args=None):
        """
        Initialize a telnet connection

        Args:
            reader: StreamReader for the connection
            writer: StreamWriter for the connection
            fs_provider: Optional filesystem provider name
            fs_provider_args: Optional arguments for the filesystem provider
        """
        self.reader = reader
        self.writer = writer
        self.shell = ShellInterpreter(fs_provider, fs_provider_args)
        self.addr = writer.get_extra_info("peername")

    async def handle(self):
        """Handle the telnet connection"""
        try:
            # Send welcome message
            welcome = "Welcome to PyodideShell Telnet Server!\r\n"
            if self.shell.fs.get_provider_name() != "MemoryStorageProvider":
                welcome += f"Using filesystem provider: {self.shell.fs.get_provider_name()}\r\n"
            welcome += "\r\n"
            self.writer.write(welcome.encode())
            await self.writer.drain()

            while self.shell.running:
                # Send prompt
                prompt = self.shell.prompt()
                self.writer.write(prompt.encode())
                await self.writer.drain()

                # Read command
                data = await self.reader.readline()
                if not data:
                    break

                cmd_line = data.decode().strip()

                # Execute command
                result = self.shell.execute(cmd_line)
                if result:
                    self.writer.write((result + "\r\n").encode())
                    await self.writer.drain()

        except (ConnectionResetError, BrokenPipeError):
            pass
        except Exception as e:
            try:
                self.writer.write(f"Error: {e}\r\n".encode())
                await self.writer.drain()
            except Exception:
                pass
        finally:
            self.writer.close()
            await self.writer.wait_closed()


class TelnetServer:
    """Telnet server for PyodideShell"""

    def __init__(
        self, host="0.0.0.0", port=8023, fs_provider=None, fs_provider_args=None
    ):
        """
        Initialize the telnet server

        Args:
            host: Host to bind to
            port: Port to bind to
            fs_provider: Optional filesystem provider name
            fs_provider_args: Optional arguments for the filesystem provider
        """
        self.host = host
        self.port = port
        self.fs_provider = fs_provider
        self.fs_provider_args = fs_provider_args
        self.connections: Set[TelnetConnection] = set()

    async def client_connected(self, reader, writer):
        """Handle a client connection"""
        conn = TelnetConnection(reader, writer, self.fs_provider, self.fs_provider_args)
        addr = conn.addr
        print(f"Client connected: {addr}")

        self.connections.add(conn)
        try:
            await conn.handle()
        finally:
            self.connections.remove(conn)
            print(f"Client disconnected: {addr}")

    async def start(self):
        """Start the telnet server"""
        server = await asyncio.start_server(self.client_connected, self.host, self.port)

        addr = server.sockets[0].getsockname()
        print(f"Serving on {addr}")

        async with server:
            await server.serve_forever()
