#!/usr/bin/env python3
"""
Clean demonstration of AI agents without async warnings.
"""

import os
import sys
import warnings
import asyncio
import signal
from pathlib import Path
from dotenv import load_dotenv

# Suppress all async-related warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", message=".*Event loop.*")
warnings.filterwarnings("ignore", message=".*Task.*")
warnings.filterwarnings("ignore", message=".*was destroyed.*")

# Redirect stderr to suppress httpx cleanup messages

from chuk_virtual_shell.shell_interpreter import ShellInterpreter
from chuk_virtual_shell.agents.cleanup import suppress_cleanup_warnings

# Apply cleanup suppression
suppress_cleanup_warnings()


def setup_environment():
    """Load environment variables from .env file"""
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        return os.getenv("OPENAI_API_KEY") is not None
    return False


def run_demo():
    """Run clean agent demonstration"""

    # Create new event loop for clean execution
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    shell = ShellInterpreter()

    print("\n🤖 AI Agent Shell Demo\n")
    print("=" * 50)

    # Create directories
    shell.execute("mkdir -p /agents")
    shell.execute("mkdir -p /workspace")

    # Create a simple assistant agent
    agent_def = """#!agent
name: assistant
model: gpt-3.5-turbo
system_prompt: |
  You are a helpful AI assistant.
  Be concise and clear in your responses.
  You can use shell commands to help users.
tools:
  - ls
  - cat
  - echo
  - pwd
input: stdin
output: stdout
temperature: 0.7
max_tokens: 150
timeout: 10
"""

    shell.fs.write_file("/agents/assistant.agent", agent_def)
    print("✓ Created AI assistant agent\n")

    # Create test files
    shell.fs.write_file("/workspace/hello.txt", "Hello, AI World!")
    shell.fs.write_file("/workspace/data.txt", "Sample data for analysis")

    # Check if using real LLM
    is_real = (
        hasattr(shell, "agent_manager")
        and not shell.agent_manager.llm_interface.mock_mode
    )
    mode = "REAL LLM (OpenAI)" if is_real else "MOCK MODE"
    print(f"Mode: {mode}\n")
    print("=" * 50 + "\n")

    # Demo interactions
    demos = [
        ("Simple Chat", "Hello, can you help me?"),
        ("File Query", "What files are in /workspace?"),
        ("Task Request", "Create a simple Python hello world script"),
    ]

    for title, prompt in demos:
        print(f"📝 {title}")
        print(f"   User: {prompt}")
        shell._pipe_input = prompt

        # Capture output with timeout
        try:
            result = shell.execute("agent /agents/assistant.agent")
            # Truncate long responses
            if len(result) > 200:
                result = result[:197] + "..."
            print(f"   Agent: {result}\n")
        except Exception as e:
            print(f"   Error: {e}\n")

    # File I/O demo
    print("📁 File I/O Demo")
    shell.fs.write_file("/workspace/question.txt", "What is Python?")
    print("   Input: 'What is Python?' (from file)")

    try:
        shell.execute(
            "agent /agents/assistant.agent -i /workspace/question.txt -o /workspace/answer.txt"
        )
        if shell.fs.exists("/workspace/answer.txt"):
            answer = shell.fs.read_file("/workspace/answer.txt")
            if len(answer) > 150:
                answer = answer[:147] + "..."
            print(f"   Output: {answer}\n")
    except Exception as e:
        print(f"   Error: {e}\n")

    # Process management
    print("⚙️ Process Management")

    # Start background agent
    shell._pipe_input = "Background task"
    result = shell.execute("agent /agents/assistant.agent -b")
    print(f"   {result}")

    # List agents
    result = shell.execute("agent -l")
    lines = result.split("\n")[:5]  # Show first 5 lines
    for line in lines:
        print(f"   {line}")

    print("\n" + "=" * 50)
    print("\n✅ Demo Complete!\n")

    # Cleanup
    if hasattr(shell, "agent_manager"):
        shell.agent_manager.cleanup_all()

    # Close event loop properly
    try:
        loop = asyncio.get_event_loop()
        if loop and not loop.is_closed():
            # Cancel remaining tasks
            pending = asyncio.all_tasks(loop)
            for task in pending:
                task.cancel()
            # Wait briefly for cancellation
            loop.run_until_complete(asyncio.sleep(0.1))
            loop.close()
    except Exception:
        pass

    return 0


def main():
    """Main entry point with proper cleanup"""

    # Set up signal handlers for clean exit
    def signal_handler(sig, frame):
        print("\n\nExiting cleanly...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("\n🚀 Starting AI Agent Demo (Clean Version)")

    # Check environment
    has_api_key = setup_environment()
    if has_api_key:
        print("✓ OpenAI API key loaded")
    else:
        print("⚠ No API key found - will use mock mode")

    # Run demo
    try:
        result = run_demo()
        return result
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        return 1
    except RuntimeError as e:
        # Ignore "Event loop is closed" errors
        if "Event loop is closed" not in str(e):
            print(f"\nError: {e}")
            return 1
        return 0
    except Exception as e:
        print(f"\nError: {e}")
        return 1
    finally:
        # Suppress any remaining warnings during exit
        warnings.filterwarnings("ignore")
        import logging

        logging.disable(logging.CRITICAL)


if __name__ == "__main__":
    sys.exit(main())
