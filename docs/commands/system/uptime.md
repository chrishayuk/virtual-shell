# uptime

Display shell session uptime.

## Synopsis

```
uptime
```

## Description

The `uptime` command displays how long the current shell session has been running, formatted as hours, minutes, and seconds.

## Examples

**Show uptime:**
```bash
uptime
# Output: Uptime: 2h 15m 42s
```

**Use in monitoring:**
```bash
echo "Session started:"
uptime
```

## Behavior

- Calculates elapsed time since shell startup
- Shows time in hours, minutes, and seconds format
- Ignores any command-line arguments
- Based on shell's `start_time` attribute

## Time Calculation

- **Start time:** Set when shell initializes (`self.shell.start_time`)
- **Current time:** Obtained via `time.time()`
- **Elapsed time:** `current_time - start_time`
- **Formatting:** Converted to hours:minutes:seconds

## Output Format

```
Uptime: Xh Ym Zs
```

Where:
- `X` = Hours (0 or more)
- `Y` = Minutes (0-59) 
- `Z` = Seconds (0-59)

## Examples of Output

```bash
# Just started
Uptime: 0h 0m 3s

# After some use  
Uptime: 1h 23m 45s

# Long-running session
Uptime: 12h 5m 18s
```

## Implementation Notes

- Uses integer division (`divmod`) for time breakdown
- Requires shell to track `start_time` attribute
- Time measured in seconds since Unix epoch
- No sub-second precision in display

## Error Handling

- Shows help if arguments provided
- Assumes `start_time` is available on shell object
- Gracefully handles time calculation

## Use Cases

**Session monitoring:**
```bash
uptime                                       # Check how long you've been working
```

**Script diagnostics:**
```bash
#!/bin/sh
echo "Shell session uptime:"
uptime
echo "Starting long process..."
```

**Performance context:**
```bash
uptime                                       # See session age
time some_long_command                       # Time a command
uptime                                       # Confirm session still running
```

## Comparison to System Uptime

This command shows **shell session** uptime, not system uptime:
- **Shell uptime:** Time since shell started
- **System uptime:** Time since system boot (different command)

## Limitations

- Only shows current shell session time
- No load average or user count (unlike system `uptime`)
- No options for different time formats
- Depends on accurate shell initialization

## See Also

- [`time`](time.md) - Measure command execution time or show current time
- [`date`] - Display current date/time (if available)
- [Shell lifecycle](../../README.md#lifecycle) - Shell initialization and timing