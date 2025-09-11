#!/bin/sh
# Demonstrate working control flow patterns in virtual shell

echo "=== Control Flow Demo ==="
echo ""
echo "This demo shows control flow patterns that work in the virtual shell."
echo ""

# Create test files first
echo "Setting up test environment..."
echo "Test content" > /tmp/test_file.txt
echo "Alice data" > /tmp/alice.txt
echo "Bob data" > /tmp/bob.txt
mkdir -p /tmp/test_dir
echo ""

echo "=== Working Patterns ==="
echo ""

echo "1. Command chaining with && (AND):"
echo "   Creating a file and confirming success..."
echo "test" > /tmp/chain1.txt && echo "   ✓ File created successfully"
echo ""

echo "2. Command chaining with || (OR):"
echo "   Trying to read non-existent file..."
cat /tmp/nonexistent.txt 2>/dev/null || echo "   ✓ Handled missing file gracefully"
echo ""

echo "3. Sequential commands with semicolon:"
echo "   Running multiple commands..."
echo "   Step 1: Create file" ; echo "data" > /tmp/seq.txt ; echo "   Step 2: Read file" ; cat /tmp/seq.txt
echo ""

echo "4. Command substitution:"
echo "   Current directory is: $(pwd)"
echo "   Current user is: $(whoami)"
echo "   File count in /tmp: $(ls /tmp/*.txt 2>/dev/null | wc -l)"
echo ""

echo "5. Pipelines:"
echo "   Finding .txt files and counting them..."
ls /tmp/*.txt | wc -l
echo ""

echo "   Processing text through pipeline..."
echo "Line 1\nLine 2\nLine 3" | grep "Line" | sed 's/Line/Item/'
echo ""

echo "6. Output redirection:"
echo "   Writing to file..."
echo "Hello World" > /tmp/output.txt
echo "   Appending to file..."
echo "Second line" >> /tmp/output.txt
echo "   File contents:"
cat /tmp/output.txt
echo ""

echo "7. Input redirection:"
echo "   Counting lines in file..."
wc -l < /tmp/output.txt
echo ""

echo "=== Pattern Examples ==="
echo ""

echo "Example 1: Processing multiple files"
echo "-----------------------------------------"
echo "Instead of: for file in *.txt; do ... done"
echo "Use: Multiple explicit commands or pipes"
echo ""
echo "Processing alice.txt:"
cat /tmp/alice.txt | sed 's/^/  > /'
echo "Processing bob.txt:"
cat /tmp/bob.txt | sed 's/^/  > /'
echo ""

echo "Example 2: Conditional-like behavior"
echo "-----------------------------------------"
echo "Instead of: if [ -f file ]; then ... fi"
echo "Use: Command chaining with && and ||"
echo ""
ls /tmp/test_file.txt >/dev/null 2>&1 && echo "  ✓ test_file.txt exists" || echo "  ✗ test_file.txt not found"
ls /tmp/missing.txt >/dev/null 2>&1 && echo "  ✓ missing.txt exists" || echo "  ✗ missing.txt not found (expected)"
echo ""

echo "Example 3: Iteration-like behavior"
echo "-----------------------------------------"
echo "Instead of: while read line; do ... done"
echo "Use: Pipes and text processing commands"
echo ""
echo "Processing each line:"
echo "First\nSecond\nThird" | sed 's/^/  Processing: /'
echo ""

echo "=== Clean Up ==="
echo "Removing test files..."
rm -f /tmp/test_file.txt /tmp/alice.txt /tmp/bob.txt
rm -f /tmp/chain1.txt /tmp/seq.txt /tmp/output.txt
rm -rf /tmp/test_dir
echo ""
echo "Demo complete!"