# rmdir

Remove empty directories.

## Synopsis

```
rmdir directory...
```

## Description

The `rmdir` command removes empty directories. It will only succeed if the directories are empty (contain no files or subdirectories).

## Arguments

- `directory...` - One or more directories to remove

## Examples

**Remove a single empty directory:**
```bash
rmdir empty_directory
```

**Remove multiple empty directories:**
```bash
rmdir dir1 dir2 dir3
```

**Remove nested empty directory:**
```bash
rmdir /path/to/empty/directory
```

## Behavior

- Only removes directories that are completely empty
- Processes each directory argument sequentially
- Stops on first failure and returns error
- Uses the virtual filesystem's `rmdir()` method

## Error Handling

- "rmdir: missing operand" - No directory arguments provided
- "rmdir: cannot remove 'dirname': Directory not empty or not found" - Directory is not empty, doesn't exist, or removal failed

## Limitations

This is a basic implementation:
- No recursive removal option (`-p` flag not supported)
- No verbose output (`-v` flag not supported)
- Cannot remove directories with any content

## Implementation Notes

- Uses the virtual filesystem's `rmdir()` method
- Returns on first error rather than continuing with remaining directories
- Does not validate directory existence or emptiness before attempting removal
- Relies on filesystem implementation to enforce empty directory requirement

## See Also

- [`mkdir`](mkdir.md) - Create directories
- [`rm`](rm.md) - Remove files  
- [`ls`](../navigation/ls.md) - List directory contents
- [`find`](find.md) - Find files in directories