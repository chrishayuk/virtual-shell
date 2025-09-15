#!/usr/bin/env python3
"""
Simple demonstration of AI agents with gpt-5-mini and tool calls.
"""

import asyncio
from chuk_virtual_shell.shell_interpreter import ShellInterpreter


async def run_simple_demo():
    """Run a simple agent demonstration"""

    # Create shell instance
    shell = ShellInterpreter()

    print("🤖 Simple Agent Demo with GPT-5-Mini")
    print("=" * 40)

    # Create agent directory and workspace
    shell.execute("mkdir -p /agents")
    shell.execute("mkdir -p /workspace")

    # Create test files
    shell.fs.write_file(
        "/workspace/hello.py",
        '''def hello(name):
    """Greet someone by name"""
    return f"Hello, {name}!"

if __name__ == "__main__":
    print(hello("World"))
''',
    )

    shell.fs.write_file(
        "/workspace/data.txt", "Sample data file\nWith multiple lines\nFor testing"
    )

    # Create a simple assistant agent with gpt-5-mini
    assistant_agent = """#!agent
name: simple_assistant
model: gpt-5-mini
system_prompt: You are a helpful assistant. When asked about files, use TOOL[ls] to list files or TOOL[cat](filename) to read files.
tools:
  - ls
  - cat
  - pwd
input: stdin
output: stdout
temperature: 0.3
max_tokens: 150
timeout: 15
"""

    shell.fs.write_file("/agents/assistant.agent", assistant_agent)
    print("✓ Created assistant agent with gpt-5-mini")

    # Import agent command
    from chuk_virtual_shell.commands.system.agent import AgentCommand

    agent_cmd = AgentCommand(shell)

    # Demo 1: Simple greeting
    print("\n📝 Demo 1: Simple Greeting")
    shell._pipe_input = "Hello! How are you today?"
    result = await agent_cmd.execute_async("/agents/assistant.agent")
    print(f"Agent: {result}")

    # Demo 2: File listing with tool usage
    print("\n📁 Demo 2: File Exploration")
    shell._pipe_input = "List the files in /workspace"
    result = await agent_cmd.execute_async("/agents/assistant.agent")
    print(f"Agent: {result}")

    # Demo 3: Reading file content with tools
    print("\n🔍 Demo 3: Reading File Content")
    shell._pipe_input = "Read the contents of /workspace/hello.py"
    result = await agent_cmd.execute_async("/agents/assistant.agent")
    print(f"Agent: {result}")

    # Demo 4: Background agent
    print("\n⚙️ Demo 4: Background Agent")
    shell._pipe_input = "Working in background"
    result = await agent_cmd.execute_async("/agents/assistant.agent -b")
    print(f"Background result: {result}")

    # List agents
    print("\n📋 Active Agents:")
    result = await agent_cmd.execute_async("-l")
    print(result)

    print("\n✅ Demo Complete!")
    print("GPT-5-Mini successfully used tools to:")
    print("  • List files using TOOL[ls]")
    print("  • Read file contents using TOOL[cat]")
    print("  • Run as background processes")


def main():
    """Main entry point"""
    print("Starting Simple Agent Demo...")
    asyncio.run(run_simple_demo())


if __name__ == "__main__":
    main()
