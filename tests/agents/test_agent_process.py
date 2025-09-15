"""
Tests for agent process management.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch

from chuk_virtual_shell.agents.agent_definition import AgentDefinition
from chuk_virtual_shell.agents.agent_process import (
    AgentProcess,
    AgentProcessManager,
    ProcessState,
)
from chuk_virtual_shell.shell_interpreter import ShellInterpreter


class TestAgentProcess:
    """Test agent process functionality"""

    def test_process_creation(self):
        """Test creating an agent process"""
        definition = AgentDefinition(name="test_agent", model="gpt-3.5-turbo")

        process = AgentProcess(pid="test_1", definition=definition)

        assert process.pid == "test_1"
        assert process.definition.name == "test_agent"
        assert process.state == ProcessState.PENDING
        assert not process.background
        assert process.input_buffer == ""
        assert process.output_buffer == ""
        assert process.error_buffer == ""

    def test_process_auto_pid(self):
        """Test that process generates PID if not provided"""
        definition = AgentDefinition(name="test")
        process = AgentProcess(pid="", definition=definition)

        assert process.pid.startswith("agent_")
        assert len(process.pid) > 6

    def test_process_runtime(self):
        """Test calculating process runtime"""
        import time

        definition = AgentDefinition(name="test")
        process = AgentProcess(pid="test", definition=definition)

        # Not started yet
        assert process.get_runtime() == 0.0

        # Running
        process.start_time = time.time() - 5.0
        runtime = process.get_runtime()
        assert 4.9 < runtime < 5.1

        # Completed
        process.start_time = time.time() - 10.0
        process.end_time = time.time() - 2.0
        runtime = process.get_runtime()
        assert 7.9 < runtime < 8.1

    def test_process_is_active(self):
        """Test checking if process is active"""
        definition = AgentDefinition(name="test")
        process = AgentProcess(pid="test", definition=definition)

        # Pending - not active
        assert not process.is_active()

        # Running - active
        process.state = ProcessState.RUNNING
        assert process.is_active()

        # Suspended - active
        process.state = ProcessState.SUSPENDED
        assert process.is_active()

        # Completed - not active
        process.state = ProcessState.COMPLETED
        assert not process.is_active()

        # Failed - not active
        process.state = ProcessState.FAILED
        assert not process.is_active()

    def test_process_terminate(self):
        """Test terminating a process"""
        definition = AgentDefinition(name="test")
        process = AgentProcess(pid="test", definition=definition)

        # Create a mock task
        mock_task = Mock()
        mock_task.done.return_value = False
        process.task = mock_task

        process.state = ProcessState.RUNNING
        process.terminate()

        assert process.state == ProcessState.TERMINATED
        assert process.end_time is not None
        mock_task.cancel.assert_called_once()


class TestAgentProcessManager:
    """Test agent process manager"""

    def setup_method(self):
        """Set up test environment"""
        self.shell = ShellInterpreter()
        self.manager = AgentProcessManager(self.shell)

    def test_create_process(self):
        """Test creating a process through manager"""
        definition = AgentDefinition(name="test_agent", model="gpt-3.5-turbo")

        process = self.manager.create_process(definition)

        assert process.pid == "agent_1"
        assert process.definition.name == "test_agent"
        assert not process.background
        assert process in self.manager.processes.values()

        # Create another process
        process2 = self.manager.create_process(definition, background=True)
        assert process2.pid == "agent_2"
        assert process2.background

    def test_list_processes(self):
        """Test listing processes"""
        # No processes initially
        assert self.manager.list_processes() == []

        # Create some processes
        def1 = AgentDefinition(name="agent1")
        def2 = AgentDefinition(name="agent2")

        proc1 = self.manager.create_process(def1)
        proc2 = self.manager.create_process(def2)

        processes = self.manager.list_processes()
        assert len(processes) == 2
        assert proc1 in processes
        assert proc2 in processes

    def test_get_process(self):
        """Test getting process by PID"""
        definition = AgentDefinition(name="test")
        process = self.manager.create_process(definition)

        # Get existing process
        retrieved = self.manager.get_process(process.pid)
        assert retrieved == process

        # Get non-existent process
        assert self.manager.get_process("nonexistent") is None

    def test_kill_process(self):
        """Test killing a process"""
        definition = AgentDefinition(name="test")
        process = self.manager.create_process(definition)
        process.state = ProcessState.RUNNING

        # Kill existing process
        assert self.manager.kill_process(process.pid)
        assert process.state == ProcessState.TERMINATED

        # Try to kill non-existent process
        assert not self.manager.kill_process("nonexistent")

        # Try to kill already terminated process
        assert not self.manager.kill_process(process.pid)

    def test_cleanup_completed(self):
        """Test cleaning up completed processes"""
        # Create processes in various states
        definitions = [AgentDefinition(name=f"agent{i}") for i in range(5)]

        proc1 = self.manager.create_process(definitions[0])
        proc1.state = ProcessState.COMPLETED

        proc2 = self.manager.create_process(definitions[1])
        proc2.state = ProcessState.RUNNING

        proc3 = self.manager.create_process(definitions[2])
        proc3.state = ProcessState.FAILED

        proc4 = self.manager.create_process(definitions[3])
        proc4.state = ProcessState.TERMINATED

        proc5 = self.manager.create_process(definitions[4])
        proc5.state = ProcessState.PENDING

        # Should have 5 processes
        assert len(self.manager.processes) == 5

        # Cleanup completed
        self.manager.cleanup_completed()

        # Should have 2 processes left (RUNNING and PENDING)
        assert len(self.manager.processes) == 2
        assert proc2.pid in self.manager.processes
        assert proc5.pid in self.manager.processes

    @pytest.mark.asyncio
    async def test_run_process_success(self):
        """Test successfully running a process"""
        definition = AgentDefinition(name="test_agent", system_prompt="Test prompt")

        process = self.manager.create_process(definition)

        # Mock the LLM interface
        with patch.object(
            self.manager.llm_interface, "generate", new_callable=AsyncMock
        ) as mock_generate:
            mock_generate.return_value = "Test response"

            result = await self.manager.run_process(process, "Test input")

            assert result == "Test response"
            assert process.state == ProcessState.COMPLETED
            assert process.input_buffer == "Test input"
            assert process.output_buffer == "Test response"
            assert len(process.context) == 3  # system, user, assistant

    @pytest.mark.asyncio
    async def test_run_process_timeout(self):
        """Test process timeout"""
        definition = AgentDefinition(
            name="test_agent",
            timeout=1,  # 1 second timeout
        )

        process = self.manager.create_process(definition)

        # Mock the LLM to take too long
        async def slow_generate(*args, **kwargs):
            await asyncio.sleep(2)
            return "Should not get here"

        with patch.object(
            self.manager.llm_interface, "generate", side_effect=slow_generate
        ):
            result = await self.manager.run_process(process, "Test")

            assert "timed out" in result
            assert process.state == ProcessState.FAILED
            assert "timed out" in process.error_buffer

    @pytest.mark.asyncio
    async def test_run_process_with_tools(self):
        """Test running process with tools"""
        definition = AgentDefinition(name="test_agent", tools=["ls", "echo"])

        process = self.manager.create_process(definition)

        # Mock the LLM interface
        with patch.object(
            self.manager.llm_interface, "generate", new_callable=AsyncMock
        ) as mock_generate:
            mock_generate.return_value = "Used tools"

            result = await self.manager.run_process(process, "List files")

            # Check that tools were passed to generate
            call_args = mock_generate.call_args
            assert call_args.kwargs["tools"] is not None
            assert len(call_args.kwargs["tools"]) == 2
            assert call_args.kwargs["tool_executor"] is not None

    def test_get_tools(self):
        """Test getting tool definitions"""
        # Add some commands to shell
        self.shell.commands = {"ls": Mock(), "cat": Mock(), "echo": Mock()}

        tools = self.manager._get_tools(["ls", "echo", "nonexistent"])

        assert len(tools) == 2
        assert tools[0]["name"] == "ls"
        assert tools[1]["name"] == "echo"
        assert "parameters" in tools[0]

    def test_create_tool_executor(self):
        """Test creating tool executor"""
        definition = AgentDefinition(name="test")
        process = self.manager.create_process(definition)

        executor = self.manager._create_tool_executor(process)

        # Mock shell execute
        with patch.object(self.shell, "execute", return_value="Command output"):
            result = executor("ls", {"args": "-la"})
            assert result == "Command output"
            self.shell.execute.assert_called_with("ls -la")

        # Test unknown tool
        result = executor("unknown_tool", {})
        assert "Unknown tool" in result
