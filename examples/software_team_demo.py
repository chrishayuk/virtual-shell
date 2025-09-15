#!/usr/bin/env python3
"""
Software Development Team - Multi-Agent Collaboration
Simulates a software team working together on a project.
"""

import os
import sys
import warnings
import time
from pathlib import Path
from dotenv import load_dotenv

warnings.filterwarnings("ignore")

from chuk_virtual_shell.shell_interpreter import ShellInterpreter
from chuk_virtual_shell.agents.cleanup import suppress_cleanup_warnings

suppress_cleanup_warnings()


def setup_environment():
    """Load environment variables"""
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        return os.getenv("OPENAI_API_KEY") is not None
    return False


def create_software_team(shell):
    """Create a software development team of agents"""

    print("\n👥 Creating Software Development Team...")

    # Product Owner
    product_owner = """#!agent
name: product_owner
model: gpt-3.5-turbo
system_prompt: |
  You are a Product Owner. When given a project idea:
  1. Define clear user stories
  2. Set acceptance criteria
  3. Prioritize features
  Format: "As a [user], I want [feature] so that [benefit]"
  Keep responses structured and clear.
tools:
  - echo
  - cat
input: stdin
output: stdout
temperature: 0.3
max_tokens: 400
"""

    # Tech Lead
    tech_lead = """#!agent
name: tech_lead
model: gpt-3.5-turbo
system_prompt: |
  You are a Tech Lead. When given user stories:
  1. Design technical architecture
  2. Choose appropriate technologies
  3. Define component structure
  4. Create technical specifications
  Be specific about implementation details.
tools:
  - mkdir
  - touch
  - echo
  - ls
input: stdin
output: stdout
temperature: 0.4
max_tokens: 500
"""

    # Backend Developer
    backend_dev = """#!agent
name: backend_developer
model: gpt-3.5-turbo
system_prompt: |
  You are a Backend Developer. When given technical specs:
  1. Implement API endpoints
  2. Create data models
  3. Write backend logic in Python
  Use 'echo' to create Python code files.
  Example: echo "class User:\\n    pass" > user.py
tools:
  - echo
  - cat
  - touch
  - python
input: stdin
output: stdout
temperature: 0.5
max_tokens: 600
"""

    # Frontend Developer
    frontend_dev = """#!agent
name: frontend_developer
model: gpt-3.5-turbo
system_prompt: |
  You are a Frontend Developer. When given specs:
  1. Create UI components
  2. Implement user interactions
  3. Write HTML/JavaScript code
  Use 'echo' to create files.
tools:
  - echo
  - cat
  - touch
input: stdin
output: stdout
temperature: 0.5
max_tokens: 600
"""

    # QA Engineer
    qa_engineer = """#!agent
name: qa_engineer
model: gpt-3.5-turbo
system_prompt: |
  You are a QA Engineer. When reviewing code:
  1. Identify test scenarios
  2. Create test cases
  3. Find potential bugs
  4. Suggest improvements
  Be thorough and specific.
tools:
  - cat
  - ls
  - grep
  - python
input: stdin
output: stdout
temperature: 0.3
max_tokens: 400
"""

    # DevOps Engineer
    devops = """#!agent
name: devops_engineer
model: gpt-3.5-turbo
system_prompt: |
  You are a DevOps Engineer. Your tasks:
  1. Set up deployment configuration
  2. Create CI/CD pipelines
  3. Configure monitoring
  4. Ensure scalability
  Focus on automation and reliability.
tools:
  - echo
  - mkdir
  - touch
  - cat
input: stdin
output: stdout
temperature: 0.4
max_tokens: 400
"""

    # Create agent files
    shell.execute("mkdir -p /team")
    agents = {
        "product_owner": product_owner,
        "tech_lead": tech_lead,
        "backend_dev": backend_dev,
        "frontend_dev": frontend_dev,
        "qa_engineer": qa_engineer,
        "devops": devops,
    }

    for name, definition in agents.items():
        shell.fs.write_file(f"/team/{name}.agent", definition)

    print("✓ Created 6 team members:")
    print("  • Product Owner")
    print("  • Tech Lead")
    print("  • Backend Developer")
    print("  • Frontend Developer")
    print("  • QA Engineer")
    print("  • DevOps Engineer")

    return True


