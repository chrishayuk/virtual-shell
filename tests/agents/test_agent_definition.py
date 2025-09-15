"""
Tests for agent definition parsing and management.
"""

import pytest
from chuk_virtual_shell.agents.agent_definition import (
    AgentDefinition,
    IOMode,
    MemoryMode,
)
from chuk_virtual_fs import VirtualFileSystem
from chuk_virtual_shell.filesystem_compat import FileSystemCompat


class TestAgentDefinition:
    """Test agent definition parsing"""

    def setup_method(self):
        """Set up test environment"""
        raw_fs = VirtualFileSystem()
        self.fs = FileSystemCompat(raw_fs)

    def test_parse_basic_agent(self):
        """Test parsing a basic agent definition"""
        agent_content = """#!agent
name: test_agent
model: gpt-3.5-turbo
system_prompt: Test prompt
tools:
  - ls
  - cat
input: stdin
output: stdout
memory: session
temperature: 0.7
"""

        agent = AgentDefinition.from_string(agent_content)

        assert agent.name == "test_agent"
        assert agent.model == "gpt-3.5-turbo"
        assert agent.system_prompt == "Test prompt"
        assert agent.tools == ["ls", "cat"]
        assert agent.input_mode == IOMode.STDIN
        assert agent.output_mode == IOMode.STDOUT
        assert agent.memory_mode == MemoryMode.SESSION
        assert agent.temperature == 0.7

    def test_parse_agent_with_defaults(self):
        """Test parsing agent with minimal definition"""
        agent_content = """#!agent
name: minimal_agent
"""

        agent = AgentDefinition.from_string(agent_content)

        assert agent.name == "minimal_agent"
        assert agent.model == "gpt-3.5-turbo"  # default
        assert agent.system_prompt == ""
        assert agent.tools == []
        assert agent.input_mode == IOMode.STDIN
        assert agent.output_mode == IOMode.STDOUT
        assert agent.memory_mode == MemoryMode.SESSION
        assert agent.temperature == 0.7

    def test_parse_agent_with_environment(self):
        """Test parsing agent with environment variables"""
        agent_content = """#!agent
name: env_agent
environment:
  API_KEY: test_key
  DEBUG: "true"
timeout: 60
max_tokens: 1000
"""

        agent = AgentDefinition.from_string(agent_content)

        assert agent.name == "env_agent"
        assert agent.environment == {"API_KEY": "test_key", "DEBUG": "true"}
        assert agent.timeout == 60
        assert agent.max_tokens == 1000

    def test_agent_without_shebang_works(self):
        """Test that agent without shebang works (shebang is optional)"""
        agent_content = """name: no_shebang_agent
model: gpt-3.5-turbo
system_prompt: Test agent
"""

        # Should not raise an error (shebang is optional)
        agent = AgentDefinition.from_string(agent_content)
        assert agent.name == "no_shebang_agent"
        assert agent.model == "gpt-3.5-turbo"
        assert agent.system_prompt == "Test agent"

    def test_invalid_yaml(self):
        """Test that invalid YAML raises error"""
        agent_content = """#!agent
name: bad_agent
model: [this is: invalid yaml
"""

        with pytest.raises(ValueError, match="Invalid agent YAML"):
            AgentDefinition.from_string(agent_content)

    def test_from_file(self):
        """Test loading agent from file"""
        agent_content = """#!agent
name: file_agent
model: gpt-4
tools:
  - echo
  - pwd
"""

        self.fs.write_file("/test.agent", agent_content)

        agent = AgentDefinition.from_file("/test.agent", self.fs)

        assert agent.name == "file_agent"
        assert agent.model == "gpt-4"
        assert agent.tools == ["echo", "pwd"]

    def test_from_file_not_found(self):
        """Test loading non-existent file raises error"""
        with pytest.raises(FileNotFoundError):
            AgentDefinition.from_file("/nonexistent.agent", self.fs)

    def test_to_dict(self):
        """Test converting agent to dictionary"""
        agent = AgentDefinition(
            name="test_agent",
            model="gpt-3.5-turbo",
            system_prompt="Test",
            tools=["ls"],
            input_mode=IOMode.FILE,
            output_mode=IOMode.SOCKET,
            memory_mode=MemoryMode.PERSISTENT,
            temperature=0.5,
            max_tokens=500,
        )

        data = agent.to_dict()

        assert data["name"] == "test_agent"
        assert data["model"] == "gpt-3.5-turbo"
        assert data["system_prompt"] == "Test"
        assert data["tools"] == ["ls"]
        assert data["input"] == "file"
        assert data["output"] == "socket"
        assert data["memory"] == "persistent"
        assert data["temperature"] == 0.5
        assert data["max_tokens"] == 500

    def test_memory_modes(self):
        """Test different memory modes"""
        for mode_str, mode_enum in [
            ("none", MemoryMode.NONE),
            ("session", MemoryMode.SESSION),
            ("persistent", MemoryMode.PERSISTENT),
        ]:
            agent_content = f"""#!agent
name: memory_test
memory: {mode_str}
"""
            agent = AgentDefinition.from_string(agent_content)
            assert agent.memory_mode == mode_enum

    def test_io_modes(self):
        """Test different I/O modes"""
        for io_str, io_enum in [
            ("stdin", IOMode.STDIN),
            ("stdout", IOMode.STDOUT),
            ("file", IOMode.FILE),
            ("socket", IOMode.SOCKET),
            ("pipe", IOMode.PIPE),
        ]:
            agent_content = f"""#!agent
name: io_test
input: {io_str}
output: {io_str}
"""
            agent = AgentDefinition.from_string(agent_content)
            assert agent.input_mode == IOMode(io_str)
            assert agent.output_mode == IOMode(io_str)
