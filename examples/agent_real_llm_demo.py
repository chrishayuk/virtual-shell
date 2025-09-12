#!/usr/bin/env python3
"""
Demonstration of AI agents with real LLM (OpenAI).
"""

import os
import warnings
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Suppress warnings about event loops
warnings.filterwarnings("ignore", message="There is no current event loop")
warnings.filterwarnings("ignore", message="Task exception was never retrieved")
warnings.filterwarnings("ignore", category=RuntimeWarning)

from chuk_virtual_shell.shell_interpreter import ShellInterpreter


def setup_environment():
    """Load environment variables from .env file"""
    # Load .env file from the project root
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✓ Loaded environment from {env_path}")
        
        # Check if API key is loaded
        if os.getenv('OPENAI_API_KEY'):
            print("✓ OpenAI API key loaded from .env")
        else:
            print("⚠ OpenAI API key not found in .env")
    else:
        print(f"⚠ No .env file found at {env_path}")


def run_real_llm_demo():
    """Run demonstration with real LLM"""
    
    # Create shell instance
    shell = ShellInterpreter()
    
    print("\n=== AI Agent Demo with Real LLM ===\n")
    
    # Create directories
    shell.execute("mkdir -p /agents")
    shell.execute("mkdir -p /workspace")
    
    # Create a simple chat agent
    chat_agent = """#!agent
name: chat_assistant
model: gpt-3.5-turbo
system_prompt: |
  You are a helpful AI assistant in a virtual shell environment.
  Be concise and helpful. When asked about files or directories,
  you can use the ls and cat tools to explore the filesystem.
tools:
  - ls
  - cat
  - pwd
  - echo
input: stdin
output: stdout
memory: session
temperature: 0.7
max_tokens: 150
timeout: 10
"""
    
    shell.fs.write_file("/agents/chat.agent", chat_agent)
    print("✓ Created chat agent at /agents/chat.agent")
    
    # Create a code analyzer agent
    code_agent = """#!agent
name: code_helper
model: gpt-3.5-turbo
system_prompt: |
  You are a code analysis assistant. When given code,
  provide a brief analysis including:
  - Main purpose
  - Key functions/methods
  - Potential improvements (if any)
  Keep responses concise.
tools:
  - cat
  - grep
  - wc
input: stdin
output: stdout
temperature: 0.3
max_tokens: 200
timeout: 10
"""
    
    shell.fs.write_file("/agents/code.agent", code_agent)
    print("✓ Created code analyzer agent at /agents/code.agent")
    
    # Create test files
    shell.fs.write_file("/workspace/example.py", '''def fibonacci(n):
    """Calculate fibonacci number"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def main():
    for i in range(10):
        print(f"fib({i}) = {fibonacci(i)}")

if __name__ == "__main__":
    main()
''')
    
    shell.fs.write_file("/workspace/data.txt", """Sample Data File
================
This is a test file with some data.
It has multiple lines.
We can use it to test agent interactions.
""")
    
    print("✓ Created test files in /workspace\n")
    
    # Check if we're using mock or real LLM
    if hasattr(shell, 'agent_manager') and shell.agent_manager.llm_interface.mock_mode:
        print("⚠ Running in MOCK mode (chuk-llm not available or API key not set)")
        print("  To use real LLM, ensure:")
        print("  1. pip install chuk-llm")
        print("  2. OpenAI API key is in .env file")
    else:
        print("✓ Running with REAL LLM integration")
    
    print("\n" + "="*50 + "\n")
    
    # Demo 1: Simple question
    print("=== Demo 1: Simple Chat ===")
    print("Input: 'What can you help me with?'")
    shell._pipe_input = "What can you help me with?"
    result = shell.execute("agent /agents/chat.agent")
    print(f"Response: {result}\n")
    
    # Demo 2: File exploration
    print("=== Demo 2: File Exploration ===")
    print("Input: 'What files are in /workspace?'")
    shell._pipe_input = "What files are in /workspace?"
    result = shell.execute("agent /agents/chat.agent")
    print(f"Response: {result}\n")
    
    # Demo 3: Code analysis
    print("=== Demo 3: Code Analysis ===")
    print("Command: cat /workspace/example.py | agent /agents/code.agent")
    result = shell.execute("cat /workspace/example.py | agent /agents/code.agent")
    print(f"Analysis: {result}\n")
    
    # Demo 4: File I/O
    print("=== Demo 4: File-based I/O ===")
    shell.fs.write_file("/workspace/question.txt", 
                       "Can you explain what the fibonacci function does?")
    print("Created question file with: 'Can you explain what the fibonacci function does?'")
    
    print("Command: agent /agents/chat.agent -i /workspace/question.txt -o /workspace/answer.txt")
    result = shell.execute("agent /agents/chat.agent -i /workspace/question.txt -o /workspace/answer.txt")
    print(f"Result: {result}")
    
    if shell.fs.exists("/workspace/answer.txt"):
        answer = shell.fs.read_file("/workspace/answer.txt")
        print(f"Answer: {answer}\n")
    
    # Demo 5: Process management
    print("=== Demo 5: Process Management ===")
    
    # Start a background agent
    print("Starting background agent...")
    shell._pipe_input = "Process this in background"
    result = shell.execute("agent /agents/chat.agent -b")
    print(f"Result: {result}")
    
    # List agents
    print("\nListing all agents:")
    result = shell.execute("agent -l")
    print(result)
    
    # Get status of specific agent if any are running
    processes = shell.agent_manager.list_processes()
    if processes:
        pid = processes[0].pid
        print(f"\nStatus of {pid}:")
        result = shell.execute(f"agent -s {pid}")
        print(result)
    
    print("\n=== Demo Complete ===")
    
    if shell.agent_manager.llm_interface.mock_mode:
        print("\nNote: This demo ran in MOCK mode.")
        print("To use real OpenAI API:")
        print("1. Install: pip install chuk-llm")
        print("2. Ensure OPENAI_API_KEY is in .env file")
    else:
        print("\nThis demo used real LLM responses via OpenAI API.")
        print("Agents can now provide intelligent responses and use tools!")


def main():
    """Main entry point"""
    print("Setting up environment...")
    setup_environment()
    
    print("\nStarting Real LLM Agent Demo...")
    try:
        run_real_llm_demo()
    except Exception as e:
        print(f"\nError during demo: {e}")
        print("Make sure chuk-llm is installed: pip install chuk-llm")
    finally:
        # Clean up any pending async tasks
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.stop()
        except:
            pass


if __name__ == "__main__":
    main()