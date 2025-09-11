#!/bin/sh
# Simple hello world script for virtual shell

echo "Hello from Virtual Shell!"
echo "Current directory: $(pwd)"
echo "Current user: $(whoami)"
echo "System uptime: $(uptime)"

# Set a variable using export
export NAME="Virtual Shell User"
echo "Welcome, $NAME!"

# Create a file
echo "This file was created by a script" > hello_output.txt
echo "File created: hello_output.txt"

# List files
echo ""
echo "Files in current directory:"
ls -la