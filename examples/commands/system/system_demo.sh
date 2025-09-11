#!/bin/bash

# System Commands Comprehensive Demo
# This script demonstrates all system commands within the virtual shell

echo "=== SYSTEM COMMANDS DEMO ==="
echo

# 1. WHOAMI COMMAND
echo "=== 1. WHOAMI COMMAND ==="
echo "Current user identification:"
whoami
echo

# 2. UPTIME COMMAND  
echo "=== 2. UPTIME COMMAND ==="
echo "System uptime information:"
uptime
echo

# 3. TIME COMMAND
echo "=== 3. TIME COMMAND ==="
echo "Time a simple command:"
time echo "This command is being timed"

echo "Time a more complex operation:"
time (echo "Creating files..." && touch file1.txt file2.txt file3.txt && echo "Files created")

echo "Time a shell operation:"
time ls -la
echo

# 4. CLEAR COMMAND
echo "=== 4. CLEAR COMMAND ==="
echo "About to clear screen (clear command)..."
echo "Note: In a real terminal, this would clear the screen"
clear
echo "Screen cleared! Continuing with demo..."
echo

# 5. HELP COMMAND
echo "=== 5. HELP COMMAND ==="
echo "Display help information:"
help

echo "Help for specific command:"
help ls

echo "Help for another command:"
help grep
echo

# 6. PYTHON COMMAND
echo "=== 6. PYTHON COMMAND ==="

echo "Creating a Python test script..."
echo "print('Hello from Python!')" > hello.py
echo "print('Python is running in the virtual shell')" >> hello.py
echo "import sys" >> hello.py
echo "print(f'Python version: {sys.version}')" >> hello.py

echo "Execute Python script:"
python hello.py

echo "Python command string execution (-c flag):"
python -c "print('Hello from command line Python!')"

echo "Python mathematical calculations:"
python -c "print(f'2^10 = {2**10}')"
python -c "import math; print(f'Pi = {math.pi:.4f}')"

echo "Python with arguments:"
echo "import sys" > args_demo.py
echo "print(f'Script name: {sys.argv[0]}')" >> args_demo.py
echo "print(f'Arguments: {sys.argv[1:]}')" >> args_demo.py
echo "print(f'Total arguments: {len(sys.argv)-1}')" >> args_demo.py

python args_demo.py arg1 arg2 arg3

echo "Python version information:"
python -V
python --version
echo

# 7. SCRIPT COMMAND
echo "=== 7. SCRIPT COMMAND ==="

echo "Creating a test shell script..."
echo "#!/bin/bash" > test_script.sh
echo "echo 'Hello from shell script!'" >> test_script.sh
echo "echo 'Arguments passed: $*'" >> test_script.sh
echo "echo 'Number of arguments: $#'" >> test_script.sh
echo "pwd" >> test_script.sh
echo "ls -la" >> test_script.sh

echo "Execute shell script using script command:"
script test_script.sh

echo "Execute script with arguments:"
script test_script.sh arg1 arg2
echo

# 8. SH COMMAND  
echo "=== 8. SH COMMAND ==="

echo "Execute shell command with sh:"
sh test_script.sh

echo "Execute inline shell commands:"
echo "echo 'Inline shell command'; pwd; whoami" > inline.sh
sh inline.sh

echo "sh with command string (-c flag):"
sh -c "echo 'Running through sh -c'; ls *.py"
echo

# 9. COMBINED SYSTEM OPERATIONS
echo "=== 9. COMBINED SYSTEM OPERATIONS ==="

echo "Creating a comprehensive system test script..."
echo "#!/bin/bash" > system_test.sh
echo "echo '=== System Information ==='" >> system_test.sh
echo "whoami" >> system_test.sh  
echo "uptime" >> system_test.sh
echo "echo" >> system_test.sh
echo "echo '=== Directory Contents ==='" >> system_test.sh
echo "pwd" >> system_test.sh
echo "ls -la" >> system_test.sh
echo "echo" >> system_test.sh
echo "echo '=== Python Integration ==='" >> system_test.sh
echo "python -c \"print('Python working from shell script!')\"" >> system_test.sh

echo "Execute comprehensive system test:"
time script system_test.sh
echo

# 10. PYTHON FILE OPERATIONS DEMO
echo "=== 10. PYTHON FILE OPERATIONS ==="

