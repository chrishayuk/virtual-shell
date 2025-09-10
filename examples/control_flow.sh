#!/bin/sh
# Demonstrate control flow in bash scripts

echo "=== Control Flow Demo ==="
echo ""

# Variables
COUNT=5
NAME="User"

# If statements
echo "If statement example:"
if [ -f "employees.txt" ]; then
    echo "  employees.txt exists"
else
    echo "  employees.txt does not exist"
fi
echo ""

# Numeric comparison
echo "Numeric comparison:"
if [ $COUNT -gt 3 ]; then
    echo "  Count ($COUNT) is greater than 3"
fi
echo ""

# String comparison
echo "String comparison:"
if [ "$NAME" = "User" ]; then
    echo "  Name matches 'User'"
fi
echo ""

# For loops
echo "For loop - counting:"
for i in 1 2 3 4 5; do
    echo "  Number: $i"
done
echo ""

echo "For loop - files:"
echo "Creating test files..."
for name in alice bob charlie; do
    echo "Hello $name" > "${name}.txt"
    echo "  Created ${name}.txt"
done
echo ""

# For loop with command substitution
echo "For loop - processing files:"
for file in *.txt; do
    if [ -f "$file" ]; then
        lines=$(wc -l < "$file")
        echo "  $file has $lines lines"
    fi
done
echo ""

# While loop (simplified)
echo "While loop example:"
COUNTER=1
while [ $COUNTER -le 3 ]; do
    echo "  Counter: $COUNTER"
    COUNTER=$((COUNTER + 1))
done
echo ""

# Case statement (if interpreter supports it)
echo "Case statement example:"
FRUIT="apple"
case $FRUIT in
    apple)
        echo "  It's an apple"
        ;;
    banana)
        echo "  It's a banana"
        ;;
    *)
        echo "  Unknown fruit"
        ;;
esac
echo ""

# Functions (if interpreter supports it)
echo "Function example:"
greet() {
    echo "  Hello, $1!"
}

greet "World"
greet "Virtual Shell"
echo ""

# Command chaining
echo "Command chaining:"
echo "  Creating file..." && echo "test content" > chain_test.txt && echo "  File created successfully"
echo ""

# Conditional execution
echo "Conditional execution:"
[ -f "chain_test.txt" ] && echo "  chain_test.txt exists" || echo "  chain_test.txt not found"
echo ""

# Clean up
echo "Cleaning up test files..."
rm -f alice.txt bob.txt charlie.txt chain_test.txt
echo "Done!"