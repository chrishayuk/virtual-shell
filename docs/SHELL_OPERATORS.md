# Shell Operators and Expansions

This document describes the bash-compatible operators and expansions supported by Chuk Virtual Shell.

## Command Chaining Operators

### && (AND Operator)
Executes the next command only if the previous command succeeds (returns exit code 0).

**Syntax:** `command1 && command2`

**Examples:**
```bash
mkdir /tmp && cd /tmp         # cd only runs if mkdir succeeds
touch file.txt && echo "File created"
grep "pattern" file.txt && echo "Pattern found"
```

### || (OR Operator)
Executes the next command only if the previous command fails (returns non-zero exit code).

**Syntax:** `command1 || command2`

**Examples:**
```bash
cd /nonexistent || echo "Directory not found"
grep "error" log.txt || echo "No errors found"
rm file.txt || echo "Could not remove file"
```

### ; (Semicolon Separator)
Executes commands sequentially, regardless of success or failure.

**Syntax:** `command1; command2; command3`

**Examples:**
```bash
echo "Starting"; ls; echo "Done"
cd /tmp; touch test.txt; ls
export VAR=value; echo $VAR; unset VAR
```

### Combining Operators
You can combine multiple operators for complex command flows:

```bash
cd /tmp && touch file.txt || echo "Failed" ; echo "Done"
mkdir dir && cd dir && echo "In new directory" || echo "Failed to create/enter"
```

## Variable Expansion

### Basic Variable Expansion
Use `$VARNAME` to expand environment variables.

**Syntax:** `$VARNAME`

**Examples:**
```bash
export NAME="World"
echo "Hello $NAME"            # Output: Hello World
echo $HOME                    # Output: /home/user
cd $HOME/documents
```

### Braced Variable Expansion
Use `${VARNAME}` when you need to clearly delimit the variable name.

**Syntax:** `${VARNAME}`

**Examples:**
```bash
export PREFIX="test"
echo "${PREFIX}ing"           # Output: testing
echo "${PREFIX}_file.txt"     # Output: test_file.txt
mkdir "${HOME}/projects"
```

### Special Variables
The shell provides several special variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `$?` | Exit code of last command | `echo $?` after a command |
| `$$` | Process ID of the shell | `echo $$` |
| `$#` | Number of arguments | `echo $#` |
| `$PWD` | Current working directory | `echo $PWD` |
| `$HOME` | Home directory | `cd $HOME` |
| `$OLDPWD` | Previous working directory | `echo $OLDPWD` |

**Examples:**
```bash
ls /nonexistent
echo "Exit code: $?"          # Output: Exit code: 1

cd /tmp
cd /home
echo "Was in: $OLDPWD"        # Output: Was in: /tmp
```

### Variable Expansion Rules
- Undefined variables expand to empty string (bash-compatible)
- Single lowercase letters like `$d` are preserved (for commands like sed)
- Variables in single quotes are NOT expanded
- Variables in double quotes ARE expanded

```bash
export VAR="value"
echo "$VAR"                   # Output: value
echo '$VAR'                   # Output: $VAR
echo "$UNDEFINED"              # Output: (empty)
sed "$d" file.txt             # $d preserved for sed
```

## Wildcard/Glob Expansion

### * (Asterisk)
Matches zero or more characters.

**Examples:**
```bash
ls *.txt                      # List all .txt files
rm /tmp/*.log                 # Remove all log files in /tmp
cp *.py /backup/              # Copy all Python files
grep "error" *.log            # Search in all log files
```

### ? (Question Mark)
Matches exactly one character.

**Examples:**
```bash
ls test?.txt                  # Matches test1.txt, test2.txt, etc.
rm file?.tmp                  # Removes file1.tmp, file2.tmp, etc.
cp doc?.pdf /archive/         # Copy doc1.pdf, doc2.pdf, etc.
```

### Glob Expansion Rules
- Patterns are expanded before command execution
- If no matches found, the pattern is passed literally
- Works with all commands that accept file arguments
- Patterns can be combined: `test*.p?` matches test1.py, test2.pl, etc.

## Command Substitution

### Modern Syntax: $()
Replaces the command with its output.

**Syntax:** `$(command)`

**Examples:**
```bash
echo "Current time: $(date)"
export FILES=$(ls | wc -l)
cd $(cat /tmp/target_dir.txt)
echo "You are in $(pwd)"

# Nested substitution
echo "File count: $(ls $(pwd) | wc -l)"
```

