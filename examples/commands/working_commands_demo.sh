#!/bin/bash

# Working Commands Demo
# Demonstrates all the virtual shell commands that work properly

echo "=========================================="
echo "VIRTUAL SHELL - WORKING COMMANDS DEMO"
echo "=========================================="
echo "This demo tests all major command categories with working examples"
echo "that operate within the virtual shell's security constraints."
echo
echo "Working within allowed directories: /tmp, /home/user"
echo "Time: $(date)"
echo "=========================================="
echo

# 1. ENVIRONMENT & SYSTEM COMMANDS
echo "=== 1. ENVIRONMENT & SYSTEM COMMANDS ==="
echo

echo "Current user and system info:"
whoami
uptime

echo "Environment variables:"
env | head -10

echo "Setting environment variables:"
export DEMO_VAR="Hello Virtual Shell"
export TEST_PATH="/tmp/demo"
echo "DEMO_VAR = $DEMO_VAR"
echo "TEST_PATH = $TEST_PATH"
echo

# 2. FILESYSTEM COMMANDS
echo "=== 2. FILESYSTEM COMMANDS ==="
echo

echo "Creating directory structure:"
mkdir -p /tmp/demo/{src,docs,tests}
mkdir -p /tmp/demo/data

echo "Creating files with echo:"
echo "Hello World!" > /tmp/demo/hello.txt
echo "Line 1" > /tmp/demo/multiline.txt
echo "Line 2" >> /tmp/demo/multiline.txt
echo "Line 3" >> /tmp/demo/multiline.txt
echo "Source code here" > /tmp/demo/src/main.py
echo "Documentation" > /tmp/demo/docs/README.md
echo "Test cases" > /tmp/demo/tests/test.py

echo "Files created successfully!"

echo "Display file contents with cat:"
cat /tmp/demo/hello.txt
cat /tmp/demo/multiline.txt

echo "Create more files with touch:"
touch /tmp/demo/file1.txt /tmp/demo/file2.txt

echo "Copy files:"
cp /tmp/demo/hello.txt /tmp/demo/hello_backup.txt

echo "Move/rename files:"
mv /tmp/demo/file2.txt /tmp/demo/renamed_file.txt

echo "Find files:"
find /tmp/demo -name "*.txt"
echo

# 3. NAVIGATION COMMANDS
echo "=== 3. NAVIGATION COMMANDS ==="
echo

echo "Current directory:"
pwd

echo "List current directory:"
ls

echo "List demo directory:"
ls /tmp/demo/

echo "Navigate to demo directory:"
cd /tmp/demo
pwd
ls

echo "Navigate to subdirectory:"
cd src
pwd
ls
cat main.py

echo "Navigate up and to docs:"
cd ../docs
pwd
cat README.md

echo "Return to demo root:"
cd ..
pwd
echo

# 4. TEXT PROCESSING COMMANDS  
echo "=== 4. TEXT PROCESSING COMMANDS ==="
echo

echo "Creating sample data file:"
echo "apple,5,red" > /tmp/demo/data.csv
echo "banana,3,yellow" >> /tmp/demo/data.csv
echo "cherry,8,red" >> /tmp/demo/data.csv
echo "date,2,brown" >> /tmp/demo/data.csv

echo "Display file:"
cat /tmp/demo/data.csv

echo "Search with grep:"
grep "red" /tmp/demo/data.csv

echo "Count lines with wc:"
wc -l /tmp/demo/data.csv

echo "Show first 2 lines with head:"
head -2 /tmp/demo/data.csv

echo "Show last 2 lines with tail:"
tail -2 /tmp/demo/data.csv

echo "Sort data:"
sort /tmp/demo/data.csv

echo "Process with awk:"
awk -F',' '{print $1 " has " $2 " items"}' /tmp/demo/data.csv

echo "Transform with sed:"
sed 's/,/ | /g' /tmp/demo/data.csv
echo

