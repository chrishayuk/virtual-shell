# df

Display filesystem disk space usage.

## Synopsis

```
df [-h] [-i] [path...]
```

## Description

The `df` command displays information about filesystem disk space usage. It shows the total space, used space, available space, and usage percentage for filesystems.

## Options

- `-h, --human-readable` - Print sizes in human readable format (e.g., 1K, 234M, 2.1G)
- `-i, --inodes` - Display inode usage information instead of block usage

## Arguments

- `path...` - Paths to show disk space for (default: root filesystem `/`)

## Examples

**Display filesystem usage:**
```bash
df
# Output:
# Filesystem     1K-blocks    Used    Available Use% Mounted on
# vfs                10240     2048         8192  20% /
```

**Human-readable format:**
```bash
df -h
# Output:
# Filesystem     1K-blocks    Used    Available Use% Mounted on
# vfs               10.0K     2.0K         8.0K  20% /
```

**Display inode usage:**
```bash
df -i
# Output:
# Filesystem      Inodes  IUsed    IFree IUse% Mounted on
# vfs                100     25       75  25% /
```

**Check specific paths:**
```bash
df /home /tmp
```

## Output Format

**Standard format:**
- Filesystem - Name of the filesystem
- 1K-blocks - Total space in 1024-byte blocks
- Used - Used space in 1024-byte blocks  
- Available - Available space in 1024-byte blocks
- Use% - Usage percentage
- Mounted on - Mount point path

**Inode format (-i):**
- Filesystem - Name of the filesystem
- Inodes - Total number of inodes
- IUsed - Used inodes
- IFree - Free inodes
- IUse% - Inode usage percentage
- Mounted on - Mount point path

## Implementation Notes

- Uses filesystem's `get_storage_stats()` method for statistics
- Automatically resolves relative paths to absolute
- Calculates percentages based on total vs used space/inodes
- Uses provider name from storage stats as filesystem identifier
- Supports multiple filesystem API variations

## Error Handling

- "df: path: No such file or directory" - Specified path doesn't exist

## See Also

- [`du`](du.md) - Display directory space usage
- [`quota`](quota.md) - Display disk usage quotas  
- [`ls`](../navigation/ls.md) - List directory contents with sizes