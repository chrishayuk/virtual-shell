# ls

List directory contents.

## Synopsis

```
ls [options] [directory]
```

## Description

The `ls` command lists the contents of directories. It displays files and subdirectories, with optional formatting and filtering options.

## Options

- `-l, --long` - Use long listing format (detailed information)
- `-a, --all` - Include hidden files (those beginning with a dot)

## Arguments

- `directory` - Directory to list (optional, defaults to current directory)

## Examples

**List current directory:**
```bash
ls
# Output: file1.txt file2.txt subdir/
```

**Long format listing:**
```bash
ls -l
# Output:
# -rw-r--r-- 1 user staff  1024 Dec 11 10:30 file1.txt  
# -rw-r--r-- 1 user staff   512 Dec 11 10:25 file2.txt
# drwxr-xr-x 1 user staff     0 Dec 11 10:20 subdir
```

**Include hidden files:**
```bash
ls -a
# Output: . .. .hidden file1.txt file2.txt subdir/
```

**List specific directory:**
```bash
ls /tmp
ls ../other-directory
```

**Combined options:**
```bash
ls -la /home/user
```

## Output Format

**Standard format:** Space-separated filenames
**Long format (`-l`):** Each file on separate line with details:
```
<permissions> <links> <owner> <group> <size> <date> <name>
```

### Long Format Details

- **Permissions:** File mode (e.g., `-rw-r--r--` for files, `drwxr-xr-x` for directories)
- **Links:** Number of hard links (always 1 in this implementation)
- **Owner:** File owner (from USER environment variable)
- **Group:** File group (defaults to "staff")
- **Size:** File size in bytes (0 for directories)
- **Date:** Last modification time (current time in this implementation)
- **Name:** Filename or directory name

## Hidden Files

With the `-a` flag:
- `.` (current directory) is shown first
- `..` (parent directory) is shown second (except for root directory)
- Files beginning with `.` are included
- Without `-a`, hidden files are filtered out

## Behavior

- Sorts output alphabetically
- Handles both files and directories
- Current directory detection uses multiple fallback methods
- Directory existence checking with comprehensive error handling
- File size calculation attempts multiple API methods

## Error Handling

- "ls: cannot access 'path': No such file or directory" - Directory doesn't exist
- "ls: error: <details>" - Other filesystem errors
- "ls: unexpected result from filesystem: <result>" - Filesystem API returned non-list

## Implementation Notes

- Uses filesystem's `ls()` method for directory listing
- Determines current directory via multiple fallback strategies:
  1. Filesystem's `pwd()` method
  2. Shell's PWD environment variable
- File size detection tries multiple approaches:
  1. Filesystem's `get_size()` method
  2. Reading file content and measuring length
- Directory detection supports various filesystem APIs

## API Compatibility

Adapts to different filesystem implementations:
- **Directory listing:** `ls()` method
- **Current directory:** `pwd()` method, PWD environment variable
- **File properties:** `get_node_info()`, `is_dir()`, `get_size()`
- **Size calculation:** `get_size()`, `read_file()` fallback

## See Also

- [`cd`](cd.md) - Change directory
- [`pwd`](pwd.md) - Print working directory
- [`find`](../filesystem/find.md) - Search for files
- [`du`](../filesystem/du.md) - Directory space usage