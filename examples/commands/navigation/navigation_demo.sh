#!/bin/bash

# Navigation Commands Comprehensive Demo
# This script demonstrates all navigation commands with working examples

echo "=== NAVIGATION COMMANDS DEMO ==="
echo

# Setup test environment
echo "Setting up navigation test environment..."
mkdir -p /tmp/nav_test/level1/level2/level3
mkdir -p /tmp/nav_test/level1/level2/alt_level3
mkdir -p /tmp/nav_test/level1/alt_level2
mkdir -p /tmp/nav_test/alt_level1
mkdir -p /tmp/nav_test/hidden/.hidden_dir
mkdir -p /tmp/nav_test/documents
mkdir -p /tmp/nav_test/projects/project1
mkdir -p /tmp/nav_test/projects/project2

# Create test files
echo "Main file" > /tmp/nav_test/main.txt
echo "Level 1 file" > /tmp/nav_test/level1/file1.txt
echo "Level 2 file" > /tmp/nav_test/level1/level2/file2.txt
echo "Level 3 file" > /tmp/nav_test/level1/level2/level3/file3.txt
echo "Hidden file" > /tmp/nav_test/hidden/.hidden_file
echo "Doc file 1" > /tmp/nav_test/documents/doc1.txt
echo "Doc file 2" > /tmp/nav_test/documents/doc2.txt
echo "Project 1 file" > /tmp/nav_test/projects/project1/main.py
echo "Project 2 file" > /tmp/nav_test/projects/project2/app.js

echo "Navigation environment setup complete!"
echo

# 1. PWD COMMAND - Print Working Directory
echo "=== 1. PWD COMMAND ==="
echo "Current working directory:"
pwd
echo

# 2. LS COMMAND - List Directory Contents
echo "=== 2. LS COMMAND ==="

echo "Basic directory listing:"
ls

echo "List current directory contents:"
ls /tmp/nav_test/

echo "Long format listing (-l):"
ls -l /tmp/nav_test/

echo "Show all files including hidden (-a):"
ls -a /tmp/nav_test/hidden/

echo "Combined long format with hidden files:"
ls -la /tmp/nav_test/hidden/

echo "List specific directories:"
ls /tmp/nav_test/documents/
ls /tmp/nav_test/projects/

echo "List multiple directories:"
ls /tmp/nav_test/level1/ /tmp/nav_test/documents/
echo

# 3. CD COMMAND - Change Directory
echo "=== 3. CD COMMAND ==="

echo "Current directory before navigation:"
pwd

echo "Navigate to nav_test directory:"
cd /tmp/nav_test
echo "New current directory:"
pwd

echo "Navigate to nested directory:"
cd level1/level2
echo "Current directory:"
pwd

echo "Navigate up one level (..):"
cd ..
echo "Current directory:"
pwd

echo "Navigate up multiple levels:"
cd ../..
echo "Back to:"
pwd

echo "Navigate with absolute path:"
cd /tmp/nav_test/projects/project1
echo "Current directory:"
pwd

echo "Navigate to tmp directory (home not available in virtual shell):"
cd /tmp
echo "Tmp directory:"
pwd

echo "Navigate back to our test area:"
cd /tmp/nav_test
echo "Back in test area:"
pwd
echo

# 4. NAVIGATION PATTERNS DEMO
echo "=== 4. NAVIGATION PATTERNS ==="

echo "Exploring directory structure with navigation:"

echo "Starting from nav_test, explore each level:"
cd /tmp/nav_test
cd level1
pwd
ls

echo "Go deeper:"
cd level2
pwd
ls

echo "Explore deepest level:"
cd level3
pwd
ls
cat file3.txt

echo "Navigate to sibling directory:"
cd ../alt_level3
pwd

echo "Navigate back to level1 from deep directory:"
cd ../../..
pwd

echo "Quick navigation to projects:"
cd projects
pwd
ls

echo "Explore project1:"
cd project1
pwd
ls
cat main.py

echo "Switch to project2:"
cd ../project2
pwd
ls
cat app.js

echo "Return to nav_test root:"
cd ../..
pwd
echo

# 5. LISTING VARIATIONS DEMO
echo "=== 5. LISTING VARIATIONS ==="

echo "Different listing styles for various directories:"

echo "Documents directory - standard listing:"
ls documents/

echo "Documents directory - detailed listing:"
ls -l documents/

echo "Projects directory structure:"
ls projects/
ls -l projects/project1/
ls -l projects/project2/

echo "Hidden files exploration:"
ls hidden/
ls -a hidden/
ls -la hidden/

echo "Multi-level directory exploration:"
ls level1/
ls level1/level2/
ls level1/level2/level3/
echo

# 6. COMBINED NAVIGATION AND LISTING
echo "=== 6. COMBINED OPERATIONS ==="

echo "Navigation tour with listings at each stop:"

echo "Tour stop 1: Documents"
cd documents
pwd
ls -la

echo "Tour stop 2: Projects overview"
cd ../projects
pwd
ls

echo "Tour stop 3: Project 1 details"
cd project1
pwd
ls -l

echo "Tour stop 4: Back to projects, then project 2"
cd ..
pwd
cd project2
pwd
ls -l

echo "Tour stop 5: Deep dive into nested structure"
cd ../../level1/level2/level3
pwd
ls -la

echo "Tour stop 6: Return to tmp"
cd /tmp
pwd
echo

# 7. DIRECTORY VERIFICATION DEMO
echo "=== 7. DIRECTORY VERIFICATION ==="

echo "Verify directory structure with navigation and listing:"

echo "Navigate and verify nav_test structure:"
cd /tmp/nav_test
echo "Contents of nav_test:"
ls -la

echo "Verify level1 and its contents:"
cd level1
ls -la

echo "Verify level2 and its contents:"  
cd level2
ls -la

echo "Verify level3:"
cd level3
ls -la

echo "Navigate back and verify documents:"
cd ../../../documents
ls -la

echo "Verify projects structure:"
cd ../projects
ls -la
ls project1/
ls project2/

echo "Final verification - return to original directory:"
cd ../..
pwd
echo

# 8. ERROR HANDLING DEMO
echo "=== 8. ERROR HANDLING ==="

echo "Demonstrate error cases:"

echo "Try to list non-existent directory:"
ls non_existent_directory || echo "Error handled: Directory does not exist"

echo "Try to navigate to non-existent directory:"
cd non_existent_directory || echo "Error handled: Cannot change to non-existent directory"

echo "Verify we're still in correct directory after failed navigation:"
pwd

echo "Try to list with various invalid paths:"
ls nav_test/non_existent || echo "Error handled: Path does not exist"
echo

# 9. PRACTICAL NAVIGATION SCENARIOS
echo "=== 9. PRACTICAL SCENARIOS ==="

echo "Scenario 1: Finding and navigating to project files"
echo "Looking for Python files:"
find . -name "*.py"
echo "Navigate to project with Python file:"
cd nav_test/projects/project1
pwd
cat main.py

echo "Scenario 2: Working with document directories"
echo "Navigate to documents and list contents:"
cd ../../../documents
pwd
ls -l

echo "Scenario 3: Exploring hidden directories"
echo "Navigate to and explore hidden directories:"
cd ../hidden
pwd
ls -a

echo "Return to starting directory:"
cd ../..
pwd
echo

echo "=== NAVIGATION DEMO COMPLETE ==="
echo "All navigation commands demonstrated successfully!"
echo "Final directory listing to show created structure:"
ls -la nav_test/