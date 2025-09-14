"""
Tests for the MCP server implementation
"""

import asyncio
import os
import pytest
import sys
import time
from unittest.mock import AsyncMock, MagicMock, Mock, patch

# Skip all MCP server tests on Windows due to uvloop dependency
pytestmark = pytest.mark.skipif(
    sys.platform == "win32", 
    reason="MCP server functionality not supported on Windows (uvloop dependency)"
)

# Import the module under test
from chuk_virtual_shell.mcp_server import (
    SessionInfo,
    get_user_id,
    get_user_sessions,
    get_user_tasks,
    truncate_output,
    collect_command_output,
    sessions,
    background_tasks,
    bash,
    get_task_output,
    cancel_task,
    list_sessions,
    destroy_session,
    get_session_state,
    whoami,
    cleanup,
)


@pytest.fixture
def clean_state():
    """Clean up global state before and after each test"""
    sessions.clear()
    background_tasks.clear()
    yield
    sessions.clear()
    background_tasks.clear()


@pytest.fixture
def mock_session_manager():
    """Mock session manager for testing"""
    manager = AsyncMock()
    manager.create_session = AsyncMock(return_value="test_session_id")
    manager.run_command = AsyncMock()
    manager.get_session_state = AsyncMock(
        return_value={
            "current_directory": "/test/dir",
            "environment": {"TEST_VAR": "test_value"},
        }
    )
    manager.is_session_active = AsyncMock(return_value=True)

    with patch("chuk_virtual_shell.mcp_server.session_manager", manager):
        yield manager


class TestUtilityFunctions:
    """Test utility functions"""

    def test_get_user_id_from_env(self):
        """Test getting user ID from environment variables"""
        with patch.dict(os.environ, {"MCP_USER_ID": "test_user_123"}):
            user_id = get_user_id()
            assert len(user_id) == 16  # SHA256 hash truncated to 16 chars
            assert user_id.isalnum()

    def test_get_user_id_from_system_user(self):
        """Test fallback to system user"""
        with patch.dict(os.environ, {}, clear=True):
            with patch.dict(os.environ, {"USER": "testuser"}):
                user_id = get_user_id()
                assert len(user_id) == 16
                assert user_id.isalnum()

    def test_get_user_id_fallback_to_pid(self):
        """Test fallback to PID-based ID"""
        with patch.dict(os.environ, {}, clear=True):
            with patch("os.getpid", return_value=12345):
                user_id = get_user_id()
                assert len(user_id) == 16
                assert user_id.isalnum()

    def test_get_user_sessions(self, clean_state):
        """Test filtering sessions by user"""
        user1 = "user1_id"
        user2 = "user2_id"

        sessions["session1"] = SessionInfo("session1", user1)
        sessions["session2"] = SessionInfo("session2", user2)
        sessions["session3"] = SessionInfo("session3", user1)

        user1_sessions = get_user_sessions(user1)
        assert len(user1_sessions) == 2
        assert "session1" in user1_sessions
        assert "session3" in user1_sessions
        assert "session2" not in user1_sessions

    def test_get_user_tasks(self, clean_state):
        """Test filtering background tasks by user"""
        user1 = "user1_id"
        user2 = "user2_id"

        task1 = AsyncMock()
        task2 = AsyncMock()

        background_tasks["task1"] = {"user_id": user1, "task": task1}
        background_tasks["task2"] = {"user_id": user2, "task": task2}

        user1_tasks = get_user_tasks(user1)
        assert len(user1_tasks) == 1
        assert "task1" in user1_tasks
        assert user1_tasks["task1"] == task1

    def test_truncate_output_normal(self):
        """Test normal output doesn't get truncated"""
        output = "Hello world"
        result = truncate_output(output)
        assert result == output

    def test_truncate_output_long(self):
        """Test long output gets truncated"""
        output = "x" * 35000
        result = truncate_output(output)
        assert len(result) <= 30000
        assert "[Output truncated" in result


