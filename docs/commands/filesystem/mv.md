# mv

Move or rename files and directories.

## Synopsis

```
mv source... destination
```

## Description

The `mv` command moves or renames files and directories. It copies the source content to the destination and then removes the original file, effectively implementing a move operation.

## Arguments

- `source...` - One or more source files or directories to move
- `destination` - Target location for the move operation

## Examples

**Rename a file:**
```bash
mv oldname.txt newname.txt
```

**Move file to directory:**
```bash
mv file.txt /target/directory/
```

**Move multiple files to directory:**
```bash
mv file1.txt file2.txt file3.txt /target/directory/
```

**Move with path resolution:**
```bash
mv ../source.txt ./destination.txt
```

## Behavior

- If destination is a directory, source files are moved into it
- If moving multiple sources, destination must be a directory
- Implements move as copy + delete operation
- Preserves original content during move
- Uses basename of source for filename when moving to directory

## Error Handling

- "mv: missing operand" - Less than 2 arguments provided
- "mv: target 'dest' is not a directory" - Multiple sources but destination isn't directory
- "mv: cannot stat 'source': No such file or directory" - Source file doesn't exist
- "mv: cannot read 'source': Permission denied or file not found" - Unable to read source
- "mv: failed to write to 'dest'" - Unable to write to destination
- "mv: file copied, but failed to remove original at 'source'" - Copy succeeded but delete failed

## Implementation Notes

- Uses multiple fallback methods to detect directories and file existence
- Implements atomic-style operation (copy then delete)
- Handles various filesystem API differences through helper methods
- Does not currently support directory moves (only files)

## Filesystem API Compatibility

The command adapts to different filesystem implementations by trying multiple API methods:

**Directory detection:**
- `get_node_info()` and `is_dir` attribute
- `is_dir()` method
- `isdir()` method  
- `ls()` attempt as fallback

**File existence:**
- `get_node_info()` method
- `exists()` method
- `read_file()` as fallback

**File removal:**
- `rm()` method
- `delete_file()` method
- `delete_node()` method

## See Also

- [`cp`](cp.md) - Copy files and directories
- [`rm`](rm.md) - Remove files
- [`ls`](../navigation/ls.md) - List directory contents
- [`mkdir`](mkdir.md) - Create directories