"""
Agent definition parser and manager for AI agents in the shell.
"""

import yaml
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum


class IOMode(Enum):
    """Input/Output modes for agents"""
    STDIN = "stdin"
    STDOUT = "stdout"
    FILE = "file"
    SOCKET = "socket"
    PIPE = "pipe"


class MemoryMode(Enum):
    """Memory persistence modes for agents"""
    NONE = "none"
    SESSION = "session"
    PERSISTENT = "persistent"


@dataclass
class AgentDefinition:
    """Definition of an AI agent"""
    name: str
    model: str = "gpt-3.5-turbo"
    system_prompt: str = ""
    tools: List[str] = field(default_factory=list)
    input_mode: IOMode = IOMode.STDIN
    output_mode: IOMode = IOMode.STDOUT
    context_size: int = 4096
    memory_mode: MemoryMode = MemoryMode.SESSION
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    environment: Dict[str, str] = field(default_factory=dict)
    timeout: Optional[int] = None  # seconds
    
    @classmethod
    def from_file(cls, file_path: str, fs) -> 'AgentDefinition':
        """Load agent definition from a file"""
        content = fs.read_file(file_path)
        if content is None:
            raise FileNotFoundError(f"Agent file not found: {file_path}")
        
        return cls.from_string(content)
    
    @classmethod
    def from_string(cls, content: str) -> 'AgentDefinition':
        """Parse agent definition from a string"""
        lines = content.strip().split('\n')
        
        # Check for agent shebang
        if not lines[0].startswith('#!agent'):
            raise ValueError("Invalid agent file: missing #!agent shebang")
        
        # Remove shebang and parse rest as YAML
        yaml_content = '\n'.join(lines[1:])
        
        try:
            data = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid agent YAML: {e}")
        
        # Parse and validate fields
        name = data.get('name', 'unnamed_agent')
        model = data.get('model', 'gpt-3.5-turbo')
        system_prompt = data.get('system_prompt', '')
        tools = data.get('tools', [])
        
        # Parse I/O modes
        input_str = data.get('input', 'stdin')
        output_str = data.get('output', 'stdout')
        
        try:
            input_mode = IOMode(input_str)
        except ValueError:
            input_mode = IOMode.STDIN
            
        try:
            output_mode = IOMode(output_str)
        except ValueError:
            output_mode = IOMode.STDOUT
        
        # Parse memory mode
        memory_str = data.get('memory', 'session')
        try:
            memory_mode = MemoryMode(memory_str)
        except ValueError:
            memory_mode = MemoryMode.SESSION
        
        context_size = data.get('context_size', 4096)
        temperature = data.get('temperature', 0.7)
        max_tokens = data.get('max_tokens')
        environment = data.get('environment', {})
        timeout = data.get('timeout')
        
        return cls(
            name=name,
            model=model,
            system_prompt=system_prompt,
            tools=tools,
            input_mode=input_mode,
            output_mode=output_mode,
            context_size=context_size,
            memory_mode=memory_mode,
            temperature=temperature,
            max_tokens=max_tokens,
            environment=environment,
            timeout=timeout
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'name': self.name,
            'model': self.model,
            'system_prompt': self.system_prompt,
            'tools': self.tools,
            'input': self.input_mode.value,
            'output': self.output_mode.value,
            'context_size': self.context_size,
            'memory': self.memory_mode.value,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'environment': self.environment,
            'timeout': self.timeout
        }