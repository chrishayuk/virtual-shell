# Chuk Virtual Shell Examples

This directory contains example scripts demonstrating various features of the Chuk Virtual Shell.

## 🚀 Quick Start

```bash
# Run in script mode
chuk-virtual-shell examples/hello_world.sh

# Run in interactive mode
chuk-virtual-shell
user@pyodide:/$ source examples/multiline_control_flow.sh
```

## 📚 Core Shell Examples (.sh)

### Basic Examples
- **`hello_world.sh`** - Simple hello world example
- **`file_operations.sh`** - File creation, reading, writing, and manipulation
- **`working_demo.sh`** - Demonstrates all working features in the shell

### Control Flow
- **`multiline_control_flow.sh`** ⭐ - Comprehensive multi-line control flow demo
  - Multi-line if/then/else statements
  - For, while, and until loops
  - Nested control structures
  - Break and continue statements
  - Interactive mode examples
- **`control_flow.sh`** - Working control flow patterns using operators
- **`control_flow_demo.sh`** - Python-based control flow demonstration

### Text Processing
- **`text_processing.sh`** - Basic text processing (grep, sed, awk)
- **`advanced_text_processing.sh`** - Advanced text manipulation
- **`diff_patch_demo.sh`** - Diff and patch command demonstrations

### Shell Features
- **`redirection_pipeline_demo.sh`** - Input/output redirection and pipelines
- **`new_features_demo.sh`** - Latest features (aliases, history, tree)
- **`comprehensive_demo.sh`** - Full feature showcase

## 🐍 Python Integration

### Python Test Runner
- **`python_integration_demo.py`** - Comprehensive Python integration test that demonstrates:
  - Executing shell commands from Python
  - Virtual filesystem operations
  - Data processing with CSV and JSON
  - Dynamic script generation
  - Pipeline integration
  - Environment variables
  - Control flow execution

Run it with:
```bash
python examples/python_integration_demo.py
```

### Python Usage in the Shell

The virtual shell includes a full Python interpreter. You can run Python code directly:

### Interactive Python
```bash
user@pyodide:/$ python
>>> print("Hello from Python!")
Hello from Python!
>>> import os
>>> os.getcwd()
'/home/user'
>>> exit()
```

### One-line Python Commands
```bash
user@pyodide:/$ python -c "print('Hello World')"
Hello World

user@pyodide:/$ python -c "import math; print(math.pi)"
3.141592653589793
```

### Python Scripts
```bash
# Create a Python script
user@pyodide:/$ cat > script.py << EOF
> #!/usr/bin/env python
> import os
> 
> print("Current directory:", os.getcwd())
> 
> # Write to virtual filesystem
> with open('/tmp/output.txt', 'w') as f:
>     f.write("Hello from Python script!\n")
> 
> # Read from virtual filesystem
> with open('/tmp/output.txt', 'r') as f:
>     print("File contents:", f.read())
> EOF

# Run the script
user@pyodide:/$ python script.py
Current directory: /home/user
File contents: Hello from Python script!
```

### Python with Virtual Filesystem
```bash
# Python can interact with the virtual filesystem
user@pyodide:/$ mkdir /data
user@pyodide:/$ echo "test data" > /data/input.txt

user@pyodide:/$ python -c "
with open('/data/input.txt', 'r') as f:
    data = f.read()
    print('Read:', data)
    
with open('/data/output.txt', 'w') as f:
    f.write(data.upper())
"

user@pyodide:/$ cat /data/output.txt
TEST DATA
```

## 📁 Commands Directory

The `commands/` subdirectory contains comprehensive demonstrations organized by command category:

```
commands/
├── README.md                    # Detailed documentation
├── all_commands_demo.sh         # Master script that runs all categories
├── working_commands_demo.sh     # Verified working commands
├── filesystem/
│   └── filesystem_demo.sh       # File and directory operations
├── navigation/
│   ├── navigation_demo.sh       # Directory navigation and listing
│   └── navigation_simple_demo.sh # Simple navigation examples
├── text/
│   └── text_demo.sh             # Text processing and analysis
├── system/
│   └── system_demo.sh           # System utilities and shell control
└── environment/
    └── environment_demo.sh      # Environment variable management
```

### Running Command Demos

```bash
# Run all command demos
chuk-virtual-shell examples/commands/all_commands_demo.sh

# Run individual category
chuk-virtual-shell examples/commands/filesystem/filesystem_demo.sh
```

See `commands/README.md` for detailed documentation of each category.

## 🎯 Key Features Demonstrated

### Multi-line Input (NEW!)
The shell now supports multi-line control flow in interactive mode:

```bash
user@pyodide:/$ num=5
user@pyodide:/$ if [ $num -gt 3 ]; then
>   echo "Greater than 3"
> else
>   echo "Not greater"
> fi
Greater than 3
```

### Virtual Filesystem
All file operations work within the virtual filesystem:
```bash
mkdir -p /demo/test
echo "Hello" > /demo/test/file.txt
cat /demo/test/file.txt
```

### Pipes and Redirection
Full support for pipes and redirects:
```bash
ls /demo | grep txt | wc -l
echo "data" > output.txt
cat < input.txt | sort | uniq >> output.txt
```

### Control Flow
Working control structures:
```bash
for i in 1 2 3; do
  echo "Number: $i"
done

if [ -e /file.txt ]; then
  echo "File exists"
fi
```

### Text Processing
Complete text processing toolkit:
```bash
cat file.txt | grep pattern | sed 's/old/new/g' | awk '{print $1}'
```

## 🔧 Running Examples

### Method 1: Script Mode
```bash
# Run directly
chuk-virtual-shell examples/multiline_control_flow.sh

# With custom filesystem provider
chuk-virtual-shell --fs-provider sqlite examples/file_operations.sh
```

### Method 2: Interactive Mode
```bash
# Start interactive shell
chuk-virtual-shell

# Then source a script
user@pyodide:/$ source examples/hello_world.sh

# Or run commands directly
user@pyodide:/$ for i in 1 2 3; do
>   echo "Number: $i"
> done
```

### Method 3: Python Scripts
```bash
# Using Python runner
python examples/session_demo.py

# Or within the shell
chuk-virtual-shell
user@pyodide:/$ python examples/data_processing.py
```

## 📝 Notes

- All examples are designed to work with the virtual filesystem
- Scripts can be modified and re-run without affecting the host system
- The shell supports both single-line and multi-line command entry
- See individual script comments for specific feature documentation