"""
Tests for shell session management.
"""

import pytest
import pytest_asyncio
import time

from chuk_virtual_shell.session import (
    ShellSession,
    ShellSessionManager,
    SessionMode,
    CommandState,
    StreamChunk,
)
from chuk_virtual_shell.shell_interpreter import ShellInterpreter


@pytest.fixture
def shell_factory():
    """Factory for creating shell interpreter instances."""

    def factory():
        return ShellInterpreter()

    return factory


@pytest_asyncio.fixture
async def session_manager(shell_factory):
    """Create a session manager for testing."""
    manager = ShellSessionManager(shell_factory=shell_factory)
    yield manager
    # Cleanup
    for session_id in list(manager.active_sessions.keys()):
        await manager.close_session(session_id)


class TestShellSession:
    """Test ShellSession class."""

    def test_session_creation(self):
        """Test creating a shell session."""
        shell = ShellInterpreter()
        session = ShellSession(
            session_id="test-session", shell_interpreter=shell, mode=SessionMode.PIPE
        )

        assert session.session_id == "test-session"
        assert session.mode == SessionMode.PIPE
        assert session.state.cwd == "/"
        assert len(session.state.history) == 0

    def test_pty_mode_creation(self):
        """Test creating a PTY mode session."""
        shell = ShellInterpreter()
        session = ShellSession(
            session_id="pty-session",
            shell_interpreter=shell,
            mode=SessionMode.PTY,
            pty_size=(30, 100),
        )

        # On non-Unix systems, PTY mode should fall back to PIPE
        if session.mode == SessionMode.PTY:
            assert session.pty_size == (30, 100)
            assert session.state.pty_size == (30, 100)
        else:
            # Fallback on Windows
            assert session.mode == SessionMode.PIPE

    @pytest.mark.asyncio
    async def test_run_command(self):
        """Test running a command in a session."""
        shell = ShellInterpreter()
        session = ShellSession(
            session_id="test-session", shell_interpreter=shell, mode=SessionMode.PIPE
        )

        chunks = []
        async for chunk in session.run("echo hello"):
            chunks.append(chunk)

        assert len(chunks) == 1
        assert chunks[0].stream_type == "stdout"
        assert "hello" in chunks[0].data
        assert chunks[0].sequence_id == 1

        # Check command result
        assert len(session.command_results) == 1
        result = list(session.command_results.values())[0]
        assert result.state == CommandState.COMPLETED
        assert result.exit_code == 0
        assert "hello" in result.stdout

    @pytest.mark.asyncio
    async def test_command_history(self):
        """Test that commands are added to history."""
        shell = ShellInterpreter()
        session = ShellSession(
            session_id="test-session", shell_interpreter=shell, mode=SessionMode.PIPE
        )

        # Run multiple commands
        async for _ in session.run("echo first"):
            pass
        async for _ in session.run("echo second"):
            pass
        async for _ in session.run("pwd"):
            pass

        assert len(session.state.history) == 3
        assert session.state.history == ["echo first", "echo second", "pwd"]

    @pytest.mark.asyncio
    async def test_working_directory_persistence(self):
        """Test that working directory persists across commands."""
        shell = ShellInterpreter()
        session = ShellSession(
            session_id="test-session", shell_interpreter=shell, mode=SessionMode.PIPE
        )

        # Create a directory and change to it
        async for _ in session.run("mkdir /testdir"):
            pass
        async for _ in session.run("cd /testdir"):
            pass

        assert session.state.cwd == "/testdir"

        # Run another command and verify we're still in the same directory
        chunks = []
        async for chunk in session.run("pwd"):
            chunks.append(chunk)

        assert len(chunks) == 1
        assert "/testdir" in chunks[0].data

    @pytest.mark.asyncio
    async def test_environment_persistence(self):
        """Test that environment variables persist across commands."""
        shell = ShellInterpreter()
        session = ShellSession(
            session_id="test-session", shell_interpreter=shell, mode=SessionMode.PIPE
        )

        # Set an environment variable
        async for _ in session.run("export TEST_VAR=hello"):
            pass

        assert "TEST_VAR" in session.state.env
        assert session.state.env["TEST_VAR"] == "hello"

        # Verify it's available in the shell environment
        assert "TEST_VAR" in session.shell.environ
        assert session.shell.environ["TEST_VAR"] == "hello"

        # Test that env persists across multiple commands
        async for _ in session.run("export ANOTHER_VAR=world"):
            pass

        assert "ANOTHER_VAR" in session.state.env
        assert session.state.env["ANOTHER_VAR"] == "world"

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test handling of command errors."""
        shell = ShellInterpreter()
        session = ShellSession(
            session_id="test-session", shell_interpreter=shell, mode=SessionMode.PIPE
        )

        chunks = []
        async for chunk in session.run("nonexistent_command"):
            chunks.append(chunk)

        # Check that we get an error
        assert len(session.command_results) == 1
        result = list(session.command_results.values())[0]
        # The virtual shell returns "command not found" for unknown commands
        assert (
            "not found" in result.stdout.lower() or "not found" in result.stderr.lower()
        )

    def test_sequence_counter(self):
        """Test sequence ID generation."""
        shell = ShellInterpreter()
        session = ShellSession(
            session_id="test-session", shell_interpreter=shell, mode=SessionMode.PIPE
        )

        assert session._next_sequence() == 1
        assert session._next_sequence() == 2
        assert session._next_sequence() == 3


class TestShellSessionManager:
    """Test ShellSessionManager class."""

    @pytest.mark.asyncio
    async def test_create_session(self, session_manager):
        """Test creating a new session."""
        session_id = await session_manager.create_session(mode=SessionMode.PIPE)

        assert session_id is not None
        assert session_id in session_manager.active_sessions

        session = await session_manager.get_session(session_id)
        assert session is not None
        assert session.session_id == session_id

    @pytest.mark.asyncio
    async def test_create_pty_session(self, session_manager):
        """Test creating a PTY mode session."""
        session_id = await session_manager.create_session(
            mode=SessionMode.PTY, pty_size=(40, 120)
        )

        session = await session_manager.get_session(session_id)
        assert session is not None
        # Mode might fall back to PIPE on non-Unix systems
        if session.mode == SessionMode.PTY:
            assert session.pty_size == (40, 120)

    @pytest.mark.asyncio
    async def test_run_command_in_session(self, session_manager):
        """Test running commands through the session manager."""
        session_id = await session_manager.create_session()

        chunks = []
        async for chunk in session_manager.run_command(
            session_id=session_id, command="echo test"
        ):
            chunks.append(chunk)

        assert len(chunks) == 1
        assert "test" in chunks[0].data

    @pytest.mark.asyncio
    async def test_session_not_found(self, session_manager):
        """Test handling of invalid session ID."""
        with pytest.raises(ValueError, match="not found"):
            async for _ in session_manager.run_command(
                session_id="invalid-session", command="echo test"
            ):
                pass

    @pytest.mark.asyncio
    async def test_close_session(self, session_manager):
        """Test closing a session."""
        session_id = await session_manager.create_session()

        # Session should exist
        session = await session_manager.get_session(session_id)
        assert session is not None

        # Close the session
        success = await session_manager.close_session(session_id)
        assert success

        # Session should no longer be active
        assert session_id not in session_manager.active_sessions

    @pytest.mark.asyncio
    async def test_resize_terminal(self, session_manager):
        """Test resizing terminal in a PTY session."""
        session_id = await session_manager.create_session(
            mode=SessionMode.PTY, pty_size=(24, 80)
        )

        # Resize the terminal
        await session_manager.resize_terminal(session_id, 40, 120)

        session = await session_manager.get_session(session_id)
        if session.mode == SessionMode.PTY:
            assert session.pty_size == (40, 120)
            assert session.state.pty_size == (40, 120)

    @pytest.mark.asyncio
    async def test_session_persistence(self, session_manager):
        """Test that session state is persisted."""
        session_id = await session_manager.create_session()

        # Run commands to modify state
        async for _ in session_manager.run_command(
            session_id=session_id, command="mkdir /persistdir"
        ):
            pass

        async for _ in session_manager.run_command(
            session_id=session_id, command="cd /persistdir"
        ):
            pass

        async for _ in session_manager.run_command(
            session_id=session_id, command="export PERSIST_VAR=test"
        ):
            pass

        # Get session and check state
        session = await session_manager.get_session(session_id)
        assert session.state.cwd == "/persistdir"
        assert session.state.env.get("PERSIST_VAR") == "test"
        assert len(session.state.history) == 3

    @pytest.mark.asyncio
    async def test_multiple_sessions(self, session_manager):
        """Test managing multiple sessions simultaneously."""
        # Create multiple sessions
        session1 = await session_manager.create_session()
        session2 = await session_manager.create_session()
        session3 = await session_manager.create_session()

        assert len(session_manager.active_sessions) == 3

        # Run different commands in each session
        async for _ in session_manager.run_command(
            session_id=session1, command="export VAR1=session1"
        ):
            pass

        async for _ in session_manager.run_command(
            session_id=session2, command="export VAR2=session2"
        ):
            pass

        async for _ in session_manager.run_command(
            session_id=session3, command="export VAR3=session3"
        ):
            pass

        # Verify session isolation
        s1 = await session_manager.get_session(session1)
        s2 = await session_manager.get_session(session2)
        s3 = await session_manager.get_session(session3)

        assert s1.state.env.get("VAR1") == "session1"
        assert "VAR2" not in s1.state.env
        assert "VAR3" not in s1.state.env

        assert s2.state.env.get("VAR2") == "session2"
        assert "VAR1" not in s2.state.env
        assert "VAR3" not in s2.state.env

        assert s3.state.env.get("VAR3") == "session3"
        assert "VAR1" not in s3.state.env
        assert "VAR2" not in s3.state.env


class TestStreamChunk:
    """Test StreamChunk data class."""

    def test_stream_chunk_creation(self):
        """Test creating a stream chunk."""
        chunk = StreamChunk(
            sequence_id=1,
            stream_type="stdout",
            data="test output",
            timestamp=time.time(),
            truncated=False,
            command_id="cmd-123",
        )

        assert chunk.sequence_id == 1
        assert chunk.stream_type == "stdout"
        assert chunk.data == "test output"
        assert chunk.truncated is False
        assert chunk.command_id == "cmd-123"

    def test_stream_chunk_defaults(self):
        """Test stream chunk default values."""
        chunk = StreamChunk(
            sequence_id=1, stream_type="stderr", data="error", timestamp=time.time()
        )

        assert chunk.truncated is False
        assert chunk.command_id is None
