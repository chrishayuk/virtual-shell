#!/usr/bin/env python3
"""
Simple demonstration of AI agents as shell processes (using mock LLM).
"""

from chuk_virtual_shell.shell_interpreter import ShellInterpreter


def run_simple_demo():
    """Run a simple agent demonstration"""
    
    # Create shell instance
    shell = ShellInterpreter()
    
    print("=== Simple AI Agent Demo (Mock Mode) ===\n")
    
    # Create agent directory
    shell.execute("mkdir -p /agents")
    shell.execute("mkdir -p /workspace")
    
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
    print("✓ Created assistant agent at /agents/assistant.agent")
    
    # Create some test files
    shell.fs.write_file("/workspace/hello.txt", "Hello, World!")
    shell.fs.write_file("/workspace/data.txt", """Line 1
Line 2
Line 3""")
    print("✓ Created test files in /workspace\n")
    
    # Demo 1: List running agents (should be empty)
    print("=== Demo 1: List Running Agents ===")
    print("Command: agent -l")
    result = shell.execute("agent -l")
    print(f"Result: {result}\n")
    
    # Demo 2: Show help
    print("=== Demo 2: Agent Help ===")
    print("Command: agent --help")
    help_text = shell.commands.get('agent').get_help() if 'agent' in shell.commands else "Agent command not found"
    print(help_text[:500] + "...\n" if len(help_text) > 500 else help_text + "\n")
    
    # Demo 3: Simple execution with mock response
    print("=== Demo 3: Simple Agent Interaction (Mock) ===")
    print("Note: Using mock LLM - responses are simulated")
    
    # Set pipe input manually since we're not using actual pipes
    shell._pipe_input = "list files"
    result = shell.execute("agent /agents/assistant.agent")
    print(f"Input: 'list files'")
    print(f"Agent response: {result}\n")
    
    # Demo 4: File operations with agent
    print("=== Demo 4: Agent Using Tools (Mock) ===")
    shell._pipe_input = "list files in /workspace"
    result = shell.execute("agent /agents/assistant.agent")
    print(f"Input: 'list files in /workspace'")
    print(f"Agent response: {result}\n")
    
    # Demo 5: Background execution
    print("=== Demo 5: Background Agent ===")
    print("Command: agent /agents/assistant.agent -b")
    result = shell.execute("agent /agents/assistant.agent -b")
    print(f"Result: {result}\n")
    
    # List agents again
    print("Listing agents after background launch:")
    result = shell.execute("agent -l")
    print(f"{result}\n")
    
    # Demo 6: Agent process info
    print("=== Demo 6: Process Management ===")
    
    # Get the PID from the agent list
    processes = shell.agent_manager.list_processes()
    if processes:
        pid = processes[0].pid
        print(f"Checking status of agent {pid}:")
        result = shell.execute(f"agent -s {pid}")
        print(result)
        
        print(f"\nKilling agent {pid}:")
        result = shell.execute(f"agent -k {pid}")
        print(result)
    else:
        print("No agents running to demonstrate process management")
    
    # Demo 7: Input/Output files
    print("\n=== Demo 7: File-based I/O ===")
    shell.fs.write_file("/workspace/question.txt", "hello")
    print("Created /workspace/question.txt with content: 'hello'")
    
    print("Command: agent /agents/assistant.agent -i /workspace/question.txt -o /workspace/answer.txt")
    result = shell.execute("agent /agents/assistant.agent -i /workspace/question.txt -o /workspace/answer.txt")
    print(f"Result: {result}")
    
    if shell.fs.exists("/workspace/answer.txt"):
        answer = shell.fs.read_file("/workspace/answer.txt")
        print(f"Answer file content: {answer[:100]}...")
    
    print("\n=== Demo Complete ===")
    print("This demo used mock LLM responses.")
    print("To use real LLMs, install chuk-llm and set API keys:")
    print("  pip install chuk-llm")
    print("  export OPENAI_API_KEY=your_key")
    print("\nKey concepts demonstrated:")
    print("  • Agents as processes with PIDs")
    print("  • Background execution")
    print("  • Process management (list, status, kill)")
    print("  • File-based I/O")
    print("  • Tool access (ls, cat, etc.)")


def main():
    """Main entry point"""
    print("Starting Simple Agent Demo...\n")
    run_simple_demo()


if __name__ == "__main__":
    main()