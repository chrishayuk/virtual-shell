# mkdir

Create directories.

## Synopsis

```
mkdir [-p] directory...
```

## Description

The `mkdir` command creates directories with the specified names. By default, it only creates the final directory in the path, but with the `-p` option, it will create parent directories as needed.

## Options

- `-p` - Create parent directories as needed (no error if existing)

## Arguments

- `directory...` - One or more directory names/paths to create

## Examples

**Create a single directory:**
```bash
mkdir mydir
```

**Create multiple directories:**
```bash
mkdir dir1 dir2 dir3
```

**Create nested directories:**
```bash
mkdir -p path/to/deep/directory
```

**Create multiple nested paths:**
```bash
mkdir -p project/{src,tests,docs}  # Note: brace expansion may not be supported
```

## Behavior

- Without `-p`: Only creates the final directory, fails if parent doesn't exist
- With `-p`: Creates all necessary parent directories in the path
- Handles both absolute and relative paths
- No error if directory already exists when using `-p`

## Error Handling

- "mkdir: missing operand" - No directory names provided
- "mkdir: cannot create directory 'dirname'" - Failed to create directory (permissions, already exists without `-p`, etc.)

## Implementation Notes

- Uses the virtual filesystem's `mkdir()` method
- With `-p`, splits path into components and creates each level
- Normalizes paths by removing trailing slashes
- Creates directories using absolute paths resolved through the filesystem

## See Also

- [`rmdir`](rmdir.md) - Remove empty directories
- [`rm`](rm.md) - Remove files and directories
- [`ls`](../navigation/ls.md) - List directory contents
- [`cd`](../navigation/cd.md) - Change directory