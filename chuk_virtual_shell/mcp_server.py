#!/usr/bin/env python3
"""
Virtual Shell MCP Server with User Isolation

Provides virtual shell execution capabilities to AI agents through MCP.
Uses the chuk-virtual-shell library for safe, sandboxed command execution.
Implements user-based session isolation for multi-user security.
"""

import asyncio
import hashlib
import os
import sys
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from chuk_mcp_server import ChukMCPServer  # type: ignore[import-not-found]
from chuk_virtual_shell.session import ShellSessionManager
from chuk_virtual_shell.shell_interpreter import ShellInterpreter

# Initialize the MCP server
mcp = ChukMCPServer("virtual-shell-mcp")

# Initialize the virtual shell session manager
session_manager = ShellSessionManager(shell_factory=lambda: ShellInterpreter())


# Store for session information with user isolation
@dataclass
class SessionInfo:
    """Information about a virtual shell session"""

    session_id: str
    user_id: str
    created_at: float = field(default_factory=time.time)
    last_command: str | None = None
    working_directory: str = "/"
    environment: dict[str, str] = field(default_factory=dict)


# User-isolated storage
sessions: dict[str, SessionInfo] = {}
background_tasks: dict[str, dict[str, Any]] = {}  # task_id -> {user_id, task}


def get_user_id() -> str:
    """
    Get a unique user identifier from the environment.
    This can be customized based on your authentication mechanism.
    """
    # Try different methods to identify the user
    user_id = None

    # Method 1: MCP context (if provided by the MCP client)
    user_id = os.environ.get("MCP_USER_ID")

    # Method 2: System user
    if not user_id:
        user_id = os.environ.get("USER") or os.environ.get("USERNAME")

    # Method 3: Session-based ID from MCP transport
    if not user_id:
        user_id = os.environ.get("MCP_SESSION_ID")

    # Method 4: Process-based isolation (each client process gets unique ID)
    if not user_id:
        # Use a combination of PID and hostname for uniqueness
        hostname = os.environ.get("HOSTNAME", "localhost")
        pid = os.getpid()
        user_id = f"{hostname}_{pid}"

    # Hash the user_id for privacy
    return hashlib.sha256(user_id.encode()).hexdigest()[:16]


def get_user_sessions(user_id: str) -> dict[str, SessionInfo]:
    """Get all sessions belonging to a specific user"""
    return {sid: info for sid, info in sessions.items() if info.user_id == user_id}


def get_user_tasks(user_id: str) -> dict[str, Any]:
    """Get all background tasks belonging to a specific user"""
    return {
        tid: task_info["task"]
        for tid, task_info in background_tasks.items()
        if task_info["user_id"] == user_id
    }


def truncate_output(output: str, max_chars: int = 30000) -> str:
    """Truncate output if it exceeds max_chars"""
    # Ensure output is a string
    if not isinstance(output, str):
        output = str(output) if output is not None else ""

    # Ensure max_chars is an int
    if not isinstance(max_chars, int):
        max_chars = int(max_chars) if max_chars else 30000

    if len(output) <= max_chars:
        return output

    truncated_msg = f"\n\n[Output truncated - exceeded {max_chars} characters]"
    return output[: max_chars - len(truncated_msg)] + truncated_msg


async def collect_command_output(
    session_id: str, command: str, timeout_seconds: float
) -> dict[str, Any]:
    """
    Collect output from the async generator returned by run_command.
    Returns a dict with stdout, stderr, and exit_code.
    """
    stdout_lines = []
    stderr_lines = []
    exit_code = 0

    try:
        # Wrap the async generator in wait_for for timeout
        async def collect():
            async for chunk in session_manager.run_command(session_id, command):
                # Extract data from StreamChunk
                if hasattr(chunk, "data"):
                    data = chunk.data
                    if hasattr(chunk, "stream_type"):
                        if chunk.stream_type == "stderr":
                            stderr_lines.append(data)
                        else:
                            stdout_lines.append(data)
                    else:
                        stdout_lines.append(data)

        await asyncio.wait_for(collect(), timeout=timeout_seconds)

    except TimeoutError:
        stderr_lines.append(f"Command timed out after {timeout_seconds} seconds")
        exit_code = -1
    except Exception as e:
        stderr_lines.append(str(e))
        exit_code = -1

    return {
        "stdout": "\n".join(stdout_lines) if stdout_lines else "",
        "stderr": "\n".join(stderr_lines) if stderr_lines else "",
        "exit_code": exit_code,
    }


