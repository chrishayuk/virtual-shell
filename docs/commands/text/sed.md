# sed

Stream editor for filtering and transforming text.

## Synopsis

```
sed [OPTIONS] 'SCRIPT' [FILE]...
```

## Description

The `sed` command is a stream editor that performs basic text transformations on input streams or files. It's particularly useful for substitution, deletion, and line-based text manipulation.

## Options

- `-e SCRIPT` - Add script to commands to be executed (allows multiple scripts)
- `-i` - Edit files in place (modify original files)
- `-n` - Suppress automatic printing (quiet mode)
- `-E` - Use extended regular expressions

## Script Commands

### Substitution Commands
- `s/old/new/` - Substitute first occurrence per line
- `s/old/new/g` - Substitute all occurrences (global)
- `s/old/new/i` - Case-insensitive substitution
- `s/old/new/gi` - Global case-insensitive substitution
- `2s/old/new/` - Substitute only on line 2
- `$s/old/new/` - Substitute only on last line

### Delete Commands
- `/pattern/d` - Delete lines matching pattern
- `1d` - Delete first line
- `$d` - Delete last line
- `2,5d` - Delete lines 2 through 5

### Print Commands (for use with `-n`)
- `/pattern/p` - Print lines matching pattern
- `1p` - Print first line
- `2,5p` - Print lines 2 through 5

## Arguments

- `SCRIPT` - sed commands to execute
- `FILE...` - Files to process (optional, uses stdin if not provided)

## Examples

**Basic substitution:**
```bash
sed 's/old/new/' file.txt                    # Replace first occurrence per line
sed 's/old/new/g' file.txt                   # Replace all occurrences
```

**Case-insensitive substitution:**
```bash
sed 's/error/ERROR/i' logfile.txt
```

**Delete lines:**
```bash
sed '/debug/d' logfile.txt                   # Delete lines containing "debug"
sed '1d' file.txt                            # Delete first line
sed '$d' file.txt                            # Delete last line
sed '2,5d' file.txt                          # Delete lines 2-5
```

**Quiet mode with explicit printing:**
```bash
sed -n '/error/p' logfile.txt                # Only print lines containing "error"
sed -n '1,10p' file.txt                      # Print only lines 1-10
```

**Line-specific substitution:**
```bash
sed '2s/old/new/' file.txt                   # Only substitute on line 2
sed '$s/old/new/' file.txt                   # Only substitute on last line
```

**In-place editing:**
```bash
sed -i 's/old/new/g' file.txt               # Modify file directly
```

**Multiple scripts:**
```bash
sed -e 's/foo/bar/' -e '/debug/d' file.txt   # Multiple operations
```

**Using pipes:**
```bash
echo "Hello World" | sed 's/World/Universe/'
cat file.txt | sed '/error/d'
```

## Advanced Examples

**Remove blank lines:**
```bash
sed '/^$/d' file.txt
```

**Add line numbers:**
```bash
sed '=' file.txt | sed 'N;s/\n/\t/'
```

**Extract specific lines:**
```bash
sed -n '10,20p' largefile.txt               # Lines 10-20 only
```

## Delimiters

The `s` command supports different delimiters:
```bash
sed 's/old/new/'                            # Forward slashes (standard)
sed 's|old|new|'                            # Pipes
sed 's#old#new#'                            # Hash symbols
```

## Regular Expressions

- Basic regex by default: `.*`, `^`, `$`, `[]`
- Extended regex with `-E`: `+`, `?`, `|`, `{}`
- Pattern matching in addresses: `/regex/d`, `/regex/p`

## Error Handling

- "sed: missing script" - No script provided
- "sed: filename: No such file or directory" - File doesn't exist
- "sed: option requires an argument -- 'e'" - Missing argument for `-e`
- "sed: invalid option -- 'x'" - Unknown option

## Implementation Notes

- Supports line-addressed commands (`1d`, `$s/old/new/`, `2,5d`)
- Pattern addresses use regex matching
- In-place editing modifies original files
- Quiet mode requires explicit print commands
- Multiple scripts executed in sequence

## Limitations

- Interactive prompts in `-i` mode are skipped
- Complex regex features may have limited support
- Advanced sed features (hold space, branches) not implemented

## See Also

- [`awk`](awk.md) - Pattern scanning and processing
- [`grep`](grep.md) - Search text patterns
- [`tr`] - Character translation (if available)
- [Regular expressions](../../README.md#regex) - Pattern syntax reference