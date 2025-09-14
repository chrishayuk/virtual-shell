#!/bin/bash
# Demo script showcasing new virtual shell features

echo "======================================"
echo "Virtual Shell - New Features Demo"
echo "======================================"
echo ""

# Feature 1: Command chaining with && and ||
echo "=== 1. Command Chaining with && and || ==="
echo "Testing: echo 'First' && echo 'Second' && echo 'Third'"
echo "First" && echo "Second" && echo "Third"
echo ""

echo "Testing: false_command || echo 'Fallback executed'"
false_command || echo "Fallback executed"
echo ""

# Feature 2: Semicolon separator
echo "=== 2. Semicolon Command Separator ==="
echo "Testing: echo 'One'; echo 'Two'; echo 'Three'"
echo "One"; echo "Two"; echo "Three"
echo ""

# Feature 3: Variable expansion
echo "=== 3. Variable Expansion ==="
export MY_NAME="Virtual Shell"
export VERSION="2.0"
echo "Testing variable expansion:"
echo "MY_NAME=$MY_NAME"
echo "VERSION=$VERSION"
echo "Welcome to $MY_NAME version $VERSION!"
echo ""

# Feature 4: Variable expansion with ${} syntax
echo "=== 4. Curly Brace Variable Expansion ==="
export PREFIX="test"
echo "Testing: echo \${PREFIX}ing"
echo "${PREFIX}ing"
echo "${PREFIX}_file.txt"
echo ""

# Feature 5: Special variables
echo "=== 5. Special Variables ==="
echo "Exit code of last command: $?"
echo "Process ID (simulated): $$"
echo "Current directory: $PWD"
echo "Home directory: $HOME"
echo ""

# Feature 6: Wildcard/Glob expansion
echo "=== 6. Wildcard/Glob Expansion ==="
echo "Creating test files..."
touch test1.txt test2.txt test3.log data.csv
echo "Listing *.txt files:"
ls *.txt
echo ""
echo "Listing test?.txt files:"
ls test?.txt
echo ""
echo "Removing *.log files:"
rm *.log
echo "Verifying removal:"
ls
echo ""

# Feature 7: Tilde expansion
echo "=== 7. Tilde (~) Home Directory Expansion ==="
echo "Going to home directory with ~:"
cd ~
pwd
echo ""
echo "Creating ~/documents directory:"
mkdir -p ~/documents
cd ~/documents
pwd
echo ""

# Feature 8: cd - (previous directory)
echo "=== 8. Previous Directory (cd -) ==="
cd /tmp
echo "Current directory: $(pwd)"
cd /home
echo "Current directory: $(pwd)"
echo "Going back with cd -:"
cd -
echo ""

# Feature 9: Command substitution with $()
echo "=== 9. Command Substitution with \$() ==="
echo "test content" > /tmp/test.txt
echo "File contains: $(cat /tmp/test.txt)"
echo "Current time: $(date)"
echo ""

# Feature 10: Command substitution with backticks
echo "=== 10. Command Substitution with Backticks ==="
echo "another test" > /tmp/test2.txt
echo "File contains: `cat /tmp/test2.txt`"
echo "User is: `whoami`"
echo ""

# Feature 11: Complex combinations
echo "=== 11. Complex Feature Combinations ==="
export DIR="/tmp"
cd $DIR && echo "Changed to $DIR" || echo "Failed to change directory"
echo ""

echo "Creating files in $DIR:"
touch file1.txt file2.txt file3.dat
echo "Text files in $(pwd):"
ls *.txt | grep file
echo ""

# Feature 12: Variables in paths
echo "=== 12. Variables in Paths ==="
export WORKSPACE="/tmp/workspace"
mkdir -p $WORKSPACE
cd $WORKSPACE
echo "Working in: $PWD"
touch $WORKSPACE/config.json
ls $WORKSPACE
echo ""

# Cleanup
echo "=== Cleanup ==="
cd /
rm -rf /tmp/workspace /tmp/*.txt /tmp/*.dat
echo "Demo completed!"
echo ""
echo "Summary of new features demonstrated:"
echo "  ✓ Logical operators (&&, ||)"
echo "  ✓ Command separator (;)"
echo "  ✓ Variable expansion (\$VAR and \${VAR})"
echo "  ✓ Special variables (\$?, \$$, \$PWD, \$HOME)"
echo "  ✓ Wildcard/glob patterns (*, ?)"
echo "  ✓ Tilde expansion (~)"
echo "  ✓ Previous directory (cd -)"
echo "  ✓ Command substitution (\$() and backticks)"
echo "  ✓ Complex combinations of features"