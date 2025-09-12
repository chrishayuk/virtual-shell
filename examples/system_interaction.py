#!/usr/bin/env python
"""Interact with virtual OS and subprocess"""

import os
import sys
import subprocess


def system_info():
    """Display system information"""
    print("=== System Information ===")

    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Current directory: {os.getcwd()}")

    # Environment variables
    print("\nEnvironment variables:")
    important_vars = ["USER", "HOME", "PATH", "SHELL"]
    for var in important_vars:
        value = os.getenv(var, "Not set")
        print(f"  {var}: {value}")

    print()


def directory_operations():
    """Demonstrate directory operations"""
    print("=== Directory Operations ===")

    # Create directory tree
    print("Creating directory structure...")
    os.makedirs("project/src", exist_ok=True)
    os.makedirs("project/tests", exist_ok=True)
    os.makedirs("project/docs", exist_ok=True)

    # Change directory
    original_dir = os.getcwd()
    os.chdir("project")
    print(f"Changed to: {os.getcwd()}")

    # Create files in subdirectories
    with open("src/main.py", "w") as f:
        f.write('# Main application file\nprint("Hello from main")\n')

    with open("tests/test_main.py", "w") as f:
        f.write('# Test file\nprint("Running tests...")\n')

    with open("docs/README.md", "w") as f:
        f.write("# Project Documentation\n\nThis is the project readme.\n")

    # List directory tree
    print("\nProject structure:")
    for root, dirs, files in os.walk("."):
        level = root.replace(".", "").count(os.sep)
        indent = " " * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = " " * 2 * (level + 1)
        for file in files:
            print(f"{subindent}{file}")

    # Change back
    os.chdir(original_dir)
    print(f"\nChanged back to: {os.getcwd()}\n")


def subprocess_demo():
    """Demonstrate subprocess execution"""
    print("=== Subprocess Execution ===")

    # Execute echo command
    print("Running: echo 'Hello from subprocess'")
    result = subprocess.run(
        ["echo", "Hello from subprocess"], capture_output=True, text=True
    )
    print(f"Output: {result.stdout}")
    print(f"Return code: {result.returncode}")

    # List files
    print("\nRunning: ls")
    result = subprocess.run(["ls"], capture_output=True, text=True)
    print(f"Files:\n{result.stdout}")

    # Create and read file via subprocess
    print("Creating file via subprocess...")
    subprocess.run(["echo", "Subprocess created this"], capture_output=True, text=True)

    print()


def path_operations():
    """Demonstrate path operations"""
    print("=== Path Operations ===")

    test_paths = [
        "file.txt",
        "project/src/main.py",
        "/absolute/path/file.py",
        "../parent/file.txt",
    ]

    for path in test_paths:
        print(f"\nPath: {path}")
        print(f"  Basename: {os.path.basename(path)}")
        print(f"  Dirname: {os.path.dirname(path)}")
        print(f"  Absolute: {os.path.abspath(path)}")
        print(f"  Exists: {os.path.exists(path)}")

        # Create the file if it's simple
        if "/" not in path:
            with open(path, "w") as f:
                f.write("test")
            print(f"  Is file: {os.path.isfile(path)}")
            print(f"  Is dir: {os.path.isdir(path)}")

    # Join paths
    print("\nPath joining:")
    parts = ["home", "user", "documents", "file.txt"]
    joined = os.path.join(*parts)
    print(f"  Parts: {parts}")
    print(f"  Joined: {joined}")

    print()


def file_checking():
    """Check various file conditions"""
    print("=== File Checking ===")

    # Create test files
    with open("readable.txt", "w") as f:
        f.write("This file exists and is readable")

    os.makedirs("test_dir", exist_ok=True)

    # Check conditions
    checks = [
        ("readable.txt", "exists", os.path.exists),
        ("readable.txt", "is file", os.path.isfile),
        ("readable.txt", "is dir", os.path.isdir),
        ("test_dir", "exists", os.path.exists),
        ("test_dir", "is file", os.path.isfile),
        ("test_dir", "is dir", os.path.isdir),
        ("nonexistent", "exists", os.path.exists),
    ]

    for path, check_name, check_func in checks:
        result = check_func(path)
        status = "✓" if result else "✗"
        print(f"  {status} {path} {check_name}: {result}")

    print()


def environment_manipulation():
    """Manipulate environment variables"""
    print("=== Environment Manipulation ===")

    # Set new environment variable
    os.environ["MY_CUSTOM_VAR"] = "CustomValue123"
    print("Set MY_CUSTOM_VAR = 'CustomValue123'")

    # Read it back
    value = os.getenv("MY_CUSTOM_VAR")
    print(f"Read back: {value}")

    # Check if variable exists
    print(f"Exists: {'MY_CUSTOM_VAR' in os.environ}")

    # Get with default
    missing = os.getenv("MISSING_VAR", "default_value")
    print(f"Missing var with default: {missing}")

    print()


def exception_handling():
    """Demonstrate exception handling with file operations"""
    print("=== Exception Handling ===")

    # Try to read non-existent file
    try:
        with open("does_not_exist.txt", "r") as f:
            content = f.read()
    except FileNotFoundError:
        print("Caught FileNotFoundError: File not found")

    # Try to create file in non-existent directory
    try:
        with open("missing_dir/file.txt", "w") as f:
            f.write("test")
    except FileNotFoundError:
        print("Caught: Cannot create file in non-existent directory")

    # Safe file operations
    def safe_read(filename):
        try:
            with open(filename, "r") as f:
                return f.read()
        except FileNotFoundError:
            return None

    content = safe_read("missing.txt")
    print(f"Safe read result: {content}")

    print()


def cleanup():
    """Clean up created files"""
    print("=== Cleanup ===")

    files_to_remove = ["file.txt", "readable.txt", "python_hello.txt"]

    dirs_to_remove = ["test_dir", "project", "python_data"]

    for file in files_to_remove:
        if os.path.exists(file):
            os.remove(file)
            print(f"  Removed {file}")

    # Note: Directory removal would need rmdir implementation
    # For now, just list what would be removed
    for dir in dirs_to_remove:
        if os.path.exists(dir):
            print(f"  Would remove directory: {dir}")

    print("\nCleanup complete!")


def main():
    print("=== System Interaction Demo ===\n")

    system_info()
    directory_operations()
    subprocess_demo()
    path_operations()
    file_checking()
    environment_manipulation()
    exception_handling()
    cleanup()


if __name__ == "__main__":
    main()
