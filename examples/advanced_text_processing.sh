#!/bin/sh
# Advanced Text Processing Demonstration
# This script showcases all text processing commands with real-world examples

echo "========================================="
echo "Advanced Text Processing with Virtual Shell"
echo "========================================="
echo ""

# Setup
mkdir -p /tmp/text_demo
cd /tmp/text_demo

echo "=== Part 1: Data Preparation ==="
echo ""

# Create a sample log file
cat > server.log << EOF
2024-01-15 08:15:23 INFO Server started on port 8080
2024-01-15 08:15:24 DEBUG Loading configuration from config.yml
2024-01-15 08:15:25 INFO Database connection established
2024-01-15 08:16:10 WARNING High memory usage detected: 85%
2024-01-15 08:16:45 ERROR Failed to process request: timeout
2024-01-15 08:17:00 INFO Request from 192.168.1.100: GET /api/users
2024-01-15 08:17:01 INFO Request from 192.168.1.101: POST /api/login
2024-01-15 08:17:30 ERROR Database connection lost
2024-01-15 08:17:31 WARNING Attempting to reconnect...
2024-01-15 08:17:35 INFO Database reconnected successfully
2024-01-15 08:18:00 INFO Request from 192.168.1.100: GET /api/data
2024-01-15 08:18:15 DEBUG Cache hit for key: user_sessions
2024-01-15 08:18:30 ERROR Disk space critical: 95% used
2024-01-15 08:19:00 INFO Scheduled backup completed
2024-01-15 08:19:30 WARNING SSL certificate expires in 7 days
EOF

# Create a CSV file with sales data
cat > sales.csv << EOF
Date,Product,Category,Quantity,Price,Total
2024-01-01,Laptop,Electronics,5,1200,6000
2024-01-01,Mouse,Accessories,20,25,500
2024-01-02,Keyboard,Accessories,15,75,1125
2024-01-02,Monitor,Electronics,8,400,3200
2024-01-03,Laptop,Electronics,3,1200,3600
2024-01-03,Headphones,Accessories,10,150,1500
2024-01-04,Tablet,Electronics,7,600,4200
2024-01-04,Mouse,Accessories,25,25,625
2024-01-05,Monitor,Electronics,5,400,2000
2024-01-05,Keyboard,Accessories,12,75,900
EOF

# Create a configuration file
cat > app.conf << EOF
# Application Configuration
server.host=localhost
server.port=8080
server.ssl=false

database.host=db.example.com
database.port=5432
database.name=myapp
database.pool_size=10

cache.enabled=true
cache.ttl=3600
cache.max_size=100MB

logging.level=INFO
logging.file=/var/log/app.log
logging.rotate=daily
EOF

echo "Sample files created:"
echo "- server.log (system log file)"
echo "- sales.csv (sales data)"
echo "- app.conf (configuration file)"
echo ""

echo "=== Part 2: GREP - Pattern Searching ==="
echo ""

echo "1. Find all ERROR messages:"
grep ERROR server.log
echo ""

echo "2. Count WARNING and ERROR messages:"
grep -c WARNING server.log > warn_count.txt
grep -c ERROR server.log > err_count.txt
echo "Warnings: "
cat warn_count.txt
echo "Errors: "
cat err_count.txt
echo ""

echo "3. Find requests from specific IP with line numbers:"
grep -n "192.168.1.100" server.log
echo ""

echo "4. Find lines NOT containing INFO (inverse match):"
grep -v INFO server.log
echo ""

echo "5. Case-insensitive search for 'error':"
grep -i error server.log
echo ""

echo "6. Find whole word 'port' (not 'portable', 'support', etc.):"
grep -w "port" app.conf
echo ""

echo "=== Part 3: AWK - Data Extraction and Processing ==="
echo ""

echo "1. Extract timestamp and log level from server.log:"
awk '{print $1, $2, $3}' server.log | head -5
echo ""

echo "2. Calculate total sales sum:"
tail -n +2 sales.csv | awk -F, '{sum+=$6} END {print "Total sales: $" sum}'
echo ""

echo "3. Find high-value transactions (total > 2000):"
tail -n +2 sales.csv | awk -F, '$6>2000 {print $2 " on " $1 ": $" $6}'
echo ""

echo "4. Count log entries by level:"
awk '{print $3}' server.log | sort | uniq -c
echo ""

echo "5. Calculate average quantity per sale:"
tail -n +2 sales.csv | awk -F, '{sum+=$4; count++} END {print "Average quantity: " sum/count}'
echo ""

echo "6. Extract and format configuration values:"
grep -v "^#" app.conf | grep "=" | awk -F= '{print $1 " => " $2}' | head -5
echo ""

echo "=== Part 4: SED - Stream Editing ==="
echo ""

