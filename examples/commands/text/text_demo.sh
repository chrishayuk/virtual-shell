#!/bin/bash

# Text Processing Commands Comprehensive Demo
# This script demonstrates all text processing commands with working examples

echo "=== TEXT PROCESSING COMMANDS DEMO ==="
echo

# Setup test environment
echo "Setting up text processing test environment..."
mkdir -p /tmp/text_demo
cd /tmp/text_demo

# Create various test files using virtual shell commands
echo "Creating test files with diverse content..."

# Sample log file
echo "2023-12-01 10:00:01 INFO Server started on port 8080" > server.log
echo "2023-12-01 10:00:15 INFO User john logged in" >> server.log
echo "2023-12-01 10:01:23 ERROR Failed to connect to database" >> server.log
echo "2023-12-01 10:01:45 WARN Database connection retrying" >> server.log
echo "2023-12-01 10:02:10 INFO Database connection restored" >> server.log
echo "2023-12-01 10:02:15 INFO User mary logged in" >> server.log
echo "2023-12-01 10:03:22 ERROR Invalid password for user bob" >> server.log
echo "2023-12-01 10:03:45 INFO User alice logged in" >> server.log
echo "2023-12-01 10:04:12 DEBUG Memory usage: 45%" >> server.log
echo "2023-12-01 10:04:33 INFO Processing 150 requests" >> server.log

# Data file with numbers and text
echo "apple,5,red" > data.txt
echo "banana,3,yellow" >> data.txt
echo "cherry,8,red" >> data.txt
echo "date,2,brown" >> data.txt
echo "elderberry,12,purple" >> data.txt
echo "fig,7,purple" >> data.txt
echo "grape,15,green" >> data.txt
echo "honeydew,4,green" >> data.txt

# Source code file
echo "#!/usr/bin/env python3" > script.py
echo "" >> script.py
echo "def calculate_sum(numbers):" >> script.py
echo '    """Calculate sum of numbers."""' >> script.py
echo "    total = 0" >> script.py
echo "    for num in numbers:" >> script.py
echo "        total += num" >> script.py
echo "    return total" >> script.py
echo "" >> script.py
echo "def main():" >> script.py
echo "    # Sample data" >> script.py
echo "    data = [1, 2, 3, 4, 5]" >> script.py
echo "    result = calculate_sum(data)" >> script.py
echo '    print(f"Sum: {result}")' >> script.py
echo "" >> script.py
echo 'if __name__ == "__main__":' >> script.py
echo "    main()" >> script.py

# Mixed content file
echo "This is line 1" > mixed.txt
echo "This is line 2" >> mixed.txt
echo "Another line here" >> mixed.txt
echo "This is line 4" >> mixed.txt
echo "Yet another line" >> mixed.txt
echo "This is line 6" >> mixed.txt
echo "Final line here" >> mixed.txt
echo "Some random text" >> mixed.txt
echo "This is line 9" >> mixed.txt
echo "Last line of file" >> mixed.txt

# Sorted/unsorted data for demonstration
echo "zebra" > unsorted.txt
echo "apple" >> unsorted.txt
echo "banana" >> unsorted.txt
echo "dog" >> unsorted.txt
echo "cat" >> unsorted.txt
echo "elephant" >> unsorted.txt
echo "fish" >> unsorted.txt

# Duplicate data for uniq demonstration
echo "apple" > duplicates.txt
echo "banana" >> duplicates.txt
echo "apple" >> duplicates.txt
echo "cherry" >> duplicates.txt
echo "banana" >> duplicates.txt
echo "date" >> duplicates.txt
echo "apple" >> duplicates.txt
echo "cherry" >> duplicates.txt

echo "Test files created successfully!"
echo

# 1. GREP COMMAND
echo "=== 1. GREP COMMAND ==="

echo "Basic text search:"
grep "INFO" server.log

echo "Case insensitive search (-i):"
grep -i "error" server.log

echo "Show line numbers (-n):"
grep -n "User" server.log

echo "Count matches (-c):"
grep -c "INFO" server.log

echo "Invert match (-v) - show non-INFO lines:"
grep -v "INFO" server.log

