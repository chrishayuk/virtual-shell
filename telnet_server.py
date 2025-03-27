"""
telnet_server.py - Telnet server implementation for PyodideShell
"""

import asyncio
from shell_interpreter import ShellInterpreter
from filesystem import VirtualFileSystem

class TelnetServer:
    def __init__(self, host='0.0.0.0', port=23):
        self.host = host
        self.port = port
        self.sessions = {}
        self.fs = VirtualFileSystem()
    
    async def handle_client(self, reader, writer):
        """Handle a telnet client connection"""
        session_id = id(writer)
        addr = writer.get_extra_info('peername')
        self.sessions[session_id] = {
            'reader': reader,
            'writer': writer,
            'addr': addr,
            'shell': ShellInterpreter(self.fs)
        }
        
        print(f"New connection from {addr}")
        
        # Send welcome message
        welcome_msg = self.fs.read_file("/etc/motd") or "Welcome to PyodideShell!\n"
        writer.write(welcome_msg.encode())
        
        shell = self.sessions[session_id]['shell']
        
        try:
            while shell.running:
                # Send prompt
                prompt = shell.prompt()
                writer.write(prompt.encode())
                await writer.drain()
                
                # Read command
                data = await reader.readline()
                cmd_line = data.decode().strip()
                
                if not cmd_line and not data:
                    # Connection closed
                    break
                
                # Execute command
                result = shell.execute(cmd_line)
                if result:
                    writer.write((result + "\n").encode())
                    await writer.drain()
                
                if not shell.running:
                    break
        except Exception as e:
            print(f"Error in session {session_id}: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
            del self.sessions[session_id]
            print(f"Connection from {addr} closed")
    
    async def start(self):
        """Start the telnet server"""
        server = await asyncio.start_server(
            self.handle_client, self.host, self.port)
        
        addr = server.sockets[0].getsockname()
        print(f'Serving on {addr}')
        
        async with server:
            await server.serve_forever()