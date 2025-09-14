# Echo Command

The `echo` command displays a line of text/arguments to the standard output.

## Usage

```bash
echo [-neE] [--help] [text] [> file | >> file]
```

## Options

- `-n` : Do not output trailing newline
- `-e` : Enable interpretation of backslash escapes
- `-E` : Disable interpretation of backslash escapes (default)
- `--help` : Display help and exit

## Redirection

Echo supports output redirection:
- `>` : Redirect output to file (overwrite)
- `>>` : Redirect output to file (append)

## Escape Sequences (with -e flag)

When the `-e` option is enabled, echo interprets the following backslash escape sequences:

### Basic Escapes
- `\n` : newline
- `\t` : horizontal tab
- `\r` : carriage return
- `\b` : backspace
- `\f` : form feed
- `\v` : vertical tab
- `\a` : alert (bell)
- `\\` : backslash
- `\"` : double quote
- `\'` : single quote

### Numeric Escapes
- `\0NNN` : character with octal value NNN (1 to 3 digits)
- `\NNN` : character with octal value NNN (1 to 3 digits)
- `\xHH` : character with hexadecimal value HH (1 to 2 digits)
- `\uHHHH` : Unicode character with hex value HHHH (4 digits)
- `\UHHHHHHHH` : Unicode character with hex value HHHHHHHH (8 digits)

## Examples

### Basic Usage
```bash
# Simple text output
echo Hello World
# Output: Hello World

# Empty output
echo
# Output: (empty)

# Multiple arguments
echo one two three
# Output: one two three
```

### Using Flags
```bash
# Suppress newline
echo -n "No newline"

# Enable escape sequences
echo -e "Line1\nLine2\tTabbed"
# Output:
# Line1
# Line2    Tabbed

# Disable escapes (default)
echo -E "Literal\ntext"
# Output: Literal\ntext

# Stop flag processing
echo -- -n -e
# Output: -n -e
```

### Redirection
```bash
# Write to file
echo "Hello" > file.txt

# Append to file
echo "World" >> file.txt

# Error: redirect to directory
echo "test" > /existing/directory
# Output: echo: cannot write to '/existing/directory': Is a directory
```

### Escape Sequences
```bash
# Newlines and tabs
echo -e "Column1\tColumn2\nRow1\tData1"
# Output:
# Column1    Column2
# Row1       Data1

# Octal escape (A = \101)
echo -e "Test\101"
# Output: TestA

# Hexadecimal escape (! = \x21)
echo -e "Test\x21"
# Output: Test!

# Unicode escape (A = \u0041)
echo -e "Test\u0041"
# Output: TestA
```

### Special Characters
```bash
# Unicode characters
echo "Hello 世界 🌍"
# Output: Hello 世界 🌍

# Special shell characters (literal)
echo '$VAR ${HOME} $(date)'
# Output: $VAR ${HOME} $(date)

# ANSI escape codes
echo -e "\033[31mRed Text\033[0m Normal"
# Output: Red Text Normal (with colors in terminal)
```

### Real-world Examples
```bash
# Create shell script header
echo "#!/bin/bash" > script.sh
echo "# Generated script" >> script.sh

# Generate CSV data
echo "Name,Age,City" > data.csv
echo "Alice,30,NYC" >> data.csv

# Create configuration file
echo "[Database]" > config.ini
echo "host=localhost" >> config.ini
echo "port=5432" >> config.ini

# Generate JSON (simple)
echo "{" > data.json
echo '  "name": "test",' >> data.json
echo '  "value": 123' >> data.json
echo "}" >> data.json
```

## Error Handling

The echo command handles several error conditions:

1. **Directory redirection**: Cannot redirect output to a directory
2. **Write failures**: Reports when file cannot be written
3. **Invalid escape sequences**: Silently ignores invalid sequences

## Implementation Notes

- The command is compatible with POSIX echo behavior
- Default behavior does not add trailing newlines (for shell compatibility)
- Escape sequence processing only occurs with `-e` flag
- The `--` marker stops flag processing, treating subsequent arguments as literal text
- Output redirection is handled before escape sequence processing
- Binary and Unicode content is preserved correctly

## Testing

The echo command includes comprehensive tests covering:
- Basic functionality with various argument types
- Flag combinations and interactions
- All supported escape sequences
- Redirection scenarios and error cases
- Edge cases with special characters and large content
- Real-world usage scenarios

## See Also

- `cat` - Display file contents
- `printf` - Format and print data (if implemented)
- Shell redirection operators