def run_sprint_simulation(shell):
    """Simulate a development sprint with the team"""

    print("\n" + "=" * 70)
    print("🏃 SPRINT SIMULATION: Building a Task Management API")
    print("=" * 70)

    # Project setup
    shell.execute("mkdir -p /sprint/backlog")
    shell.execute("mkdir -p /sprint/development")
    shell.execute("mkdir -p /sprint/testing")
    shell.execute("mkdir -p /sprint/deployment")
    shell.execute("mkdir -p /sprint/communication")

    # Initial project brief
    project_brief = """Build a RESTful API for task management with these features:
- Create, read, update, delete tasks
- User authentication
- Task assignment to users
- Priority levels (high, medium, low)
- Due date tracking"""

    shell.fs.write_file("/sprint/project_brief.txt", project_brief)

    print("\n📋 PROJECT BRIEF:")
    print(project_brief)
    print("\n" + "-" * 70)

    # Sprint Day 1: Planning
    print("\n📅 DAY 1: Sprint Planning")
    print("-" * 40)

    print("🔹 Product Owner creating user stories...")
    result = shell.execute(
        "cat /sprint/project_brief.txt | agent /team/product_owner.agent"
    )
    shell.fs.write_file("/sprint/backlog/user_stories.txt", result)
    lines = result.split("\n")
    print(f"   Created: {len(lines)} user stories")

    print("\n🔹 Tech Lead designing architecture...")
    result = shell.execute(
        "cat /sprint/backlog/user_stories.txt | agent /team/tech_lead.agent"
    )
    shell.fs.write_file("/sprint/development/architecture.txt", result)
    print(f"   Architecture defined: {result[:100]}...")

    # Sprint Day 2: Development
    print("\n📅 DAY 2: Development")
    print("-" * 40)

    print("🔹 Backend Developer implementing API...")
    # Create actual Python code
    api_code = """from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)
tasks = []

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    return jsonify(tasks)

@app.route('/api/tasks', methods=['POST'])
def create_task():
    task = request.json
    task['id'] = len(tasks) + 1
    task['created_at'] = datetime.now().isoformat()
    tasks.append(task)
    return jsonify(task), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = next((t for t in tasks if t['id'] == task_id), None)
    if task:
        task.update(request.json)
        return jsonify(task)
    return jsonify({'error': 'Task not found'}), 404

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    global tasks
    tasks = [t for t in tasks if t['id'] != task_id]
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)
"""
    shell.fs.write_file("/sprint/development/task_api.py", api_code)
    print("   ✓ API implementation complete")

    print("\n🔹 Frontend Developer creating UI...")
    ui_code = """<!DOCTYPE html>
<html>
<head>
    <title>Task Manager</title>
    <style>
        .task { padding: 10px; margin: 5px; border: 1px solid #ccc; }
        .high { border-color: red; }
        .medium { border-color: orange; }
        .low { border-color: green; }
    </style>
</head>
<body>
    <h1>Task Manager</h1>
    <div id="task-list"></div>
    <script src="app.js"></script>
</body>
</html>
"""
    shell.fs.write_file("/sprint/development/index.html", ui_code)
    print("   ✓ UI components created")

    # Sprint Day 3: Testing
    print("\n📅 DAY 3: Testing")
    print("-" * 40)

    print("🔹 QA Engineer reviewing code...")
    result = shell.execute(
        "cat /sprint/development/task_api.py | agent /team/qa_engineer.agent"
    )
    shell.fs.write_file("/sprint/testing/test_report.txt", result)
    print(f"   Test scenarios identified: {result[:100]}...")

    # Sprint Day 4: DevOps
    print("\n📅 DAY 4: Deployment Preparation")
    print("-" * 40)

    print("🔹 DevOps Engineer setting up deployment...")
    dockerfile = """FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "task_api.py"]
"""
    shell.fs.write_file("/sprint/deployment/Dockerfile", dockerfile)

    ci_config = """name: CI/CD Pipeline
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: python -m pytest
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: echo "Deploying..."
"""
    shell.fs.write_file("/sprint/deployment/ci_cd.yml", ci_config)
    print("   ✓ Deployment configuration ready")

    # Sprint Review
    print("\n📊 SPRINT REVIEW")
    print("=" * 70)

    # Show what was created
    print("\n📁 Sprint Deliverables:")

    directories = [
        ("/sprint/backlog", "Product Backlog"),
        ("/sprint/development", "Development"),
        ("/sprint/testing", "Testing"),
        ("/sprint/deployment", "Deployment"),
    ]

    for dir_path, label in directories:
        result = shell.execute(f"ls {dir_path}")
        files = result.split("\n")
        print(f"\n   {label}:")
        for file in files:
            if file.strip():
                print(f"      ✓ {file}")

    # Metrics
    print("\n📈 Sprint Metrics:")
    print("   • Team Size: 6 agents")
    print("   • Sprint Duration: 4 days (simulated)")
    print("   • Deliverables: API, UI, Tests, Deployment")
    print("   • Files Created: 10+")

    return True


