# du

Display directory space usage.

## Synopsis

```
du [-h] [-s] [-c] [path...]
```

## Description

The `du` command displays disk usage statistics for directories and files. It recursively calculates the space used by directories and their contents.

## Options

- `-h, --human-readable` - Print sizes in human readable format (e.g., 1K, 234M, 2.1G)
- `-s, --summarize` - Display only a total for each argument (don't show subdirectories)
- `-c, --total` - Produce a grand total at the end

## Arguments

- `path...` - Paths to analyze (default: current directory `.`)

## Examples

**Display usage for current directory:**
```bash
du
# Output:
# 4    ./subdir1
# 8    ./subdir2  
# 16   .
```

**Human-readable format:**
```bash
du -h
# Output:
# 4.0K ./subdir1
# 8.0K ./subdir2
# 16K  .
```

**Summarize only (no subdirectories):**
```bash
du -s /home/user
# Output:
# 1024    /home/user
```

**Show total across multiple paths:**
```bash
du -c /home /tmp
# Output:
# 1024    /home
# 256     /tmp
# 1280    total
```

**Combined options:**
```bash
du -hsc /var/*
```

## Behavior

- Recursively traverses directories to calculate total space
- For files, reports the file size
- Displays sizes in KB blocks by default (or human-readable with `-h`)
- With `-s`, shows only the total for each specified path
- With `-c`, adds a grand total line when multiple paths are given
- Handles various filesystem API implementations

## Output Format

Each line shows:
```
<size><tab><path>
```

- Size is in 1KB blocks (default) or human-readable format (`-h`)
- Path shows the directory or file being measured
- Final `total` line appears with `-c` and multiple paths

## Error Handling

- "du: cannot access 'path': No such file or directory" - Path doesn't exist
- "du: cannot access 'path': <error>" - Other access errors
- Continues processing other paths even if some fail

## Implementation Notes

- Uses multiple fallback methods to check file existence and directory status
- Recursively calculates directory sizes by summing all contained files
- Supports various filesystem APIs through adapter methods
- Formats sizes using standard binary prefixes (1K = 1024 bytes)

## Filesystem API Compatibility

Adapts to different filesystem implementations:
- **Existence checking:** `exists()`, `read_file()` + `ls()` fallback
- **Directory detection:** `is_dir()`, `isdir()`, `get_node_info()`
- **Size calculation:** `get_size()`, `read_file()` length fallback
- **Directory listing:** `ls()` method

## See Also

- [`df`](df.md) - Display filesystem disk space usage
- [`quota`](quota.md) - Display disk usage quotas
- [`find`](find.md) - Find files in directory hierarchies
- [`ls`](../navigation/ls.md) - List directory contents