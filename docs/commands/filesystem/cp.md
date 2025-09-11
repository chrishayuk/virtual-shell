# cp

Copy files and directories.

## Synopsis

```
cp [OPTIONS] source... destination
```

## Description

The `cp` command copies files and directories from source locations to a destination. It supports recursive copying of directories and various options to control the copy behavior.

## Options

- `-r, -R` - Copy directories recursively
- `-f` - Force (ignore nonexistent files, never prompt)
- `-i` - Interactive (prompt before overwrite) - currently non-functional in non-interactive mode
- `-v` - Verbose (explain what is being done)
- `-p` - Preserve mode, ownership, timestamps (parsed but not implemented)
- `--help` - Display help text

## Arguments

- `source...` - One or more source files or directories to copy
- `destination` - Target location for the copy operation

## Examples

**Copy a single file:**
```bash
cp file.txt backup.txt
```

**Copy multiple files to a directory:**
```bash
cp file1.txt file2.txt target_dir/
```

**Copy a directory recursively:**
```bash
cp -r source_dir/ destination_dir/
```

**Verbose copy with output:**
```bash
cp -v file.txt backup.txt
# Output: 'file.txt' -> 'backup.txt'
```

**Force copy (ignore errors):**
```bash
cp -f nonexistent.txt backup.txt  # Won't fail if source doesn't exist
```

## Behavior

- If destination is a directory, source files are placed inside it
- If copying multiple sources, destination must be a directory
- Prevents copying a file to itself
- Supports both filesystem-native `copy_dir()` and manual recursive copying

## Error Handling

- "cp: missing operand" - No arguments provided
- "cp: target 'dest' is not a directory" - Multiple sources but destination isn't a directory
- "cp: cannot stat 'file': No such file or directory" - Source file doesn't exist (unless `-f` used)
- "cp: 'source' and 'dest' are the same file" - Attempting to copy to self
- "cp: omitting directory 'dir'" - Directory specified without `-r` flag

## Implementation Notes

- Uses virtual filesystem's `copy_dir()` method when available
- Falls back to manual recursive copying if `copy_dir()` not implemented
- Resolves paths and handles trailing slashes appropriately
- Interactive mode prompts are skipped in non-interactive environment

## See Also

- [`mv`](mv.md) - Move/rename files and directories
- [`rm`](rm.md) - Remove files
- [`mkdir`](mkdir.md) - Create directories