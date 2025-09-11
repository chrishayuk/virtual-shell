#!/bin/sh
# Demonstration of new shell features

echo "=== New Shell Features Demo ==="
echo

# 1. Which command
echo "1. Which Command - Find command locations:"
which ls
which cd
which python
echo

# 2. Alias commands
echo "2. Alias Commands - Create command shortcuts:"
alias ll="ls -la"
alias la="ls -a"
alias l="ls"
echo "Defined aliases:"
alias
echo
echo "Using alias 'll':"
ll /home
echo
unalias l
echo "After removing 'l' alias:"
alias
echo

# 3. History command
echo "3. History Command - View command history:"
history 5
echo
echo "Search history for 'alias':"
history alias
echo

# 4. Tree command
echo "4. Tree Command - Visualize directory structure:"
mkdir -p /demo/project/src
mkdir -p /demo/project/tests
mkdir -p /demo/project/docs
touch /demo/project/README.md
touch /demo/project/src/main.py
touch /demo/project/src/utils.py
touch /demo/project/tests/test_main.py
touch /demo/project/docs/api.md

echo "Full tree:"
tree /demo
echo

echo "Directories only:"
tree -d /demo
echo

echo "Max 2 levels:"
tree -L 2 /demo
echo

# 5. Command timing
echo "5. Command Timing Statistics:"
timings -e
echo "Timing enabled, running some commands..."

# Run some commands to generate timing data
ls /demo > /dev/null
pwd > /dev/null
echo "test" > /dev/null
cat /demo/project/README.md > /dev/null 2>&1
ls -la /demo/project > /dev/null

echo "Timing statistics:"
timings
echo

timings -d
echo "Timing disabled"
echo

echo "=== Demo Complete ==="