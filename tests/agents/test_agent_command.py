"""
Tests for the agent command.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch

from chuk_virtual_shell.shell_interpreter import ShellInterpreter
from chuk_virtual_shell.commands.system.agent import AgentCommand
from chuk_virtual_shell.agents.agent_process import ProcessState


class TestAgentCommand:
    """Test the agent shell command"""
    
    def setup_method(self):
        """Set up test environment"""
        self.shell = ShellInterpreter()
        self.command = AgentCommand(self.shell)
        
        # Create test agent file
        agent_content = """#!agent
name: test_agent
model: gpt-3.5-turbo
system_prompt: Test agent
tools:
  - ls
  - echo
input: stdin
output: stdout
"""
        self.shell.fs.write_file("/test.agent", agent_content)
    
    def test_command_initialization(self):
        """Test that command initializes properly"""
        assert self.command.name == "agent"
        assert self.command.category == "system"
        assert hasattr(self.shell, 'agent_manager')
        assert self.shell.agent_manager is not None
    
    def test_missing_agent_file(self):
        """Test error when agent file is missing"""
        result = self.command.execute("")
        assert "missing agent file" in result
        
        result = self.command.execute("nonexistent.agent")
        assert "No such file" in result
    
    def test_load_agent_file(self):
        """Test loading an agent file"""
        with patch.object(self.shell.agent_manager, 'run_process', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = "Agent response"
            
            result = self.command.execute("/test.agent")
            
            assert result == "Agent response"
            mock_run.assert_called_once()
    
    def test_load_agent_with_extension(self):
        """Test loading agent file without extension"""
        with patch.object(self.shell.agent_manager, 'run_process', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = "Agent response"
            
            # Should find /test.agent even without extension
            result = self.command.execute("/test")
            
            assert result == "Agent response"
            mock_run.assert_called_once()
    
    def test_background_execution(self):
        """Test running agent in background"""
        with patch.object(self.shell.agent_manager, 'run_process', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = "Background result"
            
            result = self.command.execute("/test.agent -b")
            
            assert "started in background" in result
            assert "test_agent" in result
    
    def test_list_agents(self):
        """Test listing running agents"""
        # Create some mock processes
        mock_proc1 = Mock()
        mock_proc1.pid = "agent_1"
        mock_proc1.definition.name = "test_agent"
        mock_proc1.state = ProcessState.RUNNING
        mock_proc1.get_runtime.return_value = 10.5
        
        mock_proc2 = Mock()
        mock_proc2.pid = "agent_2"
        mock_proc2.definition.name = "analyzer"
        mock_proc2.state = ProcessState.COMPLETED
        mock_proc2.get_runtime.return_value = 5.2
        
        with patch.object(self.shell.agent_manager, 'list_processes', return_value=[mock_proc1, mock_proc2]):
            result = self.command.execute("-l")
            
            assert "agent_1" in result
            assert "test_agent" in result
            assert "running" in result  # Lowercase in output
            assert "10.5s" in result
            assert "agent_2" in result
            assert "analyzer" in result
            assert "completed" in result  # Lowercase in output
    
    def test_list_agents_empty(self):
        """Test listing when no agents are running"""
        with patch.object(self.shell.agent_manager, 'list_processes', return_value=[]):
            result = self.command.execute("-l")
            assert "No agents running" in result
    
    def test_kill_agent(self):
        """Test killing an agent process"""
        with patch.object(self.shell.agent_manager, 'kill_process', return_value=True):
            result = self.command.execute("-k agent_1")
            assert "terminated" in result
            assert "agent_1" in result
        
        with patch.object(self.shell.agent_manager, 'kill_process', return_value=False):
            result = self.command.execute("-k nonexistent")
            assert "No such agent process" in result
    
    def test_show_status(self):
        """Test showing agent status"""
        mock_proc = Mock()
        mock_proc.pid = "agent_1"
        mock_proc.definition.name = "test_agent"
        mock_proc.definition.model = "gpt-3.5-turbo"
        mock_proc.state = ProcessState.RUNNING
        mock_proc.background = True
        mock_proc.get_runtime.return_value = 15.3
        mock_proc.input_buffer = "Test input"
        mock_proc.output_buffer = "Test output that is very long and should be truncated"
        mock_proc.error_buffer = ""
        
        with patch.object(self.shell.agent_manager, 'get_process', return_value=mock_proc):
            result = self.command.execute("-s agent_1")
            
            assert "agent_1" in result
            assert "test_agent" in result
            assert "gpt-3.5-turbo" in result
            assert "running" in result  # Lowercase in output
            assert "15.3s" in result
            assert "Background: True" in result
            assert "Input:" in result
            assert "Output:" in result
    
    def test_show_status_not_found(self):
        """Test showing status of non-existent agent"""
        with patch.object(self.shell.agent_manager, 'get_process', return_value=None):
            result = self.command.execute("-s nonexistent")
            assert "No such agent process" in result
    
    def test_input_file(self):
        """Test reading input from file"""
        self.shell.fs.write_file("/input.txt", "Input from file")
        
        with patch.object(self.shell.agent_manager, 'run_process', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = "Processed input"
            
            result = self.command.execute("/test.agent -i /input.txt")
            
            assert result == "Processed input"
            # Check that input was passed
            call_args = mock_run.call_args
            assert call_args[0][1] == "Input from file"
    
    def test_output_file(self):
        """Test writing output to file"""
        with patch.object(self.shell.agent_manager, 'run_process', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = "Agent output"
            
            result = self.command.execute("/test.agent -o /output.txt")
            
            assert "Output written to /output.txt" in result
            # Check file was written
            content = self.shell.fs.read_file("/output.txt")
            assert content == "Agent output"
    
    def test_timeout_option(self):
        """Test setting timeout via command line"""
        with patch.object(self.shell.agent_manager, 'create_process') as mock_create:
            mock_proc = Mock()
            mock_proc.task = None
            mock_create.return_value = mock_proc
            
            with patch.object(self.shell.agent_manager, 'run_process', new_callable=AsyncMock) as mock_run:
                mock_run.return_value = "Result"
                
                result = self.command.execute("/test.agent -t 30")
                
                # Check that definition was modified
                call_args = mock_create.call_args
                definition = call_args[0][0]
                assert definition.timeout == 30
    
    def test_piped_input(self):
        """Test handling piped input"""
        # Simulate piped input
        self.shell._pipe_input = "Piped data"
        
        with patch.object(self.shell.agent_manager, 'run_process', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = "Processed piped data"
            
            result = self.command.execute("/test.agent")
            
            assert result == "Processed piped data"
            # Check that piped input was passed
            call_args = mock_run.call_args
            assert call_args[0][1] == "Piped data"
            # Check that pipe input was cleared
            assert self.shell._pipe_input is None
    
    def test_invalid_arguments(self):
        """Test handling invalid arguments"""
        result = self.command.execute("--invalid-flag")
        # --invalid-flag is treated as agent file name, not a flag
        assert "missing agent file" in result or "No such file" in result
    
    def test_help_text(self):
        """Test that help text is comprehensive"""
        help_text = self.command.get_help()
        
        assert "agent" in help_text
        assert "AI agents" in help_text
        assert "-l" in help_text
        assert "-k" in help_text
        assert "-s" in help_text
        assert "-b" in help_text
        assert "Examples:" in help_text