"""
Agent command for running AI agents as shell processes.
"""

import asyncio
import argparse
import time
from typing import Optional

from chuk_virtual_shell.commands.command_base import ShellCommand
from chuk_virtual_shell.agents.agent_definition import AgentDefinition
from chuk_virtual_shell.agents.agent_process import AgentProcessManager, ProcessState
from chuk_virtual_shell.agents.cleanup import track_task, suppress_cleanup_warnings

# Suppress warnings on import
suppress_cleanup_warnings()


class AgentCommand(ShellCommand):
    """Execute AI agents as shell processes"""
    
    name = "agent"
    help_text = (
        "agent - Run AI agents as shell processes\n"
        "Usage: agent <agent_file> [options]\n"
        "       agent -l | --list     List running agents\n"
        "       agent -k <pid>        Kill an agent process\n"
        "       agent -s <pid>        Show agent status\n"
        "\n"
        "Options:\n"
        "  -b, --background    Run agent in background\n"
        "  -i, --input FILE    Read input from file\n"
        "  -o, --output FILE   Write output to file\n"
        "  -t, --timeout SEC   Set execution timeout\n"
        "\n"
        "Examples:\n"
        "  agent assistant.agent                    # Run agent\n"
        "  agent analyzer.agent < data.txt          # Pipe input\n"
        "  echo 'hello' | agent chat.agent          # Pipe from command\n"
        "  agent monitor.agent -b                   # Run in background\n"
        "  agent -l                                 # List agents\n"
        "  agent -k agent_1                         # Kill agent"
    )
    category = "system"
    
    def __init__(self, shell_context):
        """Initialize the agent command"""
        super().__init__(shell_context)
        
        # Initialize process manager if not exists
        if not hasattr(self.shell, 'agent_manager'):
            self.shell.agent_manager = AgentProcessManager(self.shell)
    
    def execute(self, args):
        """Execute the agent command synchronously"""
        # Use a new event loop to avoid conflicts
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.execute_async(args))
        finally:
            # Cancel all pending tasks
            pending = asyncio.all_tasks(loop)
            for task in pending:
                task.cancel()
            
            # Wait for cancellation to complete
            if pending:
                loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            
            # Close the loop
            try:
                loop.close()
            except:
                pass
    
    async def execute_async(self, args):
        """Execute the agent command asynchronously"""
        parser = argparse.ArgumentParser(prog='agent', add_help=False)
        
        # Add arguments
        parser.add_argument('agent_file', nargs='?', help='Agent definition file')
        parser.add_argument('-l', '--list', action='store_true', help='List running agents')
        parser.add_argument('-k', '--kill', metavar='PID', help='Kill an agent process')
        parser.add_argument('-s', '--status', metavar='PID', help='Show agent status')
        parser.add_argument('-b', '--background', action='store_true', help='Run in background')
        parser.add_argument('-i', '--input', metavar='FILE', help='Input file')
        parser.add_argument('-o', '--output', metavar='FILE', help='Output file')
        parser.add_argument('-t', '--timeout', type=int, metavar='SEC', help='Timeout in seconds')
        
        # Parse arguments
        try:
            parsed_args, remaining = parser.parse_known_args(args.split() if isinstance(args, str) else args)
        except SystemExit:
            return "agent: invalid arguments"
        
        # Handle different modes
        if parsed_args.list:
            return self._list_agents()
        
        if parsed_args.kill:
            return self._kill_agent(parsed_args.kill)
        
        if parsed_args.status:
            return self._show_status(parsed_args.status)
        
        if not parsed_args.agent_file:
            return "agent: missing agent file\nUsage: agent <agent_file> [options]"
        
        # Load agent definition
        try:
            # Check if it's a path to an agent file or inline definition
            agent_path = parsed_args.agent_file
            
            # First check if it's an actual file
            if self.shell.fs.exists(agent_path):
                definition = AgentDefinition.from_file(agent_path, self.shell.fs)
            else:
                # Try with .agent extension
                agent_path_with_ext = f"{agent_path}.agent"
                if self.shell.fs.exists(agent_path_with_ext):
                    definition = AgentDefinition.from_file(agent_path_with_ext, self.shell.fs)
                else:
                    return f"agent: cannot open '{parsed_args.agent_file}': No such file"
            
            # Override timeout if specified
            if parsed_args.timeout:
                definition.timeout = parsed_args.timeout
            
        except Exception as e:
            return f"agent: error loading agent definition: {e}"
        
        # Get input data
        input_data = ""
        
        # Check for piped input
        if hasattr(self.shell, '_pipe_input') and self.shell._pipe_input:
            input_data = self.shell._pipe_input
            self.shell._pipe_input = None  # Clear pipe input
        
        # Check for input file
        elif parsed_args.input:
            content = self.shell.fs.read_file(parsed_args.input)
            if content is None:
                return f"agent: cannot read input file '{parsed_args.input}'"
            input_data = content
        
        # Create and run process
        process = self.shell.agent_manager.create_process(
            definition,
            background=parsed_args.background
        )
        
        if parsed_args.background:
            # Run in background
            task = asyncio.create_task(
                self._run_background_safe(process, input_data)
            )
            process.task = task
            track_task(task)  # Track for cleanup
            return f"[{process.pid}] Agent '{definition.name}' started in background"
        else:
            # Run in foreground
            result = await self.shell.agent_manager.run_process(process, input_data)
            
            # Handle output redirection
            if parsed_args.output:
                self.shell.fs.write_file(parsed_args.output, result)
                return f"Output written to {parsed_args.output}"
            
            return result
    
    def _list_agents(self) -> str:
        """List all agent processes"""
        processes = self.shell.agent_manager.list_processes()
        
        if not processes:
            return "No agents running"
        
        lines = ["PID       NAME            STATE      RUNTIME"]
        lines.append("-" * 50)
        
        for proc in processes:
            runtime = f"{proc.get_runtime():.1f}s"
            lines.append(
                f"{proc.pid:<10} {proc.definition.name[:15]:<15} "
                f"{proc.state.value:<10} {runtime}"
            )
        
        return "\n".join(lines)
    
    def _kill_agent(self, pid: str) -> str:
        """Kill an agent process"""
        if self.shell.agent_manager.kill_process(pid):
            return f"Agent process {pid} terminated"
        return f"No such agent process: {pid}"
    
    async def _run_background_safe(self, process, input_data):
        """Run a process in background with safe cleanup"""
        try:
            result = await self.shell.agent_manager.run_process(process, input_data)
            return result
        except asyncio.CancelledError:
            # Silently handle cancellation
            process.state = ProcessState.TERMINATED
            return None
        except Exception as e:
            # Handle errors gracefully
            process.state = ProcessState.FAILED
            process.error_buffer = str(e)
            return None
    
    async def _run_background_process(self, process, input_data):
        """Legacy background process runner"""
        return await self._run_background_safe(process, input_data)
    
    def _show_status(self, pid: str) -> str:
        """Show detailed status of an agent"""
        process = self.shell.agent_manager.get_process(pid)
        
        if not process:
            return f"No such agent process: {pid}"
        
        lines = [
            f"Agent Process: {pid}",
            f"Name: {process.definition.name}",
            f"Model: {process.definition.model}",
            f"State: {process.state.value}",
            f"Runtime: {process.get_runtime():.1f}s",
            f"Background: {process.background}",
        ]
        
        if process.input_buffer:
            lines.append(f"Input: {process.input_buffer[:100]}...")
        
        if process.output_buffer:
            lines.append(f"Output: {process.output_buffer[:100]}...")
        
        if process.error_buffer:
            lines.append(f"Error: {process.error_buffer}")
        
        return "\n".join(lines)