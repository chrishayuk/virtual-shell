"""
Agent system for the virtual shell.
"""

from .agent_definition import AgentDefinition, IOMode, MemoryMode
from .agent_process import AgentProcess, AgentProcessManager, ProcessState
from .llm_interface import LLMInterface

__all__ = [
    "AgentDefinition",
    "IOMode",
    "MemoryMode",
    "AgentProcess",
    "AgentProcessManager",
    "ProcessState",
    "LLMInterface",
]
