# System Commands

System operations, utilities, and shell control commands for managing the shell environment and executing scripts.

## Commands Overview

### Shell Control
| Command | Description | Documentation |
|---------|-------------|---------------|
| [`help`](help.md) | Display help information for commands | [help.md](help.md) |
| [`exit`](exit.md) | Exit the shell session | [exit.md](exit.md) |
| [`clear`](clear.md) | Clear the terminal screen | [clear.md](clear.md) |

### System Information
| Command | Description | Documentation |
|---------|-------------|---------------|
| [`time`](time.md) | Measure command execution time or show current time | [time.md](time.md) |
| [`timings`](timings.md) | Display command execution statistics | [timings.md](timings.md) |
| [`uptime`](uptime.md) | Display shell session uptime | [uptime.md](uptime.md) |
| [`whoami`](whoami.md) | Display the current user | [whoami.md](whoami.md) |
| [`which`](which.md) | Locate commands in PATH or built-ins | [which.md](which.md) |
| [`history`](history.md) | Display and search command history | [history.md](history.md) |

### Script Execution
| Command | Description | Documentation |
|---------|-------------|---------------|
| [`python`](python.md) | Execute Python scripts in virtual environment | [python.md](python.md) |
| [`sh`](sh.md) | Execute shell commands and scripts | [sh.md](sh.md) |
| [`script`](script.md) | Run shell scripts using the script runner | [script.md](script.md) |

## Common Usage Patterns

### Getting Help and Information
```bash
# Get help
help                            # Show all available commands
help ls                         # Show help for specific command
help grep                       # Show grep usage and examples

# System information
whoami                          # Show current user
uptime                          # Show shell session uptime
time                           # Show current system time

# Command location
which ls                        # Find ls command location
which -a python                 # Find all python locations
which cd pwd ls                 # Check multiple commands

# Command history
history                         # Show all command history
history 20                      # Show last 20 commands
history grep                    # Search for grep commands
history -c                      # Clear command history
```

### Shell Session Management
```bash
# Clean workspace
clear                          # Clear terminal screen

# Monitor performance
time ls -la                    # Time command execution
time grep "pattern" largefile.txt

# Exit session
exit                          # Graceful shell exit
```

### Script Execution
```bash
# Python scripts
python script.py               # Execute Python file
python -c "print('Hello')"     # Execute Python command
python -c "import sys; print(sys.version)"

# Shell scripts  
sh deploy.sh                   # Execute shell script
sh -c "echo 'Hello World'"     # Execute shell command
script setup.sh configure.sh   # Run multiple scripts
```

## Advanced Usage

### Performance Monitoring
```bash
# Time individual operations
time find . -name "*.py" | wc -l              # Time file search and count
time sort large_dataset.txt                   # Time sorting operation
time python data_processor.py input.csv       # Time script execution

# Command timing statistics
timings -e                                     # Enable command timing
timings                                        # Show timing statistics
timings -s avg                                 # Sort by average time
timings -s total                               # Sort by total time
timings -c                                     # Clear timing statistics
timings -d                                     # Disable command timing

# Session monitoring
uptime                                         # Check how long shell has been running
time python -c "import time; time.sleep(2)"   # Time with known duration
history | tail -20                             # Review recent commands
```

### Script Development and Testing
```bash
# Python development
python -c "
def factorial(n):
    return 1 if n <= 1 else n * factorial(n-1)
print(f'5! = {factorial(5)}')
"

# Shell script testing
sh -c "
for i in 1 2 3; do
    echo 'Processing item $i'
done
"

# Multiple script execution
script init.sh deploy.sh test.sh              # Run deployment pipeline
```

### Interactive Workflows
```bash
# Development cycle
clear                          # Clean screen
python test_script.py          # Run tests
time python main.py            # Time main execution
uptime                         # Check session duration
```

## Key Features

### Shell Control
- **Help System:** Comprehensive help for all commands with examples
- **Session Management:** Graceful exit and terminal control
- **User Interface:** Clear screen functionality for better organization

### System Monitoring
- **Performance Measurement:** High-precision timing for commands
- **Session Tracking:** Monitor shell uptime and usage
- **User Identification:** Current user information

### Script Execution Environment
- **Python Integration:** Full Python environment with standard libraries
- **Shell Script Support:** Execute bash-compatible scripts
- **Multi-Script Execution:** Run multiple scripts in sequence
- **Error Handling:** Comprehensive error reporting and recovery

## Security Features

- **Sandboxed Execution:** All script execution occurs within virtual environment
- **Limited System Access:** Scripts cannot access host system directly
- **Safe Python Environment:** Restricted Python execution with security controls
- **Controlled File Access:** Scripts can only access virtual filesystem

## Performance Considerations

- **Async Execution:** Python and shell commands support async execution
- **Memory Management:** Efficient handling of script execution and cleanup
- **Error Recovery:** Robust error handling prevents system instability
- **Resource Monitoring:** Time commands help identify performance bottlenecks

## Integration Examples

### With Other Command Categories
```bash
# Combine with filesystem commands
time find . -name "*.txt" | wc -l
python -c "import os; print(len([f for f in os.listdir('.') if f.endswith('.py')]))"

# Combine with text processing
sh -c "cat data.txt | grep pattern | sort | uniq -c"
python -c "
import sys
lines = sys.stdin.read().splitlines()
print(f'Processed {len(lines)} lines')
"

# System information with environment
whoami && echo "Session uptime:" && uptime
python -c "import os; print(f'Current user: {os.environ.get(\"USER\", \"unknown\")}')"
```

## Best Practices

1. **Use appropriate execution method:** `python -c` for simple commands, files for complex scripts
2. **Monitor performance:** Use `time` to identify slow operations
3. **Clean workspace:** Use `clear` to maintain organized terminal
4. **Check session health:** Monitor `uptime` for long-running sessions
5. **Handle errors gracefully:** Use help system when commands fail

## See Also

- [Environment Commands](../environment/README.md) - Environment variable management
- [Filesystem Commands](../filesystem/README.md) - File operations for scripts
- [Text Processing Commands](../text/README.md) - Text processing in scripts
- [Main Documentation](../../README.md) - Complete command reference