# 5. PYTHON INTEGRATION
echo "=== 5. PYTHON INTEGRATION ==="
echo

echo "Execute Python command:"
python -c "print('Hello from Python in Virtual Shell!')"

echo "Python calculations:"
python -c "print(f'2^10 = {2**10}')"

echo "Create and run Python script:"
echo "print('Python script execution test')" > /tmp/demo/test_script.py
echo "import os" >> /tmp/demo/test_script.py
echo "print(f'Environment variable: {os.environ.get(\"DEMO_VAR\", \"not found\")}')" >> /tmp/demo/test_script.py
echo "print('Virtual shell Python integration working!')" >> /tmp/demo/test_script.py

python /tmp/demo/test_script.py
echo

# 6. SHELL SCRIPTING
echo "=== 6. SHELL SCRIPTING ==="
echo

echo "Create shell script:"
echo "#!/bin/bash" > /tmp/demo/test.sh
echo "echo 'Shell script execution test'" >> /tmp/demo/test.sh
echo "echo 'Current directory: '$(pwd)" >> /tmp/demo/test.sh
echo "echo 'Files in current directory:'" >> /tmp/demo/test.sh
echo "ls" >> /tmp/demo/test.sh

echo "Execute shell script:"
script /tmp/demo/test.sh
echo

# 7. ADVANCED OPERATIONS
echo "=== 7. ADVANCED OPERATIONS ==="
echo

echo "Pipeline operations:"
cat /tmp/demo/data.csv | grep "red"
cat /tmp/demo/multiline.txt | wc -l

echo "Redirection operations:"
ls /tmp/demo/ > /tmp/demo/file_list.txt
echo "File list saved to file_list.txt:"
cat /tmp/demo/file_list.txt

echo "Environment variable expansion in files:"
echo "Demo variable: $DEMO_VAR" > /tmp/demo/env_test.txt
echo "Path variable: $TEST_PATH" >> /tmp/demo/env_test.txt
cat /tmp/demo/env_test.txt
echo

# 8. PERFORMANCE TIMING
echo "=== 8. PERFORMANCE TIMING ==="
echo

echo "Time file operations:"
time (find /tmp/demo -name "*.py")

echo "Time Python execution:"
time python -c "sum(range(100))"
echo

# 9. HELP SYSTEM
echo "=== 9. HELP SYSTEM ==="
echo

echo "Help system test:"
help | head -10

echo "Specific command help:"
help cat
help grep | head -10
echo

# 10. FINAL VERIFICATION
echo "=== 10. FINAL VERIFICATION ==="
echo

echo "Complete directory structure created:"
find /tmp/demo -type f

echo "Total files created:"
find /tmp/demo -type f | wc -l

echo "Directory tree:"
ls -R /tmp/demo/

echo "Current working directory:"
pwd

echo "User information:"
whoami

echo "System uptime:"
uptime

echo "Environment variables set during demo:"
env | grep -E "(DEMO_|TEST_)"

echo
echo "=========================================="
echo "VIRTUAL SHELL COMMANDS DEMO COMPLETE!"
echo "=========================================="
echo

echo "✅ SUCCESSFULLY DEMONSTRATED:"
echo "   - Environment commands: env, export"
echo "   - System commands: whoami, uptime, time, help, python, script"
echo "   - Filesystem commands: mkdir, echo, cat, touch, cp, mv, find"
echo "   - Navigation commands: cd, pwd, ls"
echo "   - Text processing: grep, wc, head, tail, sort, awk, sed"
echo "   - Python integration: -c commands and script execution"
echo "   - Shell scripting: script execution"
echo "   - Pipelines: command | command"
echo "   - Redirection: command > file, command >> file"
echo "   - Variable expansion: $VAR usage"
echo "   - Performance timing: time command"

echo
echo "🎉 Virtual Shell is fully functional!"
echo "All major command categories working within security constraints."
echo "Demo completed at: $(date)"