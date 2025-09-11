# sort

Sort lines of text files.

## Synopsis

```
sort [OPTIONS] [FILE]...
```

## Description

The `sort` command sorts lines of text files and outputs the result. It supports various sorting modes including numeric, reverse, and field-based sorting.

## Options

- `-r` - Reverse sort order (descending)
- `-n` - Numeric sort (treats numbers as numeric values)
- `-u` - Unique (remove duplicate lines)
- `-k NUM` - Sort by field NUM (1-based)
- `-t SEP` - Field separator for field-based sorting
- `-f` - Ignore case (fold case)
- `-b` - Ignore leading blanks

## Arguments

- `FILE...` - Files to sort (optional, uses stdin if not provided)

## Examples

**Basic sorting:**
```bash
sort file.txt                               # Sort lines alphabetically
sort -r file.txt                            # Reverse alphabetical order
```

**Numeric sorting:**
```bash
sort -n numbers.txt                         # Sort numbers numerically
sort -nr numbers.txt                        # Reverse numeric sort
```

**Remove duplicates:**
```bash
sort -u file.txt                            # Sort and remove duplicates
sort file.txt | uniq                        # Alternative approach
```

**Field-based sorting:**
```bash
sort -k 2 data.txt                          # Sort by second field
sort -k 3 -n data.txt                       # Sort by third field numerically
```

**Custom field separator:**
```bash
sort -t: -k 1 /etc/passwd                   # Sort by first field, colon-separated
sort -t, -k 2 data.csv                      # Sort CSV by second column
```

**Case-insensitive sorting:**
```bash
sort -f file.txt                            # Ignore case differences
sort -fu file.txt                           # Case-insensitive unique sort
```

**Ignore leading blanks:**
```bash
sort -b file.txt                            # Ignore leading whitespace
```

**Combined options:**
```bash
sort -rnu data.txt                          # Reverse, numeric, unique
sort -k 2 -nr sales.txt                     # Sort by field 2, reverse numeric
```

## Sorting Behavior

### Alphabetical (Default)
- Character-by-character comparison
- Numbers sorted as strings: "10" comes before "2"
- Case-sensitive: "A" comes before "a"

### Numeric (`-n`)
- Recognizes numeric values at start of lines/fields
- Proper numeric ordering: 2 comes before 10
- Non-numeric content treated as 0

### Field-based (`-k NUM`)
- Splits lines into fields (default: whitespace)
- Sort using specified field as key
- Empty fields treated as empty strings

## Field Processing

**Default field separation:** Whitespace (spaces and tabs)
**Custom separation:** Use `-t` option
```bash
sort -t'|' -k 3 data.txt                    # Pipe-separated, sort by field 3
```

**Field numbering:** 1-based (field 1, field 2, etc.)

## Input Sources

**Files:**
```bash
sort file1.txt file2.txt file3.txt          # Sort all files together
```

**Standard input:**
```bash
cat file.txt | sort
echo -e "c\na\nb" | sort
```

**Multiple files merged:**
All input files are combined before sorting, producing one sorted output.

## Error Handling

- "sort: filename: No such file or directory" - File doesn't exist
- "sort: invalid field number: 'value'" - Non-numeric field number
- "sort: option requires an argument -- 'k'" - Missing field number
- "sort: option requires an argument -- 't'" - Missing separator

## Implementation Notes

- Collects all input lines before sorting
- Uses Python's stable sort algorithm
- Field extraction handles both custom and default separators
- Numeric sorting extracts numeric prefix from values
- Unique mode removes exact duplicates after sorting

## Performance

- Memory usage scales with input size (all lines loaded)
- Efficient for typical file sizes
- Large files may require significant memory

## Use Cases

**Data processing:**
```bash
sort -t, -k 2 -n sales.csv                  # Sort sales data by amount
```

**Log analysis:**
```bash
sort -k 1 access.log | uniq -c              # Count unique entries
```

**System administration:**
```bash
sort -k 5 -nr du_output.txt                 # Sort by file size
```

**Text processing:**
```bash
sort -u wordlist.txt                        # Remove duplicate words
```

## See Also

- [`uniq`](uniq.md) - Report or omit repeated lines
- [`wc`](wc.md) - Count lines, words, characters
- [`grep`](grep.md) - Search text patterns
- [`awk`](awk.md) - Pattern scanning and processing