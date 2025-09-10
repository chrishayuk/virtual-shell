#!/usr/bin/env python
"""Process data files using Python in virtual filesystem"""

import os
import sys
import re
from collections import Counter

def create_sample_data():
    """Create sample data files"""
    print("Creating sample data files...")
    
    # Create log file
    with open('server.log', 'w') as f:
        f.write("2024-01-15 10:30:15 INFO Server started\n")
        f.write("2024-01-15 10:30:20 ERROR Connection failed: timeout\n")
        f.write("2024-01-15 10:30:25 INFO Client connected from 192.168.1.100\n")
        f.write("2024-01-15 10:30:30 WARNING High memory usage: 85%\n")
        f.write("2024-01-15 10:30:35 ERROR Database connection lost\n")
        f.write("2024-01-15 10:30:40 INFO Request processed successfully\n")
        f.write("2024-01-15 10:30:45 ERROR Authentication failed for user: admin\n")
        f.write("2024-01-15 10:30:50 INFO Cache cleared\n")
        f.write("2024-01-15 10:30:55 WARNING Disk space low: 10GB remaining\n")
        f.write("2024-01-15 10:31:00 INFO Backup completed\n")
    
    # Create sales data
    with open('sales.csv', 'w') as f:
        f.write("Date,Product,Quantity,Price\n")
        f.write("2024-01-01,Widget A,5,10.99\n")
        f.write("2024-01-01,Widget B,3,15.99\n")
        f.write("2024-01-02,Widget A,8,10.99\n")
        f.write("2024-01-02,Widget C,2,25.99\n")
        f.write("2024-01-03,Widget B,6,15.99\n")
        f.write("2024-01-03,Widget A,4,10.99\n")
        f.write("2024-01-04,Widget C,5,25.99\n")
        f.write("2024-01-04,Widget B,7,15.99\n")
        f.write("2024-01-05,Widget A,10,10.99\n")
    
    # Create text file for word analysis
    with open('document.txt', 'w') as f:
        f.write("The quick brown fox jumps over the lazy dog. ")
        f.write("The dog was very lazy. The fox was quick and brown. ")
        f.write("Python is a great programming language. ")
        f.write("Python makes data processing easy and fun. ")
        f.write("The virtual filesystem allows safe file operations. ")
    
    print("  Sample data files created\n")

def analyze_logs():
    """Analyze log file"""
    print("=== Log Analysis ===")
    
    with open('server.log', 'r') as f:
        lines = f.readlines()
    
    # Count log levels
    levels = {'INFO': 0, 'WARNING': 0, 'ERROR': 0}
    errors = []
    
    for line in lines:
        for level in levels:
            if level in line:
                levels[level] += 1
                if level == 'ERROR':
                    # Extract error message
                    match = re.search(r'ERROR (.+)$', line)
                    if match:
                        errors.append(match.group(1))
    
    print(f"Total log entries: {len(lines)}")
    print("\nLog levels:")
    for level, count in levels.items():
        print(f"  {level}: {count}")
    
    print("\nErrors found:")
    for error in errors:
        print(f"  - {error}")
    
    # Write analysis report
    with open('log_analysis.txt', 'w') as f:
        f.write("Log Analysis Report\n")
        f.write("=" * 20 + "\n\n")
        f.write(f"Total entries: {len(lines)}\n")
        f.write(f"INFO: {levels['INFO']}\n")
        f.write(f"WARNING: {levels['WARNING']}\n")
        f.write(f"ERROR: {levels['ERROR']}\n")
        f.write(f"\nError rate: {levels['ERROR']/len(lines)*100:.1f}%\n")
    
    print("\n  Report saved to log_analysis.txt\n")

