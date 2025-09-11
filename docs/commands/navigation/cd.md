# cd

Change the current working directory.

## Synopsis

```
cd [directory]
```

## Description

The `cd` command changes the shell's current working directory to the specified directory. If no directory is provided, it changes to the user's home directory.

## Arguments

- `directory` - Directory to change to (optional, defaults to HOME directory)

## Examples

**Change to home directory:**
```bash
cd
# or explicitly
cd ~
cd $HOME
```

**Change to specific directory:**
```bash
cd /tmp
cd /home/user/projects
```

**Use relative paths:**
```bash
cd ..          # Parent directory
cd ../other    # Sibling directory  
cd ./subdir    # Subdirectory
```

**Navigate with path resolution:**
```bash
cd ~/Documents
cd /var/log
```

## Behavior

- Updates the shell's current working directory
- Updates the `PWD` environment variable
- Restricts access to directories within the sandbox
- Uses HOME environment variable as default destination
- Performs security checks through the filesystem layer

## Path Resolution

The command accepts various path formats:
- **Absolute paths:** `/home/user/documents`
- **Relative paths:** `../parent`, `./current`, `subdir`
- **Home directory:** `~` or `$HOME`
- **Special directories:** `.` (current), `..` (parent)

## Error Handling

- "cd: directory: No such directory" - Specified directory doesn't exist or is inaccessible
- Returns empty string on successful directory change

## Security

- All directory changes are validated by the filesystem layer
- Access is restricted to the sandbox environment
- Path traversal attempts are handled by the security wrapper

## Implementation Notes

- Uses the filesystem's `cd()` method for directory changes
- Updates shell environment variable `PWD` after successful change
- Argument parsing handles optional directory parameter
- Falls back to HOME environment variable when no argument provided

## Environment Variables

- **PWD** - Updated to reflect current working directory after successful change
- **HOME** - Used as default destination when no directory specified

## See Also

- [`pwd`](pwd.md) - Print current working directory
- [`ls`](ls.md) - List directory contents
- [`mkdir`](../filesystem/mkdir.md) - Create directories
- [`find`](../filesystem/find.md) - Find files and directories