def run_parallel_development(shell):
    """Demonstrate parallel development by multiple agents"""

    print("\n" + "=" * 70)
    print("⚡ PARALLEL DEVELOPMENT DEMO")
    print("=" * 70)

    print("\n🔄 Multiple agents working simultaneously...")

    # Create tasks for parallel execution
    tasks = [
        ("Create user model", "/team/backend_dev.agent"),
        ("Design dashboard", "/team/frontend_dev.agent"),
        ("Write test cases", "/team/qa_engineer.agent"),
        ("Setup monitoring", "/team/devops.agent"),
    ]

    print("\nStarting parallel tasks:")
    for task, agent in tasks:
        shell.fs.write_file(f"/sprint/communication/{task.replace(' ', '_')}.txt", task)
        cmd = f"echo '{task}' | agent {agent} -b"
        result = shell.execute(cmd)
        print(f"   • {result}")

    # Show active agents
    print("\n📊 Active Agent Processes:")
    result = shell.execute("agent -l")
    lines = result.split("\\n")[:10]
    for line in lines:
        if line.strip():
            print(f"   {line}")

    # Wait a moment for some to complete
    time.sleep(2)

    # Check status again
    print("\n📊 Updated Status:")
    result = shell.execute("agent -l")
    lines = result.split("\\n")[:10]
    for line in lines:
        if line.strip():
            print(f"   {line}")

    # Clean up
    processes = shell.agent_manager.list_processes()
    active_count = sum(1 for p in processes if p.is_active())
    completed_count = sum(1 for p in processes if p.state.value == "completed")

    print("\n✓ Parallel execution complete:")
    print(f"   • Active: {active_count}")
    print(f"   • Completed: {completed_count}")

    # Cleanup all processes
    for proc in processes:
        if proc.is_active():
            shell.execute(f"agent -k {proc.pid}")

    return True


def main():
    """Main entry point"""

    print("\n🚀 SOFTWARE DEVELOPMENT TEAM SIMULATION")
    print("=" * 70)

    # Setup
    has_api = setup_environment()
    shell = ShellInterpreter()

    is_real = (
        hasattr(shell, "agent_manager")
        and not shell.agent_manager.llm_interface.mock_mode
    )
    print(f"✓ Mode: {'REAL LLM' if is_real else 'MOCK MODE'}")

    try:
        # Create the team
        if create_software_team(shell):
            # Run sprint simulation
            run_sprint_simulation(shell)

            # Run parallel development
            run_parallel_development(shell)

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {e}")

    # Cleanup
    if hasattr(shell, "agent_manager"):
        shell.agent_manager.cleanup_all()

    print("\n" + "=" * 70)
    print("🎉 SIMULATION COMPLETE!")
    print("\nKey Demonstrations:")
    print("  ✓ 6 specialized agents working as a team")
    print("  ✓ Sprint planning and execution")
    print("  ✓ Sequential task handoffs")
    print("  ✓ Parallel development tasks")
    print("  ✓ File-based communication")
    print("  ✓ Real software artifacts created")
    print("\nAI agents truly working as Unix processes!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
