#!/usr/bin/env python3
"""
Advanced demonstration of AI agents with tool usage.
"""

import os
import warnings
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Suppress warnings
warnings.filterwarnings("ignore", message="There is no current event loop")
warnings.filterwarnings("ignore", message="Task exception was never retrieved")
warnings.filterwarnings("ignore", category=RuntimeWarning)

from chuk_virtual_shell.shell_interpreter import ShellInterpreter


def setup_environment():
    """Load environment variables from .env file"""
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print("✓ Environment loaded")
        if os.getenv("OPENAI_API_KEY"):
            print("✓ OpenAI API key found")
    else:
        print("⚠ No .env file found")


def run_advanced_demo():
    """Run advanced agent demonstration"""

    shell = ShellInterpreter()

    print("\n=== Advanced AI Agent Demo ===\n")

    # Create directories
    shell.execute("mkdir -p /agents")
    shell.execute("mkdir -p /project/src")
    shell.execute("mkdir -p /project/tests")
    shell.execute("mkdir -p /data")

    # Create a smart file manager agent
    file_manager_agent = """#!agent
name: file_manager
model: gpt-3.5-turbo
system_prompt: |
  You are a file management assistant. When asked about files:
  1. Use 'ls' to list directories
  2. Use 'cat' to read file contents
  3. Use 'echo' to create simple files
  4. Use 'touch' to create empty files
  5. Use 'mkdir' to create directories
  Always execute the appropriate tool to fulfill the request.
  When using tools, format as: TOOL[command](arguments)
tools:
  - ls
  - cat
  - echo
  - touch
  - mkdir
  - pwd
  - rm
input: stdin
output: stdout
temperature: 0.3
max_tokens: 200
timeout: 15
"""

    # Create a code generator agent
    code_generator_agent = """#!agent
name: code_generator
model: gpt-3.5-turbo
system_prompt: |
  You are a code generation assistant. When asked to create code:
  1. Generate clean, well-commented code
  2. Use 'echo' or 'cat' to save code to files
  3. Follow best practices for the language requested
  Format tool usage as: TOOL[command](arguments)
tools:
  - echo
  - cat
  - touch
input: stdin
output: stdout
temperature: 0.5
max_tokens: 500
timeout: 15
"""

    # Create a data analyzer agent
    data_analyzer_agent = """#!agent
name: data_analyzer
model: gpt-3.5-turbo
system_prompt: |
  You are a data analysis assistant. When given data:
  1. Use 'wc' to count lines, words, characters
  2. Use 'grep' to search for patterns
  3. Use 'sort' to organize data
  4. Use 'head' and 'tail' to preview data
  Provide insights based on the analysis.
  Format tool usage as: TOOL[command](arguments)
tools:
  - cat
  - wc
  - grep
  - sort
  - uniq
  - head
  - tail
input: stdin
output: stdout
temperature: 0.3
max_tokens: 300
timeout: 15
"""

    # Save agents
    shell.fs.write_file("/agents/file_manager.agent", file_manager_agent)
    shell.fs.write_file("/agents/code_generator.agent", code_generator_agent)
    shell.fs.write_file("/agents/data_analyzer.agent", data_analyzer_agent)
    print("✓ Created advanced agents\n")

    # Create sample data
    shell.fs.write_file(
        "/project/README.md",
        """# Sample Project
This is a demonstration project for AI agents.

## Features
- File management
- Code generation
- Data analysis
""",
    )

    shell.fs.write_file(
        "/data/numbers.csv",
        """value,category
10,A
25,B
15,A
30,B
20,A
35,B
""",
    )

    shell.fs.write_file(
        "/data/log.txt",
        """2024-01-01 10:00:00 INFO Application started
2024-01-01 10:00:05 DEBUG Loading configuration
2024-01-01 10:00:10 INFO Connected to database
2024-01-01 10:00:15 WARNING High memory usage detected
2024-01-01 10:00:20 ERROR Failed to connect to API
2024-01-01 10:00:25 INFO Retrying connection
2024-01-01 10:00:30 INFO Connection successful
""",
    )

    print("✓ Created sample data\n")

    # Check LLM mode
    is_mock = (
        hasattr(shell, "agent_manager") and shell.agent_manager.llm_interface.mock_mode
    )
    if is_mock:
        print("⚠ Running in MOCK mode - responses are simulated\n")
    else:
        print("✓ Running with REAL LLM - OpenAI GPT-3.5\n")

    print("=" * 60 + "\n")

    # Demo 1: File Manager Agent
    print("=== Demo 1: File Manager Agent ===")
    print("Task: 'List all files in the /project directory'")
    shell._pipe_input = "Please list all files in the /project directory"
    result = shell.execute("agent /agents/file_manager.agent")
    print(f"Response:\n{result}\n")

    # Demo 2: Code Generator Agent
    print("=== Demo 2: Code Generator Agent ===")
    print("Task: 'Create a simple Python hello world function'")
    shell._pipe_input = "Create a simple Python function that prints hello world"
    result = shell.execute("agent /agents/code_generator.agent")
    print(f"Response:\n{result}\n")

    # Demo 3: Data Analyzer Agent
    print("=== Demo 3: Data Analyzer Agent ===")
    print("Command: cat /data/log.txt | agent /agents/data_analyzer.agent")
    print("Task: Analyze the log file")
    result = shell.execute("cat /data/log.txt | agent /agents/data_analyzer.agent")
    print(f"Analysis:\n{result}\n")

    # Demo 4: Agent Pipeline
    print("=== Demo 4: Agent Pipeline (Mock Only) ===")
    print("Create file → Analyze it")

    # First create a file with the file manager
    shell.fs.write_file(
        "/data/request.txt",
        "Create a file called test.py with a function that adds two numbers",
    )
    shell.execute(
        "agent /agents/code_generator.agent -i /data/request.txt -o /project/src/test.py"
    )

    # Then analyze what was created
    if shell.fs.exists("/project/src/test.py"):
        content = shell.fs.read_file("/project/src/test.py")
        print(f"Generated file content:\n{content[:200]}...\n")

    # Demo 5: Parallel Agents
    print("=== Demo 5: Parallel Agent Execution ===")

    # Launch multiple agents in parallel
    cmds = [
        "agent /agents/file_manager.agent -b -i /data/request.txt",
        "agent /agents/data_analyzer.agent -b -i /data/numbers.csv",
    ]

    print("Launching agents in parallel:")
    for cmd in cmds:
        result = shell.execute(cmd)
        print(f"  {result}")

    print("\nActive agents:")
    result = shell.execute("agent -l")
    print(result)

    # Clean up
    processes = shell.agent_manager.list_processes()
    for proc in processes:
        if proc.is_active():
            shell.execute(f"agent -k {proc.pid}")

    print("\n" + "=" * 60)
    print("\n=== Advanced Demo Complete ===\n")

    print("Key Concepts Demonstrated:")
    print("  ✓ Specialized agents with different roles")
    print("  ✓ Tool usage for file operations")
    print("  ✓ Data analysis capabilities")
    print("  ✓ Code generation")
    print("  ✓ Parallel agent execution")
    print("  ✓ Agent pipelines")

    if not is_mock:
        print("\n💡 With real LLM integration, agents can:")
        print("  • Understand natural language requests")
        print("  • Execute appropriate shell commands")
        print("  • Provide intelligent analysis")
        print("  • Generate code and content")
        print("  • Work together in pipelines")


def main():
    """Main entry point"""
    print("Starting Advanced Agent Demo...")
    setup_environment()

    try:
        run_advanced_demo()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        # Cleanup
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.stop()
        except Exception:
            pass


if __name__ == "__main__":
    main()
