#!/usr/bin/env python
"""Demonstrate file operations in virtual filesystem using Python"""

import os

def create_directory_structure():
    """Create a directory structure"""
    print("Creating directory structure...")
    
    # Create nested directories
    os.makedirs('python_data/input', exist_ok=True)
    os.makedirs('python_data/output', exist_ok=True)
    os.makedirs('python_data/processed', exist_ok=True)
    
    print("  Directories created")

def create_sample_files():
    """Create some sample files"""
    print("\nCreating sample files...")
    
    # Write text file
    with open('python_data/input/data.txt', 'w') as f:
        f.write("Line 1: Sample data\n")
        f.write("Line 2: More data\n")
        f.write("Line 3: Even more data\n")
    
    # Write CSV file
    with open('python_data/input/records.csv', 'w') as f:
        f.write("Name,Age,City\n")
        f.write("Alice,30,New York\n")
        f.write("Bob,25,San Francisco\n")
        f.write("Charlie,35,Chicago\n")
    
    print("  Files created")

def process_files():
    """Process the files"""
    print("\nProcessing files...")
    
    # Read and process text file
    with open('python_data/input/data.txt', 'r') as f:
        lines = f.readlines()
        
    # Write processed version
    with open('python_data/output/processed_data.txt', 'w') as f:
        for i, line in enumerate(lines, 1):
            f.write(f"[{i}] {line.upper()}")
    
    print("  Text file processed")
    
    # Process CSV file
    with open('python_data/input/records.csv', 'r') as f:
        header = f.readline()
        records = f.readlines()
    
    # Create summary
    with open('python_data/output/summary.txt', 'w') as f:
        f.write(f"Total records: {len(records)}\n")
        f.write(f"Fields: {header.strip()}\n")
        f.write("\nRecords:\n")
        for record in records:
            f.write(f"  - {record.strip()}\n")
    
    print("  CSV file processed")

def list_files():
    """List all files in the structure"""
    print("\nDirectory listing:")
    
    for root, dirs, files in os.walk('python_data'):
        level = root.replace('python_data', '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            path = os.path.join(root, file)
            size = len(open(path, 'r').read()) if os.path.isfile(path) else 0
            print(f"{subindent}{file} ({size} bytes)")

def file_operations():
    """Demonstrate various file operations"""
    print("\nFile operations:")
    
    # Check file existence
    test_file = 'python_data/input/data.txt'
    if os.path.exists(test_file):
        print(f"  ✓ {test_file} exists")
    
    # Get file info
    if os.path.isfile(test_file):
        with open(test_file, 'r') as f:
            content = f.read()
        print(f"  ✓ {test_file} is a file with {len(content)} bytes")
    
    # Copy file content
    source = 'python_data/output/processed_data.txt'
    dest = 'python_data/processed/final_data.txt'
    
    if os.path.exists(source):
        with open(source, 'r') as f:
            content = f.read()
        with open(dest, 'w') as f:
            f.write(content)
        print(f"  ✓ Copied {source} to {dest}")
    
    # Append to file
    with open('python_data/processed/log.txt', 'a') as f:
        f.write("Processing completed\n")
    print("  ✓ Appended to log file")

def read_file_methods():
    """Demonstrate different ways to read files"""
    print("\nDifferent file reading methods:")
    
    test_file = 'python_data/input/data.txt'
    
    # Read entire file
    print("  1. Read entire file:")
    with open(test_file, 'r') as f:
        content = f.read()
        print(f"     Total: {len(content)} characters")
    
    # Read line by line
    print("  2. Read line by line:")
    with open(test_file, 'r') as f:
        for i, line in enumerate(f, 1):
            print(f"     Line {i}: {line.strip()}")
    
    # Read into list
    print("  3. Read into list:")
    with open(test_file, 'r') as f:
        lines = f.readlines()
        print(f"     Got {len(lines)} lines")

def main():
    print("=== Python File Operations Demo ===\n")
    
    create_directory_structure()
    create_sample_files()
    process_files()
    list_files()
    file_operations()
    read_file_methods()
    
    print("\nDemo completed!")

if __name__ == '__main__':
    main()