# df - Display Filesystem Disk Space Usage

## Synopsis

```bash
df [-ahikPT] [-B SIZE] [-t TYPE] [-x TYPE] [--total] [--help] [path...]
```

## Description

The `df` command displays information about filesystem disk space usage. It shows the total space, used space, available space, and usage percentage for filesystems. By default, it displays information about all mounted filesystems or the filesystems containing the specified paths.

## Options

### Display Options
- `-a, --all` - Include all filesystems, including pseudo, duplicate, and inaccessible filesystems
- `-h, --human-readable` - Print sizes in human-readable format (e.g., 1K, 234M, 2.1G)
- `-i, --inodes` - Display inode usage information instead of block usage
- `-k` - Use 1024-byte blocks (default)
- `-P, --portability` - Use POSIX output format (512-byte blocks, "Capacity" header)
- `-T, --print-type` - Print filesystem type in output

### Block Size Options
- `-B, --block-size=SIZE` - Use SIZE-byte blocks. SIZE can be:
  - A number (e.g., `512`, `1024`)
  - A number with unit suffix (e.g., `1K`, `1M`, `1G`)

### Filtering Options
- `-t, --type=TYPE` - Limit listing to filesystems of type TYPE
- `-x, --exclude-type=TYPE` - Exclude filesystems of type TYPE

### Summary Options
- `--total` - Produce a grand total line at the end

### Help
- `--help` - Display help information and exit

## Arguments

- `path...` - One or more paths to show disk space for. If no paths are specified, displays information for all mounted filesystems (defaults to root `/`)

## Output Format

### Standard Format
```
Filesystem     1K-blocks    Used    Available Use% Mounted on
testfs           102400    2048        100352   2% /
```

- **Filesystem** - Name of the filesystem or device
- **1K-blocks** - Total space in 1024-byte blocks (or specified block size)
- **Used** - Used space in blocks
- **Available** - Available space in blocks
- **Use%** - Percentage of space used
- **Mounted on** - Mount point path

### Human-Readable Format (-h)
```
Filesystem      Size  Used Avail Use% Mounted on
testfs          100M  2.0M   98M   2% /
```

Sizes are displayed with appropriate unit suffixes (B, K, M, G, T, P, E).

### Inode Format (-i)
```
Filesystem      Inodes  IUsed    IFree IUse% Mounted on
testfs            10000     25     9975    0% /
```

- **Inodes** - Total number of inodes
- **IUsed** - Number of used inodes
- **IFree** - Number of free inodes
- **IUse%** - Percentage of inodes used

### POSIX Format (-P)
```
Filesystem     512-blocks      Used Available Capacity Mounted on
testfs            204800      4096    200704       2% /
```

Uses 512-byte blocks and "Capacity" instead of "Use%".

### With Type Information (-T)
```
Filesystem     Type      1K-blocks    Used    Available Use% Mounted on
testfs         vfs          102400    2048        100352   2% /
```

## Examples

### Basic Usage
```bash
# Display all filesystems
df

# Display specific path
df /home

# Display multiple paths
df / /tmp /var
```

### Human-Readable Output
```bash
# Human-readable sizes
df -h

# Human-readable with specific paths
df -h /home /var/log
```

### Inode Information
```bash
# Show inode usage
df -i

# Check inode usage for specific path
df -i /var
```

### Block Size Options
```bash
# Use 512-byte blocks
df -B 512

# Use 1MB blocks
df -B 1M

# Use 4K blocks
df -B 4K
```

### Filesystem Type
```bash
# Show filesystem types
df -T

# Show only ext4 filesystems
df -t ext4

# Exclude tmpfs filesystems
df -x tmpfs
```

### POSIX Compatibility
```bash
# POSIX-compliant output
df -P

# POSIX with human-readable
df -Ph
```

### Combined Options
```bash
# Human-readable with types
df -hT

# Show all with totals
df -a --total

# Human-readable totals for specific paths
df -h --total / /home /var

# POSIX format with types
df -PT
```

## Real-World Use Cases

### System Monitoring
```bash
# Quick disk usage check
df -h

# Monitor specific critical paths
df -h / /var /tmp /home

# Check for inode exhaustion
df -i /var/log
```

### Scripting and Automation
```bash
# Parse-friendly output
df -P /

# Get usage percentage for monitoring
df / | awk 'NR==2 {print $5}'

# Check available space in MB
df -B 1M /var | awk 'NR==2 {print $4}'
```

### Troubleshooting
```bash
# Check if filesystem is full
df -h /

# Check inode usage (small files exhaustion)
df -i /tmp

# Show all filesystems including hidden
df -a

# Check specific filesystem type
df -t ext4
```

### Capacity Planning
```bash
# Generate usage report with totals
df -hT --total

# Track growth over time
df -B 1G / > disk_usage_$(date +%Y%m%d).log

# Compare multiple systems
df -Ph | grep -v "Filesystem"
```

## Implementation Notes

### Storage Statistics
The command retrieves storage statistics from the filesystem's `get_storage_stats()` method, which provides:
- `provider_name` - Filesystem identifier
- `fs_type` - Filesystem type (e.g., vfs, ext4, tmpfs)
- `max_total_size` - Total capacity in bytes
- `total_size_bytes` - Used space in bytes
- `max_files` - Maximum number of files (inodes)
- `file_count` - Current number of files

### Calculation Methods
- **Usage Percentage**: `(used / total) * 100`, rounded down to integer
- **Available Space**: `total - used`, never negative
- **Block Conversion**: Bytes divided by block size
- **Human-Readable**: Automatic unit selection based on size magnitude

### Default Values
- Default block size: 1024 bytes (1K)
- Default filesystem type: "vfs"
- Default capacity: 100MB for space, 10000 for inodes
- POSIX mode: 512-byte blocks

## Differences from Standard df

This implementation closely follows GNU df behavior with some adaptations for the virtual filesystem:
- All standard flags are supported (-h, -i, -k, -B, -P, -T, -t, -x)
- Output format matches standard df for compatibility
- Works with virtual filesystem paths instead of actual mount points
- Storage statistics come from the virtual filesystem provider

## Error Handling

- **No such file or directory** - Specified path doesn't exist
- **Invalid block size** - Block size specification is not valid
- **Division by zero** - Handled gracefully, shows "-" for undefined percentages

## Exit Status

- `0` - Success
- `1` - Error occurred (invalid arguments, path not found)

## See Also

- [`du`](du.md) - Display directory space usage
- [`quota`](quota.md) - Display disk usage quotas
- [`ls`](../navigation/ls.md) - List directory contents with sizes
- [`find`](find.md) - Find files by size criteria

## Testing

The df command includes comprehensive tests covering:
- All command-line flags and combinations
- Various filesystem states (empty, full, large)
- Human-readable size formatting
- POSIX compatibility mode
- Inode usage calculation
- Block size conversions
- Type filtering
- Total calculations
- Edge cases and error conditions
- Real-world usage scenarios