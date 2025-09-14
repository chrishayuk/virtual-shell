#!/bin/bash
# Comprehensive Demo Script for Chuk Virtual Shell
# This script demonstrates all major features of the shell interpreter
# including control flow, variable expansion, pipes, and more.

echo "========================================="
echo "Chuk Virtual Shell - Comprehensive Demo"
echo "========================================="
echo ""

# ==========================
# 1. Basic Commands
# ==========================
echo "=== 1. Basic Commands ==="
echo "Current directory:"
pwd
echo ""

echo "Creating test directory structure:"
mkdir -p /demo/src/components /demo/tests /demo/docs
touch /demo/README.md /demo/package.json
touch /demo/src/index.js /demo/src/app.js
touch /demo/src/components/header.js /demo/src/components/footer.js
touch /demo/tests/test_app.js /demo/tests/test_header.js
echo "Hello World" > /demo/hello.txt
echo "Line 1" > /demo/data.txt
echo "Line 2" >> /demo/data.txt
echo "Line 3" >> /demo/data.txt

echo "Directory listing:"
ls /demo
echo ""

echo "Tree view:"
tree /demo
echo ""

# ==========================
# 2. Variable Expansion
# ==========================
echo "=== 2. Variable Expansion ==="
export NAME="Alice"
export COUNT=5
echo "Simple variable: NAME=$NAME"
echo "Variable in string: Hello, $NAME!"
echo "Braces syntax: ${NAME} is here"
echo ""

# Variable assignment without export
MESSAGE="Welcome"
echo "Assignment without export: $MESSAGE"
echo ""

# Special variables
echo "Process ID: $$"
echo "Last return code: $?"
false
echo "After false command: $?"
true
echo "After true command: $?"
echo ""

# ==========================
# 3. Arithmetic Expansion
# ==========================
echo "=== 3. Arithmetic Expansion ==="
export X=10
export Y=3
echo "X=$X, Y=$Y"
echo "Addition: $((X + Y)) = $((10 + 3))"
echo "Subtraction: $((X - Y)) = $((10 - 3))"
echo "Multiplication: $((X * Y)) = $((10 * 3))"
echo "Division: $((X / Y)) = $((10 / 3))"
echo "Modulo: $((X % Y)) = $((10 % 3))"
echo ""

# ==========================
# 4. Command Substitution
# ==========================
echo "=== 4. Command Substitution ==="
echo "Current directory using \$(): $(pwd)"
echo "Current directory using backticks: `pwd`"
echo "File count in /demo: $(ls /demo | wc -l) files"
echo "Nested substitution: Found $(echo $(ls /demo/*.txt | wc -l)) text files"
echo ""

