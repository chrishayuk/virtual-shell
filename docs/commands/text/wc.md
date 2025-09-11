# wc

Count lines, words, characters, and bytes in files.

## Synopsis

```
wc [OPTIONS] [FILE]...
```

## Description

The `wc` command counts lines, words, characters, and bytes in files. By default, it displays line count, word count, and byte count for each file.

## Options

- `-l` - Print line count only
- `-w` - Print word count only  
- `-c` - Print byte count only
- `-m` - Print character count only
- `-L` - Print length of longest line

**Default behavior:** Display lines, words, and bytes (`-l -w -c`)

## Arguments

- `FILE...` - Files to analyze (optional, uses stdin if not provided)

## Examples

**Default output (lines, words, bytes):**
```bash
wc file.txt
# Output:      42     123    1024 file.txt
#          lines   words   bytes filename
```

**Count lines only:**
```bash
wc -l file.txt
# Output:      42 file.txt
```

**Count words only:**
```bash
wc -w document.txt
# Output:     123 document.txt
```

**Count characters:**
```bash
wc -m text.txt
# Output:     1000 text.txt
```

**Find longest line:**
```bash
wc -L code.py
# Output:      85 code.py
```

**Multiple files:**
```bash
wc *.txt
# Output:
#      10      50     300 file1.txt
#      20     100     500 file2.txt  
#      30     150     800 total
```

**Combined options:**
```bash
wc -lw *.py        # Lines and words only
wc -c -L file.txt  # Bytes and longest line
```

**Use with pipes:**
```bash
cat file.txt | wc -l
echo "hello world" | wc -w
```

## Output Format

Each line shows counts followed by filename:
```
[lines] [words] [bytes] [chars] [longest] filename
```

- Numbers are right-aligned in 8-character fields
- Only selected counts are shown based on options
- Multiple files include a "total" line
- No filename shown when reading from stdin

## Counting Rules

**Lines:** Number of newline characters (empty file = 0 lines)
**Words:** Whitespace-separated sequences (uses `split()`)
**Bytes:** UTF-8 encoded byte count
**Characters:** Unicode character count
**Longest line:** Character count of longest line (excluding newline)

## Default vs Explicit Options

**Default behavior:**
```bash
wc file.txt           # Shows lines, words, bytes
```

**Explicit options:**
```bash
wc -l -w -c file.txt  # Same as default
wc -lwc file.txt      # Same as default (combined)
```

**Character vs Byte Count:**
- `-c` shows bytes (UTF-8 encoded)
- `-m` shows characters (Unicode count)
- If both specified, `-c` takes precedence

## Multiple Files

With multiple files, `wc` shows:
1. Individual counts for each file
2. Total line at the end

```bash
wc file1.txt file2.txt file3.txt
# Individual file counts
# ...
#      60     300    1800 total
```

## Error Handling

- "wc: filename: No such file or directory" - File doesn't exist
- Returns immediately on first file error
- Empty files return zero counts

## Implementation Notes

- Uses `splitlines()` for line counting
- Word counting uses `split()` on each line
- Byte count uses UTF-8 encoding
- Character count uses Unicode length
- Longest line calculation checks each line individually

## Use Cases

**File analysis:**
```bash
wc -l *.py           # Count lines of Python code
wc -w document.txt   # Word count for writing
```

**Data processing:**
```bash
wc -l data.csv       # Number of records
wc -c binary.dat     # File size in bytes
```

**Code metrics:**
```bash
wc -L *.js           # Find longest code lines
```

**Log analysis:**
```bash
cat error.log | wc -l    # Count error entries
```

## See Also

- [`cat`](../filesystem/cat.md) - Display file contents
- [`head`](head.md) - Display first lines of files
- [`tail`](tail.md) - Display last lines of files
- [`du`](../filesystem/du.md) - Directory space usage