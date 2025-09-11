# Chuk Virtual Shell - Command Documentation

This directory contains comprehensive documentation for all commands available in the Chuk Virtual Shell.

## Command Categories

### Filesystem Commands (`/commands/filesystem/`)
File and directory manipulation commands:
- `cat` - Display file contents
- `cp` - Copy files and directories  
- `df` - Display filesystem disk space usage
- `du` - Display directory space usage
- `echo` - Display text
- `find` - Search for files and directories
- `mkdir` - Create directories
- `more` - Display file contents page by page
- `mv` - Move/rename files and directories
- `quota` - Display disk usage quotas
- `rm` - Remove files
- `rmdir` - Remove directories
- `touch` - Create empty files or update timestamps

### Navigation Commands (`/commands/navigation/`)
Directory navigation and listing:
- `cd` - Change directory
- `ls` - List directory contents  
- `pwd` - Print working directory

### Text Processing Commands (`/commands/text/`)
Text manipulation and analysis:
- `awk` - Pattern scanning and processing
- `diff` - Compare files line by line
- `grep` - Search text patterns in files
- `head` - Display first lines of files
- `patch` - Apply difference patches to files
- `sed` - Stream editor for text transformation
- `sort` - Sort lines in text files
- `tail` - Display last lines of files
- `uniq` - Report or omit repeated lines
- `wc` - Word, line, character, and byte count

### System Commands (`/commands/system/`)
System operations and utilities:
- `clear` - Clear terminal screen
- `exit` - Exit shell
- `help` - Display help information
- `python` - Execute Python code
- `script` - Execute shell scripts
- `sh` - Execute shell commands
- `time` - Time command execution
- `uptime` - Display system uptime
- `whoami` - Display current user

### Environment Commands (`/commands/environment/`)
Environment variable management:
- `env` - Display environment variables
- `export` - Set environment variables

### MCP Commands (`/commands/mcp/`)
Model Context Protocol integration:
- Dynamic MCP command loading and execution

## Usage

Each command documentation includes:
- Description and purpose
- Syntax and usage patterns
- Available options and flags
- Practical examples
- See also references to related commands

## Command Structure

All commands inherit from `ShellCommand` base class and implement:
- `name` - Command identifier
- `help_text` - Built-in help documentation
- `category` - Command categorization
- `execute(args)` - Main command logic