# history

## Synopsis
```bash
history [options] [pattern | count]
```

## Description
The `history` command displays the command history list with line numbers. When a pattern is provided, only commands containing that pattern are shown. When a number is provided, only the last N commands are displayed.

## Options
- `-c` - Clear the history list
- `-d offset` - Delete the history entry at position offset
- `-n` - Display history without line numbers
- `-r` - Display history in reverse order (newest first)
- `-s string` - Add string to history without executing it

## Arguments
- `pattern` - Search for commands containing this pattern (case-insensitive)
- `count` - Show only the last N commands

## Examples

### Basic Usage
```bash
# Show all history
$ history
  1  ls
  2  cd /home
  3  pwd
  4  echo "Hello"
  5  history

# Show last 3 commands
$ history 3
  3  pwd
  4  echo "Hello"
  5  history 3
```

### Search History
```bash
# Find all commands containing 'echo'
$ history echo
  4  echo "Hello"
  7  echo $USER
 12  echo "test" > file.txt
```

### Manage History
```bash
# Add a command to history without executing
$ history -s "git commit -m 'Important commit'"

# Delete entry at position 5
$ history -d 5

# Clear all history
$ history -c
```

### Display Options
```bash
# Show history without line numbers
$ history -n
ls
cd /home
pwd

# Show history in reverse order
$ history -r
 10  history -r
  9  echo "latest"
  8  cd /tmp
```

## Exit Status
- `0` - Success
- `1` - Invalid option or argument

## Environment Variables
The history is stored in memory and is not persistent across shell sessions unless explicitly saved.

## See Also
- [`alias`](../environment/alias.md) - Create command shortcuts
- [`which`](which.md) - Find command locations

## Implementation Notes
- History is maintained per shell session
- No limit on history size (stored in memory)
- Pattern matching is case-insensitive
- Commands are added to history before execution

## Differences from Bash history
- No support for history expansion (!, !!, !$, etc.)
- No persistent history file by default
- No HISTSIZE or HISTFILE environment variables
- Simpler pattern matching (substring search only)