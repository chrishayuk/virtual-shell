#!/usr/bin/env python3
"""
Multi-Agent Collaboration Demo
Shows multiple AI agents working together to solve a complex task.
"""

import os
import sys
import warnings
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Suppress warnings
warnings.filterwarnings("ignore")

from chuk_virtual_shell.shell_interpreter import ShellInterpreter
from chuk_virtual_shell.agents.cleanup import suppress_cleanup_warnings

suppress_cleanup_warnings()


def setup_environment():
    """Load environment variables"""
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        return os.getenv('OPENAI_API_KEY') is not None
    return False


def create_specialized_agents(shell):
    """Create a team of specialized agents"""
    
    # 1. Requirements Analyst Agent
    analyst_agent = """#!agent
name: requirements_analyst
model: gpt-3.5-turbo
system_prompt: |
  You are a requirements analyst. Your job is to:
  1. Analyze user requirements
  2. Break them down into clear tasks
  3. Output a structured task list
  Format output as a numbered list.
tools:
  - cat
  - echo
input: stdin
output: stdout
temperature: 0.3
max_tokens: 300
timeout: 15
"""
    
    # 2. Architect Agent
    architect_agent = """#!agent
name: system_architect
model: gpt-3.5-turbo
system_prompt: |
  You are a system architect. Your job is to:
  1. Take task lists and design system structure
  2. Define components and their interactions
  3. Create file/folder structure plans
  Output should be clear and actionable.
tools:
  - mkdir
  - touch
  - echo
  - ls
input: stdin
output: stdout
temperature: 0.4
max_tokens: 400
timeout: 15
"""
    
    # 3. Developer Agent
    developer_agent = """#!agent
name: developer
model: gpt-3.5-turbo
system_prompt: |
  You are a software developer. Your job is to:
  1. Implement code based on architectural plans
  2. Create Python functions and classes
  3. Use echo to write code to files
  Focus on clean, simple implementations.
tools:
  - echo
  - cat
  - touch
  - python
input: stdin
output: stdout
temperature: 0.5
max_tokens: 500
timeout: 15
"""
    
    # 4. Tester Agent
    tester_agent = """#!agent
name: qa_tester
model: gpt-3.5-turbo
system_prompt: |
  You are a QA tester. Your job is to:
  1. Review code and identify potential issues
  2. Suggest test cases
  3. Verify implementations meet requirements
  Be thorough but concise.
tools:
  - cat
  - ls
  - python
  - grep
input: stdin
output: stdout
temperature: 0.3
max_tokens: 300
timeout: 15
"""
    
    # 5. Project Manager Agent
    pm_agent = """#!agent
name: project_manager
model: gpt-3.5-turbo
system_prompt: |
  You are a project manager. Your job is to:
  1. Coordinate between other agents
  2. Track progress
  3. Summarize results
  4. Ensure requirements are met
  Be clear and organized in your communication.
tools:
  - cat
  - echo
  - ls
input: stdin
output: stdout
temperature: 0.4
max_tokens: 400
timeout: 15
"""
    
    # Create agent files
    shell.execute("mkdir -p /agents")
    shell.fs.write_file("/agents/analyst.agent", analyst_agent)
    shell.fs.write_file("/agents/architect.agent", architect_agent)
    shell.fs.write_file("/agents/developer.agent", developer_agent)
    shell.fs.write_file("/agents/tester.agent", tester_agent)
    shell.fs.write_file("/agents/pm.agent", pm_agent)
    
    print("✓ Created team of 5 specialized agents")
    return True


