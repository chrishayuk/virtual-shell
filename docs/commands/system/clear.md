# clear

Clear the terminal screen.

## Synopsis

```
clear
```

## Description

The `clear` command clears the terminal screen by sending ANSI escape sequences to reset the display and move the cursor to the top-left corner.

## Examples

**Clear the screen:**
```bash
clear                                        # Clears terminal display
```

**Use in scripts:**
```bash
#!/bin/sh
echo "Starting process..."
sleep 2
clear                                        # Clear before showing results
echo "Process complete!"
```

## Behavior

- Sends ANSI escape sequence `\033[2J` to clear entire screen
- Sends ANSI escape sequence `\033[H` to move cursor to home position (1,1)
- Does not clear command history or shell state
- Ignores any command-line arguments

## ANSI Escape Sequences

The command uses standard ANSI escape codes:
- `\033[2J` - Clear entire screen
- `\033[H` - Move cursor to home position

These sequences are supported by most modern terminals.

## Terminal Compatibility

- Works with ANSI-compatible terminals
- Supported by most terminal emulators (xterm, bash, PowerShell, etc.)
- May not work correctly in very old or minimal terminal environments

## Error Handling

- Ignores all arguments (no error for extra arguments)
- Always returns the escape sequence regardless of terminal support
- Terminal determines actual clearing behavior

## Implementation Notes

- Uses hardcoded ANSI escape sequences
- No terminal capability detection
- Minimal argument parsing (ignores all arguments)
- Returns escape sequence as output rather than sending directly

## Use Cases

**Clean working environment:**
```bash
clear                                        # Start with clean screen
```

**Script presentation:**
```bash
clear
echo "Welcome to the application!"
```

**Between command sequences:**
```bash
ls -la
# ... review output ...
clear
df -h
```

## Alternative Methods

**In some environments:**
- `printf "\033[2J\033[H"` (equivalent)  
- `tput clear` (if available)
- Ctrl+L (keyboard shortcut in many shells)

## See Also

- [`reset`] - Reset terminal to initial state (if available)
- [`tput`] - Terminal capability interface (if available)
- [Terminal control](../../README.md#terminal) - Terminal manipulation features