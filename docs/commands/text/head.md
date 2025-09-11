# head

Display first lines or bytes of files.

## Synopsis

```
head [OPTIONS] [FILE]...
```

## Description

The `head` command displays the first lines (or bytes) of files. By default, it shows the first 10 lines of each file.

## Options

- `-n NUM` - Display first NUM lines (default: 10)
- `-nNUM` - Display first NUM lines (compact format)
- `-NUM` - Display first NUM lines (legacy format)
- `-c NUM` - Display first NUM bytes instead of lines
- `-q` - Never print headers with file names
- `-v` - Always print headers with file names

## Arguments

- `FILE...` - Files to display (optional, uses stdin if not provided)

## Examples

**Display first 10 lines (default):**
```bash
head file.txt
```

**Display first 5 lines:**
```bash
head -n 5 file.txt
head -n5 file.txt
head -5 file.txt       # legacy format
```

**Display first 100 bytes:**
```bash
head -c 100 file.txt
```

**Multiple files with headers:**
```bash
head file1.txt file2.txt
# Output:
# ==> file1.txt <==
# [first 10 lines]
#
# ==> file2.txt <==
# [first 10 lines]
```

**Suppress headers:**
```bash
head -q file1.txt file2.txt
```

**Force headers (single file):**
```bash
head -v file.txt
```

**Use with pipes:**
```bash
cat largefile.txt | head -n 20
```

## Behavior

- Default: Shows first 10 lines of each file
- With multiple files: Shows headers unless `-q` specified
- Headers always shown with `-v`
- Bytes mode (`-c`) takes precedence over lines mode
- Supports stdin input from pipes or shell buffer

## Output Format

**Single file:** Direct content output
**Multiple files:** Headers separate each file:
```
==> filename <==
[content]

==> next_file <==
[content]
```

## Error Handling

- "head: filename: No such file or directory" - File doesn't exist
- "head: invalid number of lines: 'value'" - Non-numeric line count
- "head: invalid number of bytes: 'value'" - Non-numeric byte count
- "head: option requires an argument -- 'n'" - Missing argument for `-n`

## Line vs Byte Modes

**Line mode (default):**
- Splits content by newlines
- Returns complete lines only
- Preserves line endings

**Byte mode (`-c NUM`):**
- Returns exactly NUM bytes
- May cut lines in the middle
- Preserves all characters including newlines

## Implementation Notes

- Uses `splitlines()` for line-based processing
- Supports various argument formats (`-n 5`, `-n5`, `-5`)
- Headers appear only when processing multiple files (unless overridden)
- Integrates with shell's stdin buffer for pipe support

## Use Cases

**Preview files:**
```bash
head *.txt                    # Quick preview of multiple files
```

**Debugging:**
```bash
head -n 1 data.csv           # Check CSV header
```

**Log analysis:**
```bash
head /var/log/system.log     # Recent log entries
```

**Binary file inspection:**
```bash
head -c 512 binary_file      # First 512 bytes
```

## See Also

- [`tail`](tail.md) - Display last lines of files
- [`cat`](../filesystem/cat.md) - Display entire file contents
- [`more`](../filesystem/more.md) - Display file contents page by page
- [`less`] - Advanced file pager (if available)