#!/usr/bin/env python3
"""
Demonstration of AI agents running as shell processes.
"""

import asyncio
from chuk_virtual_shell.shell_interpreter import ShellInterpreter


async def run_agent_demo():
    """Run the agent demonstration"""

    # Create shell instance
    shell = ShellInterpreter()

    print("=== AI Agent Shell Demo ===\n")

    # Create agent directory
    shell.execute("mkdir -p /agents")

    # Create a simple assistant agent
    assistant_agent = """#!agent
name: demo_assistant
model: gpt-5-mini
system_prompt: |
  You are a helpful assistant. When asked about files, use TOOL[ls] to list files or TOOL[cat](filename) to read files.
tools:
  - ls
  - cat
  - echo
  - pwd
input: stdin
output: stdout
memory: session
temperature: 0.3
max_tokens: 150
timeout: 15
"""

    shell.fs.write_file("/agents/assistant.agent", assistant_agent)
    print("Created assistant agent at /agents/assistant.agent")

    # Create a code analyzer agent
    analyzer_agent = """#!agent
name: code_analyzer
model: gpt-5-mini
system_prompt: |
  You analyze code. Use TOOL[cat](filename) to read files before analyzing.
tools:
  - cat
  - grep
  - wc
input: stdin
output: stdout
memory: none
temperature: 0.2
max_tokens: 200
timeout: 15
"""

    shell.fs.write_file("/agents/analyzer.agent", analyzer_agent)
    print("Created analyzer agent at /agents/analyzer.agent")

    # Create some test files
    shell.execute("mkdir -p /workspace")
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
        "/workspace/data.txt",
        """This is sample data.
It contains multiple lines.
We can analyze this text.
The agent will process it.""",
    )

    # Import agent command for async execution
    from chuk_virtual_shell.commands.system.agent import AgentCommand

    agent_cmd = AgentCommand(shell)

    print("\n=== Demo 1: Simple Agent Interaction ===")
    print("Input: 'List files in /workspace'")
    shell._pipe_input = "List files in /workspace"
    result = await agent_cmd.execute_async("/agents/assistant.agent")
    print(f"Agent response:\n{result}\n")

    print("=== Demo 2: Analyzing Code ===")
    print("Input: 'Analyze the hello.py file in /workspace'")
    shell._pipe_input = "Analyze the hello.py file in /workspace"
    result = await agent_cmd.execute_async("/agents/analyzer.agent")
    print(f"Agent response:\n{result}\n")

    print("=== Demo 3: Agent with Current Directory ===")
    print("Input: 'What is the current directory and list its contents?'")
    shell._pipe_input = "What is the current directory and list its contents?"
    result = await agent_cmd.execute_async("/agents/assistant.agent")
    print(f"Agent response:\n{result}\n")

    print("=== Demo 4: Background Agent ===")
    print("Input: 'Working in background' | agent /agents/assistant.agent -b")
    shell._pipe_input = "Working in background"
    result = await agent_cmd.execute_async("/agents/assistant.agent -b")
    print(f"Background launch: {result}")

    # List running agents
    print("\nListing agents: agent -l")
    result = await agent_cmd.execute_async("-l")
    print(result)

    print("\n=== Demo 5: File-based Input/Output ===")
    shell.fs.write_file(
        "/workspace/question.txt",
        "Read the file /workspace/hello.py and explain what the hello function does",
    )
    print(
        "Created question: 'Read the file /workspace/hello.py and explain what the hello function does'"
    )
    print(
        "Running: agent /agents/assistant.agent -i /workspace/question.txt -o /workspace/answer.txt"
    )
    result = await agent_cmd.execute_async(
        "/agents/assistant.agent -i /workspace/question.txt -o /workspace/answer.txt"
    )
    print(f"File I/O result: {result}")

    answer = shell.fs.read_file("/workspace/answer.txt")
    if answer:
        print(f"Answer written to file: {answer[:100]}...")

    print("\n=== Agent Demo Complete ===")


def main():
    """Main entry point"""
    print("Starting Agent Demo...")
    asyncio.run(run_agent_demo())


if __name__ == "__main__":
    main()
