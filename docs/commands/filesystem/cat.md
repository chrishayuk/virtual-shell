# cat

Display file contents to standard output.

## Synopsis

```
cat [file]...
```

## Description

The `cat` command reads files and displays their contents to standard output. When called without arguments, it reads from standard input if available (useful in pipelines).

## Arguments

- `file` - One or more files to display. If no files are specified, reads from standard input.

## Examples

**Display a single file:**
```bash
cat myfile.txt
```

**Display multiple files (concatenated):**
```bash
cat file1.txt file2.txt file3.txt
```

**Read from standard input (in pipelines):**
```bash
echo "Hello World" | cat
```

## Error Handling

- Returns "cat: missing operand" if no arguments and no stdin available
- Returns "cat: {filename}: No such file" if a specified file doesn't exist

## Implementation Notes

- Files are read using the virtual filesystem's `read_file()` method
- Multiple files are concatenated without separators
- Supports stdin input through the shell's `_stdin_buffer`

## See Also

- [`more`](more.md) - Display file contents page by page
- [`head`](../text/head.md) - Display first lines of files
- [`tail`](../text/tail.md) - Display last lines of files