# uniq

Report or omit repeated consecutive lines.

## Synopsis

```
uniq [OPTIONS] [INPUT [OUTPUT]]
```

## Description

The `uniq` command processes a file or input stream to report or remove consecutive duplicate lines. Note that it only works on adjacent duplicates, so input is typically sorted first.

## Options

- `-c` - Count occurrences of each unique line
- `-d` - Only print duplicate lines (lines that appear more than once)
- `-u` - Only print unique lines (lines that appear exactly once)
- `-i` - Ignore case when comparing lines
- `-f NUM` - Skip the first NUM fields when comparing
- `-s NUM` - Skip the first NUM characters when comparing
- `-w NUM` - Compare at most NUM characters

## Arguments

- `INPUT` - Input file (optional, uses stdin if not provided)
- `OUTPUT` - Output file (optional, writes to stdout if not provided)

## Examples

**Basic duplicate removal:**
```bash
uniq file.txt                               # Remove consecutive duplicates
sort file.txt | uniq                        # Remove all duplicates
```

**Count occurrences:**
```bash
uniq -c file.txt                            # Count consecutive duplicates
sort file.txt | uniq -c                     # Count all duplicates
# Output:    3 apple
#           1 banana
#           2 cherry
```

**Show only duplicates:**
```bash
uniq -d file.txt                            # Only lines with duplicates
sort file.txt | uniq -d                     # All duplicate lines
```

**Show only unique lines:**
```bash
uniq -u file.txt                            # Only non-duplicate lines
sort file.txt | uniq -u                     # All unique lines
```

**Case-insensitive comparison:**
```bash
uniq -i file.txt                            # Ignore case differences
```

**Field-based comparison:**
```bash
uniq -f 1 data.txt                          # Skip first field when comparing
uniq -f 2 -c data.txt                       # Skip first 2 fields, count occurrences
```

**Character-based comparison:**
```bash
uniq -s 5 file.txt                          # Skip first 5 characters
uniq -w 10 file.txt                         # Compare only first 10 characters
```

**Write to output file:**
```bash
uniq input.txt output.txt                   # Remove duplicates, save to file
```

## Typical Usage Patterns

**Remove all duplicates:**
```bash
sort file.txt | uniq                        # Sort first, then remove duplicates
```

**Count frequency:**
```bash
sort words.txt | uniq -c | sort -nr         # Frequency count, most common first
```

**Find common lines:**
```bash
sort file1.txt file2.txt | uniq -d          # Lines that appear in both files
```

**Data deduplication:**
```bash
sort -u file.txt                            # Alternative: sort with unique option
sort file.txt | uniq -c                     # Show counts of each unique line
```

## Comparison Options

### Field Skipping (`-f NUM`)
Skip specified number of fields (whitespace-separated):
```
Input: "user1 john smith"
       "user2 john smith"
uniq -f 1: Compares "john smith" parts only
```

### Character Skipping (`-s NUM`)
Skip specified number of characters:
```
Input: "prefix_apple"
       "prefix_banana"
uniq -s 7: Compares "apple" vs "banana"
```

### Character Limiting (`-w NUM`)
Compare only first NUM characters:
```
Input: "apple_red"
       "apple_green"  
uniq -w 5: Compares only "apple" parts
```

## Output Formats

**Default:** Unique lines only
**Count (`-c`):** `   COUNT line`
**Duplicates (`-d`):** Only repeated lines
**Unique (`-u`):** Only non-repeated lines

## Behavior Notes

- **Adjacent duplicates only:** `uniq` only removes consecutive identical lines
- **Sort first:** For complete deduplication, sort input first
- **Case sensitivity:** Default is case-sensitive unless `-i` used
- **Empty lines:** Treated as regular lines for comparison
- **Trailing whitespace:** Significant for comparison

## Error Handling

- "uniq: filename: No such file or directory" - Input file doesn't exist
- "uniq: invalid number of fields to skip: 'value'" - Non-numeric field count
- "uniq: option requires an argument -- 'f'" - Missing argument

## Implementation Notes

- Processes input line by line
- Maintains state of previous line for comparison
- Supports various preprocessing for comparison (case, fields, characters)
- Output file writing when specified as second argument

## Examples with Data

**Input file (data.txt):**
```
apple
apple
banana  
banana
banana
cherry
```

**Commands and results:**
```bash
uniq data.txt              # apple, banana, cherry
uniq -c data.txt           #    2 apple,    3 banana,    1 cherry
uniq -d data.txt           # apple, banana
uniq -u data.txt           # cherry
```

## See Also

- [`sort`](sort.md) - Sort lines of text files
- [`wc`](wc.md) - Count lines, words, characters
- [`comm`] - Compare sorted files (if available)
- [Data deduplication](../../README.md#deduplication) - Removing duplicates