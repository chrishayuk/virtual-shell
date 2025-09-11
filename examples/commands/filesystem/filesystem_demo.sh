#!/bin/bash

# Filesystem Commands Comprehensive Demo
# This script demonstrates all filesystem commands with working examples

echo "=== FILESYSTEM COMMANDS DEMO ==="
echo

# Setup test environment
echo "Setting up test environment..."
mkdir -p /tmp/demo_dir/subdir1/subdir2
mkdir -p /tmp/demo_dir/empty_dir
mkdir -p /tmp/backup_dir

echo "Creating test files..."

# Using echo command to create files with content
echo "Hello, World!" > /tmp/demo_dir/hello.txt
echo "This is a test file." > /tmp/demo_dir/test.txt
echo "Line 1" > /tmp/demo_dir/multiline.txt
echo "Line 2" >> /tmp/demo_dir/multiline.txt
echo "Line 3" >> /tmp/demo_dir/multiline.txt
echo "Large file content" > /tmp/demo_dir/large.txt
echo "More content for large file" >> /tmp/demo_dir/large.txt

# Create files in subdirectory
echo "Subdirectory file" > /tmp/demo_dir/subdir1/sub_file.txt
echo "Deep file content" > /tmp/demo_dir/subdir1/subdir2/deep_file.txt

echo "Environment setup complete!"
echo

# 1. ECHO COMMAND
echo "=== 1. ECHO COMMAND ==="
echo "Basic output:"
echo "Hello from echo!"

echo "Output redirection to file:"
echo "New content" > /tmp/demo_dir/echo_output.txt
echo "Appended content" >> /tmp/demo_dir/echo_output.txt

echo "Echo with special characters:"
echo "Tab:\tNewline:\nEscape:\\n"
echo

# 2. TOUCH COMMAND  
echo "=== 2. TOUCH COMMAND ==="
echo "Creating new files with touch:"
touch /tmp/demo_dir/touched_file.txt
touch /tmp/demo_dir/file1.txt /tmp/demo_dir/file2.txt /tmp/demo_dir/file3.txt
echo "Files created: touched_file.txt, file1.txt, file2.txt, file3.txt"

echo "Updating timestamps on existing files:"
touch /tmp/demo_dir/hello.txt
echo "Timestamp updated on hello.txt"
echo

# 3. CAT COMMAND
echo "=== 3. CAT COMMAND ==="
echo "Display single file:"
cat /tmp/demo_dir/hello.txt

echo "Display multiple files (concatenated):"
cat /tmp/demo_dir/hello.txt /tmp/demo_dir/test.txt

echo "Cat with pipe input:"
echo "Piped content" | cat
echo

# 4. MORE COMMAND
echo "=== 4. MORE COMMAND ==="
echo "Display file page by page (more command):"
more /tmp/demo_dir/multiline.txt
echo

# 5. MKDIR COMMAND
echo "=== 5. MKDIR COMMAND ==="
echo "Create single directory:"
mkdir /tmp/new_directory

echo "Create nested directories with -p:"
mkdir -p /tmp/deep/nested/directory/structure

echo "Create multiple directories:"
mkdir /tmp/dir1 /tmp/dir2 /tmp/dir3
echo "Directories created: new_directory, /tmp/deep/nested/directory/structure, dir1, dir2, dir3"
echo

# 6. LS (using it to verify directory creation)
echo "Current directory structure:"
ls -la
echo

# 7. CP COMMAND
echo "=== 7. CP COMMAND ==="
echo "Copy single file:"
cp /tmp/demo_dir/hello.txt /tmp/demo_dir/hello_copy.txt

echo "Copy multiple files to directory:"
cp /tmp/demo_dir/file1.txt /tmp/demo_dir/file2.txt /tmp/backup_dir/

echo "Copy directory recursively:"
cp -r /tmp/demo_dir /tmp/backup_dir/demo_backup

echo "Verify copies:"
ls /tmp/backup_dir/
echo

# 8. MV COMMAND
echo "=== 8. MV COMMAND ==="
echo "Rename file:"
mv /tmp/demo_dir/file3.txt /tmp/demo_dir/renamed_file.txt

echo "Move file to directory:"
mv /tmp/demo_dir/touched_file.txt /tmp/backup_dir/

echo "Move directory:"
mv /tmp/dir3 /tmp/moved_directory

echo "Verify moves:"
ls /tmp/demo_dir/
ls /tmp/backup_dir/
echo

# 9. FIND COMMAND
echo "=== 9. FIND COMMAND ==="
echo "Find all .txt files:"
find . -name "*.txt"

echo "Find files by pattern:"
find . -name "*hello*"

echo "Find directories:"
find . -type d

echo "Find with path pattern:"
find /tmp/demo_dir -name "sub*"
echo

# 10. RM COMMAND
echo "=== 10. RM COMMAND ==="
echo "Remove single file:"
rm /tmp/demo_dir/echo_output.txt

echo "Remove multiple files:"
rm /tmp/demo_dir/file1.txt /tmp/demo_dir/file2.txt

echo "Remove files recursively:"
rm -r /tmp/dir1 /tmp/dir2

echo "Verify removals:"
ls /tmp/demo_dir/
echo

# 11. RMDIR COMMAND
echo "=== 11. RMDIR COMMAND ==="
echo "Remove empty directory:"
rmdir /tmp/demo_dir/empty_dir

echo "Try to remove non-empty directory (should fail):"
rmdir /tmp/demo_dir && echo "Success" || echo "Failed as expected - directory not empty"
echo

# 12. STORAGE INFORMATION COMMANDS
echo "=== 12. STORAGE INFORMATION ==="

echo "Disk space usage (df):"
df -h

echo "Directory space usage (du):"
du -h demo_dir

echo "Quota information:"
quota -h
echo

# 13. COMBINED OPERATIONS DEMO
echo "=== 13. COMBINED OPERATIONS DEMO ==="
echo "Creating a project structure with multiple commands:"

mkdir -p /tmp/project/{src,tests,docs,bin}
echo "Project created!" > /tmp/project/README.txt
echo "Source code here" > /tmp/project/src/main.py
echo "Test cases here" > /tmp/project/tests/test_main.py
echo "Documentation here" > /tmp/project/docs/README.md
echo "Binary files here" > /tmp/project/bin/executable

echo "Project structure:"
find /tmp/project -type f
echo

echo "Copy project for backup:"
cp -r /tmp/project /tmp/project_backup

echo "Find Python files in project:"
find /tmp/project -name "*.py"

echo "Show project file contents:"
cat /tmp/project/README.txt
cat /tmp/project/src/main.py

echo "Space usage of project:"
du -s /tmp/project

echo "=== FILESYSTEM DEMO COMPLETE ==="
echo "All filesystem commands demonstrated successfully!"