# echo

Display text and support output redirection.

## Synopsis

```
echo [text]... [> file | >> file]
```

## Description

The `echo` command displays its arguments separated by spaces. It supports output redirection to write text directly to files, making it useful for creating simple text files or appending content.

## Arguments

- `text...` - Text to display or write to file

## Redirection

- `> file` - Redirect output to file (overwrite)
- `>> file` - Redirect output to file (append)

## Examples

**Display text to console:**
```bash
echo Hello World
# Output: Hello World
```

**Create a file with content:**
```bash
echo "This is content" > myfile.txt
```

**Append to a file:**
```bash
echo "Additional line" >> myfile.txt
```

**Create empty output:**
```bash
echo
# Output: (empty line)
```

**Echo without arguments:**
```bash
echo
# Output: (nothing)
```

## Behavior

- Joins all arguments with single spaces
- If no arguments, returns empty string
- Supports both overwrite (`>`) and append (`>>`) redirection
- For append mode, reads existing file content and concatenates new text
- When redirecting, returns empty string (no console output)

## Error Handling

- "echo: cannot write to 'filename'" - Failed to write to specified file during redirection

## Implementation Notes

- Handles redirection by parsing `>` and `>>` tokens in arguments
- For append mode, reads current file content before writing
- Uses virtual filesystem's `read_file()` and `write_file()` methods
- Returns empty string when output is redirected to file

## See Also

- [`cat`](cat.md) - Display file contents
- [`touch`](touch.md) - Create empty files
- [`grep`](../text/grep.md) - Search text patterns
- [Text redirection](../../README.md#redirection) - More about I/O redirection