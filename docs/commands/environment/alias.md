# alias

## Synopsis
```bash
alias [name[=value] ...]
```

## Description
The `alias` command defines or displays command aliases. Without arguments, it prints the list of aliases in the reusable form `alias name=value`. When arguments are supplied, an alias is defined for each name whose value is given.

## Arguments
- `name=value` - Define an alias with the specified name and value
- `name` - Display the alias for the specified name

## Examples

### Display Aliases
```bash
# Show all defined aliases
$ alias
alias ll='ls -la'
alias la='ls -a'
alias grep='grep --color'

# Show specific alias
$ alias ll
alias ll='ls -la'

# Non-existent alias
$ alias foo
alias: foo: not found
```

### Define Aliases
```bash
# Create simple alias
$ alias ll='ls -la'

# Create alias with options
$ alias grep='grep --color=auto -n'

# Create alias for navigation
$ alias ..='cd ..'
$ alias ...='cd ../..'

# Create alias with multiple commands (use semicolon)
$ alias update='pwd; ls -la'
```

### Common Aliases
```bash
# File operations
alias cp='cp -i'          # Interactive copy
alias mv='mv -i'          # Interactive move
alias rm='rm -i'          # Interactive remove

# Directory navigation
alias ..='cd ..'
alias ...='cd ../..'
alias home='cd ~'

# Listing variations
alias ll='ls -la'         # Long format with hidden files
alias la='ls -a'          # All files
alias l='ls -CF'          # Classify files

# Shortcuts
alias h='history'
alias c='clear'
alias e='echo'
```

## Quoting
Values containing spaces must be quoted:
```bash
# Single quotes (literal)
alias myls='ls -la'

# Double quotes (allows variable expansion)
alias prompt="echo $USER"

# Escape special characters
alias show='echo '\''single quote'\'''
```

## Alias Expansion
- Aliases are expanded when a command line is read
- Only the first word of a command is checked for aliases
- Aliases can reference other aliases (recursive expansion)
- Maximum recursion depth is 10 to prevent infinite loops

## Persistence
Aliases are not persistent across shell sessions. To make them permanent, add them to your `.shellrc` file:

```bash
# ~/.shellrc
alias ll='ls -la'
alias la='ls -a'
alias grep='grep --color'
```

## Exit Status
- `0` - Success
- `1` - Alias not found (when querying specific alias)

## See Also
- [`unalias`](unalias.md) - Remove aliases
- [`which`](../system/which.md) - Locate commands
- [`export`](export.md) - Set environment variables

## Implementation Notes
- Aliases are stored in a dictionary in memory
- Alias names can contain alphanumeric characters and underscores
- Alias expansion happens before command parsing
- Aliases cannot be used in shell scripts by default

## Differences from Bash alias
- No support for global aliases
- No support for suffix aliases
- Simpler expansion rules
- No alias tracking with `set -x`