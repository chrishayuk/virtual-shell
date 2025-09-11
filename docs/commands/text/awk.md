# awk

Pattern scanning and data processing language.

## Synopsis

```
awk [OPTIONS] 'PROGRAM' [FILE]...
```

## Description

The `awk` command is a powerful pattern-scanning and data-processing language. It processes text files line by line, splitting each line into fields and allowing complex data manipulation and reporting.

## Options

- `-F fs` - Field separator (default: space/tab)
- `-Ffs` - Field separator (compact format, e.g., `-F,` or `-F:`)
- `-v var=val` - Set variable

## Program Structure

AWK programs can contain three types of blocks:
- `BEGIN { ... }` - Execute before processing any input
- `pattern { action }` - Execute action for lines matching pattern
- `END { ... }` - Execute after processing all input

## Built-in Variables

- `NF` - Number of fields in current line
- `NR` - Number of records (line number)
- `FS` - Field separator (input)
- `OFS` - Output field separator (default: space)
- `$0` - Entire current line
- `$1, $2, ...` - Individual fields (1-indexed)

## Arguments

- `PROGRAM` - AWK program to execute
- `FILE...` - Files to process (optional, uses stdin if not provided)

## Basic Examples

**Print entire file:**
```bash
awk '{print}' file.txt
awk '{print $0}' file.txt                   # Same as above
```

**Print specific fields:**
```bash
awk '{print $1}' file.txt                   # First field only
awk '{print $1, $3}' file.txt               # Fields 1 and 3
awk '{print $1 " " $3}' file.txt            # Custom separator
```

**Field information:**
```bash
awk '{print NF}' file.txt                   # Number of fields per line
awk '{print NR}' file.txt                   # Line numbers
awk '{print NR, $0}' file.txt               # Line numbers with content
```

## Field Separators

**Default (space/tab):**
```bash
awk '{print $1}' file.txt
```

**Custom separator:**
```bash
awk -F, '{print $1}' data.csv               # Comma-separated
awk -F: '{print $1}' /etc/passwd             # Colon-separated
awk -F'|' '{print $2}' data.txt              # Pipe-separated
```

## Pattern Matching

**Regular expressions:**
```bash
awk '/error/ {print}' logfile.txt            # Lines containing "error"
awk '/^#/ {print}' script.sh                 # Lines starting with #
```

**Field comparisons:**
```bash
awk '$1 == "user" {print}' data.txt          # First field equals "user"  
awk '$3 > 100 {print}' numbers.txt           # Third field greater than 100
awk '$2 != "N/A" {print}' data.txt           # Second field not equal to N/A
```

**Line number conditions:**
```bash
awk 'NR == 1 {print}' file.txt               # First line only
awk 'NR > 5 {print}' file.txt                # Lines after 5th
```

## BEGIN and END Blocks

**Initialize and summarize:**
```bash
awk 'BEGIN {print "Starting"} {print} END {print "Done"}' file.txt
```

**Calculate totals:**
```bash
awk '{sum += $1} END {print "Total:", sum}' numbers.txt
```

**Count lines:**
```bash
awk 'END {print "Lines:", NR}' file.txt
```

## Advanced Examples

**Sum a column:**
```bash
awk '{sum += $3} END {print sum}' data.txt
```

**Average calculation:**
```bash
awk '{sum += $1; count++} END {print sum/count}' numbers.txt
```

**Count occurrences:**
```bash
awk '{count[$1]++} END {for(item in count) print item, count[item]}' data.txt
```

**Print specific columns from CSV:**
```bash
awk -F, '{print $2, $4}' data.csv
```

**Format output:**
```bash
awk '{printf "%s: %d\n", $1, $2}' data.txt
```

**Filter and process:**
```bash
awk '$3 > 50 {print $1, $2 * 2}' data.txt    # Filter and calculate
```

## Variables and Arrays

**Set variables:**
```bash
awk -v threshold=100 '$1 > threshold {print}' data.txt
```

**Use associative arrays:**
```bash
awk '{sum[$1] += $2} END {for(key in sum) print key, sum[key]}' data.txt
```

**String operations:**
```bash
awk '{print length($1)}' file.txt            # Length of first field
```

## Programming Constructs

**Multiple statements:**
```bash
awk '{count++; sum += $1} END {print count, sum}' data.txt
```

**Conditional processing:**
```bash
awk '{if($1 > 100) print "High:", $1; else print "Low:", $1}' data.txt
```

**For loops:**
```bash
awk 'BEGIN {for(i=1; i<=5; i++) print i}'
```

## printf Formatting

```bash
awk '{printf "%-10s %5d\n", $1, $2}' data.txt    # Formatted columns
awk '{printf "%.2f\n", $1}' numbers.txt           # Two decimal places
```

## Error Handling

- "awk: missing program" - No program provided
- "awk: filename: No such file or directory" - File doesn't exist
- "awk: option requires an argument -- 'F'" - Missing field separator
- "awk: no input files" - No input and no stdin (unless BEGIN/END only)

## Implementation Notes

- Fields are 1-indexed (`$1` is first field, `$0` is entire line)
- Supports associative arrays for counting and grouping
- Regular expressions use Python `re` module
- printf formatting supports basic format specifiers
- Variables persist across all input lines
- Arrays and variables available in END block

## Use Cases

**Data analysis:**
```bash
awk -F, '{sum[$2] += $3} END {for(cat in sum) print cat, sum[cat]}' sales.csv
```

**Log processing:**
```bash
awk '/ERROR/ {errors++} /WARNING/ {warnings++} END {print "Errors:", errors, "Warnings:", warnings}' app.log
```

**Report generation:**
```bash
awk 'BEGIN {print "Report"} {total += $2} END {print "Total:", total}' data.txt
```

## See Also

- [`sed`](sed.md) - Stream editor for text transformation
- [`grep`](grep.md) - Search text patterns  
- [`cut`] - Extract columns (if available)
- [`sort`](sort.md) - Sort lines in files
- [Field processing](../../README.md#field-processing) - Working with columnar data