@mcp.tool  # type: ignore[arg-type]
async def bash(
    command: str,
    session_id: str | None = None,
    timeout: int | None = 120000,
    run_in_background: bool = False,
    description: str | None = None,
) -> dict[str, Any]:
    """
    Execute a command in the virtual shell.
    Sessions are isolated per user - you can only access your own sessions.

    Args:
        command: The shell command to execute
        session_id: Optional session ID to use (creates new session if not provided)
        timeout: Optional timeout in milliseconds (max 600000ms / 10 minutes). Default is 120000ms (2 minutes)
        run_in_background: If True, run the command in the background and return immediately
        description: Clear, concise description of what this command does in 5-10 words

    Returns:
        Dictionary containing:
        - stdout: Standard output from the command
        - stderr: Standard error output from the command
        - exit_code: Exit code of the command (0 for success)
        - session_id: The session ID used for this command
        - working_directory: Current working directory after command execution
    """
    # Get user ID for isolation
    user_id = get_user_id()

    # Validate timeout - ensure it's an integer
    if timeout is not None:
        # Convert to int if it's a string
        if isinstance(timeout, str):
            try:
                timeout = int(timeout)
            except ValueError:
                timeout = 120000  # Default if conversion fails
        timeout = min(timeout, 600000)  # Cap at 10 minutes
        timeout_seconds = timeout / 1000.0
    else:
        timeout_seconds = 120.0  # Default 2 minutes

    try:
        # Create or get session (with user validation)
        if session_id and session_id in sessions:
            session_info = sessions[session_id]
            # Verify user owns this session
            if session_info.user_id != user_id:
                return {
                    "error": "Access denied: Session belongs to another user",
                    "exit_code": -1,
                }
        else:
            # Create new session for this user
            new_session_id = await session_manager.create_session()
            session_info = SessionInfo(session_id=new_session_id, user_id=user_id)
            sessions[new_session_id] = session_info
            session_id = new_session_id

        # Update last command
        session_info.last_command = command

        if run_in_background:
            # Create background task
            task_id = str(uuid.uuid4())[:8]

            async def run_background():
                try:
                    result = await collect_command_output(
                        session_id, command, timeout_seconds
                    )
                    return result
                except Exception as e:
                    return {"stdout": "", "stderr": str(e), "exit_code": -1}

            task = asyncio.create_task(run_background())
            background_tasks[task_id] = {
                "user_id": user_id,
                "task": task,
                "session_id": session_id,
            }

            return {
                "task_id": task_id,
                "session_id": session_id,
                "status": "running",
                "message": f"Command started in background with task ID: {task_id}",
            }
        else:
            # Run command and collect output
            result = await collect_command_output(session_id, command, timeout_seconds)

            # Get current state
            try:
                session = await session_manager.get_session(session_id)
                if session:
                    session_info.working_directory = session.state.cwd
                    session_info.environment = session.state.env
            except Exception:
                # If state retrieval fails, keep existing values
                pass

            # Truncate output if needed
            result["stdout"] = truncate_output(result["stdout"])
            result["stderr"] = truncate_output(result["stderr"])

            # Add session info to result
            result["session_id"] = session_id
            result["working_directory"] = session_info.working_directory

            return result

    except Exception as e:
        return {
            "stdout": "",
            "stderr": f"Error executing command: {str(e)}",
            "exit_code": -1,
            "session_id": session_id if session_id else None,
        }


