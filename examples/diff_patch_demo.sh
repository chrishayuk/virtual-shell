#!/bin/sh
# Demonstrate diff and patch commands

echo "=== Diff and Patch Demo ==="
echo ""

# Create original file
cat > original.txt << EOF
# Configuration File
# Version 1.0

server_name = localhost
port = 8080
debug = false
max_connections = 100

# Database settings
db_host = localhost
db_port = 5432
db_name = myapp
EOF

echo "Original configuration created."
echo ""

# Create modified version
cat > modified.txt << EOF
# Configuration File
# Version 1.1

server_name = production.example.com
port = 443
debug = false
max_connections = 500
ssl_enabled = true

# Database settings
db_host = db.example.com
db_port = 5432
db_name = myapp
db_pool_size = 20
EOF

echo "Modified configuration created."
echo ""

# Show the differences
echo "=== Showing differences ==="
echo "Unified diff format:"
diff -u original.txt modified.txt
echo ""

echo "Side-by-side comparison:"
diff --side-by-side original.txt modified.txt
echo ""

echo "Brief check (just report if different):"
diff -q original.txt modified.txt
echo ""

# Create a patch file
echo "=== Creating patch file ==="
diff -u original.txt modified.txt > config.patch
echo "Patch saved to config.patch"
echo ""

echo "Patch contents:"
cat config.patch
echo ""

# Apply the patch
echo "=== Applying patch ==="
cp original.txt original_backup.txt
patch original.txt < config.patch
echo ""

echo "Original file after patching:"
cat original.txt
echo ""

# Reverse the patch
echo "=== Reversing patch ==="
patch -R original.txt < config.patch
echo ""

echo "File after reversing patch (should match original):"
cat original.txt
echo ""

# Demonstrate sed usage
echo "=== Sed examples ==="
echo "Change all ports to 9090:"
sed 's/port = [0-9]*/port = 9090/g' original_backup.txt
echo ""

echo "Delete comment lines:"
sed '/^#/d' original_backup.txt
echo ""

echo "Replace localhost with 127.0.0.1:"
sed 's/localhost/127.0.0.1/g' original_backup.txt
echo ""

# Clean up
rm config.patch original_backup.txt
echo "=== Demo complete ==="