class TestCollectCommandOutput:
    """Test command output collection"""

    @pytest.mark.asyncio
    async def test_collect_command_output_success(self, mock_session_manager):
        """Test successful command output collection"""

        # Mock the async generator
        async def mock_run_command(*args):
            chunk1 = MagicMock()
            chunk1.data = "Hello"
            chunk1.stream_type = "stdout"
            yield chunk1

            chunk2 = MagicMock()
            chunk2.data = "World"
            chunk2.stream_type = "stdout"
            yield chunk2

        mock_session_manager.run_command = mock_run_command

        result = await collect_command_output("session_id", "echo hello", 30)

        assert result["stdout"] == "Hello\nWorld"
        assert result["stderr"] == ""
        assert result["exit_code"] == 0

    @pytest.mark.asyncio
    async def test_collect_command_output_with_stderr(self, mock_session_manager):
        """Test command output with stderr"""

        async def mock_run_command(*args):
            chunk1 = MagicMock()
            chunk1.data = "Error occurred"
            chunk1.stream_type = "stderr"
            yield chunk1

        mock_session_manager.run_command = mock_run_command

        result = await collect_command_output("session_id", "error_command", 30)

        assert result["stdout"] == ""
        assert result["stderr"] == "Error occurred"
        assert result["exit_code"] == 0

    @pytest.mark.asyncio
    async def test_collect_command_output_timeout(self, mock_session_manager):
        """Test command timeout"""

        async def mock_run_command(*args):
            await asyncio.sleep(2)  # Sleep longer than timeout
            chunk = MagicMock()
            chunk.data = "Should not see this"
            yield chunk

        mock_session_manager.run_command = mock_run_command

        result = await collect_command_output("session_id", "slow_command", 0.1)

        assert "timed out" in result["stderr"]
        assert result["exit_code"] == -1

    @pytest.mark.asyncio
    async def test_collect_command_output_exception(self, mock_session_manager):
        """Test command execution exception"""

        async def mock_run_command(*args):
            raise Exception("Command failed")
            # This yield is never reached but makes it a proper async generator
            yield  # pragma: no cover

        mock_session_manager.run_command = mock_run_command

        result = await collect_command_output("session_id", "failing_command", 30)

        assert "Command failed" in result["stderr"]
        assert result["exit_code"] == -1


class TestBashTool:
    """Test the bash MCP tool"""

    @pytest.mark.asyncio
    async def test_bash_new_session(self, clean_state, mock_session_manager):
        """Test bash command creates new session"""
        with patch(
            "chuk_virtual_shell.mcp_server.get_user_id", return_value="test_user"
        ):
            result = await bash("pwd")

            assert result["session_id"] == "test_session_id"
            assert "test_session_id" in sessions
            assert sessions["test_session_id"].user_id == "test_user"
            mock_session_manager.create_session.assert_called_once()

    @pytest.mark.asyncio
    async def test_bash_existing_session(self, clean_state, mock_session_manager):
        """Test bash command with existing session"""
        user_id = "test_user"
        session_id = "existing_session"

        sessions[session_id] = SessionInfo(session_id, user_id)

        with patch("chuk_virtual_shell.mcp_server.get_user_id", return_value=user_id):
            with patch(
                "chuk_virtual_shell.mcp_server.collect_command_output"
            ) as mock_collect:
                mock_collect.return_value = {
                    "stdout": "output",
                    "stderr": "",
                    "exit_code": 0,
                }

                result = await bash("pwd", session_id=session_id)

                assert result["session_id"] == session_id
                mock_collect.assert_called_once_with(session_id, "pwd", 120.0)

    @pytest.mark.asyncio
    async def test_bash_access_denied(self, clean_state, mock_session_manager):
        """Test access denied for session belonging to different user"""
        sessions["other_session"] = SessionInfo("other_session", "other_user")

        with patch(
            "chuk_virtual_shell.mcp_server.get_user_id", return_value="current_user"
        ):
            result = await bash("pwd", session_id="other_session")

            assert result["error"] == "Access denied: Session belongs to another user"
            assert result["exit_code"] == -1

    @pytest.mark.asyncio
    async def test_bash_background_execution(self, clean_state, mock_session_manager):
        """Test background command execution"""
        with patch(
            "chuk_virtual_shell.mcp_server.get_user_id", return_value="test_user"
        ):
            result = await bash("sleep 5", run_in_background=True)

            assert "task_id" in result
            assert result["status"] == "running"
            assert result["task_id"] in background_tasks

            # Check that the task is properly stored
            task_info = background_tasks[result["task_id"]]
            assert task_info["user_id"] == "test_user"

    @pytest.mark.asyncio
    async def test_bash_timeout_validation(self, clean_state, mock_session_manager):
        """Test timeout validation"""
        with patch(
            "chuk_virtual_shell.mcp_server.get_user_id", return_value="test_user"
        ):
            with patch(
                "chuk_virtual_shell.mcp_server.collect_command_output"
            ) as mock_collect:
                mock_collect.return_value = {"stdout": "", "stderr": "", "exit_code": 0}

                # Test max timeout is enforced
                await bash("pwd", timeout=700000)  # 700 seconds

                # Should be capped at 600 seconds (600000 ms)
                mock_collect.assert_called_once()
                args = mock_collect.call_args[0]
                assert args[2] == 600.0  # timeout_seconds


