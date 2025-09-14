# Control Flow and Conditional Commands

This document describes the control flow structures and conditional commands available in the virtual shell.

## Table of Contents
- [Conditional Commands](#conditional-commands)
  - [test / [ Command](#test--command)
  - [true Command](#true-command)
  - [false Command](#false-command)
- [Control Flow Structures](#control-flow-structures)
  - [if/then/else/fi](#ifthenelsefi)
  - [for Loops](#for-loops)
  - [while Loops](#while-loops)
  - [until Loops](#until-loops)
- [Utility Commands](#utility-commands)
  - [sleep Command](#sleep-command)
- [Examples](#examples)

## Conditional Commands

### test / [ Command

The `test` command (also available as `[`) evaluates conditional expressions and sets the return code accordingly.

#### Syntax
```bash
test expression
[ expression ]  # Note: closing ] is required
```

#### File Tests
- `-e FILE` - True if FILE exists
- `-f FILE` - True if FILE exists and is a regular file
- `-d FILE` - True if FILE exists and is a directory
- `-s FILE` - True if FILE exists and has size greater than zero
- `-r FILE` - True if FILE is readable
- `-w FILE` - True if FILE is writable
- `-x FILE` - True if FILE is executable

#### String Tests
- `-z STRING` - True if STRING is empty
- `-n STRING` - True if STRING is not empty
- `STRING1 = STRING2` - True if strings are equal
- `STRING1 != STRING2` - True if strings are not equal
- `STRING1 < STRING2` - True if STRING1 sorts before STRING2
- `STRING1 > STRING2` - True if STRING1 sorts after STRING2

#### Numeric Tests
- `NUM1 -eq NUM2` - True if NUM1 equals NUM2
- `NUM1 -ne NUM2` - True if NUM1 not equals NUM2
- `NUM1 -lt NUM2` - True if NUM1 is less than NUM2
- `NUM1 -le NUM2` - True if NUM1 is less than or equal to NUM2
- `NUM1 -gt NUM2` - True if NUM1 is greater than NUM2
- `NUM1 -ge NUM2` - True if NUM1 is greater than or equal to NUM2

#### Logical Operators
- `! EXPR` - Negation
- `EXPR1 -a EXPR2` - Logical AND
- `EXPR1 -o EXPR2` - Logical OR

#### Examples
```bash
# File tests
[ -e /path/to/file ]
test -d /path/to/directory

# String comparisons
[ "$VAR" = "value" ]
test -z "$EMPTY_VAR"

# Numeric comparisons
[ 5 -lt 10 ]
test $COUNT -eq 0

# Negation
[ ! -e /nonexistent ]
```

### true Command

Always returns success (exit code 0).

#### Syntax
```bash
true [arguments]  # Arguments are ignored
```

#### Example
```bash
true && echo "This will always print"
```

### false Command

Always returns failure (exit code 1).

#### Syntax
```bash
false [arguments]  # Arguments are ignored
```

#### Example
```bash
false || echo "This will always print"
```

## Control Flow Structures

### if/then/else/fi

Conditional execution of commands based on test conditions.

#### Syntax
```bash
if condition; then
    commands
fi

if condition; then
    commands
else
    other_commands
fi

if condition1; then
    commands1
elif condition2; then
    commands2
else
    default_commands
fi
```

#### Examples
```bash
# Simple if
if [ -e /file.txt ]; then
    echo "File exists"
fi

# If/else
if test $USER = "root"; then
    echo "Running as root"
else
    echo "Running as $USER"
fi

# If/elif/else
if [ $NUM -lt 10 ]; then
    echo "Less than 10"
elif [ $NUM -lt 20 ]; then
    echo "Between 10 and 20"
else
    echo "20 or greater"
fi
```

### for Loops

Iterate over a list of items.

#### Syntax
```bash
for variable in list; do
    commands
done
```

#### Examples
```bash
# Iterate over explicit list
for i in 1 2 3 4 5; do
    echo "Number: $i"
done

# Iterate over files (with glob expansion)
for file in *.txt; do
    echo "Processing $file"
done

# Iterate over command output
for word in hello world test; do
    echo "Word: $word"
done
```

### while Loops

Execute commands while a condition is true.

#### Syntax
```bash
while condition; do
    commands
done
```

#### Examples
```bash
# While file exists
while [ -e /tmp/lock ]; do
    echo "Waiting..."
    sleep 1
done

# While counter is less than limit
COUNT=0
while [ $COUNT -lt 5 ]; do
    echo "Count: $COUNT"
    COUNT=$((COUNT + 1))  # Note: arithmetic expansion
done
```

### until Loops

Execute commands until a condition becomes true (opposite of while).

#### Syntax
```bash
until condition; do
    commands
done
```

#### Examples
```bash
# Until file exists
until [ -e /tmp/ready ]; do
    echo "Waiting for ready signal..."
    sleep 1
done

# Until condition is met
until false; do
    echo "This runs once"
    break  # Exit the loop
done
```

## Utility Commands

### sleep Command

Pause execution for a specified number of seconds.

#### Syntax
```bash
sleep NUMBER
```

- `NUMBER` can be an integer or decimal (e.g., `1`, `0.5`, `2.5`)

#### Examples
```bash
# Sleep for 1 second
sleep 1

# Sleep for half a second
sleep 0.5

# Use in a loop
for i in 1 2 3; do
    echo "Step $i"
    sleep 0.5
done
```

## Examples

### File Processing Script
```bash
# Process all .txt files in a directory
for file in /data/*.txt; do
    if [ -s $file ]; then
        echo "Processing $file (has content)"
        # Process the file
    else
        echo "Skipping $file (empty)"
    fi
done
```

### Retry Logic
```bash
# Retry a command until it succeeds
ATTEMPTS=0
MAX_ATTEMPTS=5

until [ $ATTEMPTS -ge $MAX_ATTEMPTS ]; do
    if some_command; then
        echo "Success!"
        break
    fi
    ATTEMPTS=$((ATTEMPTS + 1))
    echo "Attempt $ATTEMPTS failed, retrying..."
    sleep 1
done
```

### Menu System
```bash
# Simple menu
while true; do
    echo "1. Option 1"
    echo "2. Option 2"
    echo "3. Exit"
    read choice
    
    if [ "$choice" = "1" ]; then
        echo "You chose option 1"
    elif [ "$choice" = "2" ]; then
        echo "You chose option 2"
    elif [ "$choice" = "3" ]; then
        break
    else
        echo "Invalid choice"
    fi
done
```

### Validation Function
```bash
# Check if a directory is valid for processing
validate_dir() {
    DIR=$1
    
    if [ ! -d "$DIR" ]; then
        echo "Error: $DIR is not a directory"
        return 1
    fi
    
    if [ ! -r "$DIR" ]; then
        echo "Error: $DIR is not readable"
        return 1
    fi
    
    return 0
}

# Use the validation
if validate_dir /some/path; then
    echo "Directory is valid"
fi
```

## Notes and Limitations

1. **Arithmetic Expansion**: The shell doesn't yet support `$((expression))` for arithmetic. Use external commands or counters with files as workarounds.

2. **Break/Continue**: Loop control statements like `break` and `continue` are not yet implemented.

3. **Case Statements**: The `case/esac` construct is not yet available.

4. **Functions**: Shell functions are not yet implemented.

5. **Maximum Iterations**: While and until loops have a safety limit of 10,000 iterations to prevent infinite loops.

6. **Nested Quotes**: Complex quoting in control structures may have limitations.

## Best Practices

1. **Always quote variables** in test conditions to handle empty values:
   ```bash
   [ "$VAR" = "value" ]  # Good
   [ $VAR = "value" ]    # May fail if VAR is empty
   ```

2. **Use meaningful variable names** in loops:
   ```bash
   for file in *.txt     # Good
   for f in *.txt        # Less clear
   ```

3. **Check file existence** before operations:
   ```bash
   if [ -e "$FILE" ]; then
       # Safe to operate on file
   fi
   ```

4. **Provide else branches** for important conditions:
   ```bash
   if command; then
       echo "Success"
   else
       echo "Failed: handling error"
   fi
   ```