echo "1. Replace localhost with production server:"
sed 's/localhost/prod.example.com/g' app.conf | grep server.host
echo ""

echo "2. Delete comment lines from config:"
sed '/^#/d' app.conf | head -5
echo ""

echo "3. Add line numbers to log entries:"
sed = server.log | sed 'N;s/\n/: /' | head -5
echo ""

echo "4. Replace multiple values in config:"
sed -e 's/8080/443/g' -e 's/false/true/g' app.conf | grep "port\|ssl"
echo ""

echo "5. Extract lines between timestamps:"
sed -n '/08:17:00/,/08:18:00/p' server.log
echo ""

echo "=== Part 5: SORT - Data Sorting ==="
echo ""

echo "1. Sort sales by product name:"
tail -n +2 sales.csv | sort -t, -k2
echo ""

echo "2. Sort sales by total (numeric, descending):"
tail -n +2 sales.csv | sort -t, -k6 -rn | head -5
echo ""

echo "3. Sort unique IP addresses from log:"
grep "Request from" server.log | awk '{split($8,a,":"); print a[1]}' | sort -u
echo ""

echo "4. Sort configuration alphabetically:"
sort app.conf | head -10
echo ""

echo "=== Part 6: UNIQ - Duplicate Management ==="
echo ""

# Create file with duplicates
awk '{print $3}' server.log > log_levels.txt

echo "1. Remove consecutive duplicate log levels:"
sort log_levels.txt | uniq
echo ""

echo "2. Count occurrences of each log level:"
sort log_levels.txt | uniq -c
echo ""

echo "3. Show only duplicate entries:"
sort log_levels.txt | uniq -d
echo ""

echo "4. Show only unique entries:"
sort log_levels.txt | uniq -u
echo ""

echo "=== Part 7: HEAD and TAIL - File Viewing ==="
echo ""

echo "1. First 3 log entries:"
head -n 3 server.log
echo ""

echo "2. Last 3 log entries:"
tail -n 3 server.log
echo ""

echo "3. All except last 5 lines:"
head -n -5 server.log
echo ""

echo "4. From line 10 to end:"
tail -n +10 server.log | head -5
echo ""

echo "=== Part 8: WC - Counting ==="
echo ""

echo "1. Count lines, words, and bytes in server.log:"
wc server.log
echo ""

echo "2. Count number of sales records:"
tail -n +2 sales.csv | wc -l > sales_count.txt
echo "Total sales records:"
cat sales_count.txt
echo ""

echo "3. Count words in configuration file:"
grep -v '^#' app.conf | wc -l > config_count.txt
echo "Configuration parameters:"
cat config_count.txt
echo ""

echo "4. Count total bytes in all files:"
wc -c *.log *.csv *.conf
echo ""

echo "=== Part 9: DIFF and PATCH - File Comparison ==="
echo ""

# Create modified config
sed 's/8080/9090/g' app.conf > app_new.conf
sed -i 's/INFO/DEBUG/g' app_new.conf

echo "1. Compare original and modified configs:"
diff app.conf app_new.conf
echo ""

echo "2. Create unified diff patch:"
diff -u app.conf app_new.conf > config.patch
echo "Patch created. Contents:"
cat config.patch
echo ""

echo "3. Apply patch to original:"
cp app.conf app_backup.conf
patch app_backup.conf < config.patch
echo "Patch applied. Verification:"
grep -E "port|level" app_backup.conf
echo ""

echo "=== Part 10: Complex Pipeline Examples ==="
echo ""

echo "1. Top 3 products by revenue:"
tail -n +2 sales.csv | awk -F, '{print $2 "," $6}' | sort -t, -k2 -rn | head -3
echo ""

echo "2. Extract unique error messages and count:"
grep ERROR server.log | sed 's/.*ERROR //' | sort | uniq -c
echo ""

echo "3. Process log to create summary report:"
echo "Log Summary Report:"
echo "=================="
wc -l < server.log > total_lines.txt
echo "Total entries:"
cat total_lines.txt
head -1 server.log | awk '{print "Start time: " $1, $2}'
tail -1 server.log | awk '{print "End time: " $1, $2}'
echo ""
echo "Log levels distribution:"
awk '{print $3}' server.log | sort | uniq -c | awk '{printf "  %-10s: %3d entries\n", $2, $1}'
echo ""

echo "4. Show sales by category:"
echo "Sales by Category:"
echo "=================="
tail -n +2 sales.csv | awk -F, '{print $3 ": $" $6}' | sort
echo ""

echo "5. Configuration audit - find security issues:"
echo "Security Audit:"
echo "=============="
grep -E "ssl=false|password|secret" app.conf > security_issues.txt
if [ -s security_issues.txt ]; then
    echo "Found potential security issues:"
    cat security_issues.txt
else
    echo "No obvious security issues found"
fi
echo ""

