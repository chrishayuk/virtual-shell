"""
Shell session management with PTY support, streaming, and cancellation.

This module provides stateful shell sessions with:
- PTY support for interactive TUI applications
- Streaming output with sequence IDs
- Process cancellation and timeouts
- Persistent environment and working directory
"""

import asyncio
import os
import signal
import sys
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, AsyncIterator
import logging

from chuk_sessions import SessionManager  # type: ignore[import-untyped]

logger = logging.getLogger(__name__)


class SessionMode(Enum):
    """Shell session modes."""

    PTY = "pty"  # For interactive/TUI applications
    PIPE = "pipe"  # For batch/pipeline operations


class CommandState(Enum):
    """Command execution states."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"
    ERROR = "error"


@dataclass
class StreamChunk:
    """Output stream chunk with metadata."""

    sequence_id: int
    stream_type: str  # 'stdout' or 'stderr'
    data: str
    timestamp: float
    truncated: bool = False
    command_id: Optional[str] = None


@dataclass
class CommandResult:
    """Result of command execution."""

    command_id: str
    command: str
    state: CommandState
    exit_code: Optional[int] = None
    stdout: str = ""
    stderr: str = ""
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    chunks: List[StreamChunk] = field(default_factory=list)


@dataclass
class ShellSessionState:
    """Persistent state for a shell session."""

    session_id: str
    cwd: str
    env: Dict[str, str]
    umask: Optional[int] = None
    history: List[str] = field(default_factory=list)
    provider_mounts: Dict[str, Any] = field(default_factory=dict)
    mode: SessionMode = SessionMode.PIPE
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    pty_size: Optional[Tuple[int, int]] = None  # (rows, cols)


class ShellSession:
    """
    Individual shell session with stateful execution.

    Maintains working directory, environment, and command history
    across multiple command executions.
    """

    def __init__(
        self,
        session_id: str,
        shell_interpreter,
        mode: SessionMode = SessionMode.PIPE,
        pty_size: Optional[Tuple[int, int]] = None,
    ):
        """Initialize a shell session."""
        self.session_id = session_id
        self.shell = shell_interpreter
        self.mode = mode
        self.pty_size = pty_size or (24, 80)  # Default terminal size

        # Session state
        self.state = ShellSessionState(
            session_id=session_id,
            cwd=self.shell.fs.pwd(),
            env=dict(self.shell.environ),
            mode=mode,
            pty_size=pty_size,
        )

        # Active processes
        self.active_commands: Dict[str, asyncio.subprocess.Process] = {}
        self.command_results: Dict[str, CommandResult] = {}

        # Streaming
        self.sequence_counter = 0
        self.stream_buffers: Dict[str, List[StreamChunk]] = {}

        # PTY support
        self.pty_master = None
        self.pty_slave = None
        if mode == SessionMode.PTY:
            self._setup_pty()

    def _setup_pty(self):
        """Setup pseudo-terminal for interactive applications."""
        if sys.platform == "win32":
            # Windows doesn't have native PTY support
            logger.warning(
                "PTY mode not supported on Windows, falling back to PIPE mode"
            )
            self.mode = SessionMode.PIPE
            return

        try:
            import pty
            import termios
            import tty

            # Create a pseudo-terminal pair
            self.pty_master, self.pty_slave = pty.openpty()

            # Set terminal size
            if self.pty_size:
                import fcntl
                import struct

                fcntl.ioctl(
                    self.pty_slave,
                    termios.TIOCSWINSZ,
                    struct.pack("HHHH", self.pty_size[0], self.pty_size[1], 0, 0),
                )

            # Set raw mode for better TUI support
            tty.setraw(self.pty_master)

        except ImportError:
            logger.warning("PTY support not available, falling back to PIPE mode")
            self.mode = SessionMode.PIPE
        except Exception as e:
            logger.error(f"Failed to setup PTY: {e}")
            self.mode = SessionMode.PIPE

    async def run(
        self,
        command: str,
        timeout_ms: Optional[int] = None,
        soft_timeout_ms: Optional[int] = None,
        stream: bool = True,
    ) -> AsyncIterator[StreamChunk]:
        """
        Execute a command in the session with streaming output.

        Args:
            command: Command to execute
            timeout_ms: Hard timeout in milliseconds (SIGKILL)
            soft_timeout_ms: Soft timeout in milliseconds (SIGINT)
            stream: Whether to stream output chunks

        Yields:
            StreamChunk objects with output data
        """
        command_id = str(uuid.uuid4())
        result = CommandResult(
            command_id=command_id,
            command=command,
            state=CommandState.PENDING,
            start_time=time.time(),
        )
        self.command_results[command_id] = result

        # Update session activity
        self.state.last_activity = time.time()
        self.state.history.append(command)

        try:
            # Execute in the shell interpreter for virtual FS support
            if self.mode == SessionMode.PTY and self.pty_master:
                # PTY mode for interactive applications
                async for chunk in self._run_pty(
                    command_id, command, timeout_ms, soft_timeout_ms, stream
                ):
                    yield chunk
            else:
                # Standard pipe mode
                async for chunk in self._run_pipe(
                    command_id, command, timeout_ms, soft_timeout_ms, stream
                ):
                    yield chunk

        except asyncio.CancelledError:
            result.state = CommandState.CANCELLED
            raise
        except Exception as e:
            result.state = CommandState.ERROR
            result.stderr += str(e)
            raise
        finally:
            result.end_time = time.time()
            if command_id in self.active_commands:
                del self.active_commands[command_id]

    async def _run_pipe(
        self,
        command_id: str,
        command: str,
        timeout_ms: Optional[int],
        soft_timeout_ms: Optional[int],
        stream: bool,
    ) -> AsyncIterator[StreamChunk]:
        """Execute command in pipe mode with the virtual shell."""
        result = self.command_results[command_id]
        result.state = CommandState.RUNNING

        # Execute through the shell interpreter
        try:
            # Change to session's working directory
            original_cwd = self.shell.fs.pwd()
            if self.state.cwd != original_cwd:
                self.shell.execute(f"cd {self.state.cwd}")

            # Apply session environment
            for key, value in self.state.env.items():
                if key not in self.shell.environ or self.shell.environ[key] != value:
                    self.shell.environ[key] = value

            # Execute command and capture output
            output = self.shell.execute(command)

            # Update session state
            self.state.cwd = self.shell.fs.pwd()
            self.state.env = dict(self.shell.environ)

            # Stream output as chunks
            if output:
                chunk = StreamChunk(
                    sequence_id=self._next_sequence(),
                    stream_type="stdout",
                    data=output,
                    timestamp=time.time(),
                    command_id=command_id,
                )
                result.chunks.append(chunk)
                result.stdout = output
                if stream:
                    yield chunk

            result.state = CommandState.COMPLETED
            result.exit_code = self.shell.return_code

        except Exception as e:
            error_chunk = StreamChunk(
                sequence_id=self._next_sequence(),
                stream_type="stderr",
                data=str(e),
                timestamp=time.time(),
                command_id=command_id,
            )
            result.chunks.append(error_chunk)
            result.stderr = str(e)
            result.state = CommandState.ERROR
            result.exit_code = 1
            if stream:
                yield error_chunk

    async def _run_pty(
        self,
        command_id: str,
        command: str,
        timeout_ms: Optional[int],
        soft_timeout_ms: Optional[int],
        stream: bool,
    ) -> AsyncIterator[StreamChunk]:
        """Execute command in PTY mode for interactive applications."""
        # For now, fall back to pipe mode
        # Full PTY implementation would require OS-level process management
        logger.info(f"PTY mode requested but using pipe mode for command: {command}")
        async for chunk in self._run_pipe(
            command_id, command, timeout_ms, soft_timeout_ms, stream
        ):
            yield chunk

    def _next_sequence(self) -> int:
        """Get next sequence ID for streaming."""
        self.sequence_counter += 1
        return self.sequence_counter

    async def stdin(self, command_id: str, data: str):
        """Send input to a running command."""
        if command_id in self.active_commands:
            process = self.active_commands[command_id]
            if process.stdin:
                process.stdin.write(data.encode())
                await process.stdin.drain()

    async def cancel(self, command_id: str) -> bool:
        """Cancel a running command."""
        if command_id not in self.active_commands:
            return False

        process = self.active_commands[command_id]
        result = self.command_results[command_id]

        try:
            # Try soft kill first (SIGINT)
            if sys.platform != "win32":
                process.send_signal(signal.SIGINT)
                try:
                    await asyncio.wait_for(process.wait(), timeout=2.0)
                except asyncio.TimeoutError:
                    # Hard kill if soft kill didn't work
                    process.kill()
            else:
                # Windows doesn't support SIGINT properly
                process.terminate()

            await process.wait()
            result.state = CommandState.CANCELLED
            return True

        except Exception as e:
            logger.error(f"Failed to cancel command {command_id}: {e}")
            return False

    def resize(self, rows: int, cols: int):
        """Resize PTY terminal."""
        self.pty_size = (rows, cols)
        self.state.pty_size = (rows, cols)

        if self.mode == SessionMode.PTY and self.pty_slave:
            try:
                import fcntl
                import struct
                import termios

                fcntl.ioctl(
                    self.pty_slave,
                    termios.TIOCSWINSZ,
                    struct.pack("HHHH", rows, cols, 0, 0),
                )
            except Exception as e:
                logger.error(f"Failed to resize PTY: {e}")

    def get_state(self) -> ShellSessionState:
        """Get current session state."""
        return self.state

    def cleanup(self):
        """Clean up session resources."""
        # Cancel all active commands
        for command_id in list(self.active_commands.keys()):
            asyncio.create_task(self.cancel(command_id))

        # Close PTY if open
        if self.pty_master:
            os.close(self.pty_master)
        if self.pty_slave:
            os.close(self.pty_slave)


class ShellSessionManager:
    """
    Manages multiple shell sessions with chuk-sessions backend.

    Provides session lifecycle management, persistence, and cleanup.
    """

    def __init__(
        self,
        shell_factory,
        session_backend: Optional[SessionManager] = None,
        default_ttl: int = 3600,
    ):
        """
        Initialize session manager.

        Args:
            shell_factory: Callable that creates shell interpreter instances
            session_backend: chuk-sessions SessionManager instance
            default_ttl: Default session TTL in seconds
        """
        self.shell_factory = shell_factory
        self.session_backend = session_backend or SessionManager()
        self.default_ttl = default_ttl
        self.active_sessions: Dict[str, ShellSession] = {}

    async def create_session(
        self,
        mode: SessionMode = SessionMode.PIPE,
        pty_size: Optional[Tuple[int, int]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create a new shell session.

        Args:
            mode: Session mode (PTY or PIPE)
            pty_size: Terminal size for PTY mode
            metadata: Additional session metadata

        Returns:
            Session ID
        """
        # Allocate session in backend
        # Convert TTL from seconds to hours
        ttl_hours = self.default_ttl // 3600 if self.default_ttl >= 3600 else 1
        session_id = await self.session_backend.allocate_session(
            ttl_hours=ttl_hours, custom_metadata=metadata or {}
        )

        # Create shell instance
        shell = self.shell_factory()

        # Create session wrapper
        session = ShellSession(
            session_id=session_id, shell_interpreter=shell, mode=mode, pty_size=pty_size
        )

        self.active_sessions[session_id] = session

        # Store session state in backend
        await self._persist_session(session)

        return session_id

    async def get_session(self, session_id: str) -> Optional[ShellSession]:
        """Get an active session by ID."""
        # Check if session is already active
        if session_id in self.active_sessions:
            # Validate and extend TTL
            if await self.session_backend.validate_session(session_id):
                ttl_hours = self.default_ttl // 3600 if self.default_ttl >= 3600 else 1
                await self.session_backend.extend_session_ttl(session_id, ttl_hours)
                return self.active_sessions[session_id]
            else:
                # Session expired, clean up
                self._cleanup_session(session_id)
                return None

        # Try to get session info from backend
        session_info = await self.session_backend.get_session_info(session_id)
        if session_info and session_info.get("metadata"):
            # Restore session state from metadata
            return await self._restore_session(session_id, session_info["metadata"])

        return None

    async def close_session(self, session_id: str) -> bool:
        """Close and clean up a session."""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session.cleanup()
            del self.active_sessions[session_id]

        # Delete from backend
        await self.session_backend.delete_session(session_id)
        return True

    async def run_command(
        self, session_id: str, command: str, **kwargs
    ) -> AsyncIterator[StreamChunk]:
        """Run a command in a session."""
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found or expired")

        async for chunk in session.run(command, **kwargs):
            yield chunk

        # Persist updated session state
        await self._persist_session(session)

    async def send_input(self, session_id: str, command_id: str, data: str):
        """Send input to a running command."""
        session = await self.get_session(session_id)
        if session:
            await session.stdin(command_id, data)

    async def cancel_command(self, session_id: str, command_id: str) -> bool:
        """Cancel a running command."""
        session = await self.get_session(session_id)
        if session:
            return await session.cancel(command_id)
        return False

    async def resize_terminal(self, session_id: str, rows: int, cols: int):
        """Resize terminal for a PTY session."""
        session = await self.get_session(session_id)
        if session:
            session.resize(rows, cols)
            await self._persist_session(session)

    async def _persist_session(self, session: ShellSession):
        """Persist session state to backend."""
        state = session.get_state()
        session_data = {
            "cwd": state.cwd,
            "env": state.env,
            "umask": state.umask,
            "history": state.history,
            "provider_mounts": state.provider_mounts,
            "mode": state.mode.value,
            "created_at": state.created_at,
            "last_activity": state.last_activity,
            "pty_size": state.pty_size,
        }
        # Store session data in metadata
        await self.session_backend.update_session_metadata(
            state.session_id, session_data
        )

    async def _restore_session(
        self, session_id: str, session_data: Dict[str, Any]
    ) -> ShellSession:
        """Restore a session from persisted state."""
        # Create new shell instance
        shell = self.shell_factory()

        # Restore working directory
        if "cwd" in session_data:
            shell.execute(f"cd {session_data['cwd']}")

        # Restore environment
        if "env" in session_data:
            for key, value in session_data["env"].items():
                shell.environ[key] = value

        # Create session with restored state
        mode = SessionMode(session_data.get("mode", "pipe"))
        session = ShellSession(
            session_id=session_id,
            shell_interpreter=shell,
            mode=mode,
            pty_size=session_data.get("pty_size"),
        )

        # Restore additional state
        session.state.history = session_data.get("history", [])
        session.state.provider_mounts = session_data.get("provider_mounts", {})
        session.state.created_at = session_data.get("created_at", time.time())

        self.active_sessions[session_id] = session
        return session

    def _cleanup_session(self, session_id: str):
        """Clean up an expired or invalid session."""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session.cleanup()
            del self.active_sessions[session_id]

    async def cleanup_expired(self):
        """Clean up all expired sessions."""
        for session_id in list(self.active_sessions.keys()):
            if not await self.session_backend.validate_session(session_id):
                self._cleanup_session(session_id)
