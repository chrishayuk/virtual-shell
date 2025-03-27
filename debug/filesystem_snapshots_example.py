"""
Example usage of the enhanced virtual filesystem with snapshots and templates
"""
import os
from virtual_shell.shell_interpreter import ShellInterpreter
from virtual_shell.filesystem.snapshot_manager import SnapshotManager
from virtual_shell.filesystem.template_loader import TemplateLoader

# Utility function to list files recursively
def list_files_recursively(fs, start_path="/"):
    """
    Recursively list all files and directories in the given path
    
    Args:
        fs: Filesystem instance
        start_path: Path to start listing from
        
    Returns:
        List of file and directory paths
    """
    paths = []
    try:
        # Find all paths recursively
        all_paths = fs.find(start_path, recursive=True)
        paths = sorted(all_paths)
    except Exception as e:
        print(f"Error listing files: {e}")
    
    return paths

# Example 1: Basic usage with snapshots
def example_snapshot_usage(shell):
    print("===== Example: Snapshot Usage =====")
    
    # Create snapshot manager
    snapshot_mgr = SnapshotManager(shell.fs)
    
    # Create some initial content
    shell.fs.mkdir("/home/user/projects")
    shell.fs.write_file("/home/user/hello.txt", "Hello World")
    shell.fs.mkdir("/home/user/documents")
    
    # Create a snapshot of the initial state
    initial_snapshot = snapshot_mgr.create_snapshot("initial_state", "Initial filesystem setup")
    print(f"Created snapshot: {initial_snapshot}")
    
    # Make some changes
    shell.fs.mkdir("/home/user/projects/python")
    shell.fs.write_file("/home/user/projects/python/hello.py", 'print("Hello")')
    shell.fs.rm("/home/user/hello.txt")
    
    # List current files
    print("\nCurrent files after changes:")
    current_paths = list_files_recursively(shell.fs, "/home/user")
    for path in current_paths:
        print(path)
    
    # Create another snapshot
    modified_snapshot = snapshot_mgr.create_snapshot("modified_state", "After adding project files")
    print(f"Created snapshot: {modified_snapshot}")
    
    # List available snapshots
    print("\nAvailable snapshots:")
    snapshots = snapshot_mgr.list_snapshots()
    for snap in snapshots:
        print(f"- {snap['name']}: {snap['description']} (created: {snap['created']})")
    
    # Restore to initial state
    print("\nRestoring to initial state...")
    snapshot_mgr.restore_snapshot("initial_state")
    
    # Verify restore
    print("\nFiles after restore to initial state:")
    initial_paths = list_files_recursively(shell.fs, "/home/user")
    for path in initial_paths:
        print(path)
    
    # Export a snapshot
    export_path = "/tmp/fs_snapshot.json"
    snapshot_mgr.export_snapshot("modified_state", export_path)
    print(f"\nExported snapshot to: {export_path}")
    
    # Restore to modified state
    print("\nRestoring to modified state...")
    snapshot_mgr.restore_snapshot("modified_state")
    
    # Verify restore
    print("\nFiles after restore to modified state:")
    modified_paths = list_files_recursively(shell.fs, "/home/user")
    for path in modified_paths:
        print(path)

# Example 2: Template loading
def example_template_usage(shell):
    print("\n===== Example: Template Usage =====")
    
    # Create template loader
    template_loader = TemplateLoader(shell.fs)
    
    # Example template as Python dictionary
    python_project_template = {
        "directories": [
            "/home/user/project",
            "/home/user/project/src",
            "/home/user/project/tests",
            "/home/user/project/docs"
        ],
        "files": [
            {
                "path": "/home/user/project/README.md",
                "content": "# ${project_name}\n\n${project_description}\n\n## Installation\n\n```\npip install ${project_name}\n```"
            },
            {
                "path": "/home/user/project/src/__init__.py",
                "content": "# ${project_name} package"
            },
            {
                "path": "/home/user/project/src/main.py",
                "content": "def main():\n    print('Hello from ${project_name}!')\n\nif __name__ == '__main__':\n    main()"
            },
            {
                "path": "/home/user/project/tests/test_main.py",
                "content": "import unittest\n\nclass TestMain(unittest.TestCase):\n    def test_example(self):\n        self.assertTrue(True)"
            }
        ]
    }
    
    # Variables for template substitution
    variables = {
        "project_name": "awesome-project",
        "project_description": "A really awesome Python project template"
    }
    
    # Apply the template with variables
    print("Applying Python project template...")
    template_loader.apply_template(python_project_template, variables=variables)
    
    # List created files
    print("\nTemplate created the following structure:")
    project_paths = list_files_recursively(shell.fs, "/home/user/project")
    for path in project_paths:
        print(path)
    
    # Display README content
    print("\nREADME.md content:")
    readme_content = shell.fs.read_file("/home/user/project/README.md")
    print(readme_content)
    
    # Quick load some additional files
    additional_files = {
        "/home/user/project/LICENSE": "MIT License\nCopyright (c) 2025",
        "/home/user/project/.gitignore": "*.pyc\n__pycache__/\n.venv/\n"
    }
    
    print("\nQuick loading additional files...")
    template_loader.quick_load(additional_files)
    
    # Display all files now
    print("\nFinal project structure:")
    final_project_paths = list_files_recursively(shell.fs, "/home/user/project")
    for path in final_project_paths:
        print(path)

