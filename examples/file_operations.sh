#!/bin/sh
# Demonstrate file operations in virtual filesystem

echo "=== File Operations Demo ==="
echo ""

# Create directory structure
echo "Creating directory structure..."
mkdir -p /tmp/data/input
mkdir -p /tmp/data/output
mkdir -p /tmp/data/temp

# Create some test files
echo "Creating test files..."
echo "Sample data line 1" > /tmp/data/input/file1.txt
echo "Sample data line 2" >> /tmp/data/input/file1.txt
echo "Sample data line 3" >> /tmp/data/input/file1.txt

echo "Another file content" > /tmp/data/input/file2.txt
echo "With multiple lines" >> /tmp/data/input/file2.txt

# List directory contents
echo ""
echo "Directory structure:"
ls -la /tmp/data/

# Copy files
echo ""
echo "Copying files..."
cp /tmp/data/input/file1.txt /tmp/data/output/file1_copy.txt
cp /tmp/data/input/file2.txt /tmp/data/temp/

# Move files
echo "Moving files..."
mv /tmp/data/temp/file2.txt /tmp/data/temp/file2_renamed.txt

# Read file contents
echo ""
echo "Contents of file1.txt:"
cat /tmp/data/input/file1.txt

# Count lines, words, characters
echo ""
echo "File statistics:"
wc /tmp/data/input/file1.txt

# Find files
echo ""
echo "Finding .txt files:"
find /tmp/data -name "*.txt"

# Check disk usage
echo ""
echo "Disk usage:"
du -h /tmp/data/

# Clean up
echo ""
echo "Cleaning up temp directory..."
rm -r /tmp/data/temp
echo "Done!"