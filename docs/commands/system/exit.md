# exit

Exit the shell session.

## Synopsis

```
exit [--force]
```

## Description

The `exit` command terminates the shell session gracefully. It stops the main shell loop and ends the current session.

## Options

- `--force` - Force exit immediately (optional, same behavior as normal exit)

## Examples

**Exit normally:**
```bash
exit
# Output: Goodbye!
# (shell terminates)
```

**Force exit:**
```bash
exit --force
# Output: Goodbye!  
# (shell terminates)
```

## Behavior

- Sets the shell's `running` flag to `False`
- Causes the main shell loop to terminate
- Returns "Goodbye!" message before exiting
- Ignores unknown arguments
- Both normal and force exit have same behavior in this implementation

## Exit Process

1. Command is executed
2. Shell's `running` attribute set to `False`
3. "Goodbye!" message is displayed
4. Shell main loop detects `running = False` and exits
5. Session terminates

## Error Handling

- No error conditions - command always succeeds
- Unknown arguments are silently ignored
- Always returns success message before termination

## Implementation Notes

- Uses `argparse` for option parsing
- `--force` option is parsed but has no special behavior
- Modifies shell state (`self.shell.running = False`)
- Return message displayed before shell actually exits

## Use Cases

**Normal session ending:**
```bash
# After completing work
exit
```

**Script termination:**
```bash
#!/bin/sh
echo "Task completed"
exit                                         # Terminate script
```

**Conditional exit:**
```bash
#!/bin/sh
if [ $? -ne 0 ]; then
    echo "Error occurred"
    exit
fi
```

## Alternative Exit Methods

**Keyboard shortcuts (if supported):**
- Ctrl+D (EOF signal)
- Ctrl+C (interrupt, may not exit cleanly)

**Script contexts:**
- `return` (in functions)
- End of script (implicit exit)

## Session Cleanup

The exit command provides graceful termination:
- Allows cleanup operations to complete
- Maintains shell state until final loop iteration
- Provides user feedback with goodbye message

## See Also

- [`logout`] - Alternative exit command (if available)
- [Shell lifecycle](../../README.md#lifecycle) - Shell startup and shutdown process
- [Session management](../../README.md#sessions) - Managing shell sessions