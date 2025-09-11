# tree

## Synopsis
```bash
tree [options] [directory ...]
```

## Description
The `tree` command displays the contents of directories in a tree-like format, showing the hierarchical structure with indentation and tree branch characters.

## Options
- `-a` - Show all files including hidden files (starting with .)
- `-d` - List directories only
- `-f` - Print the full path prefix for each file
- `-L level` - Descend only level directories deep
- `-I pattern` - Do not list files that match the given pattern
- `--dirsfirst` - List directories before files

## Arguments
- `directory` - One or more directories to display (defaults to current directory)

## Examples

### Basic Usage
```bash
# Display current directory tree
$ tree
.
├── src
│   ├── main.py
│   └── utils.py
├── tests
│   └── test_main.py
└── README.md

2 directories, 4 files

# Display specific directory
$ tree /home/user/project
/home/user/project
├── docs
│   ├── api.md
│   └── guide.md
├── src
│   └── app.py
└── setup.py

2 directories, 4 files
```

### Filter Options
```bash
# Show only directories
$ tree -d
.
├── src
├── tests
└── docs

3 directories

# Include hidden files
$ tree -a
.
├── .gitignore
├── .env
├── src
│   └── main.py
└── README.md

1 directory, 4 files

# Exclude pattern
$ tree -I "*.pyc"
.
├── src
│   ├── main.py
│   └── utils.py
└── tests
    └── test_main.py

2 directories, 3 files
```

### Depth Control
```bash
# Limit to 2 levels deep
$ tree -L 2
.
├── project
│   ├── src
│   ├── tests
│   └── docs
└── README.md

4 directories, 1 file

# Full paths
$ tree -f
/home/user
├── /home/user/project
│   ├── /home/user/project/main.py
│   └── /home/user/project/utils.py
└── /home/user/README.md

1 directory, 3 files
```

### Sorting
```bash
# Directories first
$ tree --dirsfirst
.
├── docs
│   └── guide.md
├── src
│   └── main.py
├── README.md
└── setup.py

2 directories, 4 files
```

## Output Format
The tree uses ASCII characters to draw the structure:
- `├──` - Regular branch
- `└──` - Last item in directory
- `│` - Vertical continuation line

## Exit Status
- `0` - Success
- `1` - Error (invalid directory, permission denied, etc.)

## See Also
- [`ls`](ls.md) - List directory contents
- [`find`](../filesystem/find.md) - Search for files and directories
- [`du`](../filesystem/du.md) - Display disk usage

## Implementation Notes
- Symlinks are not followed to prevent infinite recursion
- Pattern matching uses shell-style wildcards (fnmatch)
- Hidden directories are also excluded when not using `-a`
- Summary line shows total directories and files found

## Differences from Unix tree
- No color output support
- No file size or permission display
- No date/time information
- Simplified pattern matching
- No XML/JSON/HTML output formats