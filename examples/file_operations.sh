#!/bin/sh
# Demonstrate file operations in virtual filesystem

echo "=== File Operations Demo ==="
echo ""

# Create directory structure
echo "Creating directory structure..."
mkdir -p data/input
mkdir -p data/output
mkdir -p data/temp

# Create some test files
echo "Creating test files..."
echo "Sample data line 1" > data/input/file1.txt
echo "Sample data line 2" >> data/input/file1.txt
echo "Sample data line 3" >> data/input/file1.txt

echo "Another file content" > data/input/file2.txt
echo "With multiple lines" >> data/input/file2.txt

# List directory contents
echo ""
echo "Directory structure:"
ls -la data/

# Copy files
echo ""
echo "Copying files..."
cp data/input/file1.txt data/output/file1_copy.txt
cp data/input/file2.txt data/temp/

# Move files
echo "Moving files..."
mv data/temp/file2.txt data/temp/file2_renamed.txt

# Read file contents
echo ""
echo "Contents of file1.txt:"
cat data/input/file1.txt

# Count lines, words, characters
echo ""
echo "File statistics:"
wc data/input/file1.txt

# Find files
echo ""
echo "Finding .txt files:"
find data -name "*.txt"

# Check disk usage
echo ""
echo "Disk usage:"
du -h data/

# Clean up
echo ""
echo "Cleaning up temp directory..."
rm -r data/temp
echo "Done!"