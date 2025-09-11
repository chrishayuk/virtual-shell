# env

Display environment variables.

## Synopsis

```
env [filter]
```

## Description

The `env` command displays all environment variables currently set in the shell session. It can optionally filter the output to show only variables whose names contain a specified substring.

## Arguments

- `filter` - Optional substring to match against variable names

## Examples

**Display all environment variables:**
```bash
env
# Output:
# HOME=/home/user
# PATH=/usr/bin:/bin
# USER=john
# PWD=/current/directory
# SHELL=/bin/sh
```

**Filter environment variables:**
```bash
env PATH                                     # Show variables containing "PATH"
# Output:
# PATH=/usr/bin:/bin

env HOME                                     # Show variables containing "HOME"  
# Output:
# HOME=/home/user
```

**Case-sensitive filtering:**
```bash
env usr                                      # Show variables containing "usr"
env USER                                     # Show variables containing "USER"
```

## Output Format

Each environment variable is displayed in the format:
```
KEY=value
```

Variables are displayed in the order they exist in the shell's environment dictionary.

## Common Environment Variables

**System variables:**
- `HOME` - User's home directory
- `USER` - Current username
- `PWD` - Present working directory
- `PATH` - Command search path

**Shell variables:**
- `SHELL` - Current shell program
- Custom variables set with `export`

## Behavior

- **No filter:** Shows all environment variables
- **With filter:** Shows only variables whose names contain the filter string
- **No matches:** Returns empty output if filter matches no variables
- **Case-sensitive:** Filter matching is case-sensitive

## Use Cases

**View all environment:**
```bash
env                                          # See complete environment
```

**Find specific variables:**
```bash
env PATH                                     # Check PATH settings
env HOME                                     # Check home directory
```

**Debug environment:**
```bash
env | grep -i python                        # Find Python-related variables
env JAVA                                     # Check Java environment
```

**Script validation:**
```bash
#!/bin/sh
if env | grep -q "REQUIRED_VAR="; then
    echo "Environment is configured"
else
    echo "Missing required environment variable"
fi
```

## Filtering Examples

**Find user-related variables:**
```bash
env USER                                     # Variables with "USER" in name
```

**Find path-related variables:**
```bash  
env PATH                                     # Variables with "PATH" in name
```

**Check for custom variables:**
```bash
env MY_APP                                   # Variables with "MY_APP" in name
```

## Error Handling

- No error conditions - command always succeeds
- Empty output if no variables match filter
- Returns help text on argument parsing errors

## Implementation Notes

- Accesses shell's `environ` dictionary directly
- Filters by checking if filter substring is in variable name
- Returns variables in dictionary iteration order
- No sorting or special formatting applied

## Integration with Other Commands

**Combine with grep:**
```bash
env | grep -i path                           # Case-insensitive PATH search
```

**Count variables:**
```bash
env | wc -l                                  # Count total environment variables
```

**Save to file:**
```bash
env > current_env.txt                        # Save environment snapshot
```

## See Also

- [`export`](export.md) - Set environment variables
- [`whoami`](../system/whoami.md) - Display current user (uses USER variable)
- [Environment management](../../README.md#environment) - Managing shell environment