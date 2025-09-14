#!/bin/bash
# Multi-line Control Flow Demo
# This script demonstrates multi-line control flow structures
# that work in both script mode and interactive mode

echo "========================================="
echo "Multi-line Control Flow Demo"
echo "========================================="
echo ""
echo "This demo shows how to use multi-line control flow"
echo "structures in the virtual shell. In interactive mode,"
echo "the shell will show a '>' prompt for continuation lines."
echo ""

# ==========================
# 1. Multi-line IF Statements
# ==========================
echo "=== 1. Multi-line IF Statements ==="
echo ""

echo "Basic if/then/else (multi-line):"
num=10
if [ $num -gt 5 ]; then
    echo "  $num is greater than 5"
else
    echo "  $num is not greater than 5"
fi
echo ""

echo "Nested if statements:"
score=85
if [ $score -ge 90 ]; then
    echo "  Grade: A"
elif [ $score -ge 80 ]; then
    echo "  Grade: B"
    if [ $score -ge 85 ]; then
        echo "  (High B - almost an A!)"
    fi
elif [ $score -ge 70 ]; then
    echo "  Grade: C"
else
    echo "  Grade: F"
fi
echo ""

echo "Complex condition with multiple tests:"
file_path="/demo/test.txt"
echo "Test content" > $file_path

if [ -e $file_path ]; then
    echo "  File exists: $file_path"
    if [ -s $file_path ]; then
        echo "  File has content"
        content=$(cat $file_path)
        echo "  Content: $content"
    else
        echo "  File is empty"
    fi
else
    echo "  File does not exist"
fi
echo ""

# ==========================
# 2. Multi-line FOR Loops
# ==========================
echo "=== 2. Multi-line FOR Loops ==="
echo ""

echo "Basic for loop (multi-line):"
for i in 1 2 3 4 5
do
    echo "  Number: $i"
done
echo ""

echo "For loop with conditional:"
for color in red green blue yellow
do
    echo "  Processing color: $color"
    if [ "$color" = "blue" ]; then
        echo "    -> Found my favorite color!"
    fi
done
echo ""

echo "Nested for loops:"
for i in 1 2 3
do
    echo "  Outer loop: $i"
    for j in a b c
    do
        echo "    Inner loop: $i-$j"
    done
done
echo ""

# ==========================
# 3. Multi-line WHILE Loops
# ==========================
echo "=== 3. Multi-line WHILE Loops ==="
echo ""

echo "While loop with counter:"
counter=1
while [ $counter -le 5 ]
do
    echo "  Counter: $counter"
    counter=$((counter + 1))
done
echo ""

echo "While loop with file check:"
mkdir -p /demo/locks
touch /demo/locks/lock1 /demo/locks/lock2 /demo/locks/lock3

while [ -e /demo/locks/lock1 ]
do
    echo "  Lock file exists, removing it..."
    rm /demo/locks/lock1
    echo "  Lock removed"
done
echo "  While loop completed"
echo ""

# ==========================
# 4. UNTIL Loops
# ==========================
echo "=== 4. UNTIL Loops ==="
echo ""

echo "Until loop example:"
value=0
until [ $value -ge 3 ]
do
    echo "  Value is $value (waiting for >= 3)"
    value=$((value + 1))
done
echo "  Final value: $value"
echo ""

# ==========================
# 5. Loop Control: break and continue
# ==========================
echo "=== 5. Loop Control: break and continue ==="
echo ""

echo "Using break in a loop:"
for i in 1 2 3 4 5
do
    if [ $i -eq 3 ]; then
        echo "  Breaking at $i"
        break
    fi
    echo "  Number: $i"
done
echo ""

echo "Using continue in a loop:"
for i in 1 2 3 4 5
do
    if [ $i -eq 3 ]; then
        echo "  Skipping $i"
        continue
    fi
    echo "  Number: $i"
done
echo ""

# ==========================
# 6. Complex Nested Example
# ==========================
echo "=== 6. Complex Nested Control Flow ==="
echo ""

echo "Processing a directory structure:"
mkdir -p /demo/project/src /demo/project/tests /demo/project/docs
touch /demo/project/src/main.js /demo/project/src/utils.js
touch /demo/project/tests/test_main.js
touch /demo/project/docs/README.md

for dir in src tests docs
do
    full_path="/demo/project/$dir"
    echo "Checking directory: $dir"
    
    if [ -d $full_path ]; then
        echo "  Directory exists"
        
        # Count files in directory
        file_count=0
        for file in $full_path/*
        do
            if [ -e $file ]; then
                file_count=$((file_count + 1))
                echo "    Found: $(basename $file)"
            fi
        done
        
        if [ $file_count -eq 0 ]; then
            echo "  Directory is empty"
        else
            echo "  Total files: $file_count"
        fi
    else
        echo "  Directory does not exist"
    fi
    echo ""
done

# ==========================
# 7. Interactive Mode Example
# ==========================
echo "=== 7. Interactive Mode Example ==="
echo ""
echo "In interactive mode, you can type multi-line commands:"
echo ""
echo "Example 1: Type this in interactive mode:"
echo "  $ num=5"
echo "  $ if [ \$num -gt 3 ]; then"
echo "  >   echo \"Greater than 3\""
echo "  > else"
echo "  >   echo \"Not greater\""
echo "  > fi"
echo ""
echo "The shell will show '>' for continuation lines"
echo "and execute when the structure is complete."
echo ""

echo "Example 2: Multi-line for loop:"
echo "  $ for i in 1 2 3; do"
echo "  >   echo \"Number: \$i\""
echo "  > done"
echo ""

# ==========================
# 8. Real-world Example
# ==========================
echo "=== 8. Real-world Example: Log Processing ==="
echo ""

# Create some sample log files
mkdir -p /demo/logs
echo "2024-01-01 10:00:00 INFO Starting application" > /demo/logs/app.log
echo "2024-01-01 10:00:01 DEBUG Loading configuration" >> /demo/logs/app.log
echo "2024-01-01 10:00:02 ERROR Failed to connect to database" >> /demo/logs/app.log
echo "2024-01-01 10:00:03 INFO Retrying connection" >> /demo/logs/app.log
echo "2024-01-01 10:00:04 INFO Connection successful" >> /demo/logs/app.log

echo "Processing log file for errors:"
error_count=0
info_count=0
debug_count=0

while read line
do
    if echo "$line" | grep -q "ERROR"; then
        echo "  [ERROR] $line"
        error_count=$((error_count + 1))
    elif echo "$line" | grep -q "INFO"; then
        info_count=$((info_count + 1))
    elif echo "$line" | grep -q "DEBUG"; then
        debug_count=$((debug_count + 1))
    fi
done < /demo/logs/app.log

echo ""
echo "Log Summary:"
echo "  Errors: $error_count"
echo "  Info: $info_count"
echo "  Debug: $debug_count"

if [ $error_count -gt 0 ]; then
    echo "  Status: ⚠️  Errors found in log"
else
    echo "  Status: ✅ No errors found"
fi
echo ""

# ==========================
# Cleanup
# ==========================
echo "=== Cleanup ==="
rm -rf /demo
echo "Demo files cleaned up"
echo ""

echo "========================================="
echo "Multi-line Control Flow Demo Complete!"
echo "========================================="