class TestTaskManagement:
    """Test background task management"""

    @pytest.mark.asyncio
    async def test_get_task_output_running(self, clean_state):
        """Test getting output from running task"""
        user_id = "test_user"
        task_id = "test_task"

        # Create a running task
        task = AsyncMock()
        task.done = Mock(return_value=False)  # Use regular Mock for sync methods
        background_tasks[task_id] = {"user_id": user_id, "task": task}

        with patch("chuk_virtual_shell.mcp_server.get_user_id", return_value=user_id):
            result = await get_task_output(task_id)

            assert result["status"] == "running"
            assert result["message"] == "Task is still running"

    @pytest.mark.asyncio
    async def test_get_task_output_completed(self, clean_state):
        """Test getting output from completed task"""
        user_id = "test_user"
        task_id = "test_task"

        # Create a completed task that returns a coroutine we can await
        async def task_coro():
            return {"stdout": "Task completed", "stderr": "", "exit_code": 0}

        task = asyncio.create_task(task_coro())
        await task  # Complete the task

        background_tasks[task_id] = {"user_id": user_id, "task": task}

        with patch("chuk_virtual_shell.mcp_server.get_user_id", return_value=user_id):
            result = await get_task_output(task_id)

            assert result["status"] == "completed"
            assert result["stdout"] == "Task completed"
            assert result["stderr"] == ""
            assert result["exit_code"] == 0
            assert task_id not in background_tasks  # Should be cleaned up

    @pytest.mark.asyncio
    async def test_get_task_output_not_found(self, clean_state):
        """Test getting output from non-existent task"""
        with patch(
            "chuk_virtual_shell.mcp_server.get_user_id", return_value="test_user"
        ):
            result = await get_task_output("non_existent")

            assert "not found" in result["error"]
            assert "your_tasks" in result

    @pytest.mark.asyncio
    async def test_get_task_output_access_denied(self, clean_state):
        """Test access denied for task belonging to different user"""
        background_tasks["other_task"] = {"user_id": "other_user", "task": AsyncMock()}

        with patch(
            "chuk_virtual_shell.mcp_server.get_user_id", return_value="current_user"
        ):
            result = await get_task_output("other_task")

            assert result["error"] == "Access denied: Task belongs to another user"

    @pytest.mark.asyncio
    async def test_cancel_task_success(self, clean_state):
        """Test successful task cancellation"""
        user_id = "test_user"
        task_id = "test_task"

        # Create a running task
        async def long_running():
            await asyncio.sleep(10)  # Long task

        task = asyncio.create_task(long_running())
        background_tasks[task_id] = {"user_id": user_id, "task": task}

        with patch("chuk_virtual_shell.mcp_server.get_user_id", return_value=user_id):
            result = await cancel_task(task_id)

            assert result["success"] is True
            assert "cancelled successfully" in result["message"]
            assert task.cancelled()
            # Task should be removed from background_tasks
            assert task_id not in background_tasks

    @pytest.mark.asyncio
    async def test_cancel_task_already_done(self, clean_state):
        """Test cancelling already completed task"""
        user_id = "test_user"
        task_id = "test_task"

        # Create a completed task
        async def completed_task():
            return {"result": "done"}

        task = asyncio.create_task(completed_task())
        await task  # Complete the task

        background_tasks[task_id] = {"user_id": user_id, "task": task}

        with patch("chuk_virtual_shell.mcp_server.get_user_id", return_value=user_id):
            result = await cancel_task(task_id)

            assert result["success"] is False
            assert "already completed" in result["message"]


