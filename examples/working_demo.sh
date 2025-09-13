#!/bin/bash
# Working Demo Script for Chuk Virtual Shell
# This script demonstrates features that are fully working

echo "========================================="
echo "Chuk Virtual Shell - Working Features"
echo "========================================="
echo ""

# ==========================
# 1. Basic Commands
# ==========================
echo "=== 1. Basic Commands ==="
pwd
mkdir -p /demo/src /demo/tests
touch /demo/README.md /demo/src/app.js /demo/tests/test.js
echo "Files created:"
ls /demo
echo ""

# ==========================
# 2. Variable Expansion
# ==========================
echo "=== 2. Variable Expansion ==="
export NAME="Alice"
export AGE=25
echo "Name: $NAME, Age: $AGE"
echo "PID: $$, Last exit: $?"
echo ""

# ==========================
# 3. Arithmetic
# ==========================
echo "=== 3. Arithmetic ==="
echo "5 + 3 = $((5 + 3))"
echo "10 * 4 = $((10 * 4))"
export X=7
echo "X = $X, X * 2 = $((X * 2))"
echo ""

# ==========================
# 4. Command Substitution
# ==========================
echo "=== 4. Command Substitution ==="
echo "Current dir: $(pwd)"
echo "File count: $(ls /demo | wc -l)"
echo ""

# ==========================
# 5. Pipes and Redirection
# ==========================
echo "=== 5. Pipes and Redirection ==="
echo "Line 1" > /demo/data.txt
echo "Line 2" >> /demo/data.txt
echo "Line 3" >> /demo/data.txt
cat /demo/data.txt | grep Line | wc -l
echo ""

# ==========================
# 6. For Loops
# ==========================
echo "=== 6. For Loops ==="
for i in 1 2 3; do echo "Number: $i"; done
echo ""
for file in /demo/*.md; do echo "Found: $file"; done
echo ""

# ==========================
# 7. Nested For Loops
# ==========================
echo "=== 7. Nested For Loops ==="
for i in A B; do for j in 1 2; do echo "$i$j"; done; done
echo ""

# ==========================
# 8. If Statements
# ==========================
echo "=== 8. If Statements ==="
if [ -f /demo/README.md ]; then echo "README exists"; else echo "No README"; fi
if [ 5 -gt 3 ]; then echo "5 > 3"; fi
echo ""

# ==========================
# 9. Break and Continue
# ==========================
echo "=== 9. Break and Continue ==="
for i in 1 2 3 4 5; do if [ $i -eq 3 ]; then break; fi; echo $i; done
echo ""
for i in 1 2 3 4 5; do if [ $i -eq 3 ]; then continue; fi; echo $i; done
echo ""

# ==========================
# 10. Test Command
# ==========================
echo "=== 10. Test Command ==="
[ -d /demo ] && echo "/demo is a directory"
[ -f /demo/src/app.js ] && echo "app.js exists"
[ 10 -eq 10 ] && echo "10 equals 10"
[ "hello" = "hello" ] && echo "Strings match"
echo ""

# ==========================
# 11. Glob Patterns
# ==========================
echo "=== 11. Glob Patterns ==="
touch /demo/file1.txt /demo/file2.txt /demo/file3.txt
ls /demo/*.txt
echo ""

# ==========================
# 12. Aliases
# ==========================
echo "=== 12. Aliases ==="
alias ll="ls -la"
alias count="wc -l"
echo "Aliases defined"
alias
echo ""

echo "========================================="
echo "Demo Complete!"
echo "========================================="