echo "Whole word matching (-w):"
grep -w "port" server.log

echo "Multiple files:"
grep "line" mixed.txt script.py

echo "Regular expressions:"
grep "^2023.*ERROR" server.log
grep "[0-9]+" server.log

echo "Pipe input:"
echo "test error message" | grep -i "error"
echo

# 2. SED COMMAND
echo "=== 2. SED COMMAND ==="

echo "Substitute/replace text:"
sed 's/INFO/INFORMATION/' server.log

echo "Replace all occurrences (g flag):"
sed 's/line/LINE/g' mixed.txt

echo "Case insensitive replace (i flag):"
sed 's/error/ERROR/i' server.log

echo "Delete lines matching pattern:"
sed '/DEBUG/d' server.log

echo "Print specific lines:"
sed -n '1,3p' mixed.txt

echo "Insert text before matching line:"
sed '/main/i# Main function definition' script.py

echo "Append text after matching line:"
sed '/def main/a    # This is the main function' script.py

echo "Multiple operations:"
sed -e 's/INFO/INFO:/' -e 's/ERROR/ERROR:/' server.log
echo

# 3. AWK COMMAND
echo "=== 3. AWK COMMAND ==="

echo "Print specific columns:"
awk -F',' '{print $1, $2}' data.txt

echo "Print with custom formatting:"
awk -F',' '{printf "Fruit: %-12s Quantity: %d\n", $1, $2}' data.txt

echo "Filter rows based on conditions:"
awk -F',' '$2 > 5 {print $1 " has quantity " $2}' data.txt

echo "Sum numeric column:"
awk -F',' '{sum += $2} END {print "Total quantity:", sum}' data.txt

echo "Pattern matching:"
awk '/ERROR/ {print "Found error: " $0}' server.log

echo "Built-in variables:"
awk '{print "Line", NR ":", $0}' mixed.txt

echo "String functions:"
awk -F',' '{print toupper($1)}' data.txt

echo "Complex processing:"
awk -F',' '$3 == "red" {red++} $3 == "green" {green++} END {print "Red:", red, "Green:", green}' data.txt
echo

# 4. SORT COMMAND
echo "=== 4. SORT COMMAND ==="

echo "Basic alphabetical sort:"
sort unsorted.txt

echo "Reverse sort (-r):"
sort -r unsorted.txt

echo "Numeric sort (-n):"
echo -e "10\n2\n1\n20" | sort -n

echo "Sort by specific field (-k):"
sort -t',' -k2 -n data.txt

echo "Sort and remove duplicates (-u):"
sort -u duplicates.txt

echo "Case insensitive sort (-f):"
echo -e "Zebra\napple\nBanana" | sort -f
echo

# 5. UNIQ COMMAND  
echo "=== 5. UNIQ COMMAND ==="

echo "Remove consecutive duplicates:"
sort duplicates.txt | uniq

echo "Count occurrences (-c):"
sort duplicates.txt | uniq -c

echo "Show only duplicates (-d):"
sort duplicates.txt | uniq -d

echo "Show only unique lines (-u):"
sort duplicates.txt | uniq -u

echo "Case insensitive (-i):"
echo -e "Apple\napple\nBanana\nbanana" | sort | uniq -i
echo

# 6. WC COMMAND
echo "=== 6. WC COMMAND ==="

echo "Count lines, words, characters:"
wc mixed.txt

echo "Count lines only (-l):"
wc -l server.log

echo "Count words only (-w):"
wc -w script.py

echo "Count characters only (-c):"
wc -c data.txt

echo "Multiple files:"
wc mixed.txt data.txt

echo "Pipe input:"
echo "Count these words in this sentence" | wc -w
echo

# 7. HEAD COMMAND
echo "=== 7. HEAD COMMAND ==="

echo "First 10 lines (default):"
head server.log

echo "First 5 lines (-n 5):"
head -n 5 mixed.txt

echo "First 3 lines (-3):"
head -3 data.txt

echo "Multiple files:"
head -n 3 mixed.txt data.txt

echo "Pipe input:"
ls -la | head -5
echo

