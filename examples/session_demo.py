#!/usr/bin/env python
"""
Demo of shell session management with persistent state.
"""

import asyncio
from chuk_virtual_shell.session import ShellSessionManager, SessionMode
from chuk_virtual_shell.shell_interpreter import ShellInterpreter


async def main():
    """Demonstrate session-based shell execution."""

    # Create session manager
    def shell_factory():
        return ShellInterpreter()

    manager = ShellSessionManager(shell_factory=shell_factory)

    print("=== Shell Session Demo ===\n")

    # Create a session
    session_id = await manager.create_session(mode=SessionMode.PIPE)
    print(f"Created session: {session_id}\n")

    # Run commands that share state
    commands = [
        "pwd",
        "mkdir /project",
        "cd /project",
        "pwd",
        "echo 'Hello World' > README.md",
        "ls -la",
        "export MY_VAR=test123",
        "env | grep MY_VAR",
    ]

    for cmd in commands:
        print(f"$ {cmd}")
        async for chunk in manager.run_command(session_id, cmd):
            if chunk.data:
                print(chunk.data)
        print()

    # Get session info
    session = await manager.get_session(session_id)
    if session:
        state = session.get_state()
        print("Session state:")
        print(f"  Working directory: {state.cwd}")
        print(f"  Environment vars: {len(state.env)} defined")
        print(f"  Command history: {len(state.history)} commands")
        print(f"  Last commands: {state.history[-3:]}")

    # Clean up
    await manager.close_session(session_id)
    print(f"\nClosed session: {session_id}")


async def streaming_demo():
    """Demonstrate streaming output with sequence IDs and timeouts."""

    def shell_factory():
        return ShellInterpreter()

    manager = ShellSessionManager(shell_factory=shell_factory)

    print("\n=== Streaming Output Demo ===\n")

    session_id = await manager.create_session()

    # Create many files to simulate long output
    print("Creating test files...")
    async for _ in manager.run_command(session_id, "mkdir -p /data"):
        pass

    for i in range(50):
        async for _ in manager.run_command(session_id, f"touch /data/file{i:03d}.txt"):
            pass

    # Stream output with sequence IDs
    print("\nStreaming ls output with sequence IDs:")
    seq_count = 0
    async for chunk in manager.run_command(session_id, "ls -la /data"):
        print(f"[Seq {chunk.sequence_id:3d}] {chunk.data[:50]}...")
        seq_count = chunk.sequence_id
    print(f"Total sequences received: {seq_count}")

    # Demonstrate timeout (simulated - would timeout with real long-running command)
    print("\nDemonstrating timeout handling:")
    print("Running command with 100ms timeout (simulated)...")
    try:
        # In real usage, this would be a long-running command
        async for chunk in manager.run_command(
            session_id, "echo 'Command completed quickly'", timeout_ms=100
        ):
            print(f"  Output: {chunk.data.strip()}")
    except asyncio.TimeoutError:
        print("  Command timed out as expected!")

    await manager.close_session(session_id)


async def multi_session_demo():
    """Demonstrate multiple isolated sessions."""

    def shell_factory():
        return ShellInterpreter()

    manager = ShellSessionManager(shell_factory=shell_factory)

    print("\n=== Multi-Session Demo ===\n")

    # Create multiple sessions
    session1 = await manager.create_session()
    session2 = await manager.create_session()

    print(f"Session 1: {session1}")
    print(f"Session 2: {session2}\n")

    # Set different environments
    print("Setting up session 1 (development):")
    async for chunk in manager.run_command(session1, "export ENV=development"):
        pass
    async for chunk in manager.run_command(session1, "mkdir /dev-project"):
        pass
    async for chunk in manager.run_command(session1, "cd /dev-project"):
        pass

    print("Setting up session 2 (production):")
    async for chunk in manager.run_command(session2, "export ENV=production"):
        pass
    async for chunk in manager.run_command(session2, "mkdir /prod-project"):
        pass
    async for chunk in manager.run_command(session2, "cd /prod-project"):
        pass

    # Verify isolation
    print("\nVerifying session isolation:")

    print("Session 1 environment:")
    async for chunk in manager.run_command(session1, "pwd"):
        print(f"  Working dir: {chunk.data.strip()}")
    async for chunk in manager.run_command(session1, "env | grep ENV"):
        print(f"  Environment: {chunk.data.strip()}")

    print("Session 2 environment:")
    async for chunk in manager.run_command(session2, "pwd"):
        print(f"  Working dir: {chunk.data.strip()}")
    async for chunk in manager.run_command(session2, "env | grep ENV"):
        print(f"  Environment: {chunk.data.strip()}")

    # Clean up
    await manager.close_session(session1)
    await manager.close_session(session2)
    print("\nClosed both sessions")


if __name__ == "__main__":
    # Run all demos
    asyncio.run(main())
    asyncio.run(streaming_demo())
    asyncio.run(multi_session_demo())
