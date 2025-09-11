# Environment Commands

Environment variable management commands for configuring and inspecting the shell's execution environment.

## Commands Overview

| Command | Description | Documentation |
|---------|-------------|---------------|
| [`env`](env.md) | Display environment variables | [env.md](env.md) |
| [`export`](export.md) | Set environment variables | [export.md](export.md) |
| [`alias`](alias.md) | Create command aliases | [alias.md](alias.md) |
| [`unalias`](unalias.md) | Remove command aliases | [unalias.md](unalias.md) |

## Common Usage Patterns

### Viewing Environment Variables
```bash
# Display all environment variables
env
# Output:
# HOME=/home/user
# PATH=/usr/bin:/bin
# USER=john
# PWD=/current/directory

# Filter environment variables
env PATH                        # Show PATH-related variables
env USER                        # Show user-related variables
env HOME                        # Show home directory variable
```

### Setting Environment Variables
```bash
# Set single variables
export USER=admin               # Set username
export HOME=/home/admin         # Set home directory
export DEBUG=true               # Enable debug mode

# Set multiple variables
export DB_HOST=localhost DB_PORT=5432 DB_NAME=myapp

# Set path variables
export PATH=/usr/local/bin:/usr/bin:/bin
export PYTHONPATH=/path/to/modules
```

### Managing Command Aliases
```bash
# Create aliases
alias ll="ls -la"               # Long listing
alias la="ls -a"                # Show hidden files
alias ..="cd .."                # Go up one directory
alias grep="grep -i"            # Case-insensitive grep by default

# View aliases
alias                           # Show all aliases
alias ll                        # Show specific alias

# Remove aliases
unalias ll                      # Remove single alias
unalias la ..                   # Remove multiple aliases
```

### Configuration Management
```bash
# Application configuration
export API_KEY=abc123def456
export DATABASE_URL=postgres://localhost/mydb
export ENVIRONMENT=development
export LOG_LEVEL=debug

# Development environment
export NODE_ENV=development
export DEBUG=*
export EDITOR=nano
export BROWSER=firefox
```

## Environment Variable Workflow

### Setup and Verification
```bash
# 1. Check current environment
env | grep -i python           # Check Python-related variables
env PATH                       # Check PATH configuration

# 2. Set required variables
export PROJECT_ROOT=/home/user/project
export CONFIG_FILE=$PROJECT_ROOT/config.yml
export LOG_DIR=$PROJECT_ROOT/logs

# 3. Verify settings
env | grep PROJECT             # Confirm variables are set
echo $PROJECT_ROOT             # Test variable expansion
```

### Conditional Configuration
```bash
# Set variables based on conditions
export ENVIRONMENT=production
if [ "$ENVIRONMENT" = "production" ]; then
    export LOG_LEVEL=warn
    export DEBUG=false
else
    export LOG_LEVEL=debug  
    export DEBUG=true
fi

# Verify configuration
env | grep -E "(LOG_LEVEL|DEBUG|ENVIRONMENT)"
```

## Common Environment Variables

### System Variables
- **HOME:** User's home directory
- **USER:** Current username  
- **PWD:** Present working directory
- **PATH:** Command search path
- **SHELL:** Current shell program

### Application Variables
- **DEBUG:** Enable/disable debug output
- **LOG_LEVEL:** Logging verbosity (debug, info, warn, error)
- **ENVIRONMENT:** Application environment (development, staging, production)
- **CONFIG_FILE:** Path to configuration file
- **DATABASE_URL:** Database connection string

### Development Variables
- **PYTHONPATH:** Python module search path
- **NODE_ENV:** Node.js environment
- **EDITOR:** Default text editor
- **BROWSER:** Default web browser
- **API_KEY:** API authentication credentials

## Advanced Usage

### Variable Expansion and References
```bash
# Reference existing variables
export PROJECT_ROOT=/home/user/myproject
export SOURCE_DIR=$PROJECT_ROOT/src
export BUILD_DIR=$PROJECT_ROOT/build
export LOG_FILE=$PROJECT_ROOT/logs/app.log

# Verify expansion
env | grep PROJECT
echo "Source directory: $SOURCE_DIR"
```

### Advanced Alias Usage
```bash
# Nested aliases
alias ll="ls -la"
alias myls="ll"                # Alias referring to another alias

# Complex command aliases
alias backup="cp -r /important /backup/$(date +%Y%m%d)"
alias clean="rm -f *.tmp *.log"
alias reload="export PATH=$PATH && source ~/.shellrc"

# Development shortcuts
alias gst="git status"
alias gc="git commit"
alias gp="git push"
alias py="python"
alias pip="python -m pip"

# Safety aliases
alias rm="rm -i"                # Interactive removal
alias cp="cp -i"                # Interactive copy
alias mv="mv -i"                # Interactive move
```

### Batch Configuration
```bash
# Set related variables together
export DB_HOST=localhost \
       DB_PORT=5432 \
       DB_NAME=myapp \
       DB_USER=admin \
       DB_PASSWORD=secret123

# Application suite configuration
export APP_NAME=myservice
export APP_VERSION=1.2.3
export APP_PORT=8080
export APP_HOST=0.0.0.0
export APP_CONFIG=/etc/$APP_NAME/config.yml
```

### Environment Debugging
```bash
# Debug environment issues
env | wc -l                    # Count total variables
env | grep -c "^PATH"          # Check if PATH is set
env | sort                     # Alphabetical variable list
env | grep -v "^_"            # Hide internal variables
```

## Integration with Other Commands

### With System Commands
```bash
# Show user and environment info
whoami                         # Current user
env USER                       # USER environment variable
python -c "import os; print(f'User: {os.environ.get(\"USER\")}')"
```

### With Script Execution  
```bash
# Configure before running scripts
export API_ENDPOINT=https://api.example.com
export API_TOKEN=secret123
python api_client.py           # Script uses environment variables

# Shell script configuration
export LOG_LEVEL=debug
sh deployment.sh               # Script inherits environment
```

### With Filesystem Commands
```bash
# Use environment in file operations
export BACKUP_DIR=/tmp/backups
mkdir -p $BACKUP_DIR           # Create directory from variable
cp important.txt $BACKUP_DIR/  # Copy using environment path
ls $BACKUP_DIR                 # List backup directory
```

## Key Features

- **Session Persistence:** Variables and aliases persist for entire shell session
- **Inheritance:** Child processes inherit environment variables
- **Variable Expansion:** Support for referencing existing variables
- **Flexible Assignment:** Multiple variables can be set in single command
- **Filtering:** View specific variables with pattern matching
- **Command Aliases:** Create shortcuts and custom commands
- **Alias Expansion:** Aliases can reference other aliases
- **.shellrc Support:** Load environment and aliases from configuration file

## Best Practices

1. **Use descriptive names:** Choose clear, meaningful variable names
2. **Group related variables:** Set related configuration together
3. **Document variables:** Comment complex environment setups
4. **Verify settings:** Always check variable values after setting
5. **Use consistent naming:** Follow naming conventions (UPPER_CASE for environment variables)

## Security Considerations

- **Sensitive data:** Be careful with passwords and API keys in environment
- **Variable scope:** Environment variables are visible to all processes
- **Session lifetime:** Variables are lost when shell exits
- **Logging:** Environment variables may appear in logs and process lists

## See Also

- [System Commands](../system/README.md) - Commands that use environment variables
- [Filesystem Commands](../filesystem/README.md) - File operations with environment paths  
- [Script execution](../system/python.md) - Python scripts using environment variables
- [Main Documentation](../../README.md) - Complete command reference