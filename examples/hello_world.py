#!/usr/bin/env python
"""Simple hello world script for virtual shell Python environment"""

import os
import sys


def main():
    print("Hello from Virtual Shell Python!")
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")

    # Environment variables
    user = os.getenv("USER", "Unknown")
    print(f"Current user: {user}")

    # Create a file
    with open("python_hello.txt", "w") as f:
        f.write("This file was created by Python\n")
        f.write("Running in the virtual filesystem\n")

    print("\nFile 'python_hello.txt' created")

    # List directory contents
    print("\nDirectory contents:")
    for item in os.listdir("."):
        print(f"  - {item}")

    # Read the file we created
    print("\nReading back the file:")
    with open("python_hello.txt", "r") as f:
        content = f.read()
        print(content)


if __name__ == "__main__":
    main()