def run_collaboration_scenario(shell):
    """Run a multi-agent collaboration scenario"""
    
    print("\n" + "="*70)
    print("🤝 MULTI-AGENT COLLABORATION SCENARIO")
    print("="*70)
    
    # The task to solve
    user_requirement = """Create a simple todo list application with the following features:
1. Add tasks
2. List tasks
3. Mark tasks as complete
4. Save tasks to a file"""
    
    print("\n📋 USER REQUIREMENT:")
    print(user_requirement)
    print("\n" + "-"*70 + "\n")
    
    # Create project directory
    shell.execute("mkdir -p /project")
    shell.execute("mkdir -p /project/docs")
    shell.execute("mkdir -p /project/src")
    shell.execute("mkdir -p /project/tests")
    shell.execute("mkdir -p /project/communication")
    
    # Save requirement
    shell.fs.write_file("/project/requirements.txt", user_requirement)
    
    # Phase 1: Requirements Analysis
    print("📊 PHASE 1: Requirements Analysis")
    print("   Analyst agent analyzing requirements...")
    
    result = shell.execute("cat /project/requirements.txt | agent /agents/analyst.agent")
    shell.fs.write_file("/project/communication/task_list.txt", result)
    print(f"   Output: {result[:150]}..." if len(result) > 150 else f"   Output: {result}")
    
    # Phase 2: System Architecture
    print("\n🏗️ PHASE 2: System Architecture")
    print("   Architect agent designing system...")
    
    result = shell.execute("cat /project/communication/task_list.txt | agent /agents/architect.agent")
    shell.fs.write_file("/project/communication/architecture.txt", result)
    print(f"   Output: {result[:150]}..." if len(result) > 150 else f"   Output: {result}")
    
    # Phase 3: Development
    print("\n💻 PHASE 3: Development")
    print("   Developer agent implementing solution...")
    
    # Give developer both requirements and architecture
    combined_input = f"Requirements:\n{user_requirement}\n\nArchitecture:\n{result}"
    shell.fs.write_file("/project/communication/dev_input.txt", combined_input)
    
    result = shell.execute("agent /agents/developer.agent -i /project/communication/dev_input.txt")
    shell.fs.write_file("/project/communication/implementation.txt", result)
    print(f"   Output: {result[:150]}..." if len(result) > 150 else f"   Output: {result}")
    
    # Create actual implementation file (mock)
    todo_code = """class TodoList:
    def __init__(self):
        self.tasks = []
    
    def add_task(self, task):
        self.tasks.append({'task': task, 'completed': False})
    
    def list_tasks(self):
        return self.tasks
    
    def complete_task(self, index):
        if 0 <= index < len(self.tasks):
            self.tasks[index]['completed'] = True
    
    def save_to_file(self, filename):
        with open(filename, 'w') as f:
            for task in self.tasks:
                f.write(f"{task['task']},{task['completed']}\\n")
"""
    shell.fs.write_file("/project/src/todo.py", todo_code)
    
    # Phase 4: Testing
    print("\n🧪 PHASE 4: Quality Assurance")
    print("   QA agent reviewing implementation...")
    
    result = shell.execute("cat /project/src/todo.py | agent /agents/tester.agent")
    shell.fs.write_file("/project/communication/qa_report.txt", result)
    print(f"   Output: {result[:150]}..." if len(result) > 150 else f"   Output: {result}")
    
    # Phase 5: Project Management Summary
    print("\n📈 PHASE 5: Project Summary")
    print("   PM agent coordinating and summarizing...")
    
    # Gather all communications
    summary_input = """Project Status Report
    
Requirements Analysis: Complete
System Architecture: Complete  
Development: Complete
QA Testing: Complete

Please provide a final project summary."""
    
    shell.fs.write_file("/project/communication/status.txt", summary_input)
    result = shell.execute("agent /agents/pm.agent -i /project/communication/status.txt")
    shell.fs.write_file("/project/communication/final_summary.txt", result)
    print(f"   Output: {result[:200]}..." if len(result) > 200 else f"   Output: {result}")
    
    print("\n" + "="*70)
    
    # Show project structure
    print("\n📁 PROJECT STRUCTURE CREATED:")
    result = shell.execute("ls -la /project/src")
    print(f"   /project/src/: {result}")
    
    result = shell.execute("ls -la /project/communication")
    comm_files = result.split('\n')
    print("   /project/communication/:")
    for file in comm_files[:5]:  # Show first 5 files
        if file.strip():
            print(f"      {file}")
    
    # Demonstrate parallel agent execution
    print("\n⚡ PARALLEL AGENT EXECUTION:")
    print("   Running multiple agents simultaneously...")
    
    # Start multiple background agents
    shell.execute("echo 'Review task 1' | agent /agents/analyst.agent -b")
    shell.execute("echo 'Design module A' | agent /agents/architect.agent -b")
    shell.execute("echo 'Implement function X' | agent /agents/developer.agent -b")
    
    # Show running agents
    result = shell.execute("agent -l")
    lines = result.split('\n')[:8]  # Show first 8 lines
    for line in lines:
        print(f"   {line}")
    
    # Clean up background agents
    processes = shell.agent_manager.list_processes()
    for proc in processes:
        if proc.is_active():
            shell.execute(f"agent -k {proc.pid}")
    
    print("\n" + "="*70)
    print("✅ MULTI-AGENT COLLABORATION COMPLETE!")
    print("\nKey Achievements:")
    print("  • 5 specialized agents worked together")
    print("  • Requirements analyzed and broken down")
    print("  • System architecture designed")
    print("  • Code implementation created")
    print("  • QA testing performed")
    print("  • Project management coordination")
    print("  • Agents communicated via files and pipes")
    print("  • Parallel execution demonstrated")


