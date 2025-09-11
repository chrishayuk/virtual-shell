# grep

Search for patterns in files.

## Synopsis

```
grep [OPTIONS] PATTERN [FILE]...
```

## Description

The `grep` command searches for lines matching a pattern in files or standard input. It supports various options for case-insensitive search, regular expressions, and output formatting.

## Options

- `-i` - Case insensitive search
- `-v` - Invert match (show non-matching lines)
- `-n` - Show line numbers
- `-c` - Count matching lines only
- `-r` - Recursive search in directories
- `-E` - Extended regex (ERE) - parsed but behaves same as basic
- `-w` - Match whole words only
- `-l` - List only filenames with matches
- `-h` - Suppress filename prefix

## Arguments

- `PATTERN` - Regular expression or text pattern to search for
- `FILE...` - Files to search in (optional, uses stdin if not provided)

## Examples

**Basic text search:**
```bash
grep "error" logfile.txt
```

**Case insensitive search:**
```bash
grep -i "warning" system.log
```

**Show line numbers:**
```bash
grep -n "function" script.py
```

**Count matches:**
```bash
grep -c "TODO" *.txt
```

**Invert match (show non-matching lines):**
```bash
grep -v "debug" application.log
```

**Whole word matching:**
```bash
grep -w "test" document.txt  # Won't match "testing" or "contest"
```

**Multiple files with filename display:**
```bash
grep "import" *.py
```

**Suppress filenames:**
```bash
grep -h "pattern" file1.txt file2.txt
```

**List files containing pattern:**
```bash
grep -l "class" *.py
```

**Regular expressions:**
```bash
grep "^function.*(" script.js        # Lines starting with "function" containing "("
grep "[0-9]+" data.txt               # Lines containing numbers
grep "error|warning" logs.txt        # Lines containing "error" or "warning"
```

## Pattern Matching

- Uses Python regular expressions by default
- Common regex patterns work: `.*`, `+`, `?`, `^`, `$`, `[]`, `|`
- With `-w`: Adds word boundaries (`\b`) around the pattern
- Case sensitivity controlled by `-i` flag

## Input Sources

**Files:**
```bash
grep "pattern" file.txt
grep "pattern" file1.txt file2.txt file3.txt
```

**Standard input (pipes):**
```bash
echo "test data" | grep "test"
cat file.txt | grep "pattern"
```

## Output Formats

**Default:** Matching lines
**With `-n`:** Line numbers prefixed
**With `-c`:** Count of matches
**With `-l`:** Filenames only
**With `-v`:** Non-matching lines

## Behavior

- Searches line by line through input
- Multiple files show filename prefixes unless `-h` used
- Stops on first file error and reports it
- With `-r`, recursively searches directories
- Empty pattern matches all lines

## Error Handling

- "grep: missing pattern" - No pattern provided
- "grep: no input files" - No files and no stdin available
- "grep: filename: No such file or directory" - File doesn't exist
- "grep: invalid pattern: error" - Malformed regular expression

## Implementation Notes

- Uses Python's `re` module for pattern matching
- Supports stdin input through shell's `_stdin_buffer`
- Recursive directory search traverses filesystem hierarchy
- Pattern compilation with error handling for invalid regex

## See Also

- [`find`](../filesystem/find.md) - Find files by name patterns
- [`sed`](sed.md) - Stream editor for text transformation
- [`awk`](awk.md) - Pattern scanning and processing
- [`head`](head.md) - Display first lines of files
- [`tail`](tail.md) - Display last lines of files