echo "6. Create CSV report of errors with timestamps:"
echo "Timestamp,Level,Message" > error_report.csv
grep ERROR server.log | awk '{print $1 "," $3 "," substr($0, index($0,$4))}' >> error_report.csv
echo "Error report created:"
cat error_report.csv
echo ""

echo "=== Part 11: Real-World Data Processing Pipeline ==="
echo ""

# Create sample web access log
cat > access.log << EOF
192.168.1.10 - - [15/Jan/2024:10:00:00] "GET /index.html HTTP/1.1" 200 5234 0.123
192.168.1.11 - - [15/Jan/2024:10:00:01] "GET /css/style.css HTTP/1.1" 200 2345 0.045
192.168.1.10 - - [15/Jan/2024:10:00:02] "GET /js/app.js HTTP/1.1" 200 8976 0.067
192.168.1.12 - - [15/Jan/2024:10:00:03] "POST /api/login HTTP/1.1" 200 234 0.234
192.168.1.13 - - [15/Jan/2024:10:00:04] "GET /admin HTTP/1.1" 403 234 0.012
192.168.1.11 - - [15/Jan/2024:10:00:05] "GET /api/users HTTP/1.1" 200 5678 0.456
192.168.1.10 - - [15/Jan/2024:10:00:06] "GET /images/logo.png HTTP/1.1" 304 0 0.001
192.168.1.14 - - [15/Jan/2024:10:00:07] "GET /api/data HTTP/1.1" 500 567 1.234
192.168.1.12 - - [15/Jan/2024:10:00:08] "GET /index.html HTTP/1.1" 200 5234 0.089
192.168.1.15 - - [15/Jan/2024:10:00:09] "GET /robots.txt HTTP/1.1" 404 234 0.023
EOF

echo "Web Traffic Analysis Pipeline:"
echo "=============================="
echo ""

echo "1. Top 3 IP addresses by request count:"
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -3
echo ""

echo "2. HTTP status code distribution:"
awk '{print $9}' access.log | sort | uniq -c | sort -rn
echo ""

echo "3. Slowest requests (response time > 0.1 seconds):"
awk '$11 > 0.1 {print $7 " - " $11 "s"}' access.log | sort -t- -k2 -rn
echo ""

echo "4. 404 errors - missing resources:"
grep " 404 " access.log | awk '{print $7}'
echo ""

echo "5. Calculate average response time:"
awk '{sum+=$11; count++} END {printf "Average response time: %.3f seconds\n", sum/count}' access.log
echo ""

echo "6. Data transfer by status code:"
awk '{bytes[$9]+=$10} END {for(code in bytes) printf "Status %s: %d bytes\n", code, bytes[code]}' access.log | sort
echo ""

echo "=== Part 12: Text Transformation Examples ==="
echo ""

# Create sample data file
cat > users.txt << EOF
john.doe@example.com:John Doe:Developer:Active
jane.smith@example.com:Jane Smith:Manager:Active  
bob.wilson@example.com:Bob Wilson:Designer:Inactive
alice.jones@example.com:Alice Jones:Developer:Active
charlie.brown@example.com:Charlie Brown:Tester:Active
EOF

echo "User data transformations:"
echo ""

echo "1. Extract email addresses:"
awk -F: '{print $1}' users.txt
echo ""

echo "2. Format as SQL INSERT statements:"
awk -F: '{printf "INSERT INTO users (email, name, role, status) VALUES ('\''%s'\'', '\''%s'\'', '\''%s'\'', '\''%s'\'');\n", $1, $2, $3, $4}' users.txt | head -2
echo ""

echo "3. Create JSON format:"
echo "["
awk -F: '{printf "  {\"email\": \"%s\", \"name\": \"%s\", \"role\": \"%s\", \"status\": \"%s\"},\n", $1, $2, $3, $4}' users.txt | sed '$s/,$//'
echo "]"
echo ""

echo "4. Generate username from email:"
sed 's/@.*//' users.txt | sed 's/:/ | Username: /' | head -3
echo ""

echo "5. Count users by role:"
awk -F: '{print $3}' users.txt | sort | uniq -c | awk '{printf "%-10s: %2d users\n", $2, $1}'
echo ""

echo "=== Summary ==="
echo ""
echo "This demonstration covered:"
echo "- grep: Pattern searching with various options"
echo "- awk: Advanced data extraction and processing"
echo "- sed: Stream editing and text transformation"  
echo "- sort: Data sorting with multiple keys"
echo "- uniq: Duplicate detection and counting"
echo "- head/tail: File viewing and extraction"
echo "- wc: Counting lines, words, and bytes"
echo "- diff/patch: File comparison and patching"
echo "- Complex pipelines combining multiple tools"
echo "- Real-world log analysis and data processing"
echo ""
echo "All demo files created in /tmp/text_demo/"
echo "===================================="