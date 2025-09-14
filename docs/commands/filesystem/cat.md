# Cat Command

The `cat` command concatenates and displays file contents.

## Usage

```bash
cat [OPTION]... [FILE]...
```

## Options

- `-n` : Number all output lines
- `-b` : Number non-blank output lines (overrides -n)
- `-s` : Squeeze multiple adjacent blank lines into single blank line
- `-E` : Display $ at end of each line
- `-T` : Display TAB characters as ^I
- `-v` : Display non-printing characters in visible format
- `--help` : Display help and exit
- `--` : End of options marker

## Arguments

- `FILE...` : One or more files to display. If no files specified, reads from stdin

## Behavior

### Basic Operation
- Concatenates and displays contents of specified files in order
- If no files are provided, reads from stdin (if available)
- Continues processing remaining files if one file is missing or inaccessible

### Error Handling
- Reports errors for non-existent files but continues with valid files
- Reports "Is a directory" error when attempting to read directories
- Returns appropriate error messages for each failed file

### Flag Interactions
- The `-b` flag overrides `-n` when both are specified
- Multiple flags can be combined (e.g., `-nE` or `-bET`)
- Line numbering continues across multiple files

## Examples

### Basic Usage
```bash
# Display single file
cat file.txt

# Concatenate multiple files
cat header.txt body.txt footer.txt

# Display with line numbers
cat -n script.sh

# Read from stdin
echo "Hello" | cat
```

### Using Flags
```bash
# Number all lines
cat -n document.txt

# Number only non-blank lines
cat -b document.txt

# Squeeze blank lines
cat -s spaced_file.txt

# Show line ends
cat -E config.txt

# Show tabs
cat -T Makefile

# Show non-printing characters
cat -v binary.dat

# Combine multiple flags
cat -nET source.py
```

### Error Handling
```bash
# Mix of valid and invalid files
cat file1.txt missing.txt file2.txt
# Shows content of file1.txt and file2.txt, reports error for missing.txt

# Attempting to cat a directory
cat /some/directory
# Output: cat: /some/directory: Is a directory
```

### Real-world Examples
```bash
# View log files with line numbers
cat -n /var/log/app.log

# Combine and view configuration files
cat defaults.conf custom.conf > combined.conf

# Check for trailing whitespace
cat -E source_file.py | grep '\s\+$'

# View Makefile with visible tabs
cat -T Makefile

# Squeeze multiple blank lines in documentation
cat -s README.md

# Debug script with line numbers and visible characters
cat -nvET debug_script.sh

# Create file from multiple parts
cat header.html content.html footer.html > page.html
```

## Implementation Features

- **Multi-file support**: Processes multiple files in sequence
- **Error recovery**: Continues processing after encountering errors
- **Line numbering**: Maintains numbering across multiple files
- **Character visibility**: Makes control and non-printing characters visible
- **Stdin support**: Reads from standard input when no files specified
- **Flag combination**: Supports combining multiple flags
- **Binary safe**: Correctly handles binary files with -v flag

## Differences from Standard cat

This implementation closely follows POSIX cat behavior with GNU extensions:
- Supports common flags like -n, -b, -s, -E, -T, -v
- Handles multiple files with proper error recovery
- Line numbering format matches standard cat output

## Testing

The cat command includes comprehensive tests covering:
- Basic file display and concatenation
- All supported flags and combinations
- Error handling for missing files and directories
- Edge cases with binary data and special characters
- Multi-file processing with mixed valid/invalid inputs
- Stdin input handling

## See Also

- `more` - Page through file content
- `head` - Display first lines of file
- `tail` - Display last lines of file
- `grep` - Search file content
- `echo` - Display text