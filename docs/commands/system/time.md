# time

Measure command execution time or show current time.

## Synopsis

```
time [command] [arguments]
time
```

## Description

The `time` command has two modes: it can measure the execution time of other commands, or display the current system time when called without arguments.

## Arguments

- `command` - Command to execute and time (optional)
- `arguments` - Arguments to pass to the command

## Examples

**Time command execution:**
```bash
time ls -la                                  # Time the 'ls -la' command
# Output:
# [ls output]
# Execution time: 0.0234 seconds
```

**Time complex operations:**
```bash
time find . -name "*.txt"                   # Time a find operation
time sort large_file.txt                    # Time file sorting
```

**Show current time:**
```bash
time                                         # Display current system time
# Output: Current time: 2024-01-15 14:30:22
```

## Timing Accuracy

- Uses `time.perf_counter()` for high-precision timing
- Resolution typically in microseconds or better
- Measures wall-clock time (elapsed real time)
- Does not separate user/system time like Unix `time`

## Output Format

**With command:**
```
[command output]
Execution time: X.XXXX seconds
```

**Without command:**
```
Current time: YYYY-MM-DD HH:MM:SS
```

## Behavior

- Executes the specified command normally
- Measures execution time from start to completion
- Shows both command output and timing information
- Time display shows 4 decimal places for precision

## Time Measurement

- **Start time:** Recorded immediately before command execution
- **End time:** Recorded immediately after command completion
- **Elapsed time:** Calculated as `end - start`
- **Precision:** High-resolution performance counter

## Use Cases

**Performance analysis:**
```bash
time grep "pattern" huge_file.txt            # Measure search time
time awk '{sum+=$1}END{print sum}' data.txt  # Time data processing
```

**Script optimization:**
```bash
time ./old_script.sh                         # Time current version
time ./optimized_script.sh                   # Compare with improved version
```

**System monitoring:**
```bash
time python analyze.py                       # Time Python script execution
time sort -n numbers.txt                     # Time sorting operation
```

**Current time display:**
```bash
time                                         # Show current time
```

## Limitations

- Measures wall-clock time only (not CPU time breakdown)
- No built-in averaging or statistical analysis
- Command output and timing info are mixed in output
- No options for different time formats

## Implementation Notes

- Uses shell's `execute()` method to run timed commands
- Timing measurements use `time.perf_counter()`
- Current time display uses `time.strftime()`
- Commands are joined with spaces before execution

## Error Handling

- If timed command fails, shows error output and timing
- Invalid commands show error message and execution time
- Time measurement continues even if command fails

## See Also

- [`uptime`](uptime.md) - Show system uptime
- [`date`] - Display/set system date (if available)
- [Performance analysis](../../README.md#performance) - Performance monitoring tools