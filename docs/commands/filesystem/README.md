# Filesystem Commands

File and directory manipulation commands for managing the virtual filesystem.

## Commands Overview

### File Operations
| Command | Description | Documentation |
|---------|-------------|---------------|
| [`cat`](cat.md) | Display file contents | [cat.md](cat.md) |
| [`touch`](touch.md) | Create empty files or update timestamps | [touch.md](touch.md) |
| [`echo`](echo.md) | Display text with output redirection support | [echo.md](echo.md) |
| [`more`](more.md) | Display file contents page by page | [more.md](more.md) |

### Directory Operations
| Command | Description | Documentation |
|---------|-------------|---------------|
| [`mkdir`](mkdir.md) | Create directories | [mkdir.md](mkdir.md) |
| [`rmdir`](rmdir.md) | Remove empty directories | [rmdir.md](rmdir.md) |

### File/Directory Management
| Command | Description | Documentation |
|---------|-------------|---------------|
| [`cp`](cp.md) | Copy files and directories | [cp.md](cp.md) |
| [`mv`](mv.md) | Move/rename files and directories | [mv.md](mv.md) |
| [`rm`](rm.md) | Remove files | [rm.md](rm.md) |
| [`find`](find.md) | Search for files and directories | [find.md](find.md) |

### Storage Information
| Command | Description | Documentation |
|---------|-------------|---------------|
| [`df`](df.md) | Display filesystem disk space usage | [df.md](df.md) |
| [`du`](du.md) | Display directory space usage | [du.md](du.md) |
| [`quota`](quota.md) | Display disk usage quotas | [quota.md](quota.md) |

## Common Usage Patterns

### File Management
```bash
# Create and view files
touch newfile.txt
echo "Hello World" > newfile.txt
cat newfile.txt
more largefile.txt

# Copy and move files
cp source.txt backup.txt
mv oldname.txt newname.txt

# Remove files
rm unwanted.txt
```

### Directory Management
```bash
# Create directory structure
mkdir -p project/{src,tests,docs}

# Navigate and explore
find . -name "*.txt"
ls -la

# Remove directories
rmdir empty_directory
```

### Storage Monitoring
```bash
# Check disk usage
df -h
du -s /home/user
quota -h

# Find large files
find . -name "*.log" | du -h
```

## Key Features

- **Virtual Filesystem Integration:** All commands work with the sandboxed virtual filesystem
- **Security:** File access is restricted to the sandbox environment  
- **Redirection Support:** Commands like `echo` support output redirection
- **Cross-Platform:** Works consistently across different host systems
- **Error Handling:** Comprehensive error messages for troubleshooting

## See Also

- [Navigation Commands](../navigation/README.md) - Directory navigation and listing
- [Text Processing Commands](../text/README.md) - Text manipulation and analysis
- [Main Documentation](../../README.md) - Complete command reference