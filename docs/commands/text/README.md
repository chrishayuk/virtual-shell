# Text Processing Commands

Comprehensive text manipulation, analysis, and transformation tools for processing files and data streams.

## Commands Overview

### Text Display and Extraction
| Command | Description | Documentation |
|---------|-------------|---------------|
| [`head`](head.md) | Display first lines or bytes of files | [head.md](head.md) |
| [`tail`](tail.md) | Display last lines or bytes of files | [tail.md](tail.md) |
| [`grep`](grep.md) | Search for patterns in files | [grep.md](grep.md) |

### Text Analysis and Statistics
| Command | Description | Documentation |
|---------|-------------|---------------|
| [`wc`](wc.md) | Count lines, words, characters, and bytes | [wc.md](wc.md) |
| [`sort`](sort.md) | Sort lines of text files | [sort.md](sort.md) |
| [`uniq`](uniq.md) | Report or omit repeated consecutive lines | [uniq.md](uniq.md) |

### Text Transformation
| Command | Description | Documentation |
|---------|-------------|---------------|
| [`sed`](sed.md) | Stream editor for text transformation | [sed.md](sed.md) |
| [`awk`](awk.md) | Pattern scanning and data processing language | [awk.md](awk.md) |

### File Comparison and Patching
| Command | Description | Documentation |
|---------|-------------|---------------|
| [`diff`](diff.md) | Compare files line by line | [diff.md](diff.md) |
| [`patch`](patch.md) | Apply diff patches to files | [patch.md](patch.md) |

## Common Usage Patterns

### Text Viewing and Navigation
```bash
# Preview files
head -10 largefile.txt          # First 10 lines
tail -20 logfile.log            # Last 20 lines  
more document.txt               # Page through file

# Search content
grep "error" system.log         # Find error lines
grep -i "warning" *.log         # Case-insensitive search
grep -n "function" script.py    # Show line numbers
```

### Text Analysis and Statistics
```bash
# Count and analyze
wc -l file.txt                  # Count lines
wc -w document.txt              # Count words
wc -c data.bin                  # Count bytes

# Sort and deduplicate
sort names.txt                  # Sort alphabetically
sort -n numbers.txt             # Sort numerically
sort data.txt | uniq            # Remove duplicates
sort data.txt | uniq -c         # Count occurrences
```

### Data Processing Pipelines
```bash
# Process log files
cat access.log | grep "ERROR" | wc -l          # Count errors
tail -100 app.log | grep "user" | sort | uniq  # Unique recent users

# Text transformation
sed 's/old/new/g' file.txt                     # Replace text
awk '{print $1}' data.txt                      # Extract first field
grep "pattern" file.txt | awk '{sum+=$3} END {print sum}'  # Sum values
```

### File Comparison and Version Control
```bash
# Compare files
diff original.txt modified.txt                 # Show differences
diff -u old.py new.py > changes.patch          # Create patch
patch < changes.patch                          # Apply patch

# Side-by-side comparison
diff --side-by-side file1.txt file2.txt       # Two-column view
```

## Advanced Text Processing

### Complex AWK Processing
```bash
# Data analysis
awk -F, '{sum[$2]+=$3} END {for(i in sum) print i, sum[i]}' data.csv
awk 'NR==1 {print "Header:", $0} /error/ {errors++} END {print "Errors:", errors}' log.txt

# Report generation
awk 'BEGIN {print "Sales Report"} {total+=$2} END {print "Total:", total}' sales.txt
```

### Advanced SED Operations
```bash
# Text substitution and editing
sed -i 's/production/staging/g' config.txt     # In-place editing
sed -n '/start/,/end/p' file.txt               # Print range
sed '1d;$d' file.txt                           # Remove first and last lines
```

### Pipeline Combinations
```bash
# Complex data processing
cat data.txt | grep -v "^#" | sort | uniq -c | sort -nr | head -10
# Remove comments, sort, count unique, sort by count, show top 10

# Log analysis
tail -1000 access.log | awk '{print $1}' | sort | uniq -c | sort -nr
# Get recent IPs, count occurrences, sort by frequency
```

## Data Format Support

### Structured Data
```bash
# CSV processing
awk -F, '{print $2}' data.csv                  # Extract column
sort -t, -k2 data.csv                          # Sort by column

# Tab-separated data  
cut -f1,3 data.tsv | sort                      # Extract and sort fields
```

### Log File Analysis
```bash
# System logs
grep "$(date '+%Y-%m-%d')" /var/log/system.log # Today's entries
awk '/ERROR/ {print $1, $2, $5}' app.log      # Extract error info
```

## Key Features

- **Pipeline Support:** Commands work seamlessly with Unix pipes
- **Regular Expressions:** Advanced pattern matching in grep, sed, awk
- **Multiple Input Sources:** Support for files and stdin
- **Flexible Output:** Various formatting options and modes
- **Error Handling:** Comprehensive error reporting and recovery
- **Performance:** Optimized for large files and data processing

## Performance Tips

1. **Use appropriate tools:** `grep` for searching, `awk` for field processing
2. **Pipeline efficiently:** Place filters early to reduce data volume
3. **Sort before uniq:** `uniq` only works on adjacent duplicates
4. **Use specific patterns:** More specific regex patterns are faster
5. **Process in chunks:** Use `head` and `tail` for large files

## See Also

- [Filesystem Commands](../filesystem/README.md) - File operations and management
- [Navigation Commands](../navigation/README.md) - Directory navigation
- [System Commands](../system/README.md) - Script execution and system tools
- [Main Documentation](../../README.md) - Complete command reference