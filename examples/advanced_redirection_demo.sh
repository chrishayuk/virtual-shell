#!/bin/bash
# Advanced Redirection Features Demo
# Demonstrates stderr redirection, combined output, and advanced I/O features

echo "=== Advanced Redirection Demo ==="
echo

# Setup test directory
mkdir -p /tmp/redirection_demo
cd /tmp/redirection_demo

# 1. Basic stderr redirection
echo "1. Testing stderr redirection (2>):"
echo "   Attempting to list non-existent file..."
ls /nonexistent 2> errors.txt
echo "   Error captured in errors.txt:"
cat errors.txt
echo

# 2. Append stderr
echo "2. Testing stderr append (2>>):"
ls /another_nonexistent 2>> errors.txt
echo "   Errors accumulated in errors.txt:"
cat errors.txt
echo

# 3. Redirect stderr to stdout (2>&1)
echo "3. Testing stderr to stdout (2>&1):"
echo "   Capturing both output and errors together:"
echo "SUCCESS: This is stdout" > mixed.txt
ls /nonexistent 2>&1 >> mixed.txt
cat mixed.txt
echo

# 4. Combined output redirection (&>)
echo "4. Testing combined output (&>):"
echo "   Running command with both stdout and stderr:"
(echo "Normal output" && ls /nonexistent) &> combined.txt
echo "   Combined output in combined.txt:"
cat combined.txt
echo

# 5. Append combined output (&>>)
echo "5. Testing append combined (&>>):"
(echo "More output" && ls /yet_another_nonexistent) &>> combined.txt
echo "   Accumulated combined output:"
cat combined.txt
echo

# 6. Separate stdout and stderr
echo "6. Separating stdout and stderr:"
mkdir -p /tmp/test_dir
touch /tmp/test_dir/file1.txt
echo "   Listing existing and non-existing paths:"
ls /tmp/test_dir/file1.txt /nonexistent > stdout.txt 2> stderr.txt
echo "   Standard output (stdout.txt):"
cat stdout.txt
echo "   Standard error (stderr.txt):"
cat stderr.txt
echo

# 7. Discard stderr with /dev/null
echo "7. Discarding errors with /dev/null:"
touch /dev/null  # Create /dev/null if it doesn't exist
echo "   Running command with errors discarded:"
ls /tmp/test_dir/file1.txt /nonexistent 2> /dev/null
echo "   (Only stdout shown above, errors discarded)"
echo

# 8. Complex redirection in pipelines
echo "8. Redirection in pipelines:"
echo "   Creating test data..."
echo -e "apple\nbanana\ncherry\napricot" > fruits.txt
echo "   Piping with stderr handling:"
(cat fruits.txt && ls /nonexistent) 2> pipeline_errors.txt | grep "^a" > a_fruits.txt
echo "   Fruits starting with 'a' (a_fruits.txt):"
cat a_fruits.txt
echo "   Pipeline errors (pipeline_errors.txt):"
cat pipeline_errors.txt
echo

# 9. Quoted filenames with spaces
echo "9. Handling filenames with spaces:"
echo "content" > "file with spaces.txt"
echo "   Created 'file with spaces.txt'"
ls "file with spaces.txt"
cat < "file with spaces.txt" > "output with spaces.txt"
echo "   Copied to 'output with spaces.txt'"
ls *spaces.txt
echo

# 10. Real-world example: Build script with logging
echo "10. Real-world example - Build with comprehensive logging:"
echo "   Simulating a build process..."
(
    echo "[$(date)] Build started"
    echo "[$(date)] Compiling source..."
    echo "SUCCESS: Module 1 compiled"
    ls /nonexistent_module 2>&1
    echo "SUCCESS: Module 2 compiled"
    echo "[$(date)] Build completed"
) &> build.log

echo "   Build log (build.log):"
cat build.log
echo

echo "=== Demo Complete ==="
echo "Files created in /tmp/redirection_demo:"
ls -la

# Cleanup option (commented out to preserve demo files)
# rm -rf /tmp/redirection_demo