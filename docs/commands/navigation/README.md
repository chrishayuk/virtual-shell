# Navigation Commands

Essential commands for navigating and exploring the virtual filesystem directory structure.

## Commands Overview

| Command | Description | Documentation |
|---------|-------------|---------------|
| [`cd`](cd.md) | Change the current working directory | [cd.md](cd.md) |
| [`ls`](ls.md) | List directory contents | [ls.md](ls.md) |
| [`pwd`](pwd.md) | Print the current working directory | [pwd.md](pwd.md) |
| [`tree`](tree.md) | Display directory tree structure | [tree.md](tree.md) |

## Common Usage Patterns

### Basic Navigation
```bash
# Check current location
pwd
# Output: /home/user

# List current directory contents
ls
ls -la                          # Long format with hidden files

# Change directories
cd /tmp                         # Absolute path
cd ../other                     # Relative path  
cd ~                            # Home directory
cd                              # Home directory (default)
```

### Directory Exploration
```bash
# Explore directory structure
pwd && ls -la                  # Show location and contents
cd subdir && pwd && ls          # Move and explore
cd .. && ls                     # Go up and list

# Visualize directory tree
tree                            # Show current directory tree
tree /home                      # Show specific directory tree
tree -L 2                       # Limit depth to 2 levels
tree -d                         # Show directories only
tree -a                         # Include hidden files

# Navigate with verification
cd /var/log || echo "Directory not found"
pwd                             # Confirm location
```

### Navigation Workflow
```bash
# Typical navigation session
pwd                             # Where am I?
ls                              # What's here?
cd important_folder             # Move to work area
ls -l                           # See details
cd ..                           # Go back up
```

## Command Details

### [`cd`](cd.md) - Change Directory
- Changes shell's current working directory
- Updates PWD environment variable
- Supports absolute and relative paths
- Defaults to HOME directory if no argument provided
- Restricted to sandbox boundaries

### [`ls`](ls.md) - List Contents  
- Lists files and directories in specified location
- Supports long format (`-l`) and hidden files (`-a`)
- Shows file permissions, sizes, and timestamps
- Sorts output alphabetically
- Handles both files and directories

### [`pwd`](pwd.md) - Print Working Directory
- Displays absolute path of current directory
- No options or arguments needed
- Always returns full path from root
- Essential for understanding current location

### [`tree`](tree.md) - Display Directory Tree
- Shows hierarchical directory structure
- Supports depth limiting with `-L` option
- Can show directories only with `-d`
- Includes hidden files with `-a`
- Visual representation helps understand structure

## Key Features

- **Sandbox Security:** Navigation is restricted to the virtual filesystem
- **Path Resolution:** Supports both absolute (`/path/to/dir`) and relative (`../dir`) paths
- **Environment Integration:** Commands update and use shell environment variables
- **Error Handling:** Clear error messages for invalid paths or permissions
- **Cross-Platform:** Consistent behavior across different host systems

## Integration with Other Commands

### With Filesystem Commands
```bash
pwd                             # Check location
ls                              # See what's available
mkdir new_project               # Create directory
cd new_project                  # Enter directory
touch README.md                 # Create file
ls -l                           # Verify creation
```

### With Text Processing
```bash
cd logs                         # Navigate to logs
ls *.log                        # List log files
cat error.log | head -10        # View recent errors
grep ERROR *.log                # Search all logs
```

### With Environment
```bash
echo $PWD                       # Show current directory
cd /tmp                         # Change location  
echo $PWD                       # Verify PWD updated
env | grep PWD                  # Check environment
```

## Best Practices

1. **Always verify location:** Use `pwd` to confirm your position
2. **List before acting:** Use `ls` to see directory contents before operations
3. **Use relative paths:** More flexible than absolute paths when possible
4. **Check permissions:** Use `ls -l` to see file permissions and ownership
5. **Navigate systematically:** Build familiarity with directory structure

## See Also

- [Filesystem Commands](../filesystem/README.md) - File and directory manipulation
- [System Commands](../system/README.md) - Shell control and system information
- [Main Documentation](../../README.md) - Complete command reference