# ==========================
# 5. Glob Expansion
# ==========================
echo "=== 5. Glob Expansion ==="
echo "All .txt files: "
ls /demo/*.txt
echo ""
echo "All .js files in src:"
ls /demo/src/*.js
echo ""
echo "Using ? wildcard:"
touch /demo/file1.txt /demo/file2.txt /demo/file3.txt
ls /demo/file?.txt
echo ""

# ==========================
# 6. Pipes and Redirection
# ==========================
echo "=== 6. Pipes and Redirection ==="
echo "Simple pipe - list and count:"
ls /demo | wc -l
echo ""

echo "Multi-stage pipe:"
cat /demo/data.txt | grep Line | wc -l
echo ""

echo "Input/Output redirection:"
echo "Output redirection" > /demo/output.txt
cat /demo/output.txt
echo "Append redirection" >> /demo/output.txt
cat /demo/output.txt
echo ""

echo "Input redirection:"
grep "Line" < /demo/data.txt
echo ""

# ==========================
# 7. Logical Operators
# ==========================
echo "=== 7. Logical Operators ==="
echo "AND operator (&&):"
true && echo "This runs because true succeeded"
false && echo "This won't run because false failed"
echo ""

echo "OR operator (||):"
false || echo "This runs because false failed"
true || echo "This won't run because true succeeded"
echo ""

echo "Semicolon separator (;):"
echo "First"; echo "Second"; echo "Third"
echo ""

# ==========================
# 8. If Statements
# ==========================
echo "=== 8. If Statements ==="

echo "Basic if:"
if true; then
    echo "  True condition executed"
fi

if false; then
    echo "  This won't be printed"
fi

echo ""
echo "If-else:"
if [ -f /demo/hello.txt ]; then
    echo "  hello.txt exists"
else
    echo "  hello.txt does not exist"
fi

if [ -f /demo/nonexistent.txt ]; then
    echo "  nonexistent.txt exists"
else
    echo "  nonexistent.txt does not exist"
fi

echo ""
echo "If-elif-else:"
AGE=25
if [ $AGE -lt 18 ]; then
    echo "  Minor"
elif [ $AGE -lt 65 ]; then
    echo "  Adult"
else
    echo "  Senior"
fi

echo ""
echo "Nested if:"
if [ -d /demo ]; then
    echo "  /demo exists"
    if [ -f /demo/hello.txt ]; then
        echo "    hello.txt found inside /demo"
    fi
fi
echo ""

# ==========================
# 9. For Loops
# ==========================
echo "=== 9. For Loops ==="

echo "Basic for loop:"
for i in 1 2 3; do
    echo "  Iteration $i"
done

echo ""
echo "For loop with strings:"
for name in Alice Bob Charlie; do
    echo "  Hello, $name!"
done

echo ""
echo "For loop with glob expansion:"
for file in /demo/*.txt; do
    echo "  Processing: $file"
done

echo ""
echo "For loop with command substitution:"
for word in $(echo "one two three"); do
    echo "  Word: $word"
done

echo ""
echo "Nested for loops:"
for i in A B; do
    for j in 1 2 3; do
        echo "  $i$j"
    done
done
echo ""

# ==========================
# 10. While Loops
# ==========================
echo "=== 10. While Loops ==="

echo "While loop with counter:"
COUNTER=1
while [ $COUNTER -le 3 ]; do
    echo "  Count: $COUNTER"
    COUNTER=$((COUNTER + 1))
done

echo ""
echo "While loop with file check:"
echo "yes" > /demo/flag.txt
ATTEMPT=1
while [ -f /demo/flag.txt ]; do
    echo "  Attempt $ATTEMPT: Flag file exists"
    if [ $ATTEMPT -eq 2 ]; then
        rm /demo/flag.txt
        echo "  Flag file removed"
    fi
    ATTEMPT=$((ATTEMPT + 1))
done
echo ""

# ==========================
# 11. Until Loops
# ==========================
echo "=== 11. Until Loops ==="

echo "Until loop (opposite of while):"
COUNTER=1
until [ $COUNTER -gt 3 ]; do
    echo "  Count: $COUNTER"
    COUNTER=$((COUNTER + 1))
done

echo ""
echo "Until file exists:"
ATTEMPT=1
until [ -f /demo/done.txt ]; do
    echo "  Attempt $ATTEMPT: Waiting for done.txt"
    if [ $ATTEMPT -eq 2 ]; then
        touch /demo/done.txt
        echo "  Created done.txt"
    fi
    ATTEMPT=$((ATTEMPT + 1))
done
echo "  done.txt found!"
echo ""

# ==========================
# 12. Break and Continue
# ==========================
echo "=== 12. Break and Continue ==="

echo "Break example:"
for i in 1 2 3 4 5; do
    if [ $i -eq 3 ]; then
        echo "  Breaking at $i"
        break
    fi
    echo "  Number: $i"
done

echo ""
echo "Continue example:"
for i in 1 2 3 4 5; do
    if [ $i -eq 3 ]; then
        echo "  Skipping $i"
        continue
    fi
    echo "  Number: $i"
done

echo ""
echo "Break in nested loops:"
for i in A B C; do
    echo "  Outer: $i"
    for j in 1 2 3; do
        if [ "$i" = "B" ] && [ $j -eq 2 ]; then
            echo "    Breaking inner loop at $i$j"
            break
        fi
        echo "    Inner: $i$j"
    done
done
echo ""

# ==========================
# 13. Complex Examples
# ==========================
echo "=== 13. Complex Examples ==="

echo "Finding and processing files:"
for file in /demo/src/*.js; do
    if [ -f "$file" ]; then
        BASE=$(basename "$file")
        echo "  Processing $BASE"
        echo "// Processed" >> "$file"
    fi
done

echo ""
echo "Conditional file operations:"
for ext in txt js md; do
    COUNT=$(ls /demo/*.$ext 2>/dev/null | wc -l)
    if [ $COUNT -gt 0 ]; then
        echo "  Found $COUNT .$ext files"
    else
        echo "  No .$ext files found"
    fi
done

echo ""
echo "Pipeline with conditionals:"
cat /demo/data.txt | while read line; do
    if echo "$line" | grep -q "2"; then
        echo "  Found line with 2: $line"
    fi
done

echo ""
echo "Building a summary:"
TOTAL=0
for dir in src tests docs; do
    if [ -d /demo/$dir ]; then
        COUNT=$(ls /demo/$dir | wc -l)
        echo "  $dir: $COUNT files"
        TOTAL=$((TOTAL + COUNT))
    fi
done
echo "  Total files in subdirs: $TOTAL"
echo ""

# ==========================
# 14. Test/[ Command
# ==========================
echo "=== 14. Test Command ==="

echo "File tests:"
[ -f /demo/hello.txt ] && echo "  hello.txt is a file"
[ -d /demo/src ] && echo "  src is a directory"
[ -e /demo/package.json ] && echo "  package.json exists"
[ ! -e /demo/missing.txt ] && echo "  missing.txt does not exist"

echo ""
echo "String tests:"
STR1="hello"
STR2="world"
[ "$STR1" = "hello" ] && echo "  String equals test passed"
[ "$STR1" != "$STR2" ] && echo "  Strings are different"
[ -z "" ] && echo "  Empty string test passed"
[ -n "$STR1" ] && echo "  Non-empty string test passed"

echo ""
echo "Numeric tests:"
NUM1=10
NUM2=20
[ $NUM1 -lt $NUM2 ] && echo "  $NUM1 is less than $NUM2"
[ $NUM2 -gt $NUM1 ] && echo "  $NUM2 is greater than $NUM1"
[ $NUM1 -eq 10 ] && echo "  $NUM1 equals 10"
[ $NUM1 -ne $NUM2 ] && echo "  $NUM1 does not equal $NUM2"
[ $NUM1 -le 10 ] && echo "  $NUM1 is less than or equal to 10"
[ $NUM2 -ge 20 ] && echo "  $NUM2 is greater than or equal to 20"
echo ""

# ==========================
# 15. Aliases
# ==========================
echo "=== 15. Aliases ==="
alias ll="ls -la"
alias la="ls -a"
alias count="wc -l"

echo "Defined aliases:"
alias

echo ""
echo "Using aliases:"
echo "ll /demo (expanded to ls -la):"
ll /demo | head -3
echo ""

# ==========================
# 16. Command Timing
# ==========================
echo "=== 16. Command Timing ==="
timings -e
echo "Timing enabled"

# Run some commands
ls /demo > /dev/null
cat /demo/hello.txt > /dev/null
echo "test" > /dev/null
ls /demo > /dev/null

echo "Timing statistics:"
timings
echo ""

# ==========================
# 17. Final Summary
# ==========================
echo "========================================="
echo "Demo Complete!"
echo "========================================="
echo ""
echo "This demo has shown:"
echo "  - Basic commands (ls, pwd, mkdir, touch, echo, cat)"
echo "  - Variable expansion (\$VAR, \${VAR})"
echo "  - Arithmetic expansion \$((expr))"
echo "  - Command substitution \$(cmd) and backticks"
echo "  - Glob expansion (*, ?)"
echo "  - Pipes and redirection (|, >, >>, <)"
echo "  - Logical operators (&&, ||, ;)"
echo "  - If statements (if/elif/else/fi)"
echo "  - For loops (including nested)"
echo "  - While loops"
echo "  - Until loops"
echo "  - Break and continue"
echo "  - Test/[ command"
echo "  - Aliases"
echo "  - Command timing"
echo ""
echo "All features are working correctly!"