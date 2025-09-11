# find

Search for files and directories in a directory hierarchy.

## Synopsis

```
find [path...] [expression]
```

## Description

The `find` command searches for files and directories that match specified criteria. It supports various filtering options including name patterns, file types, search depth limits, and regular expressions.

## Options

- `-name pattern` - File name matches shell pattern (supports wildcards)
- `-type d|f` - File is of type directory (d) or regular file (f)
- `-maxdepth levels` - Descend at most the specified number of directory levels
- `-regex pattern` - File name matches regular expression pattern

## Arguments

- `path...` - Starting directories for the search (default: current directory `.`)

## Examples

**Find all files in current directory:**
```bash
find
# or
find .
```

**Find files by name pattern:**
```bash
find . -name "*.txt"
find /home -name "config*"
```

**Find only directories:**
```bash
find /var -type d
```

**Find only regular files:**
```bash
find . -type f
```

**Limit search depth:**
```bash
find /usr -maxdepth 2 -name "lib*"
```

**Use regular expressions:**
```bash
find . -regex ".*\.(py|js)$"
```

**Combine multiple criteria:**
```bash
find /project -type f -name "*.py" -maxdepth 3
```

## Behavior

- Recursively searches specified paths (or current directory if none specified)
- Returns full paths to matching files/directories
- When using `-name`, displays only the basename of matches
- Continues searching even if some paths are inaccessible
- Processes multiple starting paths sequentially

## Pattern Matching

- `-name` uses shell-style patterns:
  - `*` matches any characters
  - `?` matches single character  
  - `[abc]` matches any character in brackets
- `-regex` uses standard Python regular expressions

## Error Handling

- "find: 'path': No such file or directory" - Starting path doesn't exist
- "find: invalid regular expression 'pattern'" - Invalid regex pattern
- Logs access errors to error log but continues searching

## Implementation Notes

- Uses virtual filesystem methods for directory traversal
- Implements recursive search with configurable depth limiting
- Supports both glob patterns (`fnmatch`) and regex patterns
- Resolves paths to absolute form before searching
- Handles filesystem errors gracefully

## See Also

- [`ls`](../navigation/ls.md) - List directory contents
- [`grep`](../text/grep.md) - Search text patterns in files
- [`locate`] - Alternative file finding (if available)
- [Shell patterns](../../README.md#patterns) - Pattern matching syntax