# Example 3: Combined usage for a sandbox environment
def example_sandbox_environment(shell):
    print("\n===== Example: Sandbox Environment =====")
    
    # Create snapshot manager and template loader
    snapshot_mgr = SnapshotManager(shell.fs)
    template_loader = TemplateLoader(shell.fs)
    
    # Define a sandbox template
    sandbox_template = {
        "directories": [
            "/home/student",
            "/home/student/assignments",
            "/home/student/examples",
            "/shared"
        ],
        "files": [
            {
                "path": "/home/student/README.txt",
                "content": "Welcome to the ${course_name} sandbox environment!\n\nYou can find assignments in the /home/student/assignments directory.\nExample code is available in /home/student/examples.\nShared resources are in /shared.\n\nInstructor: ${instructor}"
            },
            {
                "path": "/home/student/assignments/assignment1.py",
                "content": "# ${course_name} - Assignment 1\n\ndef main():\n    # TODO: Implement the solution\n    pass\n\nif __name__ == '__main__':\n    main()"
            },
            {
                "path": "/home/student/examples/example1.py",
                "content": "# Example 1 - Hello World\n\nprint('Hello, World!')"
            }
        ]
    }
    
    # Variables for the sandbox
    variables = {
        "course_name": "Python Programming Fundamentals",
        "instructor": "Dr. Smith"
    }
    
    # Apply the template
    print("Setting up sandbox environment...")
    template_loader.apply_template(sandbox_template, variables=variables)
    
    # Create a snapshot of the initial sandbox state
    initial_snapshot = snapshot_mgr.create_snapshot("sandbox_initial", "Initial sandbox setup")
    print(f"Created initial sandbox snapshot: {initial_snapshot}")
    
    # Add a shared resource
    shell.fs.write_file("/shared/utils.py", "Common utility functions for assignments")
    
    # Simulate student working on assignment
    shell.fs.write_file("/home/student/assignments/assignment1.py", 'def solve_problem():\n    return 42')
    
    # Create a snapshot after student work
    student_work_snapshot = snapshot_mgr.create_snapshot("student_work", "Student progress on assignment")
    print(f"Created student work snapshot: {student_work_snapshot}")
    
    # List available files
    print("\nSandbox environment structure:")
    sandbox_paths = list_files_recursively(shell.fs, "/home/student")
    shared_paths = list_files_recursively(shell.fs, "/shared")
    print("Student directory:")
    for path in sandbox_paths:
        print(path)
    print("\nShared directory:")
    for path in shared_paths:
        print(path)
    
    # Demonstrate restoring to initial state
    print("\nRestoring to initial sandbox state...")
    snapshot_mgr.restore_snapshot("sandbox_initial")
    
    # Verify restore
    print("\nFiles after restoring to initial state:")
    restored_paths = list_files_recursively(shell.fs, "/home/student")
    restored_shared_paths = list_files_recursively(shell.fs, "/shared")
    print("Student directory:")
    for path in restored_paths:
        print(path)
    print("\nShared directory:")
    for path in restored_shared_paths:
        print(path)
    
    # Export the sandbox configuration
    export_path = "/tmp/sandbox_config.json"
    snapshot_mgr.export_snapshot("student_work", export_path)
    print(f"\nExported sandbox configuration to: {export_path}")

# Run the examples
def main():
    # Create a shell with default memory filesystem
    shell = ShellInterpreter()
    
    # Run the examples with the shell
    example_snapshot_usage(shell)
    example_template_usage(shell)
    example_sandbox_environment(shell)

if __name__ == "__main__":
    main()