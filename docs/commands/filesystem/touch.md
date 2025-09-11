# touch

Create empty files or update timestamps.

## Synopsis

```
touch file...
```

## Description

The `touch` command creates empty files if they don't exist. In standard Unix systems, it also updates file timestamps, but this implementation focuses on file creation.

## Arguments

- `file...` - One or more files to create or touch

## Examples

**Create a single empty file:**
```bash
touch newfile.txt
```

**Create multiple empty files:**
```bash
touch file1.txt file2.txt file3.txt
```

**Create files with paths:**
```bash
touch /tmp/tempfile.txt
```

## Behavior

- Creates empty files if they don't exist
- Uses the virtual filesystem's `touch()` method
- Processes each file argument sequentially
- Stops on first failure and returns error

## Error Handling

- "touch: missing operand" - No file arguments provided
- "touch: cannot touch 'filename'" - Failed to create/touch file

## Implementation Notes

- Uses the virtual filesystem's `touch()` method
- Returns immediately on first error
- Does not implement timestamp updating functionality
- Creates truly empty files (zero bytes)

## See Also

- [`cat`](cat.md) - Display file contents
- [`echo`](echo.md) - Echo text (can create files with redirection)
- [`ls`](../navigation/ls.md) - List files to verify creation
- [`rm`](rm.md) - Remove files