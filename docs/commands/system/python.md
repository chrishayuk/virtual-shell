# python

Execute Python scripts in virtual environment.

## Synopsis

```
python [OPTIONS] [SCRIPT] [ARGS]...
python -c COMMAND
```

## Description

The `python` command executes Python code in a virtual Python environment. It supports running script files, executing command strings, and limited module execution.

## Options

- `-c` - Execute command string
- `-m` - Run module as script (limited support)
- `-i` - Interactive mode (not fully supported)
- `-V, --version` - Print version information

## Arguments

- `SCRIPT` - Python script file to execute
- `ARGS` - Arguments to pass to the script
- `COMMAND` - Python code string (with `-c`)

## Examples

**Execute script file:**
```bash
python script.py                             # Run Python script
python hello.py arg1 arg2                    # Run script with arguments
```

**Execute command string:**
```bash
python -c "print('Hello World')"             # Execute Python code
python -c "import sys; print(sys.version)"   # Show Python version
```

**Show version:**
```bash
python -V                                    # Show version
python --version                             # Alternative version flag
```

**Mathematical calculations:**
```bash
python -c "print(2**10)"                     # Calculate 2^10
python -c "import math; print(math.pi)"      # Use math module
```

## Virtual Environment Features

- Isolated Python execution environment
- Standard library modules available
- Safe code execution with restricted capabilities
- File system integration for script loading

## Supported Python Features

**Built-in functions:** `print()`, `len()`, `range()`, `enumerate()`, etc.
**Standard modules:** `math`, `sys`, `os` (limited), `json`, `re`, etc.
**Data structures:** Lists, dictionaries, sets, tuples
**Control flow:** `if`, `for`, `while`, `try`/`except`

## File Operations

**Script execution:**
```bash
# script.py contains:
# print("Hello from script!")
# import sys
# print(f"Arguments: {sys.argv[1:]}")

python script.py arg1 arg2
# Output:
# Hello from script!
# Arguments: ['arg1', 'arg2']
```

## Error Handling

- "python: can't open file 'script.py': No such file or directory"
- "python: 'dirname' is a directory, not a Python file"
- "python: -c requires an argument"
- "python: invalid option -- 'x'"

## Implementation Notes

- Uses `VirtualPythonInterpreter` for code execution
- Supports both async and sync execution modes
- Script arguments available via `sys.argv`
- File existence and type validation before execution

## Execution Modes

### Command String (`-c`)
```bash
python -c "x = 5; y = 10; print(f'Sum: {x+y}')"
```

### Script File
```bash
python calculate.py
```

### Interactive Mode (Limited)
```bash
python                                       # Shows message about limited support
```

## Security Features

- Restricted execution environment
- File system access limited to virtual filesystem
- No direct system access
- Safe import restrictions

## Use Cases

**Quick calculations:**
```bash
python -c "print(sum(range(1, 101)))"        # Sum 1 to 100
```

**Data processing:**
```bash
python -c "
import json
data = {'name': 'test', 'value': 42}
print(json.dumps(data, indent=2))
"
```

**Script execution:**
```bash
python data_analyzer.py input.csv            # Run analysis script
```

**Testing code snippets:**
```bash
python -c "
def factorial(n):
    return 1 if n <= 1 else n * factorial(n-1)
print(factorial(5))
"
```

## Limitations

- Interactive REPL not fully supported
- Module execution (`-m`) has limited implementation
- Some standard library modules may be restricted
- No package installation capabilities

## Aliases

- `python3` - Alias for the same command

## See Also

- [`sh`](sh.md) - Execute shell scripts
- [`script`](script.md) - Run shell scripts
- [Python environment](../../README.md#python) - Python execution environment
- [Virtual environments](../../README.md#virtual-env) - Sandboxed execution