echo "Creating Python script that interacts with virtual filesystem..."
echo "# Virtual filesystem interaction demo" > fs_demo.py
echo "import sys" >> fs_demo.py
echo "print('Python filesystem operations demo')" >> fs_demo.py
echo "print(f'Current directory: {sys.path[0] if sys.path else \"unknown\"}')" >> fs_demo.py
echo "" >> fs_demo.py
echo "# Create a file from Python" >> fs_demo.py
echo "with open('python_created.txt', 'w') as f:" >> fs_demo.py
echo "    f.write('This file was created by Python!\\\\n')" >> fs_demo.py
echo "    f.write('Running in virtual shell environment\\\\n')" >> fs_demo.py
echo "" >> fs_demo.py
echo "print('File created by Python')" >> fs_demo.py
echo "" >> fs_demo.py
echo "# Read the file back" >> fs_demo.py
echo "try:" >> fs_demo.py
echo "    with open('python_created.txt', 'r') as f:" >> fs_demo.py
echo "        content = f.read()" >> fs_demo.py
echo "        print('File content:')" >> fs_demo.py
echo "        print(content)" >> fs_demo.py
echo "except Exception as e:" >> fs_demo.py
echo "    print(f'Error reading file: {e}')" >> fs_demo.py

echo "Execute Python filesystem demo:"
python fs_demo.py

echo "Verify Python created the file:"
ls -la python_created.txt
cat python_created.txt
echo

# 11. TIMING VARIOUS OPERATIONS
echo "=== 11. PERFORMANCE TIMING ==="

echo "Time file creation operations:"
time (touch time_test1.txt time_test2.txt time_test3.txt)

echo "Time Python execution:"
time python -c "sum(range(1000))"

echo "Time shell script execution:"
time sh -c "echo 'Quick shell operation'; ls > /dev/null 2>&1 || ls"

echo "Time complex operation:"
echo "for i in {1..5}; do echo \"File \$i content\" > \"test_file_\$i.txt\"; done" > create_files.sh
time script create_files.sh

echo "Verify files were created:"
ls test_file_*.txt
echo

# 12. HELP SYSTEM EXPLORATION
echo "=== 12. HELP SYSTEM EXPLORATION ==="

echo "Explore available commands through help:"
help | head -20

echo "Get help for filesystem commands:"
help cat
help cp
help find

echo "Get help for text processing:"
help grep  
help sed
echo

# 13. EXIT COMMAND DEMO (commented out as it would end the demo)
echo "=== 13. EXIT COMMAND ==="
echo "The exit command would terminate the shell session:"
echo "exit    # This would exit the virtual shell"
echo "exit 0  # Exit with success status"
echo "exit 1  # Exit with error status"
echo "(Exit command not executed to continue demo)"
echo

# 14. INTEGRATION DEMO
echo "=== 14. SYSTEM INTEGRATION DEMO ==="

echo "Create a multi-language integration script..."
echo "#!/bin/bash" > integration_demo.sh
echo "echo '=== Multi-language Integration Demo ==='" >> integration_demo.sh
echo "echo" >> integration_demo.sh
echo "echo 'System Info:'" >> integration_demo.sh
echo "whoami" >> integration_demo.sh
echo "uptime" >> integration_demo.sh
echo "echo" >> integration_demo.sh
echo "echo 'Python calculation:'" >> integration_demo.sh
echo "python -c \"import math; print(f'Square root of 16: {math.sqrt(16)}')\"" >> integration_demo.sh
echo "echo" >> integration_demo.sh
echo "echo 'File operations:'" >> integration_demo.sh
echo "echo 'Creating test files...'" >> integration_demo.sh
echo "touch integration_file1.txt integration_file2.txt" >> integration_demo.sh
echo "ls integration_file*.txt" >> integration_demo.sh
echo "echo 'Integration demo complete!'" >> integration_demo.sh

echo "Execute integration demo:"
time script integration_demo.sh

echo "Clean up integration files:"
rm integration_file*.txt
echo

echo "=== SYSTEM COMMANDS DEMO COMPLETE ==="
echo "All system commands demonstrated successfully!"

echo "Final system status:"
whoami
uptime
echo "Demo files created:"
ls -la *.py *.sh *.txt | head -10