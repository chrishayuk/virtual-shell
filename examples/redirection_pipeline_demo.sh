#!/bin/sh
# Comprehensive demonstration of shell redirection and pipelines
# This script showcases input/output redirection, pipes, and text processing

echo "====================================="
echo "Shell Redirection & Pipeline Demo"
echo "====================================="
echo ""

# Setup: Create test directories
mkdir -p /tmp/demo
cd /tmp/demo

echo "=== Part 1: Basic Output Redirection ==="
echo ""

# Simple output redirection
echo "Creating a file with output redirection..."
echo "Hello, World!" > greeting.txt
echo "This is line 2" >> greeting.txt
echo "This is line 3" >> greeting.txt

echo "Contents of greeting.txt:"
cat greeting.txt
echo ""

# Overwriting vs appending
echo "Demonstrating overwrite (>) vs append (>>)..."
echo "First line" > test.txt
echo "File after first write:"
cat test.txt

echo "Second line" > test.txt  # This overwrites
echo "File after overwrite:"
cat test.txt

echo "Third line" >> test.txt  # This appends
echo "File after append:"
cat test.txt
echo ""

echo "=== Part 2: Input Redirection ==="
echo ""

# Create sample data files
cat > numbers.txt << EOF
42
17
99
3
55
28
61
EOF

cat > fruits.txt << EOF
apple
banana
apricot
cherry
avocado
grape
apple
banana
EOF

cat > data.csv << EOF
Alice,30,Engineer,New York
Bob,25,Designer,San Francisco
Charlie,35,Manager,Chicago
Diana,28,Developer,Boston
Eve,32,Analyst,Seattle
EOF

echo "Counting lines, words, and bytes with wc:"
wc < numbers.txt
echo ""

echo "Sorting numbers with input redirection:"
sort -n < numbers.txt
echo ""

echo "Finding unique fruits:"
sort < fruits.txt | uniq
echo ""

echo "=== Part 3: Pipelines ==="
echo ""

echo "Top 3 smallest numbers (pipeline with sort and head):"
sort -n < numbers.txt | head -n 3
echo ""

echo "Fruits containing 'ap' (grep in pipeline):"
cat fruits.txt | grep ap | sort | uniq
echo ""

echo "Extract names from CSV (awk in pipeline):"
cat data.csv | awk -F, '{print $1}' | sort
echo ""

echo "Count occurrences of each fruit:"
sort < fruits.txt | uniq -c
echo ""

echo "=== Part 4: Complex Pipelines with Redirection ==="
echo ""

# Pipeline ending with output redirection
echo "Creating sorted unique fruits file..."
cat fruits.txt | sort | uniq > unique_fruits.txt
echo "Unique fruits saved to file:"
cat unique_fruits.txt
echo ""

# Multiple stage pipeline
echo "Processing CSV data through multiple stages..."
cat data.csv | awk -F, '{print $1 "," $3}' | sort | head -n 3 > top_employees.txt
echo "Top 3 employees by name:"
cat top_employees.txt
echo ""

echo "=== Part 5: Combined Input/Output Redirection ==="
echo ""

# Both input and output redirection
echo "Sorting numbers and saving to file..."
sort -n < numbers.txt > sorted_numbers.txt
echo "Sorted numbers:"
cat sorted_numbers.txt
echo ""

# Complex example with sed
cat > config.txt << EOF
server_host=localhost
server_port=8080
debug_mode=true
max_connections=100
EOF

echo "Original config:"
cat config.txt
echo ""

echo "Updating config with sed and redirection..."
sed 's/localhost/production.example.com/g' < config.txt > production_config.txt
sed -i 's/8080/443/g' production_config.txt
sed -i 's/debug_mode=true/debug_mode=false/g' production_config.txt

echo "Production config:"
cat production_config.txt
echo ""

echo "=== Part 6: Text Processing Pipeline ==="
echo ""

# Create a log file
cat > app.log << EOF
2024-01-15 10:23:45 INFO Starting application
2024-01-15 10:23:46 DEBUG Loading configuration
2024-01-15 10:23:47 ERROR Failed to connect to database
2024-01-15 10:23:48 WARN Retrying connection
2024-01-15 10:23:49 INFO Connection established
2024-01-15 10:23:50 ERROR Invalid user credentials
2024-01-15 10:23:51 DEBUG Processing request
2024-01-15 10:23:52 INFO Request completed
2024-01-15 10:23:53 ERROR Timeout occurred
2024-01-15 10:23:54 WARN High memory usage detected
EOF

echo "Analyzing log file..."
echo ""

echo "All ERROR messages:"
grep ERROR < app.log
echo ""

echo "Count of each log level:"
awk '{print $4}' < app.log | sort | uniq -c
echo ""

