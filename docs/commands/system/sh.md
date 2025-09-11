# sh

Execute shell scripts and commands.

## Synopsis

```
sh [OPTIONS] [SCRIPT] [ARGS]...
sh -c COMMAND
```

## Description

The `sh` command executes shell scripts or command strings using a virtual bash interpreter. It provides shell scripting capabilities within the virtual environment.

## Options

- `-c` - Execute command string
- `-e` - Exit on error (parsed but limited effect)
- `-x` - Print commands as executed - debug mode (parsed)
- `-v` - Verbose mode (parsed)

## Arguments

- `SCRIPT` - Shell script file to execute
- `ARGS` - Arguments to pass to the script
- `COMMAND` - Shell command string (with `-c`)

## Examples

**Execute command string:**
```bash
sh -c "echo Hello World"                     # Execute shell command
sh -c "ls -l | grep txt"                     # Execute command pipeline
```

**Execute script file:**
```bash
sh script.sh                                 # Run shell script
sh install.sh --verbose                      # Run script with arguments
```

**Debug options:**
```bash
sh -x script.sh                              # Debug mode (parsed)
sh -v -e critical_script.sh                  # Verbose + exit on error
```

## Script Execution

**Simple script (hello.sh):**
```bash
#!/bin/sh
echo "Hello from shell script"
echo "Current directory: $(pwd)"
```

**Execute:**
```bash
sh hello.sh
# Output:
# Hello from shell script  
# Current directory: /current/path
```

## Virtual Bash Environment

- Uses `VirtualBashInterpreter` for execution
- Supports common shell constructs and commands
- Integrates with virtual filesystem
- Provides bash-like scripting capabilities

## Supported Features

**Command execution:**
- Built-in commands available in the shell
- Command pipelines and redirection (limited)
- Variable expansion and substitution

**Script constructs:**
- Comments (`#`)
- Command sequences
- Basic shell syntax

## Error Handling

- "sh: scriptname: No such file or directory" - Script file doesn't exist
- "sh: scriptname: Is a directory" - Specified path is directory, not file
- "sh: option requires an argument -- 'c'" - Missing command for `-c`
- "sh: invalid option -- 'x'" - Unknown option provided

## Execution Modes

### Async Mode (Preferred)
Uses `VirtualBashInterpreter` with full async support:
```bash
sh -c "complex command with async support"
```

### Sync Mode (Fallback)
Simplified execution for compatibility:
```bash
sh simple_script.sh
```

## Implementation Notes

- Prioritizes async execution when available
- Falls back to sync mode if async fails
- Script files are read and executed line by line in sync mode
- Comments (`#`) are ignored in line-by-line execution

## Use Cases

**Quick command execution:**
```bash
sh -c "find . -name '*.txt' | wc -l"         # Count text files
```

**Script automation:**
```bash
sh deploy.sh production                      # Run deployment script
```

**Testing shell commands:**
```bash
sh -c "echo 'test' > temp.txt && cat temp.txt"
```

**Configuration scripts:**
```bash
sh setup.sh --database --web-server          # Run configuration script
```

## Script Examples

**Basic script:**
```bash
#!/bin/sh
# Simple backup script
echo "Starting backup..."
mkdir -p backup
cp *.txt backup/
echo "Backup complete"
```

**Script with arguments:**
```bash
#!/bin/sh  
# Process files based on argument
if [ $# -eq 0 ]; then
    echo "Usage: $0 <file_pattern>"
    exit 1
fi
find . -name "$1" -exec echo "Found: {}" \;
```

## Limitations

- Interactive mode not supported
- Limited pipeline and redirection support
- Some advanced bash features may not be available
- Error handling options (`-e`) have limited implementation

## Security Features

- Executes within virtual environment
- File system access limited to virtual filesystem
- No direct system command execution outside sandbox

## See Also

- [`python`](python.md) - Execute Python scripts
- [`script`](script.md) - Run shell scripts (alternative)
- [`bash`] - Full bash shell (if available)
- [Shell scripting](../../README.md#scripting) - Writing shell scripts