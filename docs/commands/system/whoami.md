# whoami

Display the current user.

## Synopsis

```
whoami
```

## Description

The `whoami` command displays the username of the current user. It retrieves this information from the shell's environment variables.

## Examples

**Show current user:**
```bash
whoami
# Output: john_doe
```

**Use in scripts:**
```bash
#!/bin/sh
echo "Running as user: $(whoami)"
```

## Behavior

- Retrieves username from `USER` environment variable
- Returns "unknown" if `USER` variable is not set
- Ignores any command-line arguments
- Shows help text if arguments are provided

## Environment Variable

The command reads from:
- **Primary:** `USER` environment variable
- **Fallback:** Returns "unknown" if `USER` is not set

## Output Format

```
username
```

Just the username, with no additional formatting or labels.

## Error Handling

- Returns help text if any arguments provided
- Returns "unknown" if `USER` environment variable not available
- No other error conditions

## Use Cases

**Identity verification:**
```bash
whoami                                       # Confirm current user identity
```

**Script personalization:**
```bash
#!/bin/sh
user=$(whoami)
echo "Welcome, $user!"
```

**Access control:**
```bash
#!/bin/sh
if [ "$(whoami)" = "admin" ]; then
    echo "Admin access granted"
else
    echo "Regular user access"
fi
```

**Log entries:**
```bash
echo "$(date): $(whoami) performed action" >> activity.log
```

## Implementation Notes

- Uses shell's `environ.get("USER", "unknown")` method
- Minimal error handling (just argument validation)
- No user database lookups or system calls
- Relies entirely on environment variable

## Environment Setup

The `USER` variable is typically set:
- During shell initialization
- By the parent process or system
- Through manual `export USER=username`

## Limitations

- Only shows environment variable value
- No user ID (UID) information
- No group membership details
- No real vs effective user distinction

## Related Information

**Setting user identity:**
```bash
export USER=newname                          # Change USER variable
whoami                                       # Shows: newname
```

## See Also

- [`env`](../environment/env.md) - Display environment variables
- [`id`] - Display user and group IDs (if available)
- [Environment variables](../environment/README.md) - Managing shell environment