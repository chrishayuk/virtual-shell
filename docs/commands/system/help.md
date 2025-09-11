# help

Display help information for commands.

## Synopsis

```
help [command]
```

## Description

The `help` command displays help information about available commands. When called without arguments, it shows a summary of all available commands organized by category. When called with a command name, it displays detailed help for that specific command.

## Arguments

- `command` - Name of command to show help for (optional)

## Examples

**Show all commands:**
```bash
help
# Output:
# Navigation commands: cd, ls, pwd
# File commands: cat, echo, mkdir, rm, rmdir, touch
# Environment commands: env, export
# System commands: clear, exit, help
# Other commands: awk, cp, diff, ...
# Type 'help [command]' for more information
```

**Show help for specific command:**
```bash
help ls                                      # Show help for 'ls' command
help grep                                    # Show help for 'grep' command
help nonexistent                             # "help: no help found for 'nonexistent'"
```

## Command Categories

The help system organizes commands into predefined categories:

**Navigation commands:** Directory navigation and listing
- `cd`, `pwd`, `ls`

**File commands:** Basic file operations  
- `cat`, `echo`, `touch`, `mkdir`, `rm`, `rmdir`

**Environment commands:** Environment variable management
- `env`, `export`

**System commands:** System utilities and shell control
- `help`, `exit`, `clear`

**Other commands:** Additional commands not in predefined categories
- Text processing, advanced file operations, etc.

## Behavior

- **No arguments:** Shows categorized command summary
- **With command name:** Shows detailed help for that command
- **Invalid command:** Shows error message
- Commands are sorted alphabetically within each category
- Shows "Other commands" section for commands not in predefined categories

## Output Format

**Command summary format:**
```
Category Name: command1, command2, command3
...
Type 'help [command]' for more information
```

**Individual command format:**
Shows the command's built-in help text, typically including:
- Command description
- Usage syntax
- Options and flags
- Examples
- See also references

## Implementation Notes

- Uses predefined command categories for organization
- Dynamically lists only commands that are actually available
- Falls back to command's `get_help()` method for detailed help
- Handles commands not in predefined categories gracefully
- Case-sensitive command name matching

## Error Handling

- "help: no help found for 'command'" - Command doesn't exist
- Returns help text on argument parsing errors

## Use Cases

**Discover available commands:**
```bash
help                                         # See what's available
```

**Learn command usage:**
```bash
help find                                    # How to use find command
help awk                                     # AWK usage and examples
```

**Quick reference:**
```bash
help diff                                    # Refresh memory on diff options
```

## Extending Help

New commands automatically appear in help output:
- Commands with defined categories appear in appropriate sections
- Commands without predefined categories appear in "Other commands"
- Each command's help content comes from its `help_text` attribute

## See Also

- [`man`] - Manual pages (if available)
- Command-specific help (e.g., `ls --help`)
- [Command reference](../../README.md#commands) - Complete command documentation