class TestSessionManagement:
    """Test session management tools"""

    @pytest.mark.asyncio
    async def test_list_sessions(self, clean_state, mock_session_manager):
        """Test listing user sessions"""
        user_id = "test_user"
        session_id = "test_session"

        sessions[session_id] = SessionInfo(session_id, user_id)
        sessions[session_id].last_command = "ls -la"

        with patch("chuk_virtual_shell.mcp_server.get_user_id", return_value=user_id):
            result = await list_sessions()

            assert result["total"] == 1
            assert result["user"] == user_id[:8] + "..."
            assert session_id in result["sessions"]
            assert result["sessions"][session_id]["last_command"] == "ls -la"

    @pytest.mark.asyncio
    async def test_destroy_session_success(self, clean_state):
        """Test successful session destruction"""
        user_id = "test_user"
        session_id = "test_session"

        sessions[session_id] = SessionInfo(session_id, user_id)

        with patch("chuk_virtual_shell.mcp_server.get_user_id", return_value=user_id):
            result = await destroy_session(session_id)

            assert result["success"] is True
            assert session_id not in sessions

    @pytest.mark.asyncio
    async def test_destroy_session_not_found(self, clean_state):
        """Test destroying non-existent session"""
        with patch(
            "chuk_virtual_shell.mcp_server.get_user_id", return_value="test_user"
        ):
            result = await destroy_session("non_existent")

            assert result["success"] is False
            assert "not found" in result["message"]

    @pytest.mark.asyncio
    async def test_destroy_session_access_denied(self, clean_state):
        """Test access denied for session belonging to different user"""
        sessions["other_session"] = SessionInfo("other_session", "other_user")

        with patch(
            "chuk_virtual_shell.mcp_server.get_user_id", return_value="current_user"
        ):
            result = await destroy_session("other_session")

            assert result["success"] is False
            assert "Access denied" in result["message"]

    @pytest.mark.asyncio
    async def test_get_session_state_success(self, clean_state, mock_session_manager):
        """Test getting session state"""
        user_id = "test_user"
        session_id = "test_session"

        sessions[session_id] = SessionInfo(session_id, user_id)
        sessions[session_id].last_command = "cd /test"

        # Mock the get_session method to return a session with the expected state
        mock_session = AsyncMock()
        mock_session.state.cwd = "/test/dir"
        mock_session.state.env = {"TEST_VAR": "test_value"}
        mock_session_manager.get_session = AsyncMock(return_value=mock_session)

        with patch("chuk_virtual_shell.mcp_server.get_user_id", return_value=user_id):
            result = await get_session_state(session_id)

            assert result["session_id"] == session_id
            assert result["working_directory"] == "/test/dir"
            assert result["last_command"] == "cd /test"
            assert "lifetime" in result

    @pytest.mark.asyncio
    async def test_get_session_state_not_found(self, clean_state):
        """Test getting state of non-existent session"""
        with patch(
            "chuk_virtual_shell.mcp_server.get_user_id", return_value="test_user"
        ):
            result = await get_session_state("non_existent")

            assert "not found" in result["error"]

    @pytest.mark.asyncio
    async def test_whoami(self, clean_state):
        """Test whoami tool"""
        user_id = "test_user_12345678"

        # Add some sessions and tasks for the user
        sessions["session1"] = SessionInfo("session1", user_id)
        sessions["session2"] = SessionInfo("session2", user_id)

        background_tasks["task1"] = {"user_id": user_id, "task": AsyncMock()}

        with patch("chuk_virtual_shell.mcp_server.get_user_id", return_value=user_id):
            result = await whoami()

            assert result["user_id"] == user_id[:8] + "..."
            assert result["session_count"] == 2
            assert result["task_count"] == 1
            assert result["isolation_mode"] == "user-based"


class TestCleanup:
    """Test cleanup functionality"""

    @pytest.mark.asyncio
    async def test_cleanup_cancels_tasks(self, clean_state):
        """Test cleanup cancels all background tasks"""

        # Create some real tasks
        async def long_task():
            await asyncio.sleep(10)

        async def quick_task():
            return "done"

        task1 = asyncio.create_task(long_task())
        task2 = asyncio.create_task(quick_task())
        await task2  # Complete task2

        background_tasks["task1"] = {"user_id": "user1", "task": task1}
        background_tasks["task2"] = {"user_id": "user2", "task": task2}

        await cleanup()

        # Running task should be cancelled
        assert task1.cancelled()
        # Completed task should remain completed
        assert task2.done()


class TestSessionInfo:
    """Test SessionInfo dataclass"""

    def test_session_info_creation(self):
        """Test SessionInfo creation with defaults"""
        session_info = SessionInfo("test_id", "test_user")

        assert session_info.session_id == "test_id"
        assert session_info.user_id == "test_user"
        assert session_info.working_directory == "/"
        assert session_info.environment == {}
        assert session_info.last_command is None
        assert isinstance(session_info.created_at, float)
        assert session_info.created_at <= time.time()

    def test_session_info_with_values(self):
        """Test SessionInfo with custom values"""
        env = {"TEST": "value"}
        session_info = SessionInfo(
            "test_id",
            "test_user",
            created_at=1234567890,
            last_command="ls -la",
            working_directory="/custom",
            environment=env,
        )

        assert session_info.created_at == 1234567890
        assert session_info.last_command == "ls -la"
        assert session_info.working_directory == "/custom"
        assert session_info.environment == env
