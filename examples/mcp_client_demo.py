#!/usr/bin/env python3
"""
MCP Client Demo for Chuk Virtual Shell

Demonstrates how to use the Chuk Virtual Shell MCP server from an AI agent
or other MCP client. Shows session management and state persistence.
"""

import asyncio
import json
import logging
import subprocess
import sys
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleMCPClient:
    """Simple MCP client for demonstration"""

    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.request_id = 0

    async def start_server(self):
        """Start the MCP server as a subprocess"""
        self.process = subprocess.Popen(
            [sys.executable, "-m", "chuk_virtual_shell.mcp_server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        # Initialize the connection
        await self._send_request(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "demo-client", "version": "1.0.0"},
            },
        )

    async def stop_server(self):
        """Stop the MCP server"""
        if self.process:
            self.process.terminate()
            self.process.wait()

    async def _send_request(
        self, method: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send a request to the MCP server"""
        self.request_id += 1
        request = {"method": method, "params": params, "id": self.request_id}

        request_json = json.dumps(request) + "\n"
        self.process.stdin.write(request_json)
        self.process.stdin.flush()

        # Read response
        response_line = self.process.stdout.readline()
        response = json.loads(response_line)

        if "error" in response:
            raise Exception(f"MCP Error: {response['error']}")

        return response.get("result", {})

    async def list_tools(self) -> Dict[str, Any]:
        """List available tools"""
        return await self._send_request("tools/list", {})

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool"""
        result = await self._send_request(
            "tools/call", {"name": name, "arguments": arguments}
        )

        # MCP tools return content wrapped in a structure
        # Extract the actual result from the content
        if isinstance(result, dict) and "content" in result:
            content = result["content"]
            if isinstance(content, list) and len(content) > 0:
                first_content = content[0]
                if isinstance(first_content, dict) and "text" in first_content:
                    try:
                        # Try to parse as JSON
                        return json.loads(first_content["text"])
                    except (json.JSONDecodeError, KeyError):
                        # Return as-is if not JSON
                        return first_content

        return result


async def main():
    """Demo the MCP integration"""
    client = SimpleMCPClient()

    try:
        print("🚀 Starting Chuk Virtual Shell MCP Server...")
        await client.start_server()

        print("📋 Listing available tools...")
        tools = await client.list_tools()
        print(f"Available tools: {[tool['name'] for tool in tools['tools']]}")
        print()

        # Demo 1: Check current user and create a new session
        print("💫 Demo 1: Checking user context and creating session")
        whoami_result = await client.call_tool("whoami", {})
        # Handle both direct result and nested result formats
        if isinstance(whoami_result, dict):
            if "user_id" in whoami_result:
                print(f"User ID: {whoami_result['user_id']}")
                print(f"Session count: {whoami_result.get('session_count', 0)}")
                print(
                    f"Isolation mode: {whoami_result.get('isolation_mode', 'unknown')}"
                )
            else:
                print(f"Whoami result: {whoami_result}")
        else:
            print(f"Unexpected whoami result type: {type(whoami_result)}")
        print()

        # Sessions are created automatically on first bash command
        print("Creating session with first command...")
        result = await client.call_tool("bash", {"command": "pwd"})
        session_id = result["session_id"]
        print(f"Session created: {session_id}")
        print(f"Working directory: {result['working_directory']}")
        print()

        # Demo 2: Run commands in the session - state persists!
        print("🔧 Demo 2: Running commands with persistent state")

        # Set up project structure
        await client.call_tool(
            "bash",
            {
                "command": "cd / && mkdir -p myproject/src myproject/tests",
                "session_id": session_id,
            },
        )

        # Set environment variable
        await client.call_tool(
            "bash",
            {"command": "export PROJECT_NAME=MyAwesomeApp", "session_id": session_id},
        )

        # Create a Python file
        await client.call_tool(
            "bash",
            {
                "command": 'echo \'print("Hello from", "$PROJECT_NAME")\' > myproject/src/main.py',
                "session_id": session_id,
            },
        )

        # Verify state persisted - PWD and env var should still be set
        result = await client.call_tool(
            "bash",
            {
                "command": "pwd && echo $PROJECT_NAME && ls -la myproject/",
                "session_id": session_id,
            },
        )
        print("State persistence check:")
        print(result["stdout"])
        print()

        # Demo 3: Background tasks
        print("⚡ Demo 3: Background task execution")

        # Start a long-running command in background
        background_result = await client.call_tool(
            "bash",
            {
                "command": "echo 'Starting background task...' && echo 'Processing...' && echo 'Background task completed!' && ls /myproject",
                "session_id": session_id,
                "run_in_background": True,
            },
        )

        task_id = background_result["task_id"]
        print(f"Started background task: {task_id}")
        print(f"Status: {background_result['status']}")

        # Check task status
        status_result = await client.call_tool("get_task_output", {"task_id": task_id})
        print(f"Task status: {status_result.get('status', 'unknown')}")

        # Wait for completion
        final_result = await client.call_tool(
            "get_task_output", {"task_id": task_id, "wait": True}
        )
        print("Background task output:")
        if "stdout" in final_result:
            print(final_result["stdout"])
        else:
            print(f"Task result: {final_result}")
        print()

        # Demo 4: Multiple sessions - isolation
        print("🔒 Demo 4: Multiple sessions for isolation")

        # Create second session (automatically created with first bash command)
        result2 = await client.call_tool(
            "bash", {"command": 'echo PROJECT_NAME is: "$PROJECT_NAME" && pwd'}
        )
        session2_id = result2["session_id"]
        print(f"Created second session: {session2_id}")
        print("Second session (isolated):")
        print(result2["stdout"])

        # But first session still has it
        result1 = await client.call_tool(
            "bash",
            {
                "command": 'echo PROJECT_NAME is: "$PROJECT_NAME" && pwd',
                "session_id": session_id,
            },
        )
        print("First session (state preserved):")
        print(result1["stdout"])
        print()

        # Demo 5: Session management
        print("🗂️  Demo 5: Session management")

        # List all sessions
        sessions = await client.call_tool("list_sessions", {})
        print("Active sessions:")
        print(f"  Total sessions: {sessions['total']}")
        print(f"  Active sessions: {sessions['active']}")
        print(f"  Background tasks: {sessions['background_tasks']}")
        print(f"  User: {sessions['user']}")

        for session_id_key, session_info in sessions["sessions"].items():
            print(f"  Session {session_id_key}:")
            print(f"    Working directory: {session_info['working_directory']}")
            print(f"    Last command: {session_info.get('last_command', 'None')}")
            print(f"    Active: {session_info.get('active', False)}")

        # Get info about specific session
        info = await client.call_tool("get_session_state", {"session_id": session_id})
        print(f"\nSession {session_id} state:")
        print(f"  Working directory: {info['working_directory']}")
        print(f"  Environment vars: {len(info['environment'])}")
        print(f"  Lifetime: {info['lifetime']:.2f} seconds")
        print()

        # Demo 6: Complex workflow
        print("⚡ Demo 6: Complex multi-step workflow")

        # Create a Python script that uses the project structure
        script_content = """#!/usr/bin/env python3
import os
import sys

def main():
    project_name = os.getenv('PROJECT_NAME', 'Unknown')
    print(f"Welcome to {project_name}!")
    
    # List project files
    if os.path.exists('/myproject'):
        print("\\nProject files:")
        for item in os.listdir('/myproject'):
            print(f"  - {item}")
    
    print(f"\\nCurrent directory: {os.getcwd()}")
    print(f"Environment variables: {len(os.environ)} total")

if __name__ == "__main__":
    main()
"""

        # Write the script using echo (simulating file operations)
        # Here-docs don't work well in single-line context, so use echo instead
        await client.call_tool(
            "bash",
            {
                "command": f"echo '{script_content}' > /myproject/status.py",
                "session_id": session_id,
            },
        )

        # Make it executable and run it
        workflow_result = await client.call_tool(
            "bash",
            {"command": "cd /myproject && cat status.py", "session_id": session_id},
        )

        print("Workflow output:")
        print(workflow_result["stdout"])

        # Clean up sessions
        print("\n🧹 Cleaning up...")
        await client.call_tool("destroy_session", {"session_id": session_id})
        await client.call_tool("destroy_session", {"session_id": session2_id})
        print("Sessions destroyed")

        print("\n✅ Demo completed successfully!")
        print("\nKey takeaways:")
        print("  • Sessions maintain state (PWD, env vars, files) between commands")
        print("  • Multiple isolated sessions can run concurrently")
        print("  • Both shell commands and direct file operations are supported")
        print("  • Perfect for AI agents that need persistent context")

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()
    finally:
        await client.stop_server()


if __name__ == "__main__":
    asyncio.run(main())
