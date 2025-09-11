# rm

Remove files.

## Synopsis

```
rm file...
```

## Description

The `rm` command removes (deletes) files from the filesystem. This is a basic implementation that removes files one at a time.

## Arguments

- `file...` - One or more files to remove

## Examples

**Remove a single file:**
```bash
rm unwanted.txt
```

**Remove multiple files:**
```bash
rm file1.txt file2.txt file3.txt
```

## Behavior

- Removes files using the virtual filesystem's `rm()` method
- Processes each file argument sequentially
- Stops and returns error on first failure

## Error Handling

- "rm: missing operand" - No file arguments provided
- "rm: cannot remove 'filename'" - Failed to remove file (doesn't exist, permissions, etc.)

## Limitations

This is a basic implementation that differs from standard Unix `rm`:
- No recursive directory removal (`-r` flag not supported)
- No force option (`-f` flag not supported)  
- No interactive prompting (`-i` flag not supported)
- No verbose output (`-v` flag not supported)

## Implementation Notes

- Uses the virtual filesystem's `rm()` method
- Returns on first error rather than continuing with remaining files
- Does not validate file existence before attempting removal

## See Also

- [`rmdir`](rmdir.md) - Remove empty directories
- [`cp`](cp.md) - Copy files and directories
- [`mv`](mv.md) - Move/rename files and directories
- [`ls`](../navigation/ls.md) - List directory contents