def run_agent_pipeline_demo(shell):
    """Demonstrate agent pipeline processing"""
    
    print("\n" + "="*70)
    print("🔗 AGENT PIPELINE DEMO")
    print("="*70)
    
    # Create a data processing pipeline
    print("\n📊 Data Processing Pipeline:")
    print("   Raw Data → Analyzer → Formatter → Reporter")
    
    # Create sample data
    raw_data = """Sales Report
Product A: 150 units
Product B: 230 units
Product C: 87 units
Total Revenue: $45,670"""
    
    shell.fs.write_file("/project/raw_data.txt", raw_data)
    
    print("\n   Input Data:")
    print("   " + raw_data.replace('\n', '\n   '))
    
    print("\n   Running pipeline...")
    
    # Run agents in sequence (pipeline)
    result = shell.execute(
        "cat /project/raw_data.txt | "
        "agent /agents/analyst.agent | "
        "agent /agents/pm.agent"
    )
    
    print(f"\n   Pipeline Output:\n   {result[:300]}..." if len(result) > 300 else f"\n   Pipeline Output:\n   {result}")
    
    print("\n" + "="*70)


def main():
    """Main entry point"""
    
    print("\n🚀 MULTI-AGENT COLLABORATION DEMO")
    print("="*70)
    
    # Check environment
    has_api = setup_environment()
    if has_api:
        print("✓ OpenAI API key loaded - Using real LLM")
    else:
        print("⚠ No API key - Using mock mode")
    
    # Create shell
    shell = ShellInterpreter()
    
    # Check LLM mode
    is_real = hasattr(shell, 'agent_manager') and not shell.agent_manager.llm_interface.mock_mode
    print(f"✓ Mode: {'REAL LLM (OpenAI)' if is_real else 'MOCK MODE'}")
    
    # Create agents
    if create_specialized_agents(shell):
        
        # Run collaboration scenario
        try:
            run_collaboration_scenario(shell)
            
            # Run pipeline demo
            run_agent_pipeline_demo(shell)
            
        except KeyboardInterrupt:
            print("\n\nDemo interrupted by user")
        except Exception as e:
            print(f"\nError during demo: {e}")
            import traceback
            traceback.print_exc()
    
    # Cleanup
    if hasattr(shell, 'agent_manager'):
        shell.agent_manager.cleanup_all()
    
    print("\n🎉 Demo Complete!\n")
    print("This demonstrated how AI agents can:")
    print("  • Work as a coordinated team")
    print("  • Communicate through files and pipes")
    print("  • Execute in parallel or sequence")
    print("  • Solve complex tasks collaboratively")
    print("  • Maintain Unix philosophy while adding AI intelligence")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())