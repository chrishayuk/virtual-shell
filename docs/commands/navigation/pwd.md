# pwd

Print the current working directory.

## Synopsis

```
pwd
```

## Description

The `pwd` command displays the absolute pathname of the current working directory. It shows where you currently are in the filesystem hierarchy.

## Examples

**Display current directory:**
```bash
pwd
# Output: /home/user/projects
```

**Use in scripts:**
```bash
current_dir=$(pwd)
echo "Working in: $current_dir"
```

**Verify location after cd:**
```bash
cd /tmp
pwd
# Output: /tmp
```

## Behavior

- Returns the absolute path of the current working directory
- Always returns a full path starting from the root (`/`)
- No options or arguments are accepted
- Output does not include a trailing newline in some contexts

## Implementation Notes

- Uses the filesystem's `pwd()` method directly
- Provides the authoritative current directory location
- Simple, single-purpose command with minimal logic
- Directory path is maintained by the filesystem layer

## Relationship to Environment

The current directory shown by `pwd` should match:
- The `PWD` environment variable (when updated by `cd`)
- The filesystem's internal current directory state
- The starting point for relative path resolution

## Error Handling

Generally robust as it queries the filesystem's current state:
- May return empty or error if filesystem doesn't support `pwd()`
- Should always return a valid absolute path in normal operation

## Use Cases

**Navigation verification:**
```bash
cd /complex/path/with/symlinks
pwd  # Shows actual resolved location
```

**Scripting:**
```bash
#!/bin/sh
original_dir=$(pwd)
cd /tmp
# do work...
cd "$original_dir"  # return to starting location
```

**Path construction:**
```bash
current=$(pwd)
backup_dir="$current/backups"
```

## See Also

- [`cd`](cd.md) - Change current directory
- [`ls`](ls.md) - List directory contents
- [Environment variables](../environment/env.md) - Including PWD variable
- [Path resolution](../../README.md#paths) - How paths are resolved