### Legacy Syntax: Backticks
Alternative syntax using backticks (maintained for compatibility).

**Syntax:** `` `command` ``

**Examples:**
```bash
echo "User: `whoami`"
FILES=`ls *.txt`
cd `pwd`/../other_dir
echo "Date: `date`"
```

### Command Substitution Rules
- Trailing newlines are removed from the output
- The output is treated as a single argument unless word splitting occurs
- Can be nested (easier with `$()` syntax)
- Works in variable assignments and command arguments

## Path Expansion

### Tilde Expansion (~)
The tilde character expands to the home directory.

**Examples:**
```bash
cd ~                          # Go to home directory
ls ~/documents                # List documents in home
cp file.txt ~/backup/         # Copy to backup in home
echo ~                        # Output: /home/user
```

### Tilde with Path
Combines tilde with a path.

**Examples:**
```bash
cd ~/projects/myapp
mkdir ~/temp
touch ~/notes.txt
ls ~/.*                       # List hidden files in home
```

### Previous Directory (cd -)
The `cd -` command returns to the previous directory.

**Examples:**
```bash
cd /tmp
cd /home
cd -                          # Returns to /tmp
pwd                           # Output: /tmp

# OLDPWD variable tracks previous directory
echo $OLDPWD                  # Output: /home
```

## Operator Precedence and Evaluation

### Order of Expansions
The shell performs expansions in this order:
1. Command substitution (`$()` and backticks)
2. Variable expansion (`$VAR`)
3. Glob expansion (`*`, `?`)
4. Tilde expansion (`~`)

### Quoting Rules
- **Single quotes** preserve literal values (no expansions)
- **Double quotes** allow variable and command substitution
- **No quotes** allow all expansions including glob patterns

```bash
export VAR="test"
echo '$VAR *.txt'             # Output: $VAR *.txt
echo "$VAR *.txt"             # Output: test *.txt
echo $VAR *.txt               # Output: test file1.txt file2.txt ...
```

## Practical Examples

### Complex Command Chains
```bash
# Build and test workflow
mkdir build && cd build && cmake .. && make && ./test || echo "Build failed"

# Backup with verification
cp important.txt backup.txt && echo "Backup created" || echo "Backup failed"

# Conditional execution based on file existence
ls config.txt && source config.txt || echo "No config file"
```

### Variable-Based Operations
```bash
# Dynamic paths
export PROJECT_DIR="/home/user/myproject"
cd $PROJECT_DIR && ls
cp *.py $PROJECT_DIR/backup/

# Build paths with variables
export VERSION="1.0"
mkdir -p "releases/v${VERSION}"
tar -czf "app-${VERSION}.tar.gz" src/
```

### Pattern Matching Workflows
```bash
# Process all log files
for file in *.log; do
    grep "ERROR" $file && echo "Errors in $file"
done

# Clean temporary files
rm -f *.tmp *.bak *~

# Copy specific file patterns
cp test[0-9].txt /archive/
```

### Command Substitution in Scripts
```bash
# Set variables from command output
export DATE=$(date +%Y%m%d)
export BACKUP_DIR="/backup/$DATE"
mkdir -p $BACKUP_DIR

# Use command output in conditions
if [ $(ls *.txt | wc -l) -gt 0 ]; then
    echo "Text files found"
fi

# Dynamic file operations
tar -czf "backup-$(date +%Y%m%d).tar.gz" $(find . -name "*.py")
```

## Limitations and Differences from Bash

While the shell aims for bash compatibility, some differences exist:

1. **No Background Execution**: The `&` operator is not supported
2. **No Job Control**: Commands like `jobs`, `fg`, `bg` are not available
3. **No Process Substitution**: `<()` and `>()` are not supported
4. **Limited Special Variables**: Not all bash special variables are implemented
5. **No Brace Expansion**: `{1..10}` or `{a,b,c}` patterns are not supported

## Testing Shell Features

You can test these features using the provided example script:

```bash
# Run the demo script
python -m chuk_virtual_shell.main examples/new_shell_features.sh

# Or interactively
virtual-shell
> export NAME="Test"
> echo "Hello $NAME" && echo "Success" || echo "Failed"
> ls *.txt | grep test
> cd $(echo "/tmp")
```

## Implementation Notes

- Variable expansion preserves undefined variables as empty strings (bash-compatible)
- Single lowercase letters following `$` are preserved for commands like `sed "$d"`
- Empty arguments are preserved through all expansion phases
- Aliases defined in `.shellrc` store literal strings for later expansion
- All expansions respect proper quoting rules