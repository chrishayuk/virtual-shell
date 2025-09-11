# diff

Compare files line by line and show differences.

## Synopsis

```
diff [OPTIONS] FILE1 FILE2
```

## Description

The `diff` command compares two files line by line and displays the differences between them. It supports various output formats and comparison options.

## Options

- `-u, --unified` - Output unified diff format (default)
- `-c, --context` - Output context diff format  
- `-n, --normal` - Output normal diff format
- `-i, --ignore-case` - Ignore case differences
- `-w, --ignore-all-space` - Ignore all whitespace differences
- `-b, --ignore-space-change` - Ignore changes in amount of whitespace  
- `-B, --ignore-blank-lines` - Ignore blank lines
- `-q, --brief` - Report only whether files differ
- `--side-by-side` - Output in two columns

## Arguments

- `FILE1` - First file to compare
- `FILE2` - Second file to compare

## Examples

**Basic file comparison:**
```bash
diff file1.txt file2.txt                    # Show all differences
diff -q file1.txt file2.txt                 # Just check if different
```

**Different output formats:**
```bash
diff -u old.txt new.txt                     # Unified diff (default)
diff -c old.txt new.txt                     # Context diff
diff -n old.txt new.txt                     # Normal diff
diff --side-by-side old.txt new.txt         # Two-column view
```

**Ignore whitespace:**
```bash
diff -w file1.txt file2.txt                 # Ignore all whitespace
diff -b file1.txt file2.txt                 # Ignore whitespace changes
diff -B file1.txt file2.txt                 # Ignore blank lines
```

**Case-insensitive comparison:**
```bash
diff -i file1.txt file2.txt                 # Ignore case differences
```

## Output Formats

### Unified Format (Default)
```
--- file1.txt
+++ file2.txt
@@ -1,3 +1,3 @@
 line1
-old line
+new line
 line3
```
- `---` and `+++` show file names
- `@@` shows line ranges
- `-` lines removed, `+` lines added
- Space prefix for context lines

### Context Format (`-c`)
```
*** file1.txt
--- file2.txt
***************
*** 1,3 ****
  line1
! old line
  line3
--- 1,3 ----
  line1
! new line
  line3
```

### Normal Format (`-n`)
```
2c2
< old line
---
> new line
```
- `2c2`: Line 2 changed to line 2
- `<` shows old content, `>` shows new content

### Side-by-Side Format
```
file1.txt                                | file2.txt
---------------------------------------- 
line1                                    | line1
old line                                < new line
line3                                    | line3
```

## Comparison Options

**Case sensitivity:**
- Default: Case-sensitive
- `-i`: Treats "Hello" and "hello" as identical

**Whitespace handling:**
- `-w`: Ignores all spaces and tabs
- `-b`: Treats multiple spaces/tabs as single space
- `-B`: Ignores completely blank lines

## Exit Status

- **0**: Files are identical
- **1**: Files differ
- **2**: Error occurred

## Use Cases

**Version control:**
```bash
diff old_version.py new_version.py         # See code changes
```

**Configuration comparison:**
```bash
diff config.old config.new                 # Compare config files
```

**Content verification:**
```bash
diff -q original.txt backup.txt            # Quick identity check
```

**Generate patches:**
```bash
diff -u original.txt modified.txt > changes.patch
```

## Error Handling

- "diff: missing operand" - Less than 2 files provided
- "diff: filename: No such file or directory" - File doesn't exist
- Files identical: No output (exit status 0)
- Files differ: Shows differences (exit status 1)

## Implementation Notes

- Uses Python's `difflib` module for diff generation
- Supports preprocessing for case/whitespace ignoring
- Handles empty files and missing content gracefully
- Line-by-line comparison with various formatting options

## Related Operations

**Creating patches:**
```bash
diff -u original.txt modified.txt > patch.diff
```

**Applying patches:**
```bash
patch < patch.diff                         # See patch command
```

## See Also

- [`patch`](patch.md) - Apply diff patches to files
- [`cmp`] - Compare files byte by byte (if available)
- [`comm`] - Compare sorted files (if available)
- [Version control](../../README.md#version-control) - Managing file changes