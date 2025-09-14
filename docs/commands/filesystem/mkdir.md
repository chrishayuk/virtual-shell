# Mkdir Command

The `mkdir` command creates directories.

## Usage

```bash
mkdir [-p] DIRECTORY...
```

## Options

- `-p` : Create parent directories as needed (no error if existing)

## Arguments

- `DIRECTORY...` : One or more directories to create

## Behavior

### Basic Operation
- Creates specified directories in the filesystem
- Returns empty string on success
- Returns error message if directory creation fails
- Processes each directory argument in order

### Parent Directory Creation
- With `-p` flag, creates all necessary parent directories
- Without `-p` flag, fails if parent directory doesn't exist
- No error reported if directory already exists when using `-p`

### Path Resolution
- Handles both absolute and relative paths
- Resolves relative paths from current working directory
- Normalizes paths by removing trailing slashes

## Examples

### Basic Usage
```bash
# Create single directory
mkdir mydir

# Create multiple directories
mkdir dir1 dir2 dir3

# Create directory in specific path
mkdir /path/to/newdir
```

### Using -p Flag
```bash
# Create nested directories
mkdir -p /path/to/nested/dir

# Create directory tree
mkdir -p project/src/components project/tests project/docs

# No error if directory exists
mkdir -p existing_dir

# Create deep directory structure
mkdir -p /var/log/myapp/2024/01
```

### Error Cases
```bash
# Directory already exists (without -p)
mkdir existing_dir
# Output: mkdir: cannot create directory 'existing_dir'

# Parent doesn't exist (without -p)
mkdir /nonexistent/newdir
# Output: mkdir: cannot create directory '/nonexistent/newdir'

# No arguments provided
mkdir
# Output: mkdir: missing operand
```

### Real-world Examples
```bash
# Create project structure
mkdir -p myproject/src myproject/tests myproject/docs myproject/build

# Create date-based backup directory
mkdir -p /backups/2024/01/15

# Create user directories
mkdir -p /home/user/Documents /home/user/Downloads /home/user/Pictures

# Create nested config directories
mkdir -p /etc/myapp/conf.d

# Setup development environment
mkdir -p ~/dev/python/projects ~/dev/javascript/projects ~/dev/go/projects

# Create temporary work directory
mkdir -p /tmp/build-$(date +%s)

# Create versioned release directory
mkdir -p releases/v1.2.3/{bin,lib,doc}
```

## Implementation Features

- **Recursive creation**: Creates parent directories with `-p` flag
- **Multiple directory support**: Creates multiple directories in one command
- **Path resolution**: Handles both absolute and relative paths
- **Error recovery**: Continues creating remaining directories after error
- **Idempotent with -p**: Safe to run multiple times with `-p` flag
- **Atomic operations**: Each directory creation is a separate operation

## Error Handling

- Reports "missing operand" if no directories specified
- Reports "cannot create directory" for creation failures
- Without `-p`, fails if directory already exists
- Without `-p`, fails if parent directory doesn't exist
- Continues processing remaining arguments after individual failures

## Testing

The mkdir command includes tests covering:
- Basic directory creation
- Multiple directory creation
- Parent directory creation with `-p` flag
- Error handling for existing directories
- Missing operand error handling
- Path resolution and normalization
- Interaction with virtual filesystem

## See Also

- `rmdir` - Remove empty directories
- `rm -r` - Remove directories and contents
- `ls` - List directory contents
- `cd` - Change directory
- `pwd` - Print working directory
- `tree` - Display directory structure