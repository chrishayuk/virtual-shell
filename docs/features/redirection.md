# Shell Redirection Guide

## Overview

The Chuk Virtual Shell supports comprehensive I/O redirection capabilities similar to POSIX shells. This guide covers all supported redirection operators and their usage.

## Standard Output Redirection

### Basic Output (`>`)
Redirects standard output to a file, overwriting existing content:
```bash
echo "Hello World" > output.txt
ls -la > directory_listing.txt
```

### Append Output (`>>`)
Appends standard output to a file:
```bash
echo "Line 1" > log.txt
echo "Line 2" >> log.txt
echo "Line 3" >> log.txt
```

## Standard Error Redirection

### Basic Error Redirection (`2>`)
Redirects standard error to a file:
```bash
ls /nonexistent 2> errors.txt
command_that_fails 2> error_log.txt
```

### Append Error (`2>>`)
Appends standard error to a file:
```bash
ls /nonexistent1 2>> errors.txt
ls /nonexistent2 2>> errors.txt
```

### Redirect Stderr to Stdout (`2>&1`)
Merges standard error into standard output:
```bash
command 2>&1                    # Both to terminal
command > output.txt 2>&1       # Both to file
command 2>&1 | grep error       # Both through pipe
```

## Combined Output Redirection

### Combined Output (`&>`)
Redirects both stdout and stderr to the same file:
```bash
command &> all_output.txt
script.sh &> execution_log.txt
```

### Append Combined (`&>>`)
Appends both stdout and stderr to the same file:
```bash
command &>> all_output.txt
```

## Input Redirection

### Basic Input (`<`)
Redirects input from a file:
```bash
sort < unsorted_list.txt
grep "pattern" < input_file.txt
while read line; do echo "$line"; done < data.txt
```

## Here Documents

### Basic Here-Doc (`<<`)
Provides multi-line input directly in the script:
```bash
cat << EOF
This is line 1
This is line 2
This is line 3
EOF

# With output redirection
cat > config.txt << END
server=localhost
port=8080
debug=true
END
```

### Here-Doc with Tab Stripping (`<<-`)
Strips leading tabs from the content (useful for indented scripts):
```bash
if [ "$condition" = "true" ]; then
    cat <<- EOF
		This line has tabs stripped
		So does this one
		Making the output clean
	EOF
fi
```

## Special Files

### Null Device (`/dev/null`)
Discards output or provides empty input:
```bash
# Discard all output
command > /dev/null

# Discard errors only
command 2> /dev/null

# Discard everything
command &> /dev/null

# Empty input
command < /dev/null
```

## Pipeline Redirection

Redirections work with pipelines:
```bash
# Redirect final output
cat file.txt | grep "pattern" | sort > results.txt

# Redirect errors from specific command
cat file.txt 2> cat_errors.txt | grep "pattern"

# Capture everything
(command1 | command2 | command3) &> pipeline_output.txt
```

## Complex Examples

### Logging with Timestamps
```bash
# Log both output and errors with timestamp
(echo "[$(date)] Starting process" && command) &>> process.log
```

### Separate Output and Errors
```bash
command > output.txt 2> errors.txt
```

### Filter Errors Only
```bash
command 2>&1 > /dev/null | grep "ERROR"
```

### Multiple Redirections
```bash
# Read from file, write output to another, errors to third
sort < input.txt > sorted.txt 2> sort_errors.txt
```

### Here-Doc with Variables
```bash
NAME="John"
cat << EOF > greeting.txt
Hello, $NAME!
Welcome to the system.
Today is $(date)
EOF
```

## Implementation Status

| Feature | Status | Notes |
|---------|--------|-------|
| `>` (output) | ✅ Implemented | Full support |
| `>>` (append) | ✅ Implemented | Full support |
| `<` (input) | ✅ Implemented | Full support |
| `2>` (stderr) | ✅ Implemented | Full support |
| `2>>` (stderr append) | ✅ Implemented | Full support |
| `2>&1` (stderr to stdout) | ✅ Implemented | Full support |
| `&>` (combined) | ✅ Implemented | Full support |
| `&>>` (combined append) | ✅ Implemented | Full support |
| `<<` (here-doc) | ⚡ Partial | Works in script runner |
| `<<-` (here-doc strip) | ⚡ Partial | Parser ready, needs integration |
| `/dev/null` | ⚡ Partial | Works as regular file |
| File descriptors (3>, 4<) | 📋 Future | Not yet planned |
| Process substitution | 📋 Future | Not yet planned |

## Best Practices

1. **Always quote filenames with spaces**:
   ```bash
   echo "content" > "file with spaces.txt"
   ```

2. **Use `2>&1` at the end**:
   ```bash
   command > output.txt 2>&1  # Correct
   command 2>&1 > output.txt  # Won't capture stderr to file
   ```

3. **Check file permissions**:
   ```bash
   # Ensure target directory exists
   mkdir -p /path/to/directory
   command > /path/to/directory/output.txt
   ```

4. **Use append for logs**:
   ```bash
   echo "[$(date)] Event occurred" >> application.log
   ```

5. **Handle errors gracefully**:
   ```bash
   if ! command 2> errors.txt; then
       echo "Command failed. Check errors.txt"
       exit 1
   fi
   ```

## Troubleshooting

### "No such file or directory"
- Check that parent directories exist
- Verify file paths are correct
- Ensure proper permissions

### Empty output files
- Command may be writing to stderr instead of stdout
- Use `2>&1` to capture both streams

### Heredoc not working
- Ensure delimiter is on its own line
- No trailing spaces after delimiter
- Delimiter must match exactly (case-sensitive)

### Unexpected output
- Check order of redirections
- Remember pipes connect stdout to stdin only
- Use `2>&1` before pipes to include stderr