# Shell Quoting and Escaping Guide

## Overview

The Chuk Virtual Shell supports comprehensive quoting and escaping mechanisms to handle special characters, spaces, and literal values. This guide covers all supported quoting methods and their behavior.

## Types of Quotes

### Single Quotes (`'`)

Single quotes preserve the literal value of all characters within them. No expansions or substitutions occur inside single quotes.

```bash
# Preserves all characters literally
echo 'Hello $USER'          # Output: Hello $USER
echo 'Path: $PATH'          # Output: Path: $PATH
echo 'Tab:\tNewline:\n'     # Output: Tab:\tNewline:\n

# Spaces are preserved
echo 'multiple    spaces'   # Output: multiple    spaces

# Special characters are literal
echo '* ? [ ] { }'         # Output: * ? [ ] { }
```

**Important:** You cannot include a single quote inside single quotes, even with escaping.

### Double Quotes (`"`)

Double quotes preserve literal values but allow certain expansions:
- Variable expansion (`$VAR`, `${VAR}`)
- Command substitution (`$(command)`, `` `command` ``)
- Arithmetic expansion (`$((expression))`)
- Escape sequences (`\`, `\"`, `\$`, `\n`, `\t`)

```bash
# Variable expansion works
USER="alice"
echo "Hello $USER"          # Output: Hello alice
echo "Home: ${HOME}"        # Output: Home: /home/user

# Command substitution works
echo "Date: $(date)"        # Output: Date: [current date]
echo "Files: `ls | wc -l`"  # Output: Files: [number]

# Escape sequences
echo "Line 1\nLine 2"       # Output: Line 1
                           #         Line 2
echo "Tab\tseparated"       # Output: Tab    separated
echo "Quote: \"text\""      # Output: Quote: "text"
echo "Dollar: \$100"        # Output: Dollar: $100

# Spaces are preserved
echo "multiple    spaces"   # Output: multiple    spaces

# Globs don't expand
echo "*.txt"                # Output: *.txt
```

### Backslash Escaping (`\`)

The backslash escapes the next character, preventing its special interpretation.

```bash
# Escape special characters
echo \$HOME                 # Output: $HOME
echo \*                     # Output: *
echo \\                     # Output: \
echo \>                     # Output: >
echo \|                     # Output: |

# Escape spaces
echo file\ with\ spaces.txt # Output: file with spaces.txt
cd /path/to/my\ documents   # Changes to "/path/to/my documents"

# Escape newlines for continuation
echo "This is a very long \
line that continues \
on multiple lines"          # Output: This is a very long line that continues on multiple lines
```

### No Quotes

Without quotes, the shell performs all expansions and word splitting:

```bash
# Variables expand
echo $HOME                  # Output: /home/user

# Globs expand
echo *.txt                  # Output: file1.txt file2.txt ...

# Multiple spaces collapse
echo multiple    spaces     # Output: multiple spaces

# Special characters are interpreted
echo > output.txt          # Redirects to file
echo | grep pattern        # Pipes to grep
```

## Quoting Rules and Precedence

### Mixing Quote Types

You can combine different quote types by concatenation:

```bash
# Concatenate quoted strings
echo 'single'"double"'single'    # Output: singledoublesingle
echo "Hello "$USER", today is "$(date)  # Variable parts quoted differently

# Useful for including quotes
echo "It's"' a nice day'         # Output: It's a nice day
echo 'He said "Hello"'           # Output: He said "Hello"
echo "She said \"It's fine\""    # Output: She said "It's fine"
```

### Nested Quoting

Command substitution creates a new quoting context:

```bash
# Quotes inside command substitution
echo "Result: $(echo 'inner quotes')"   # Output: Result: inner quotes
echo '$(echo "not expanded")'           # Output: $(echo "not expanded")

# Complex nesting
echo "Files in '$(pwd)': $(ls '*.txt')" # pwd expands, *.txt is literal
```

## Special Cases

### Here Documents

Here documents have special quoting rules:

```bash
# Unquoted delimiter - expansions occur
cat << EOF
Hello $USER
Path: $PATH
EOF

# Quoted delimiter - no expansions
cat << 'EOF'
Hello $USER
Path: $PATH
EOF

# Either quote type works for delimiter
cat << "EOF"
Literal $text
EOF
```

### Aliases and Functions

Quotes affect alias expansion:

```bash
alias ll='ls -la'
'll'          # Won't expand (quoted)
"ll"          # Won't expand (quoted)
ll            # Will expand to ls -la
```

### Arrays (if supported)

```bash
# Array elements with spaces
arr=("element one" "element two" "element three")
echo "${arr[0]}"    # Output: element one

# Expanding arrays
echo "${arr[@]}"    # Each element as separate word
echo "${arr[*]}"    # All elements as single word
```

## Common Patterns

### Safely Handling Filenames

```bash
# Always quote variables containing filenames
file="my file.txt"
cat "$file"              # Correct
cat $file                # Wrong - treats as two arguments

# Or use escaping
file=my\ file.txt
cat $file                # Also works
```

### Passing Arguments with Spaces

```bash
# Quote arguments with spaces
grep "search term" file.txt
command --option="value with spaces"

# Multiple arguments
mycommand "arg 1" "arg 2" "arg 3"
```

### Preventing Expansion

```bash
# Prevent glob expansion
echo '*.txt'             # Literal: *.txt
find . -name '*.txt'     # Passes literal pattern to find

# Prevent variable expansion
echo '$HOME'             # Literal: $HOME
grep '$end' file.txt     # Searches for literal $end
```

### Building Commands

```bash
# Safe command building
cmd="ls"
opts="-la"
path="/home/user"
$cmd $opts "$path"       # Executes: ls -la "/home/user"

# With arrays (if supported)
args=("-l" "-a" "/home/user")
ls "${args[@]}"
```

## Escape Sequences

Common escape sequences in double quotes:

| Sequence | Meaning |
|----------|---------|
| `\"` | Literal double quote |
| `\\` | Literal backslash |
| `\$` | Literal dollar sign |
| `\`` | Literal backtick |
| `\n` | Newline |
| `\t` | Tab |
| `\r` | Carriage return |
| `\!` | Literal exclamation (in some contexts) |

## Testing Quote Behavior

### Test What Gets Passed

```bash
# See exactly what arguments a command receives
printf '<%s>\n' arg1 "arg 2" 'arg 3' arg\ 4

# Output:
# <arg1>
# <arg 2>
# <arg 3>
# <arg 4>
```

### Test Variable Content

```bash
# Check variable content with quotes
var="value with spaces"
echo "[$var]"           # Shows exact content with boundaries
printf '"%s"\n' "$var"  # Shows with quotes
```

## Common Mistakes

### 1. Forgetting Quotes Around Variables
```bash
# Wrong
file=$1
if [ -f $file ]; then   # Breaks if $file has spaces

# Correct
file="$1"
if [ -f "$file" ]; then
```

### 2. Using Single Quotes When Expansion Needed
```bash
# Wrong
echo 'Hello $USER'      # Outputs: Hello $USER

# Correct
echo "Hello $USER"      # Outputs: Hello alice
```

### 3. Trying to Escape Inside Single Quotes
```bash
# Wrong
echo 'It\'s broken'     # Syntax error

# Correct
echo "It's working"     # Or
echo 'It'"'"'s working' # Or
echo 'It'\''s working'
```

### 4. Unquoted Command Substitution
```bash
# Wrong
files=$(ls *.txt)       # Word splitting occurs
for f in $files; do     # Breaks on spaces

# Correct
files=$(ls *.txt)
IFS=$'\n'               # Set field separator
for f in $files; do     # Or use array
```

### 5. Quote Mismatch
```bash
# Wrong
echo "Missing quote     # Syntax error
echo 'Mismatched"       # Syntax error

# Correct
echo "Matched quotes"
echo 'Also matched'
```

## Best Practices

1. **Always quote variables**: `"$var"` not `$var`
2. **Use single quotes for literals**: `'literal text'`
3. **Use double quotes for expansions**: `"Hello $USER"`
4. **Quote command arguments**: `grep "$pattern" "$file"`
5. **Test with special characters**: Include spaces, asterisks, quotes in test data
6. **Use printf for exact output**: `printf '%s\n' "$var"`
7. **Check quote pairing**: Ensure all quotes are properly closed
8. **Be consistent**: Choose a quoting style and stick to it

## Implementation Status

| Feature | Status | Notes |
|---------|--------|-------|
| Single quotes | ✅ Implemented | Full support |
| Double quotes | ✅ Implemented | With expansions |
| Backslash escaping | ✅ Implemented | Basic support |
| Variable expansion in double quotes | ✅ Implemented | Full support |
| Command substitution in double quotes | ✅ Implemented | $() and `` |
| Escape sequences (\n, \t) | ⚡ Partial | In echo command |
| Here-doc quote handling | ⚡ Partial | In script runner |
| ANSI-C quoting ($'...') | 📋 Future | Not yet planned |
| Locale-specific quotes | 📋 Future | Not yet planned |