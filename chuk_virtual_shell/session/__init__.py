"""
Shell session management module.

Provides stateful shell sessions with PTY support, streaming output,
and process management.
"""

from .shell_session import (
    ShellSession,
    ShellSessionManager,
    ShellSessionState,
    SessionMode,
    CommandState,
    CommandResult,
    StreamChunk,
)

__all__ = [
    "ShellSession",
    "ShellSessionManager",
    "ShellSessionState",
    "SessionMode",
    "CommandState",
    "CommandResult",
    "StreamChunk",
]
