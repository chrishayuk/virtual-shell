# more

Display file contents page by page.

## Synopsis

```
more file...
```

## Description

The `more` command displays file contents one page at a time, making it easier to read large files. It automatically determines the terminal size and paginates content accordingly.

## Arguments

- `file...` - One or more files to display

## Examples

**Display a single file with paging:**
```bash
more largefile.txt
```

**Display multiple files:**
```bash
more file1.txt file2.txt file3.txt
```

**View system files:**
```bash
more /var/log/system.log
```

## Behavior

- Automatically detects terminal size (default 80x24 if unavailable)
- Uses terminal height minus 2 lines for page size
- Shows file headers when displaying multiple files
- Displays progress percentage at page breaks
- Non-interactive paging (continues automatically)

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

## Error Handling

- "more: missing operand" - No file arguments provided
- "more: filename: No such file" - Specified file doesn't exist

## Implementation Notes

- Uses `shutil.get_terminal_size()` to determine page dimensions
- Splits content into lines for pagination
- Calculates percentage completion for progress display
- Simplified implementation without interactive controls
- Processes all files sequentially without user input

## Differences from Standard `more`

This implementation differs from standard Unix `more`:
- No interactive navigation (space, enter, q, etc.)
- Automatic continuation without user input
- No search functionality (`/pattern`)
- No help system (`h` command)
- No line-by-line navigation

## See Also

- [`cat`](cat.md) - Display entire file contents
- [`head`](../text/head.md) - Display first lines of files
- [`tail`](../text/tail.md) - Display last lines of files
- [`less`] - More advanced pager (if available)