def process_sales_data():
    """Process sales CSV data"""
    print("=== Sales Data Processing ===")
    
    with open('sales.csv', 'r') as f:
        header = f.readline().strip().split(',')
        data = []
        for line in f:
            values = line.strip().split(',')
            data.append({
                'date': values[0],
                'product': values[1],
                'quantity': int(values[2]),
                'price': float(values[3])
            })
    
    # Calculate totals
    product_totals = {}
    daily_totals = {}
    
    for row in data:
        product = row['product']
        date = row['date']
        revenue = row['quantity'] * row['price']
        
        # Product totals
        if product not in product_totals:
            product_totals[product] = {'quantity': 0, 'revenue': 0}
        product_totals[product]['quantity'] += row['quantity']
        product_totals[product]['revenue'] += revenue
        
        # Daily totals
        if date not in daily_totals:
            daily_totals[date] = 0
        daily_totals[date] += revenue
    
    print("Product Summary:")
    for product, totals in sorted(product_totals.items()):
        print(f"  {product}:")
        print(f"    Quantity sold: {totals['quantity']}")
        print(f"    Total revenue: ${totals['revenue']:.2f}")
    
    print("\nDaily Revenue:")
    for date, revenue in sorted(daily_totals.items()):
        print(f"  {date}: ${revenue:.2f}")
    
    # Calculate statistics
    revenues = [row['quantity'] * row['price'] for row in data]
    avg_revenue = sum(revenues) / len(revenues)
    max_revenue = max(revenues)
    min_revenue = min(revenues)
    
    print(f"\nStatistics:")
    print(f"  Average transaction: ${avg_revenue:.2f}")
    print(f"  Highest transaction: ${max_revenue:.2f}")
    print(f"  Lowest transaction: ${min_revenue:.2f}")
    print(f"  Total revenue: ${sum(revenues):.2f}")
    
    # Write summary
    with open('sales_summary.txt', 'w') as f:
        f.write("Sales Summary Report\n")
        f.write("=" * 20 + "\n\n")
        for product, totals in sorted(product_totals.items()):
            f.write(f"{product}: {totals['quantity']} units, ${totals['revenue']:.2f}\n")
        f.write(f"\nTotal Revenue: ${sum(revenues):.2f}\n")
    
    print("\n  Summary saved to sales_summary.txt\n")

def word_frequency_analysis():
    """Analyze word frequency in text"""
    print("=== Word Frequency Analysis ===")
    
    with open('document.txt', 'r') as f:
        text = f.read().lower()
    
    # Remove punctuation and split into words
    words = re.findall(r'\b[a-z]+\b', text)
    
    # Count word frequency
    word_count = Counter(words)
    
    print(f"Total words: {len(words)}")
    print(f"Unique words: {len(word_count)}")
    
    print("\nTop 10 most common words:")
    for word, count in word_count.most_common(10):
        print(f"  '{word}': {count} times")
    
    # Find long words
    long_words = [word for word in word_count if len(word) > 7]
    print(f"\nWords longer than 7 characters:")
    for word in long_words:
        print(f"  - {word}")
    
    # Write word frequency report
    with open('word_analysis.txt', 'w') as f:
        f.write("Word Frequency Analysis\n")
        f.write("=" * 20 + "\n\n")
        f.write(f"Total words: {len(words)}\n")
        f.write(f"Unique words: {len(word_count)}\n\n")
        f.write("All words by frequency:\n")
        for word, count in word_count.most_common():
            f.write(f"  {word}: {count}\n")
    
    print("\n  Analysis saved to word_analysis.txt\n")

def generate_report():
    """Generate final report"""
    print("=== Generating Final Report ===")
    
    with open('final_report.txt', 'w') as f:
        f.write("Data Processing Summary Report\n")
        f.write("=" * 40 + "\n\n")
        
        # Include log analysis
        if os.path.exists('log_analysis.txt'):
            f.write("LOG ANALYSIS:\n")
            with open('log_analysis.txt', 'r') as log:
                f.write(log.read())
            f.write("\n" + "-" * 40 + "\n\n")
        
        # Include sales summary
        if os.path.exists('sales_summary.txt'):
            f.write("SALES SUMMARY:\n")
            with open('sales_summary.txt', 'r') as sales:
                f.write(sales.read())
            f.write("\n" + "-" * 40 + "\n\n")
        
        # List all generated files
        f.write("FILES GENERATED:\n")
        for file in os.listdir('.'):
            if file.endswith('.txt') or file.endswith('.csv') or file.endswith('.log'):
                f.write(f"  - {file}\n")
    
    print("  Final report saved to final_report.txt")
    print("\nAll processing complete!")

def main():
    print("=== Data Processing Demo ===\n")
    
    create_sample_data()
    analyze_logs()
    process_sales_data()
    word_frequency_analysis()
    generate_report()

if __name__ == '__main__':
    main()