@mcp.tool  # type: ignore[arg-type]
async def get_task_output(task_id: str, wait: bool = False) -> dict[str, Any]:
    """
    Retrieve output from a background task.
    You can only access tasks that you started.

    Args:
        task_id: The ID of the background task
        wait: If True, wait for the task to complete before returning

    Returns:
        Dictionary containing:
        - stdout: Standard output from the command
        - stderr: Standard error output from the command
        - exit_code: Exit code if completed
        - status: Current status (running/completed/failed)
    """
    user_id = get_user_id()

    if task_id not in background_tasks:
        # Only show user's own tasks
        user_tasks = [
            tid for tid, t in background_tasks.items() if t["user_id"] == user_id
        ]
        return {"error": f"Task ID '{task_id}' not found", "your_tasks": user_tasks}

    task_info = background_tasks[task_id]

    # Verify user owns this task
    if task_info["user_id"] != user_id:
        return {
            "error": "Access denied: Task belongs to another user",
            "your_tasks": [
                tid for tid, t in background_tasks.items() if t["user_id"] == user_id
            ],
        }

    task = task_info["task"]

    if wait or task.done():
        try:
            result = await task
            # Remove from background tasks
            del background_tasks[task_id]

            result["status"] = "completed"
            return result
        except Exception as e:
            del background_tasks[task_id]
            return {"stdout": "", "stderr": str(e), "exit_code": -1, "status": "failed"}
    else:
        return {"status": "running", "message": "Task is still running"}


@mcp.tool  # type: ignore[arg-type]
async def cancel_task(task_id: str) -> dict[str, Any]:
    """
    Cancel a running background task.
    You can only cancel tasks that you started.

    Args:
        task_id: The ID of the background task to cancel

    Returns:
        Dictionary containing:
        - success: Whether the task was successfully cancelled
        - message: Status message
    """
    user_id = get_user_id()

    if task_id not in background_tasks:
        user_tasks = [
            tid for tid, t in background_tasks.items() if t["user_id"] == user_id
        ]
        return {
            "success": False,
            "message": f"Task ID '{task_id}' not found",
            "your_tasks": user_tasks,
        }

    task_info = background_tasks[task_id]

    # Verify user owns this task
    if task_info["user_id"] != user_id:
        return {
            "success": False,
            "message": "Access denied: Task belongs to another user",
        }

    task = task_info["task"]

    if task.done():
        return {"success": False, "message": f"Task '{task_id}' has already completed"}

    try:
        task.cancel()
        await asyncio.sleep(0.1)  # Give it a moment to cancel
        del background_tasks[task_id]

        return {"success": True, "message": f"Task '{task_id}' cancelled successfully"}
    except Exception as e:
        return {"success": False, "message": f"Error cancelling task: {str(e)}"}


@mcp.tool  # type: ignore[arg-type]
async def list_sessions() -> dict[str, Any]:
    """
    List all virtual shell sessions for the current user.
    You can only see your own sessions.

    Returns:
        Dictionary containing information about your sessions
    """
    user_id = get_user_id()
    user_sessions = get_user_sessions(user_id)
    session_info = {}

    for sid, info in user_sessions.items():
        # Get current state from session manager
        try:
            session = await session_manager.get_session(sid)
            if session:
                session_info[sid] = {
                    "created_at": info.created_at,
                    "lifetime": time.time() - info.created_at,
                    "last_command": info.last_command,
                    "working_directory": session.state.cwd,
                    "environment_vars": len(session.state.env),
                    "active": True,  # Session exists so it's active
                }
            else:
                session_info[sid] = {
                    "created_at": info.created_at,
                    "lifetime": time.time() - info.created_at,
                    "last_command": info.last_command,
                    "working_directory": info.working_directory,
                    "active": False,
                }
        except Exception:
            session_info[sid] = {
                "created_at": info.created_at,
                "lifetime": time.time() - info.created_at,
                "last_command": info.last_command,
                "working_directory": info.working_directory,
                "active": False,
            }

    # Count user's background tasks
    user_task_count = sum(
        1 for t in background_tasks.values() if t["user_id"] == user_id
    )

    return {
        "sessions": session_info,
        "total": len(user_sessions),
        "active": sum(1 for s in session_info.values() if s.get("active", False)),
        "background_tasks": user_task_count,
        "user": user_id[:8] + "...",  # Show partial user ID for confirmation
    }


