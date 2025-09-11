#!/bin/sh
# Demonstrate text processing capabilities

echo "=== Text Processing Demo ==="
echo ""

# Create sample data file
cat > employees.txt << EOF
John Smith,Engineering,45000
Jane Doe,Marketing,50000
Bob Johnson,Engineering,48000
Alice Brown,Sales,42000
Charlie Wilson,Marketing,46000
Diana Prince,Engineering,52000
EOF

echo "Employee data created."
echo ""

# Display the data
echo "Original data:"
cat employees.txt
echo ""

# Grep examples
echo "=== GREP Examples ==="
echo "Engineers only:"
grep Engineering employees.txt
echo ""

echo "High earners (50k+):"
grep -E "[5-9][0-9]{4}" employees.txt
echo ""

# Sed examples
echo "=== SED Examples ==="
echo "Replace Engineering with Tech:"
sed 's/Engineering/Tech/g' employees.txt
echo ""

echo "Remove salary information:"
sed 's/,[0-9]*$//' employees.txt
echo ""

# Awk examples  
echo "=== AWK Examples ==="
echo "Names only (field 1):"
awk -F, '{print $1}' employees.txt
echo ""

echo "Calculate average salary:"
awk -F, '{sum+=$3; count++} END {print "Average: $" sum/count}' employees.txt
echo ""

echo "Employees by department:"
awk -F, '{print $2 ": " $1}' employees.txt | sort
echo ""

# Combined operations
echo "=== Combined Operations ==="
echo "Engineering salaries sorted:"
grep Engineering employees.txt | awk -F, '{print $3, $1}' | sort -n
echo ""

echo "Count employees per department:"
awk -F, '{print $2}' employees.txt | sort | uniq -c
echo ""

# Head and tail
echo "=== Head/Tail Examples ==="
echo "First 3 employees:"
head -n 3 employees.txt
echo ""

echo "Last 2 employees:"
tail -n 2 employees.txt
echo ""

# Word count
echo "=== Statistics ==="
echo "File statistics:"
wc employees.txt
echo ""

echo "Unique departments:"
awk -F, '{print $2}' employees.txt | sort -u