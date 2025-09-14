# Virtual Shell Commands Examples

This directory contains comprehensive demonstration scripts for all virtual shell commands, organized by category to match the documentation structure.

## Directory Structure

```
commands/
├── README.md                     # This file
├── all_commands_demo.sh          # Master demo script running all categories
├── filesystem/
│   └── filesystem_demo.sh        # File and directory operations
├── navigation/
│   └── navigation_demo.sh        # Directory navigation and listing
├── text/
│   └── text_demo.sh              # Text processing and analysis
├── system/
│   └── system_demo.sh            # System utilities and shell control
└── environment/
    └── environment_demo.sh       # Environment variable management
```

## Command Categories Demonstrated

### 1. Filesystem Commands (`filesystem_demo.sh`)
Demonstrates all file and directory operations:
- **File Operations**: `cat`, `touch`, `echo`, `more`
- **Directory Operations**: `mkdir`, `rmdir` 
- **File/Directory Management**: `cp`, `mv`, `rm`, `find`
- **Storage Information**: `df`, `du`, `quota`

**Features Shown**:
- Creating and manipulating files and directories
- Copying and moving operations
- File content display and editing
- Storage usage monitoring
- Complex file operations workflows

### 2. Navigation Commands (`navigation_demo.sh`)
Demonstrates directory navigation and listing:
- **Directory Navigation**: `cd`, `pwd`
- **Directory Listing**: `ls` (with various options)

**Features Shown**:
- Navigation patterns and directory traversal
- Long format and hidden file listings
- Multi-level directory exploration
- Practical navigation scenarios

### 3. Text Processing Commands (`text_demo.sh`)
Demonstrates comprehensive text processing capabilities:
- **Pattern Matching**: `grep` (with regex and options)
- **Text Transformation**: `sed`, `awk`
- **File Analysis**: `head`, `tail`, `wc`, `sort`, `uniq`
- **File Comparison**: `diff`, `patch`

**Features Shown**:
- Complex pattern matching and filtering
- Text transformation and processing pipelines
- Statistical analysis of text files
- File comparison and patch application
- Advanced regex and text manipulation

### 4. System Commands (`system_demo.sh`)
Demonstrates system utilities and control:
- **System Information**: `whoami`, `uptime`, `time`
- **Shell Control**: `clear`, `help`, `exit`
- **Script Execution**: `python`, `script`, `sh`

**Features Shown**:
- System information gathering
- Performance timing and monitoring
- Multi-language script execution (Python/Bash)
- Shell scripting within virtual environment

### 5. Environment Commands (`environment_demo.sh`)
Demonstrates environment variable management:
- **Variable Display**: `env`
- **Variable Setting**: `export`

**Features Shown**:
- Setting and displaying environment variables
- Using variables in file operations
- Variable substitution in text
- Complex environment configurations
- Python integration with environment variables

## Running the Examples

### Option 1: Run Individual Category Demos

Run a specific category demonstration directly:

```bash
# Run filesystem commands demo
chuk-virtual-shell examples/commands/filesystem/filesystem_demo.sh

# Run navigation commands demo  
chuk-virtual-shell examples/commands/navigation/navigation_demo.sh

# Run text processing demo
chuk-virtual-shell examples/commands/text/text_demo.sh

# Run system commands demo
chuk-virtual-shell examples/commands/system/system_demo.sh

# Run environment commands demo
chuk-virtual-shell examples/commands/environment/environment_demo.sh
```

### Option 2: Run Complete Demo Suite

Run all command demonstrations in sequence:

```bash
# Run the master demo script
chuk-virtual-shell examples/commands/all_commands_demo.sh

# Run the working commands demo (verified to work)
chuk-virtual-shell examples/commands/working_commands_demo.sh
```

### Option 3: Interactive Shell Execution

Start interactive shell and run demos from within:

```bash
# Start virtual shell
chuk-virtual-shell

# From within the shell, run demos:
user@pyodide:/$ source examples/commands/filesystem/filesystem_demo.sh
user@pyodide:/$ source examples/commands/navigation/navigation_demo.sh
user@pyodide:/$ source examples/commands/text/text_demo.sh
user@pyodide:/$ source examples/commands/system/system_demo.sh
user@pyodide:/$ source examples/commands/environment/environment_demo.sh
```

### Option 4: Batch Execution

Create a shell script to run multiple demos:

```bash
#!/bin/bash
# run_all_demos.sh

echo "Running all command demos..."

for category in filesystem navigation text system environment; do
    echo "Running $category demo..."
    chuk-virtual-shell examples/commands/$category/${category}_demo.sh
    echo "---"
done

echo "All demos complete!"
```

## What Each Demo Proves

### Filesystem Demo Proves:
- ✅ Virtual filesystem works correctly
- ✅ File creation, copying, moving, deletion operations
- ✅ Directory operations and nested structures
- ✅ Output redirection (`>`, `>>`) functionality
- ✅ Storage monitoring and space calculations

### Navigation Demo Proves:
- ✅ Directory navigation (`cd`) with relative/absolute paths
- ✅ Current directory tracking (`pwd`)
- ✅ Comprehensive directory listing (`ls`) with all options
- ✅ Hidden file and long format display
- ✅ Multi-level directory traversal

### Text Processing Demo Proves:
- ✅ Pattern matching and regular expressions (`grep`)
- ✅ Stream editing and text transformation (`sed`, `awk`)
- ✅ File content analysis (`head`, `tail`, `wc`)
- ✅ Data sorting and deduplication (`sort`, `uniq`) 
- ✅ File comparison and patch application (`diff`, `patch`)
- ✅ Complex text processing pipelines

### System Demo Proves:
- ✅ System information commands work
- ✅ Performance timing and monitoring
- ✅ Python script execution within virtual shell
- ✅ Shell script execution and interpretation
- ✅ Help system and command documentation
- ✅ Multi-language integration

### Environment Demo Proves:
- ✅ Environment variable setting and retrieval
- ✅ Variable persistence across commands
- ✅ Variable substitution in file operations
- ✅ Integration with Python scripts
- ✅ Complex environment configurations

## Integration Features Demonstrated

All demos collectively prove:

1. **Command Interoperability**: Commands work together seamlessly
2. **Pipeline Support**: Output from one command flows to another
3. **Redirection**: File input/output redirection works properly
4. **Variable Expansion**: Environment variables expand correctly
5. **Script Execution**: Both Python and shell scripts execute properly
6. **Virtual Filesystem**: All operations work within the sandboxed environment
7. **Error Handling**: Commands handle errors gracefully
8. **Performance**: Operations complete in reasonable time
9. **Cross-Platform**: Examples work regardless of host system
10. **Security**: All operations are contained within the virtual environment

## Use Cases Demonstrated

### Development Workflows
- Setting up project structures
- Processing data files
- Analyzing log files
- Managing configuration files

### Data Processing
- CSV/log file analysis
- Text transformation pipelines
- Statistical analysis of files
- File comparison and patching

### System Administration
- Directory structure management
- File permission and metadata handling
- Environment configuration
- Script automation

### Education and Learning
- Shell command mastery
- Text processing techniques
- Scripting best practices
- Virtual environment understanding

These examples serve as both functional tests and educational resources, proving that the virtual shell provides a complete, working Unix-like environment while maintaining security and isolation.