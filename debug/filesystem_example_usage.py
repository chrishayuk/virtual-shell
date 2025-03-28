"""
filesystem_example_usage.py - Example usage of the virtual filesystem
"""
from virtual_shell.filesystem import VirtualFileSystem
from virtual_shell.filesystem.template_loader import TemplateLoader

def basic_example():
    """Basic usage example of the virtual filesystem"""
    # Create filesystem with default memory provider
    fs = VirtualFileSystem()
    
    # Create some directories
    fs.mkdir("/home/user")
    fs.mkdir("/home/user/documents")
    
    # Create and write to a file
    fs.write_file("/home/user/documents/hello.txt", "Hello, Virtual World!")
    
    # Read from a file
    content = fs.read_file("/home/user/documents/hello.txt")
    print(f"File content: {content}")
    
    # List directory contents
    files = fs.ls("/home/user/documents")
    print(f"Files in documents: {files}")
    
    # Change directory and get current path
    fs.cd("/home/user/documents")
    print(f"Current path: {fs.pwd()}")
    
    # Copy a file
    fs.cp("hello.txt", "hello_copy.txt")
    
    # List directory again
    files = fs.ls()
    print(f"Files after copy: {files}")
    
    # Get storage stats
    stats = fs.get_storage_stats()
    print(f"Storage stats: {stats}")


def provider_example():
    """Example showing different storage providers"""
    # Start with memory provider
    fs = VirtualFileSystem("memory")
    
    # Create a file
    fs.write_file("/test.txt", "This is in memory")
    print(f"Provider: {fs.get_provider_name()}")
    print(f"Content: {fs.read_file('/test.txt')}")
    
    try:
        # Try to switch to SQLite provider
        if fs.change_provider("sqlite", db_path=":memory:"):
            print(f"Switched to provider: {fs.get_provider_name()}")
            
            # Create a file in SQLite provider
            fs.write_file("/test.txt", "This is in SQLite")
            print(f"Content: {fs.read_file('/test.txt')}")
    except Exception as e:
        print(f"SQLite provider not available: {e}")
    
    try:
        # Try to use S3 provider (requires boto3 and AWS credentials)
        s3_fs = VirtualFileSystem("s3", 
                                 bucket_name="my-test-bucket",
                                 region_name="us-east-1")
        print(f"Created S3 provider: {s3_fs.get_provider_name()}")
    except Exception as e:
        print(f"S3 provider not available: {e}")


def advanced_operations():
    """Example demonstrating advanced filesystem operations"""
    fs = VirtualFileSystem()
    
    # Create a directory structure
    fs.mkdir("/projects")
    fs.mkdir("/projects/app1")
    fs.mkdir("/projects/app1/src")
    fs.mkdir("/projects/app1/docs")
    
    # Create multiple files
    fs.write_file("/projects/app1/src/main.py", "print('Hello, World!')")
    fs.write_file("/projects/app1/README.md", "# App1\n\nExample project")
    fs.write_file("/projects/app1/docs/index.md", "# Documentation\n\nWelcome")
    
    # Search for files
    results = fs.search("/projects", "*.md", recursive=True)
    print(f"Markdown files: {results}")
    
    # Find all files and directories
    all_items = fs.find("/projects", recursive=True)
    print(f"All items: {all_items}")
    
    # Move a file
    fs.mv("/projects/app1/README.md", "/projects/app1/docs/README.md")
    
    # Get file info
    info = fs.get_node("/projects/app1/src/main.py")
    print(f"File info: {info}")
    
    # Get filesystem info
    fs_info = fs.get_fs_info()
    print(f"Filesystem info: {fs_info}")


def template_example():
    """Example demonstrating filesystem template usage"""
    # Create filesystem
    fs = VirtualFileSystem()
    
    # Create template loader
    template_loader = TemplateLoader(fs)
    
    # Define a Python project template
    python_project_template = {
        "directories": [
            "/projects/${project_name}",
            "/projects/${project_name}/src",
            "/projects/${project_name}/tests",
            "/projects/${project_name}/docs"
        ],
        "files": [
            {
                "path": "/projects/${project_name}/README.md",
                "content": "# ${project_name}\n\n## Description\n${project_description}\n\n## Setup\n```bash\npip install -r requirements.txt\n```"
            },
            {
                "path": "/projects/${project_name}/requirements.txt",
                "content": "# Project dependencies\npytest\nrequests\n"
            },
            {
                "path": "/projects/${project_name}/src/${project_name}/__init__.py",
                "content": "\"\"\"${project_name} package\"\"\"\n__version__ = '${project_version}'"
            },
            {
                "path": "/projects/${project_name}/src/${project_name}/main.py",
                "content": "def main():\n    print('Hello from ${project_name}!')\n\nif __name__ == '__main__':\n    main()"
            },
            {
                "path": "/projects/${project_name}/tests/test_main.py",
                "content": "from ${project_name}.main import main\n\ndef test_main():\n    assert main() is None"
            }
        ]
    }
    
    # Variables for template substitution
    template_variables = {
        "project_name": "awesome_project",
        "project_description": "A sample Python project created using filesystem template",
        "project_version": "0.1.0"
    }
    
    # Apply the template
    print("===== Filesystem Template Example =====")
    print("Applying Python project template...")
    template_loader.apply_template(python_project_template, variables=template_variables)
    
    # Quick load additional files
    additional_files = {
        "/projects/awesome_project/LICENSE": "MIT License\nCopyright (c) 2024",
        "/projects/awesome_project/.gitignore": "*.pyc\n__pycache__/\n.venv/"
    }
    print("\nQuick loading additional files...")
    template_loader.quick_load(additional_files)
    
    # List created project structure
    print("\nCreated project structure:")
    project_paths = fs.find("/projects/awesome_project", recursive=True)
    for path in sorted(project_paths):
        print(path)
    
    # Verify file contents
    print("\nREADME.md contents:")
    readme_content = fs.read_file("/projects/awesome_project/README.md")
    print(readme_content)
    
    print("\nMain script contents:")
    main_script_content = fs.read_file("/projects/awesome_project/src/awesome_project/main.py")
    print(main_script_content)

if __name__ == "__main__":
    # Run examples
    print("===== Basic Example =====")
    basic_example()
    
    print("\n===== Provider Example =====")
    provider_example()
    
    print("\n===== Advanced Operations =====")
    advanced_operations()
    
    print("\n===== Template Example =====")
    template_example()