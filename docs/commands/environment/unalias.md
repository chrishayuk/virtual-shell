# unalias

## Synopsis
```bash
unalias [-a] name [name ...]
```

## Description
The `unalias` command removes alias definitions from the shell. Each name is an alias that is removed from the list of defined aliases.

## Options
- `-a` - Remove all alias definitions

## Arguments
- `name` - One or more alias names to remove

## Examples

### Remove Single Alias
```bash
# Remove one alias
$ alias ll='ls -la'
$ unalias ll
$ alias ll
alias: ll: not found
```

### Remove Multiple Aliases
```bash
# Define some aliases
$ alias ll='ls -la'
$ alias la='ls -a'
$ alias l='ls'

# Remove multiple at once
$ unalias ll la
$ alias
alias l='ls'
```

### Remove All Aliases
```bash
# Define some aliases
$ alias ll='ls -la'
$ alias la='ls -a'
$ alias grep='grep --color'

# Remove all
$ unalias -a
$ alias
(no output - all aliases removed)
```

### Error Cases
```bash
# Try to remove non-existent alias
$ unalias foo
unalias: foo: not found

# Invalid option
$ unalias -x
unalias: -x: invalid option
unalias: usage: unalias [-a] name [name ...]
```

## Exit Status
- `0` - Success (all specified aliases were removed or didn't exist)
- `1` - Error (invalid option)

## Notes
- Removing an alias does not affect commands currently being executed
- After removing an alias, the original command is used
- Cannot remove built-in shell commands

## See Also
- [`alias`](alias.md) - Define or display aliases
- [`which`](../system/which.md) - Show command locations

## Implementation Notes
- Aliases are removed immediately from the shell's alias dictionary
- No confirmation is requested before removal
- The `-a` option clears the entire alias dictionary

## Common Use Cases
```bash
# Temporarily disable an alias
$ unalias rm          # Remove 'rm -i' alias to use regular rm

# Clean up after testing
$ unalias -a          # Start fresh with no aliases

# Remove conflicting aliases
$ unalias ls          # Remove custom ls to use default
```

## Differences from Bash unalias
- No pattern matching support
- No `-t` option for removing tracked aliases
- Simpler error messages