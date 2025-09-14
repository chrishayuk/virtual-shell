# Copy Command (cp)

The `cp` command copies files and directories from one location to another.

## Usage

```bash
cp [OPTIONS] source... destination
```

## Options

- `-r, -R` : Copy directories recursively
- `-f` : Force copy (ignore nonexistent files, never prompt)
- `-i` : Interactive mode (prompt before overwrite)
- `-n` : No clobber (do not overwrite existing files)
- `-v` : Verbose mode (explain what is being done)
- `-p` : Preserve mode, ownership, timestamps
- `--help` : Display help and exit

## Arguments

- `source...` : One or more source files or directories to copy
- `destination` : Target location for the copy operation

## Behavior

### Single File Copy
When copying a single file:
- If destination is a directory, the file is copied into that directory
- If destination is a file path, the file is copied to that path
- If destination exists and is a file, it will be overwritten (unless `-n` is used)

### Multiple Files Copy
When copying multiple files:
- Destination must be a directory
- All source files are copied into the destination directory

### Directory Copy
When copying directories:
- The `-r` or `-R` flag is required for recursive copying
- The entire directory structure is preserved
- If destination exists, source directory is copied into it
- If destination doesn't exist, source directory is copied as destination

## Examples

### Basic File Operations
```bash
# Copy single file
cp file.txt backup.txt

# Copy file to directory
cp file.txt /backup/

# Copy multiple files to directory
cp file1.txt file2.txt file3.txt /backup/

# Overwrite existing file
cp source.txt existing.txt
```

### Directory Operations
```bash
# Copy directory recursively
cp -r /project /backup/

# Copy directory contents
cp -r /source/. /destination/

# Copy nested directory structure
cp -r /deep/nested/structure /backup/
```

### Using Flags
```bash
# Verbose copy (show what's being copied)
cp -v file.txt backup.txt

# No clobber (don't overwrite existing files)
cp -n source.txt existing.txt

# Force copy (ignore errors, don't prompt)
cp -f source.txt destination.txt

# Interactive copy (prompt before overwrite)
cp -i source.txt existing.txt

# Recursive verbose copy
cp -rv /project /backup/

# Combined flags
cp -rvf /source /destination/
```

## Real-world Scenarios

```bash
# Backup important files
cp -r /home/user/documents /backup/documents_$(date +%Y%m%d)

# Copy configuration files
cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup

# Deploy application files
cp -r /build/app /var/www/html/

# Copy with preservation of attributes
cp -p /original/file.txt /backup/file.txt

# Safe copy (don't overwrite existing)
cp -n /source/* /destination/
```

## Implementation Features

- **Recursive copying**: Full support for directory trees with `-r`/`-R` flags
- **Multiple flags**: Support for combining flags like `-rvf`
- **No-clobber mode**: `-n` flag prevents overwriting existing files
- **Error handling**: Graceful handling of missing files, permission errors
- **Binary safe**: Correctly handles all file types including binary data
- **Path resolution**: Proper handling of relative and absolute paths
- **Verbose output**: `-v` flag shows copy operations as they happen

## Error Handling

The command handles various error conditions:
- Missing source files (with appropriate error messages)
- Permission denied scenarios
- Circular copy detection
- Invalid argument combinations
- Filesystem full conditions

## Compatibility

Compatible with POSIX `cp` command behavior and common GNU extensions.

## See Also

- `mv` - Move/rename files and directories
- `rm` - Remove files and directories
- `mkdir` - Create directories
- `ls` - List directory contents