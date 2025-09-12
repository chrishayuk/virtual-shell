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
model: gpt-3.5-turbo
system_prompt: |
  You are a helpful assistant in a virtual shell.
  Help users with file operations and answer questions.
tools:
  - ls
  - cat
  - echo
  - pwd
input: stdin
output: stdout
memory: session
temperature: 0.7
"""
    
    shell.fs.write_file("/agents/assistant.agent", assistant_agent)
    print("Created assistant agent at /agents/assistant.agent")
    
    # Create a code analyzer agent
    analyzer_agent = """#!agent
name: code_analyzer
model: gpt-3.5-turbo
system_prompt: |
  Analyze code and provide insights about structure and quality.
tools:
  - cat
  - grep
  - wc
input: stdin
output: stdout
memory: none
temperature: 0.3
"""
    
    shell.fs.write_file("/agents/analyzer.agent", analyzer_agent)
    print("Created analyzer agent at /agents/analyzer.agent")
    
    # Create some test files
    shell.execute("mkdir -p /workspace")
    shell.fs.write_file("/workspace/hello.py", '''def hello(name):
    """Greet someone by name"""
    return f"Hello, {name}!"

if __name__ == "__main__":
    print(hello("World"))
''')
    
    shell.fs.write_file("/workspace/data.txt", """This is sample data.
It contains multiple lines.
We can analyze this text.
The agent will process it.""")
    
    print("\n=== Demo 1: Simple Agent Interaction ===")
    print("Running: echo 'List files in /workspace' | agent /agents/assistant.agent")
    result = shell.execute("echo 'List files in /workspace' | agent /agents/assistant.agent")
    print(f"Agent response:\n{result}\n")
    
    print("=== Demo 2: Analyzing Code ===")
    print("Running: cat /workspace/hello.py | agent /agents/analyzer.agent")
    result = shell.execute("cat /workspace/hello.py | agent /agents/analyzer.agent")
    print(f"Agent response:\n{result}\n")
    
    print("=== Demo 3: Agent Pipeline ===")
    print("Running: ls /workspace | agent /agents/assistant.agent | head -3")
    result = shell.execute("ls /workspace | agent /agents/assistant.agent | head -3")
    print(f"Pipeline result:\n{result}\n")
    
    print("=== Demo 4: Background Agent ===")
    print("Running: agent /agents/assistant.agent -b")
    result = shell.execute("agent /agents/assistant.agent -b")
    print(f"Background launch: {result}")
    
    # List running agents
    print("\nListing agents: agent -l")
    result = shell.execute("agent -l")
    print(result)
    
    print("\n=== Demo 5: File-based Input/Output ===")
    shell.fs.write_file("/workspace/question.txt", "What is the purpose of the hello function in hello.py?")
    print("Running: agent /agents/assistant.agent -i /workspace/question.txt -o /workspace/answer.txt")
    shell.execute("agent /agents/assistant.agent -i /workspace/question.txt -o /workspace/answer.txt")
    
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