echo "Extract and save errors to separate file:"
grep ERROR app.log > errors.log
wc -l < errors.log > error_count.txt
echo "Errors saved. Count:"
cat error_count.txt
echo ""

echo "=== Part 7: Working with Diffs and Patches ==="
echo ""

# Create two versions of a file
cat > version1.txt << EOF
Feature A: enabled
Feature B: disabled
Feature C: enabled
Max users: 100
Timeout: 30
EOF

cat > version2.txt << EOF
Feature A: enabled
Feature B: enabled
Feature C: enabled
Max users: 500
Timeout: 60
Cache: enabled
EOF

echo "Creating diff between versions..."
diff -u version1.txt version2.txt > changes.patch

echo "Patch file contents:"
cat changes.patch
echo ""

echo "Applying patch to original file..."
cp version1.txt version1_backup.txt
patch version1.txt < changes.patch

echo "File after patching:"
cat version1.txt
echo ""

echo "=== Part 8: Advanced AWK Processing ==="
echo ""

cat > sales.csv << EOF
Product,Q1,Q2,Q3,Q4
Laptop,1200,1500,1800,2000
Phone,800,900,1100,1300
Tablet,400,450,500,600
Monitor,300,350,400,450
EOF

echo "Sales data:"
cat sales.csv
echo ""

echo "Calculate total sales per product:"
tail -n +2 sales.csv | awk -F, '{total=$2+$3+$4+$5; print $1 ": " total}'
echo ""

echo "Find products with Q4 sales > 1000:"
tail -n +2 sales.csv | awk -F, '$5>1000 {print $1 " had Q4 sales of " $5}'
echo ""

echo "=== Part 9: Multi-file Operations ==="
echo ""

# Create multiple input files
echo "apple" > file1.txt
echo "banana" > file2.txt
echo "cherry" > file3.txt

echo "Concatenating multiple files with cat:"
cat file1.txt file2.txt file3.txt > combined.txt
cat combined.txt
echo ""

echo "Contents of each file:"
echo "file1.txt:"
cat file1.txt
echo "file2.txt:"
cat file2.txt
echo "file3.txt:"
cat file3.txt
echo ""

echo "=== Part 10: Complex Real-world Example ==="
echo ""

# Simulate processing web server logs
cat > access.log << EOF
192.168.1.1 - - [15/Jan/2024:10:00:00] "GET /index.html HTTP/1.1" 200 5234
192.168.1.2 - - [15/Jan/2024:10:00:01] "GET /style.css HTTP/1.1" 200 1234
192.168.1.1 - - [15/Jan/2024:10:00:02] "GET /script.js HTTP/1.1" 200 8976
192.168.1.3 - - [15/Jan/2024:10:00:03] "GET /api/users HTTP/1.1" 404 234
192.168.1.2 - - [15/Jan/2024:10:00:04] "POST /api/login HTTP/1.1" 200 567
192.168.1.4 - - [15/Jan/2024:10:00:05] "GET /admin HTTP/1.1" 403 234
192.168.1.1 - - [15/Jan/2024:10:00:06] "GET /favicon.ico HTTP/1.1" 200 1234
192.168.1.3 - - [15/Jan/2024:10:00:07] "GET /api/data HTTP/1.1" 500 567
192.168.1.2 - - [15/Jan/2024:10:00:08] "GET /images/logo.png HTTP/1.1" 200 45678
192.168.1.5 - - [15/Jan/2024:10:00:09] "GET /index.html HTTP/1.1" 200 5234
EOF

echo "Web server access log analysis:"
echo ""

echo "Unique IP addresses:"
awk '{print $1}' < access.log | sort | uniq
echo ""

echo "HTTP status code distribution:"
awk '{print $9}' < access.log | sort | uniq -c
echo ""

echo "Failed requests (4xx and 5xx status codes):"
awk '$9 >= 400 {print}' < access.log > failed_requests.log
cat failed_requests.log
echo ""

echo "Top 3 IP addresses by request count:"
awk '{print $1}' < access.log | sort | uniq -c | sort -rn | head -n 3
echo ""

echo "Extract and analyze requested URLs:"
cat access.log | awk '{print $7}' | sort | uniq -c | sort -rn > url_stats.txt
echo "Most requested URLs:"
head -n 5 < url_stats.txt
echo ""

# Clean up demonstration files
echo "=== Demo Complete ==="
echo ""
echo "This demonstration covered:"
echo "- Basic output redirection (>, >>)"
echo "- Input redirection (<)"
echo "- Pipelines (|)"
echo "- Combined redirection and pipelines"
echo "- Text processing with grep, awk, sed, sort, uniq"
echo "- Diff and patch operations"
echo "- Multi-file operations"
echo "- Real-world log analysis example"
echo ""
echo "All demo files created in /tmp/demo/"