@mcp.tool  # type: ignore[arg-type]
async def destroy_session(session_id: str) -> dict[str, Any]:
    """
    Destroy a virtual shell session.
    You can only destroy your own sessions.

    Args:
        session_id: The ID of the session to destroy

    Returns:
        Dictionary containing:
        - success: Whether the session was successfully destroyed
        - message: Status message
    """
    user_id = get_user_id()

    if session_id not in sessions:
        user_sessions = get_user_sessions(user_id)
        return {
            "success": False,
            "message": f"Session '{session_id}' not found",
            "your_sessions": list(user_sessions.keys()),
        }

    session_info = sessions[session_id]

    # Verify user owns this session
    if session_info.user_id != user_id:
        user_sessions = get_user_sessions(user_id)
        return {
            "success": False,
            "message": "Access denied: Session belongs to another user",
            "your_sessions": list(user_sessions.keys()),
        }

    try:
        # Note: ShellSessionManager doesn't have destroy_session, sessions auto-expire
        del sessions[session_id]

        return {
            "success": True,
            "message": f"Session '{session_id}' removed successfully",
        }
    except Exception as e:
        return {"success": False, "message": f"Error removing session: {str(e)}"}


@mcp.tool  # type: ignore[arg-type]
async def get_session_state(session_id: str) -> dict[str, Any]:
    """
    Get the current state of a virtual shell session.
    You can only access your own sessions.

    Args:
        session_id: The ID of the session

    Returns:
        Dictionary containing:
        - working_directory: Current working directory
        - environment: Environment variables
        - session info: Creation time and other metadata
    """
    user_id = get_user_id()

    if session_id not in sessions:
        user_sessions = get_user_sessions(user_id)
        return {
            "error": f"Session '{session_id}' not found",
            "your_sessions": list(user_sessions.keys()),
        }

    session_info = sessions[session_id]

    # Verify user owns this session
    if session_info.user_id != user_id:
        user_sessions = get_user_sessions(user_id)
        return {
            "error": "Access denied: Session belongs to another user",
            "your_sessions": list(user_sessions.keys()),
        }

    try:
        session = await session_manager.get_session(session_id)
        if not session:
            return {"error": f"Session '{session_id}' not found or expired"}

        return {
            "session_id": session_id,
            "working_directory": session.state.cwd,
            "environment": session.state.env,
            "created_at": session_info.created_at,
            "lifetime": time.time() - session_info.created_at,
            "last_command": session_info.last_command,
            "user": user_id[:8] + "...",  # Show partial user ID
        }
    except Exception as e:
        return {"error": f"Error getting session state: {str(e)}"}


@mcp.tool  # type: ignore[arg-type]
async def whoami() -> dict[str, Any]:
    """
    Get information about the current user context.

    Returns:
        Dictionary containing:
        - user_id: Your unique user identifier (partial)
        - session_count: Number of your active sessions
        - task_count: Number of your background tasks
    """
    user_id = get_user_id()
    user_sessions = get_user_sessions(user_id)
    user_task_count = sum(
        1 for t in background_tasks.values() if t["user_id"] == user_id
    )

    return {
        "user_id": user_id[:8] + "...",  # Show partial ID for privacy
        "session_count": len(user_sessions),
        "task_count": user_task_count,
        "isolation_mode": "user-based",
        "info": "You can only access your own sessions and tasks",
    }


async def cleanup():
    """Clean up resources on exit"""
    # Cancel all background tasks
    for task_id, task_info in background_tasks.items():
        task = task_info["task"]
        if not task.done():
            task.cancel()

    # Wait for tasks to complete cancellation
    if background_tasks:
        all_tasks = [t["task"] for t in background_tasks.values()]
        await asyncio.gather(*all_tasks, return_exceptions=True)


def main():
    """Main entry point for the MCP server"""
    try:
        # Run the server using stdio
        mcp.run(stdio=True)
    except KeyboardInterrupt:
        print("\nServer interrupted", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
