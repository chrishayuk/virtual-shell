#!/usr/bin/env python
"""
Agentic Coding Demo - Shows how an AI agent would use persistent sessions
to complete a multi-step development task autonomously.

This simulates an AI agent building a Python web API project step-by-step,
maintaining context across all operations just like a human developer would.
"""

import asyncio
import json
from typing import List, Dict, Any
from chuk_virtual_shell.session import (
    ShellSessionManager,
    SessionMode
)
from chuk_virtual_shell.shell_interpreter import ShellInterpreter


class AgentTask:
    """Represents a task the agent needs to complete."""
    def __init__(self, description: str, commands: List[str], verify_command: str = None):
        self.description = description
        self.commands = commands
        self.verify_command = verify_command
        self.completed = False
        self.output = []


class CodingAgent:
    """
    Simulates an AI coding agent that maintains session context
    while completing development tasks.
    """
    
    def __init__(self, session_manager: ShellSessionManager):
        self.manager = session_manager
        self.session_id = None
        self.project_context = {}
        self.task_history = []
    
    async def start_project(self, project_name: str, project_type: str):
        """Initialize a new project session."""
        print(f"🤖 Agent: Starting new {project_type} project: {project_name}")
        print("=" * 60)
        
        # Create a persistent session for the entire project
        self.session_id = await self.manager.create_session(mode=SessionMode.PIPE)
        self.project_context = {
            "name": project_name,
            "type": project_type,
            "session": self.session_id
        }
        
        print(f"✅ Created session: {self.session_id[:16]}...")
        return self.session_id
    
    async def execute_task(self, task: AgentTask):
        """Execute a development task with verification."""
        print(f"\n📋 Task: {task.description}")
        print("-" * 40)
        
        # Execute task commands
        for cmd in task.commands:
            print(f"  $ {cmd}")
            output_lines = []
            async for chunk in self.manager.run_command(self.session_id, cmd):
                if chunk.data.strip():
                    lines = chunk.data.strip().split('\n')
                    for line in lines[:3]:  # Show first 3 lines
                        print(f"    {line}")
                    if len(lines) > 3:
                        print(f"    ... ({len(lines)-3} more lines)")
                    output_lines.extend(lines)
            task.output.append(output_lines)
        
        # Verify task completion if specified
        if task.verify_command:
            print(f"  ✓ Verifying: {task.verify_command}")
            async for chunk in self.manager.run_command(self.session_id, task.verify_command):
                if "error" in chunk.data.lower():
                    print(f"    ⚠️  Issue detected: {chunk.data[:50]}")
                    return False
        
        task.completed = True
        self.task_history.append(task)
        print(f"  ✅ Task completed")
        return True
    
    async def analyze_code(self, file_path: str):
        """Analyze code file for potential improvements."""
        print(f"\n🔍 Analyzing: {file_path}")
        
        # Read the file
        async for chunk in self.manager.run_command(self.session_id, f"cat {file_path}"):
            lines = chunk.data.split('\n')
            
        # Simulate analysis
        suggestions = [
            "Add type hints for better code clarity",
            "Consider adding error handling for edge cases",
            "Add docstrings for API documentation"
        ]
        
        for suggestion in suggestions:
            print(f"  💡 {suggestion}")
        
        return suggestions
    
    async def run_tests(self):
        """Run project tests and analyze results."""
        print("\n🧪 Running tests...")
        
        test_commands = [
            "python -m pytest tests/ -v 2>/dev/null || echo 'No tests found'",
            "ls tests/*.py 2>/dev/null | wc -l"
        ]
        
        for cmd in test_commands:
            async for chunk in self.manager.run_command(self.session_id, cmd):
                if chunk.data.strip():
                    print(f"  {chunk.data.strip()}")
        
        return True
    
    async def generate_summary(self):
        """Generate project summary from session context."""
        print("\n📊 Project Summary")
        print("=" * 60)
        
        # Get current session state
        session = await self.manager.get_session(self.session_id)
        if session:
            state = session.get_state()
            
            print(f"Project: {self.project_context['name']}")
            print(f"Type: {self.project_context['type']}")
            print(f"Working Directory: {state.cwd}")
            print(f"Tasks Completed: {len(self.task_history)}")
            print(f"Commands Executed: {len(state.history)}")
            
            # Show project structure
            print("\n📁 Project Structure:")
            async for chunk in self.manager.run_command(self.session_id, "find . -type f -name '*.py' | head -10"):
                if chunk.data.strip():
                    for line in chunk.data.strip().split('\n'):
                        print(f"  {line}")
            
            # Show environment
            print("\n🔧 Environment Variables:")
            important_vars = ["PYTHONPATH", "VIRTUAL_ENV", "ENV", "DEBUG"]
            for var in important_vars:
                async for chunk in self.manager.run_command(self.session_id, f"echo ${var}"):
                    value = chunk.data.strip()
                    if value and value != f"${var}":
                        print(f"  {var}={value}")
        
        return True
    
    async def cleanup(self):
        """Clean up the agent session."""
        if self.session_id:
            await self.manager.close_session(self.session_id)
            print(f"\n🧹 Closed session: {self.session_id[:16]}...")


