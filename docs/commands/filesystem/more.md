# more

Display file contents page by page with comprehensive Unix-style options.

## Synopsis

```
more [options] [file...]
more [-dlfpcsu] [-n lines] [-NUM] [+NUM] [+/PATTERN] file...
```

## Description

The `more` command displays file contents one page at a time, making it easier to read large files. It automatically determines the terminal size and paginates content accordingly. This implementation supports most standard Unix `more` options.

## Options

### Display Options

- `-d, --silent` - Prompt with helpful messages like "[Press space to continue, 'q' to quit]"
- `-l, --logical` - Do not pause after form feed characters (^L)
- `-f, --no-pause` - Count logical lines rather than screen lines
- `-p, --print-over` - Clear screen before displaying each page
- `-c, --clean-print` - Paint each screen from top, clearing remainder of lines
- `-s, --squeeze` - Squeeze multiple blank lines into one
- `-u, --plain` - Suppress underlining (for compatibility)

### Page Control

- `-n, --lines NUM` - Set lines per screenful to NUM
- `-NUM` - Same as `--lines NUM` (e.g., `-10` for 10 lines per page)
- `+NUM` - Start display at line NUM
- `+/PATTERN` - Start at first occurrence of PATTERN

### Information

- `--help` - Display help and exit
- `--version` - Display version and exit

## Arguments

- `file...` - One or more files to display. If no files specified, reads from standard input

## Interactive Commands

While the current implementation is non-interactive, these commands are documented for completeness:

- `SPACE` - Display next page
- `RETURN` - Display next line
- `q` - Quit
- `/PATTERN` - Search for pattern
- `=` - Show current line number
- `h` - Show help

## Examples

**Display a single file with default paging:**
```bash
more largefile.txt
```

**Display with 10 lines per page:**
```bash
more -10 document.txt
# or
more -n 10 document.txt
```

**Start at line 50:**
```bash
more +50 logfile.log
```

**Start at first occurrence of "ERROR":**
```bash
more +/ERROR debug.log
```

**Squeeze multiple blank lines:**
```bash
more -s config.txt
```

**Clear screen before each page:**
```bash
more -p presentation.txt
```

**Multiple files with headers:**
```bash
more file1.txt file2.txt file3.txt
```

**Combine options:**
```bash
more -s -20 +/WARNING system.log
```

**Read from stdin:**
```bash
cat longfile.txt | more
```

## Behavior

- Automatically detects terminal size (default 80x24 if unavailable)
- Uses terminal height minus 2 lines for page size by default
- Shows file headers when displaying multiple files (`:::::::::::::`)
- Displays progress percentage at page breaks (`--More--(25%)`)
- Non-interactive paging (continues automatically through entire file)
- Supports pattern searching with regular expressions
- Can squeeze consecutive blank lines
- Handles binary content gracefully
- Processes unicode and special characters

## Output Format

**Single file:**
```
[file contents page 1]
--More--(25%)
[file contents page 2]
--More--(50%)
...
```

**Multiple files:**
```
::::::::::::::
filename1.txt
::::::::::::::
[file contents]

::::::::::::::
filename2.txt
::::::::::::::
[file contents]
```

**With -d (silent) option:**
```
[file contents]
--More--(25%) [Press space to continue, 'q' to quit]
```

## Error Handling

- `"more: missing operand"` - No file arguments provided and no stdin
- `"more: filename: No such file or directory"` - Specified file doesn't exist
- `"more: filename: Is a directory"` - Attempted to display a directory
- `"more: filename: Cannot read file"` - File exists but cannot be read
- `"more: invalid number of lines: value"` - Invalid number for -n option

## Special Features

### Pattern Searching
The `+/PATTERN` option uses regular expressions to find the starting position:
```bash
more +/[Ee]rror logfile.txt  # Start at first line containing Error or error
```

### Blank Line Squeezing
The `-s` option reduces readability issues with excessive blank lines:
```bash
more -s formatted_document.txt  # Multiple blank lines become single blanks
```

### Custom Page Sizes
Useful for specific terminal sizes or presentation needs:
```bash
more -5 slides.txt  # Show 5 lines at a time for presentations
```

## Implementation Notes

- Uses `shutil.get_terminal_size()` to determine page dimensions
- Pattern matching uses Python's `re` module
- Handles file I/O through virtual filesystem abstraction
- Processes all content non-interactively
- Supports reading from stdin via `_stdin_buffer`

## Differences from Standard Unix `more`

This implementation differs from standard Unix `more`:
- Non-interactive (no keyboard navigation during display)
- Automatic continuation without user input
- No in-page search (only start position search)
- No line-by-line navigation
- No ability to skip forward/backward
- Shows entire file content with pagination markers

## See Also

- [`cat`](cat.md) - Display entire file contents without pagination
- [`head`](../text/head.md) - Display first lines of files
- [`tail`](../text/tail.md) - Display last lines of files
- [`less`] - More advanced pager with backward navigation (if available)
- [`grep`](../text/grep.md) - Search file contents for patterns