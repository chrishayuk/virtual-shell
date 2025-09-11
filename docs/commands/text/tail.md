# tail

Display last lines or bytes of files.

## Synopsis

```
tail [OPTIONS] [FILE]...
```

## Description

The `tail` command displays the last lines (or bytes) of files. By default, it shows the last 10 lines of each file. It also supports displaying content from a specific line onwards.

## Options

- `-n NUM` - Display last NUM lines (default: 10)
- `-n +NUM` - Display from line NUM onwards
- `-nNUM` - Display last NUM lines (compact format)
- `-NUM` - Display last NUM lines (legacy format)  
- `-c NUM` - Display last NUM bytes instead of lines
- `-f` - Follow file (not fully supported in virtual FS)
- `-q` - Never print headers with file names
- `-v` - Always print headers with file names

## Arguments

- `FILE...` - Files to display (optional, uses stdin if not provided)

## Examples

**Display last 10 lines (default):**
```bash
tail file.txt
```

**Display last 5 lines:**
```bash
tail -n 5 file.txt
tail -n5 file.txt  
tail -5 file.txt       # legacy format
```

**Display from line 20 onwards:**
```bash
tail -n +20 file.txt
tail -n+20 file.txt
```

**Display last 100 bytes:**
```bash
tail -c 100 file.txt
```

**Multiple files with headers:**
```bash
tail file1.txt file2.txt
# Output:
# ==> file1.txt <==
# [last 10 lines]
#
# ==> file2.txt <==
# [last 10 lines]
```

**Follow mode (limited support):**
```bash
tail -f logfile.txt
# Note: Displays warning about limited support
```

**Use with pipes:**
```bash
cat largefile.txt | tail -n 20
```

## Behavior

- Default: Shows last 10 lines of each file
- With `+NUM`: Shows content from line NUM to end
- With multiple files: Shows headers unless `-q` specified  
- Headers always shown with `-v`
- Bytes mode (`-c`) takes precedence over lines mode
- Follow mode (`-f`) shows warning about limited support

## Output Format

**Single file:** Direct content output
**Multiple files:** Headers separate each file:
```
==> filename <==
[content]

==> next_file <==  
[content]
```

## Line Numbering Modes

**Last N lines (`-n NUM`):**
```bash
tail -n 3 file.txt     # Last 3 lines
```

**From line N onwards (`-n +NUM`):**
```bash
tail -n +5 file.txt    # From line 5 to end
```

## Error Handling

- "tail: filename: No such file or directory" - File doesn't exist
- "tail: invalid number of lines: 'value'" - Non-numeric line count
- "tail: invalid number of bytes: 'value'" - Non-numeric byte count
- "tail: option requires an argument -- 'n'" - Missing argument for `-n`

## Follow Mode Limitations

The `-f` option is parsed but not fully functional:
- Shows warning: "tail: follow mode not fully supported in virtual filesystem"
- Cannot monitor file changes in real-time
- Virtual filesystem doesn't support file watching

## Implementation Notes

- Uses `splitlines()` for line-based processing
- Supports both negative indexing (last N lines) and positive (from line N)
- Various argument formats supported (`-n 5`, `-n5`, `-5`, `-n +10`)
- Headers managed similar to `head` command
- Limited follow mode due to virtual filesystem constraints

## Use Cases

**Log monitoring:**
```bash
tail /var/log/application.log    # Recent log entries
tail -f /var/log/system.log      # Monitor (with limitations)
```

**File analysis:**
```bash
tail -n 100 data.txt             # Last 100 records
tail -n +50 data.txt             # Skip first 49 lines
```

**Debugging:**
```bash
tail -c 1024 binary.dat          # Last 1KB of binary file
```

## See Also

- [`head`](head.md) - Display first lines of files
- [`cat`](../filesystem/cat.md) - Display entire file contents  
- [`more`](../filesystem/more.md) - Display file contents page by page
- [`grep`](grep.md) - Search text patterns in files