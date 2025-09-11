#!/bin/bash

# Navigation Commands Simple Demo
# This script demonstrates navigation commands working properly within /tmp

echo "=== NAVIGATION COMMANDS SIMPLE DEMO ==="
echo

# 1. PWD COMMAND - Print Working Directory
echo "=== 1. PWD COMMAND ==="
echo "Current working directory:"
pwd
echo

# 2. BASIC DIRECTORY SETUP in /tmp
echo "=== 2. SETUP DEMO ENVIRONMENT ==="
echo "Creating test directory structure in /tmp..."
mkdir -p /tmp/demo/level1/level2/level3
mkdir -p /tmp/demo/projects
mkdir -p /tmp/demo/documents
echo "Test file 1" > /tmp/demo/file1.txt
echo "Test file 2" > /tmp/demo/level1/file2.txt
echo "Deep file" > /tmp/demo/level1/level2/level3/deep.txt
echo "Project file" > /tmp/demo/projects/main.py
echo "Document file" > /tmp/demo/documents/readme.txt

echo "Demo environment created!"
echo

# 3. LS COMMAND - List Directory Contents
echo "=== 3. LS COMMAND ==="

echo "Basic directory listing of current directory:"
ls

echo "List demo directory contents:"
ls /tmp/demo/

echo "Long format listing (-l):"
ls -l /tmp/demo/

echo "List subdirectories:"
ls /tmp/demo/level1/
ls /tmp/demo/projects/
ls /tmp/demo/documents/

echo "Multiple directories at once:"
ls /tmp/demo/projects/ /tmp/demo/documents/
echo

# 4. CD COMMAND - Change Directory
echo "=== 4. CD COMMAND ==="

echo "Current directory before navigation:"
pwd

echo "Navigate to demo directory:"
cd /tmp/demo
echo "New current directory:"
pwd
echo "Contents:"
ls

echo "Navigate to level1:"
cd level1
echo "Current directory:"
pwd
echo "Contents:"
ls

echo "Navigate to level2:"
cd level2
echo "Current directory:"
pwd
echo "Contents:"
ls

echo "Navigate to level3:"
cd level3
echo "Current directory:"
pwd
echo "Contents:"
ls
echo "Display deep file:"
cat deep.txt

echo "Navigate up one level (..):"
cd ..
echo "Current directory:"
pwd

echo "Navigate up two levels:"
cd ../..
echo "Current directory:"
pwd

echo "Navigate to projects using relative path:"
cd projects
echo "Current directory:"
pwd
echo "Contents:"
ls
cat main.py

echo "Navigate to documents using absolute path:"
cd /tmp/demo/documents
echo "Current directory:"
pwd
echo "Contents:"
ls
cat readme.txt

echo "Return to root:"
cd /
echo "Back to root:"
pwd
echo

# 5. COMPREHENSIVE NAVIGATION DEMO
echo "=== 5. COMPREHENSIVE NAVIGATION ==="

echo "Navigation tour with pwd and ls at each stop:"

echo "Stop 1: Start at root"
cd /
pwd
ls

echo "Stop 2: Go to tmp"
cd tmp
pwd
ls

echo "Stop 3: Enter demo directory"
cd demo
pwd
ls -l

echo "Stop 4: Explore projects"
cd projects
pwd
ls -l

echo "Stop 5: Back to demo root"
cd ..
pwd

echo "Stop 6: Explore documents"
cd documents
pwd
ls -l

echo "Stop 7: Navigate to deep nested directory"
cd ../level1/level2/level3
pwd
ls -l

echo "Stop 8: Return home"
cd
pwd
ls

echo "Navigation tour complete!"
echo

# 6. VERIFICATION
echo "=== 6. VERIFICATION ==="
echo "Final verification of directory structure:"

echo "Listing entire demo structure:"
ls -R /tmp/demo/

echo "Current working directory:"
pwd

echo "=== NAVIGATION DEMO COMPLETE ==="
echo "All navigation commands (cd, pwd, ls) working perfectly!"