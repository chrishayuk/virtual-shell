# timings

## Synopsis
```bash
timings [options]
```

## Description
The `timings` command displays and manages command execution timing statistics. It tracks the number of executions, total time, average time, minimum and maximum execution times for each command run while timing is enabled.

## Options
- `-c` - Clear all timing statistics
- `-e` - Enable timing collection
- `-d` - Disable timing collection
- `-s field` - Sort output by specified field (count, total, avg, min, max)

## Examples

### Basic Usage
```bash
# Enable timing
$ timings -e
Timing collection enabled

# Run some commands
$ ls /home
$ pwd
$ echo "test"

# View statistics
$ timings
Command Timing Statistics (timing is enabled)
--------------------------------------------------------------------------------
Command            Count    Total (s)      Avg (s)      Min (s)      Max (s)
--------------------------------------------------------------------------------
ls                     1     0.000245     0.000245     0.000245     0.000245
pwd                    1     0.000012     0.000012     0.000012     0.000012
echo                   1     0.000008     0.000008     0.000008     0.000008
--------------------------------------------------------------------------------
Total                  3     0.000265
```

### Sort Statistics
```bash
# Sort by average execution time
$ timings -s avg
Command Timing Statistics (timing is enabled)
--------------------------------------------------------------------------------
Command            Count    Total (s)      Avg (s)      Min (s)      Max (s)
--------------------------------------------------------------------------------
grep                   5     0.002500     0.000500     0.000200     0.001000
ls                    10     0.003000     0.000300     0.000100     0.000500
echo                  20     0.000400     0.000020     0.000010     0.000050
--------------------------------------------------------------------------------

# Sort by count
$ timings -s count
```

### Manage Timing
```bash
# Disable timing
$ timings -d
Timing collection disabled

# Clear all statistics
$ timings -c
Timing statistics cleared

# Check status when no data
$ timings
No timing statistics available (timing is disabled)
```

## Sort Fields
- `count` - Number of times command was executed
- `total` - Total execution time
- `avg` - Average execution time
- `min` - Minimum execution time
- `max` - Maximum execution time

## Exit Status
- `0` - Success
- `1` - Invalid option or sort field

## Performance Impact
Enabling timing has minimal performance impact as it only records timestamps before and after command execution.

## See Also
- [`time`](time.md) - Time a single command execution
- [`history`](history.md) - View command history

## Implementation Notes
- Statistics are stored in memory and lost when shell exits
- Timing precision depends on system clock resolution
- Overhead of timing mechanism itself is not subtracted
- Pipeline commands are timed as individual commands

## Use Cases
- Performance profiling of shell scripts
- Identifying slow commands
- Optimizing command sequences
- Monitoring command performance over time