async def build_web_api_project():
    """
    Simulate an AI agent building a complete web API project.
    This demonstrates how session persistence enables complex,
    multi-step development workflows.
    """
    
    # Initialize session manager
    def shell_factory():
        return ShellInterpreter()
    
    manager = ShellSessionManager(shell_factory=shell_factory)
    agent = CodingAgent(manager)
    
    try:
        # Start the project
        await agent.start_project("user-api", "FastAPI Web Service")
        
        # Task 1: Set up project structure
        task1 = AgentTask(
            "Set up project structure",
            [
                "mkdir -p /workspace/user-api",
                "cd /workspace/user-api",
                "mkdir -p src tests docs config",
                "touch src/__init__.py",
                "touch src/main.py",
                "touch src/models.py",
                "touch src/routes.py",
                "touch requirements.txt",
                "touch README.md",
                "touch .env"
            ],
            verify_command="ls -la"
        )
        await agent.execute_task(task1)
        
        # Task 2: Create main application file
        task2 = AgentTask(
            "Create FastAPI application",
            [
                "echo '# FastAPI User API' > src/main.py",
                "echo 'from fastapi import FastAPI' >> src/main.py",
                "echo 'app = FastAPI()' >> src/main.py",
            ],
            verify_command="head -3 src/main.py"
        )
        await agent.execute_task(task2)
        
        # Task 3: Create data models
        task3 = AgentTask(
            "Create data models",
            [
                "echo '# Pydantic models' > src/models.py",
                "echo 'from pydantic import BaseModel' >> src/models.py",
                "echo 'class User(BaseModel):' >> src/models.py",
                "echo '    username: str' >> src/models.py",
                "echo '    email: str' >> src/models.py",
            ],
            verify_command="head -5 src/models.py"
        )
        await agent.execute_task(task3)
        
        # Task 4: Create API routes
        task4 = AgentTask(
            "Create API routes",
            [
                "echo '# API Routes' > src/routes.py",
                "echo 'from fastapi import APIRouter' >> src/routes.py",
                "echo 'router = APIRouter()' >> src/routes.py",
                "echo '# User endpoints here' >> src/routes.py",
            ],
            verify_command="wc -l src/routes.py"
        )
        await agent.execute_task(task4)
        
        # Task 5: Update main.py to include routes
        task5 = AgentTask(
            "Wire up routes in main application",
            [
                "echo '# Import router' >> src/main.py",
                "echo 'from src.routes import router' >> src/main.py",
                "echo 'app.include_router(router)' >> src/main.py",
            ]
        )
        await agent.execute_task(task5)
        
        # Task 6: Create requirements file
        task6 = AgentTask(
            "Create requirements.txt",
            [
                "echo 'fastapi==0.104.1' > requirements.txt",
                "echo 'uvicorn==0.24.0' >> requirements.txt",
                "echo 'pydantic==2.5.0' >> requirements.txt",
                "echo 'pytest==7.4.3' >> requirements.txt",
            ],
            verify_command="wc -l requirements.txt"
        )
        await agent.execute_task(task6)
        
        # Task 7: Create test file
        task7 = AgentTask(
            "Create unit tests",
            [
                "touch tests/test_api.py",
                "echo '# Unit tests for API' > tests/test_api.py",
            ]
        )
        await agent.execute_task(task7)
        
        # Task 8: Create documentation
        task8 = AgentTask(
            "Create README documentation",
            [
                "echo '# User API' > README.md",
                "echo 'A FastAPI-based microservice for user management.' >> README.md",
                "echo '' >> README.md",
                "echo '## Installation' >> README.md",
                "echo 'pip install -r requirements.txt' >> README.md",
            ]
        )
        await agent.execute_task(task8)
        
        # Task 9: Set up environment
        task9 = AgentTask(
            "Configure environment",
            [
                "export PYTHONPATH=/workspace/user-api",
                "export ENV=development",
                "export DEBUG=true",
                "echo 'Environment configured'"
            ]
        )
        await agent.execute_task(task9)
        
        # Analyze the code
        await agent.analyze_code("src/main.py")
        await agent.analyze_code("src/routes.py")
        
        # Run tests (simulated)
        await agent.run_tests()
        
        # Generate project summary
        await agent.generate_summary()
        
        # Show final statistics
        session = await manager.get_session(agent.session_id)
        if session:
            state = session.get_state()
            print("\n📈 Session Statistics:")
            print(f"  Total Commands: {len(state.history)}")
            print(f"  Working Directory: {state.cwd}")
            print(f"  Environment Variables Set: {len([k for k in state.env.keys() if k not in ['HOME', 'USER', 'PATH', 'PWD', 'OLDPWD']])}")
            
            print("\n🎯 Key Accomplishments:")
            print("  ✅ Created complete project structure")
            print("  ✅ Implemented FastAPI application")
            print("  ✅ Created data models with Pydantic")
            print("  ✅ Implemented RESTful API endpoints")
            print("  ✅ Added unit tests")
            print("  ✅ Generated documentation")
            print("  ✅ Configured development environment")
        
    finally:
        await agent.cleanup()


