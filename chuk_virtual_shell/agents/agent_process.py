"""
Agent process manager for running AI agents as shell processes.
"""

import asyncio
import time
import uuid
import logging
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, field
from enum import Enum
import json

from .agent_definition import AgentDefinition, MemoryMode
from .llm_interface import LLMInterface

logger = logging.getLogger(__name__)


class ProcessState(Enum):
    """States an agent process can be in"""

    PENDING = "pending"
    RUNNING = "running"
    SUSPENDED = "suspended"
    COMPLETED = "completed"
    FAILED = "failed"
    TERMINATED = "terminated"


@dataclass
class AgentProcess:
    """Represents a running agent process"""

    pid: str  # Process ID
    definition: AgentDefinition
    state: ProcessState = ProcessState.PENDING
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    input_buffer: str = ""
    output_buffer: str = ""
    error_buffer: str = ""
    context: List[Dict[str, str]] = field(default_factory=list)
    memory: Dict[str, Any] = field(default_factory=dict)
    background: bool = False
    task: Optional[asyncio.Task] = None

    def __post_init__(self):
        """Initialize process ID if not provided"""
        if not self.pid:
            self.pid = f"agent_{uuid.uuid4().hex[:8]}"

    def get_runtime(self) -> float:
        """Get the runtime of the process in seconds"""
        if self.start_time is None:
            return 0.0
        end = self.end_time if self.end_time else time.time()
        return end - self.start_time

    def is_active(self) -> bool:
        """Check if process is in an active state"""
        return self.state in [ProcessState.RUNNING, ProcessState.SUSPENDED]

    def terminate(self):
        """Terminate the process"""
        if self.task:
            if not self.task.done():
                self.task.cancel()
            # Don't wait for cancellation here, just mark as terminated
        self.state = ProcessState.TERMINATED
        self.end_time = time.time()


class AgentProcessManager:
    """Manages running agent processes"""

    def __init__(self, shell_context):
        """Initialize the process manager"""
        self.shell = shell_context
        self.processes: Dict[str, AgentProcess] = {}
        self.llm_interface = LLMInterface()
        self.next_pid = 1

    def create_process(
        self, definition: AgentDefinition, background: bool = False
    ) -> AgentProcess:
        """Create a new agent process"""
        pid = f"agent_{self.next_pid}"
        self.next_pid += 1

        process = AgentProcess(pid=pid, definition=definition, background=background)

        self.processes[pid] = process
        return process

    async def run_process(self, process: AgentProcess, input_data: str = "") -> str:
        """Run an agent process"""
        process.state = ProcessState.RUNNING
        process.start_time = time.time()
        process.input_buffer = input_data

        try:
            # Initialize context with system prompt
            if process.definition.system_prompt:
                process.context.append(
                    {"role": "system", "content": process.definition.system_prompt}
                )

            # Add input as user message
            if input_data:
                process.context.append({"role": "user", "content": input_data})

            # Load memory if needed
            if process.definition.memory_mode == MemoryMode.PERSISTENT:
                process.memory = self._load_memory(process.definition.name)
            elif process.definition.memory_mode == MemoryMode.SESSION:
                # Session memory is kept in the process object
                pass

            # Execute with timeout if specified
            if process.definition.timeout:
                result = await asyncio.wait_for(
                    self._execute_agent(process), timeout=process.definition.timeout
                )
            else:
                result = await self._execute_agent(process)

            process.output_buffer = result
            process.state = ProcessState.COMPLETED

            # Save memory if persistent
            if process.definition.memory_mode == MemoryMode.PERSISTENT:
                self._save_memory(process.definition.name, process.memory)

            return result

        except asyncio.TimeoutError:
            process.state = ProcessState.FAILED
            process.error_buffer = (
                f"Agent execution timed out after {process.definition.timeout} seconds"
            )
            return process.error_buffer

        except asyncio.CancelledError:
            # Handle cancellation gracefully
            process.state = ProcessState.TERMINATED
            process.error_buffer = "Process was cancelled"
            return "Process cancelled"

        except Exception as e:
            process.state = ProcessState.FAILED
            process.error_buffer = str(e)
            logger.error(f"Agent process {process.pid} failed: {e}")
            return f"Agent error: {e}"

        finally:
            process.end_time = time.time()

    async def _execute_agent(self, process: AgentProcess) -> str:
        """Execute the agent logic"""
        # Get available tools for this agent
        tools = self._get_tools(process.definition.tools)

        # Call LLM with context and tools
        response = await self.llm_interface.generate(
            model=process.definition.model,
            messages=process.context,
            temperature=process.definition.temperature,
            max_tokens=process.definition.max_tokens,
            tools=tools,
            tool_executor=self._create_tool_executor(process),
        )

        # Add response to context
        process.context.append({"role": "assistant", "content": response})

        return response

    def _get_tools(self, tool_names: List[str]) -> List[Dict[str, Any]]:
        """Get tool definitions for the specified tools"""
        tools = []

        for tool_name in tool_names:
            # Check if it's a shell command
            if tool_name in self.shell.commands:
                tools.append(
                    {
                        "name": tool_name,
                        "description": f"Execute {tool_name} shell command",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "args": {
                                    "type": "string",
                                    "description": "Arguments for the command",
                                }
                            },
                        },
                    }
                )
            # Could add more tool types here (MCP tools, custom functions, etc.)

        return tools

    def _create_tool_executor(self, process: AgentProcess) -> Callable:
        """Create a tool executor function for this process"""

        def execute_tool(tool_name: str, args: Dict[str, Any]) -> str:
            """Execute a tool and return the result"""
            # Execute shell commands
            if tool_name in self.shell.commands:
                command_args = args.get("args", "")
                result = self.shell.execute(f"{tool_name} {command_args}")
                return result

            return f"Unknown tool: {tool_name}"

        return execute_tool

    def _load_memory(self, agent_name: str) -> Dict[str, Any]:
        """Load persistent memory for an agent"""
        memory_file = f"/var/agent_memory/{agent_name}.json"

        if self.shell.fs.exists(memory_file):
            content = self.shell.fs.read_file(memory_file)
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {}

        return {}

    def _save_memory(self, agent_name: str, memory: Dict[str, Any]):
        """Save persistent memory for an agent"""
        memory_dir = "/var/agent_memory"

        # Ensure directory exists
        if not self.shell.fs.exists(memory_dir):
            self.shell.fs.mkdir(memory_dir)

        memory_file = f"{memory_dir}/{agent_name}.json"
        self.shell.fs.write_file(memory_file, json.dumps(memory, indent=2))

    def list_processes(self) -> List[AgentProcess]:
        """List all agent processes"""
        return list(self.processes.values())

    def get_process(self, pid: str) -> Optional[AgentProcess]:
        """Get a process by PID"""
        return self.processes.get(pid)

    def kill_process(self, pid: str) -> bool:
        """Kill a process by PID"""
        process = self.processes.get(pid)
        if process and process.is_active():
            process.terminate()
            return True
        return False

    def cleanup_completed(self):
        """Remove completed processes from the manager"""
        completed_pids = [
            pid
            for pid, proc in self.processes.items()
            if proc.state
            in [ProcessState.COMPLETED, ProcessState.FAILED, ProcessState.TERMINATED]
        ]

        for pid in completed_pids:
            proc = self.processes[pid]
            # Cancel task if still exists
            if proc.task and not proc.task.done():
                proc.task.cancel()
            del self.processes[pid]

    def cleanup_all(self):
        """Clean up all processes"""
        for pid, proc in list(self.processes.items()):
            if proc.is_active():
                proc.terminate()
        self.cleanup_completed()
