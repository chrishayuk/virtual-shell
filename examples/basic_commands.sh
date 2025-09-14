#!/bin/bash
# Basic Commands Demo
# This script demonstrates basic shell commands and navigation

echo "========================================="
echo "Basic Shell Commands Demo"
echo "========================================="
echo ""

# ==========================
# 1. Navigation
# ==========================
echo "=== 1. Navigation Commands ==="
echo ""

echo "Current directory:"
pwd
echo ""

echo "Creating directories:"
mkdir -p /demo/project/src
mkdir -p /demo/project/tests
echo "Created /demo/project structure"
echo ""

echo "Changing directory:"
cd /demo/project
echo "Now in: $(pwd)"
cd src
echo "Now in: $(pwd)"
cd ..
echo "Back to: $(pwd)"
cd /
echo "Back to root: $(pwd)"
echo ""

# ==========================
# 2. File Operations
# ==========================
echo "=== 2. File Operations ==="
echo ""

echo "Creating files:"
touch /demo/file1.txt
echo "Hello World" > /demo/file2.txt
echo "Line 1" > /demo/file3.txt
echo "Line 2" >> /demo/file3.txt
echo "Created 3 files"
echo ""

echo "Listing files:"
ls /demo
echo ""

echo "Detailed listing:"
ls -la /demo
echo ""

echo "Reading file contents:"
echo "file2.txt contains:"
cat /demo/file2.txt
echo ""
echo "file3.txt contains:"
cat /demo/file3.txt
echo ""

# ==========================
# 3. File Manipulation
# ==========================
echo "=== 3. File Manipulation ==="
echo ""

echo "Copying files:"
cp /demo/file2.txt /demo/file2_copy.txt
echo "Copied file2.txt to file2_copy.txt"
ls /demo/*.txt
echo ""

echo "Moving/renaming files:"
mv /demo/file1.txt /demo/renamed_file.txt
echo "Renamed file1.txt to renamed_file.txt"
ls /demo/*.txt
echo ""

echo "Removing files:"
rm /demo/file2_copy.txt
echo "Removed file2_copy.txt"
ls /demo/*.txt
echo ""

# ==========================
# 4. Directory Operations
# ==========================
echo "=== 4. Directory Operations ==="
echo ""

echo "Creating nested directories:"
mkdir -p /demo/deep/nested/structure
echo "Created deep nested structure"
tree /demo
echo ""

echo "Copying directories:"
cp -r /demo/project /demo/project_backup
echo "Created backup of project directory"
ls /demo
echo ""

echo "Removing directories:"
rm -rf /demo/project_backup
echo "Removed backup directory"
ls /demo
echo ""

# ==========================
# 5. Environment Variables
# ==========================
echo "=== 5. Environment Variables ==="
echo ""

echo "Setting variables:"
export MY_VAR="Hello from shell"
export COUNT=42
echo "MY_VAR=$MY_VAR"
echo "COUNT=$COUNT"
echo ""

echo "Using variables in commands:"
echo "The value of MY_VAR is: $MY_VAR"
echo "COUNT plus 1 is: $((COUNT + 1))"
echo ""

echo "Listing all environment variables:"
env | head -5
echo "... (showing first 5)"
echo ""

# ==========================
# 6. Command Output
# ==========================
echo "=== 6. Working with Command Output ==="
echo ""

echo "Redirecting output to file:"
echo "This is saved to a file" > /demo/output.txt
echo "This is appended" >> /demo/output.txt
cat /demo/output.txt
echo ""

echo "Counting lines, words, characters:"
wc /demo/output.txt
echo ""

echo "Using command substitution:"
FILE_COUNT=$(ls /demo/*.txt | wc -l)
echo "Number of .txt files: $FILE_COUNT"
echo ""

# ==========================
# 7. Basic Pipes
# ==========================
echo "=== 7. Basic Pipes ==="
echo ""

echo "Creating sample data:"
echo "apple" > /demo/fruits.txt
echo "banana" >> /demo/fruits.txt
echo "cherry" >> /demo/fruits.txt
echo "date" >> /demo/fruits.txt
echo ""

echo "Using pipes to filter:"
echo "Fruits containing 'a':"
cat /demo/fruits.txt | grep a
echo ""

echo "Counting lines with pipe:"
echo "Number of fruits:"
cat /demo/fruits.txt | wc -l
echo ""

# ==========================
# Cleanup
# ==========================
echo "=== Cleanup ==="
rm -rf /demo
echo "Demo files cleaned up"
echo ""

echo "========================================="
echo "Basic Commands Demo Complete!"
echo "========================================="