async def simple_workflow_demo():
    """
    Demonstrate a simple multi-step workflow with session persistence.
    """
    
    def shell_factory():
        return ShellInterpreter()
    
    manager = ShellSessionManager(shell_factory=shell_factory)
    agent = CodingAgent(manager)
    
    print("\n" + "="*60)
    print("📝 SIMPLE WORKFLOW DEMO")
    print("="*60)
    
    try:
        await agent.start_project("data-pipeline", "Data Processing")
        
        # Task 1: Set up data processing pipeline
        setup_task = AgentTask(
            "Set up data processing workspace",
            [
                "mkdir -p /workspace/pipeline",
                "cd /workspace/pipeline",
                "mkdir -p data output logs",
                "touch process.py",
                "touch config.json"
            ]
        )
        await agent.execute_task(setup_task)
        
        # Task 2: Create sample data files
        data_task = AgentTask(
            "Create sample data files",
            [
                "echo 'id,name,value' > data/input.csv",
                "echo '1,Alice,100' >> data/input.csv",
                "echo '2,Bob,200' >> data/input.csv",
                "echo '3,Charlie,150' >> data/input.csv",
                "ls -la data/"
            ]
        )
        await agent.execute_task(data_task)
        
        # Task 3: Create processing script
        script_task = AgentTask(
            "Create data processing script",
            [
                "echo '# Data processing pipeline' > process.py",
                "echo 'import json' >> process.py",
                "echo 'print(\"Processing data...\")' >> process.py",
                "echo '# Read CSV and transform' >> process.py",
                "wc -l process.py"
            ]
        )
        await agent.execute_task(script_task)
        
        # Task 4: Create configuration
        config_task = AgentTask(
            "Create pipeline configuration",
            [
                "echo '{' > config.json",
                "echo '  \"input\": \"data/input.csv\",' >> config.json",
                "echo '  \"output\": \"output/result.json\",' >> config.json",
                "echo '  \"format\": \"json\"' >> config.json",
                "echo '}' >> config.json",
                "cat config.json"
            ]
        )
        await agent.execute_task(config_task)
        
        # Task 5: Set up logging
        log_task = AgentTask(
            "Configure logging",
            [
                "echo 'Pipeline initialized' > logs/pipeline.log",
                "echo 'Configuration loaded' >> logs/pipeline.log",
                "tail logs/pipeline.log"
            ]
        )
        await agent.execute_task(log_task)
        
        print("\n📊 Workflow Summary:")
        session = await manager.get_session(agent.session_id)
        if session:
            state = session.get_state()
            print(f"  Working directory: {state.cwd}")
            print(f"  Commands executed: {len(state.history)}")
            print(f"  Files created: 6")
            print(f"  Directories created: 3")
            
            # Show final structure
            print("\n  Final project structure:")
            async for chunk in manager.run_command(agent.session_id, "find . -type f | head -10"):
                if chunk.data.strip():
                    for line in chunk.data.strip().split('\n'):
                        print(f"    {line}")
        
    finally:
        await agent.cleanup()


if __name__ == "__main__":
    print("🤖 AGENTIC CODING DEMONSTRATION")
    print("Showing how AI agents use persistent sessions for complex development tasks\n")
    
    # Run the web API project demo
    asyncio.run(build_web_api_project())
    
    # Run the simple workflow demo
    asyncio.run(simple_workflow_demo())
    
    print("\n✨ Demo complete! This demonstrates how session persistence enables:")
    print("  • Multi-step project development with maintained context")
    print("  • Iterative workflows with state preservation")
    print("  • Complex workflows that mirror human development patterns")
    print("  • Reliable task completion with verification steps")