# 8. TAIL COMMAND
echo "=== 8. TAIL COMMAND ==="

echo "Last 10 lines (default):"
tail mixed.txt

echo "Last 3 lines (-n 3):"
tail -n 3 server.log

echo "Last 5 lines (-5):"
tail -5 data.txt

echo "Multiple files:"
tail -n 2 mixed.txt data.txt

echo "Pipe input:"
sort unsorted.txt | tail -3
echo

# 9. DIFF COMMAND
echo "=== 9. DIFF COMMAND ==="

echo "Creating two similar files for diff demonstration:"
echo -e "line1\nline2\nline3\nline4" > file1.txt
echo -e "line1\nmodified line2\nline3\nnew line4\nline5" > file2.txt

echo "Basic diff:"
diff file1.txt file2.txt

echo "Side by side comparison (-y):"
diff -y file1.txt file2.txt

echo "Unified format (-u):"
diff -u file1.txt file2.txt

echo "Context format (-c):"
diff -c file1.txt file2.txt
echo

# 10. PATCH COMMAND
echo "=== 10. PATCH COMMAND ==="

echo "Create a patch file:"
diff -u file1.txt file2.txt > changes.patch

echo "Show patch content:"
cat changes.patch

echo "Apply patch (create backup):"
cp file1.txt file1_backup.txt
patch file1.txt < changes.patch
echo "Patched file1.txt content:"
cat file1.txt

echo "Restore original and test reverse patch:"
cp file1_backup.txt file1.txt
patch -R file1.txt < changes.patch
echo "After reverse patch:"
cat file1.txt
echo

# 11. COMBINED OPERATIONS DEMO
echo "=== 11. COMBINED TEXT PROCESSING ==="

echo "Complex pipeline example:"
echo "Find ERROR logs, extract timestamps and messages:"
grep "ERROR" server.log | sed 's/^[^ ]* [^ ]* //' | sort

echo "Process CSV data with multiple tools:"
echo "Sort by quantity, get top 3, format output:"
sort -t',' -k2 -nr data.txt | head -3 | awk -F',' '{printf "%s: %d items\n", $1, $2}'

echo "Text analysis pipeline:"
echo "Count unique words in script, sort by frequency:"
cat script.py | tr -s ' ' '\n' | grep -v '^$' | sort | uniq -c | sort -nr | head -10

echo "Log analysis pipeline:"
echo "Extract user activities and summarize:"
grep "User.*logged in" server.log | sed 's/.*User \([^ ]*\) logged in.*/\1/' | sort | uniq -c

echo "Data validation pipeline:"
echo "Find fruits with quantity > 5, count colors:"
awk -F',' '$2 > 5 {print $3}' data.txt | sort | uniq -c
echo

# 12. ADVANCED PATTERN MATCHING
echo "=== 12. ADVANCED PATTERN MATCHING ==="

echo "Complex grep patterns:"
grep -E "(ERROR|WARN)" server.log
grep "^2023.*[0-9]{2}:[0-9]{2}:[0-9]{2}" server.log

echo "AWK advanced patterns:"
awk '/^def/ || /^class/ {print "Found definition: " $0}' script.py

echo "SED advanced operations:"
sed -n '/def/,/^$/p' script.py

echo "Multi-step text transformations:"
cat data.txt | sed 's/,/ | /g' | awk '{print "Item: " $0}' | sort
echo

# 13. ERROR HANDLING DEMO
echo "=== 13. ERROR HANDLING ==="

echo "Handle non-existent files:"
grep "pattern" non_existent.txt || echo "File not found error handled"
head non_existent.txt || echo "Head command error handled"
wc non_existent.txt || echo "WC command error handled"

echo "Handle invalid patterns:"
grep -E "[" server.log || echo "Invalid regex pattern handled"

echo "Handle empty input:"
echo "" | grep "anything" || echo "No matches in empty input"
echo

echo "=== TEXT PROCESSING DEMO COMPLETE ==="
echo "All text processing commands demonstrated successfully!"

# Clean up
cd ..
echo "Demo directory contents:"
ls -la text_demo/