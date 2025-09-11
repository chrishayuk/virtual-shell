# script

Run shell scripts using the script runner.

## Synopsis

```
script filename1 [filename2] ...
```

## Description

The `script` command executes one or more shell scripts using the virtual shell environment's script runner. It provides a dedicated interface for running scripts with enhanced error handling.

## Arguments

- `filename...` - One or more script file paths to execute

## Examples

**Run single script:**
```bash
script deploy.sh                             # Execute single script
```

**Run multiple scripts:**
```bash
script setup.sh configure.sh start.sh       # Execute scripts in sequence
```

**Run scripts from different locations:**
```bash
script /path/to/init.sh ./local_config.sh   # Mix absolute and relative paths
```

## Behavior

- Executes scripts in the order specified
- Uses the shell's `ScriptRunner` for execution
- Continues with remaining scripts even if one fails
- Reports errors for each failed script separately

## Script Execution

**Example script (setup.sh):**
```bash
#!/bin/sh
echo "Setting up environment..."
mkdir -p logs temp
echo "Setup complete"
```

**Execute:**
```bash
script setup.sh
# Output:
# Setting up environment...
# Setup complete
```

## Multiple Script Execution

When multiple scripts are specified:
1. Scripts execute in command-line order
2. Each script runs to completion before next starts
3. Errors in one script don't stop execution of others
4. All results are combined in output

**Example:**
```bash
# Three scripts: init.sh, config.sh, start.sh
script init.sh config.sh start.sh
# Output includes results from all three scripts
```

## Error Handling

- "script: missing operand" - No script files specified
- "Error running script 'filename': error_details" - Script execution failed
- Individual script errors don't prevent other scripts from running

## Script Runner Integration

Uses the shell's `ScriptRunner` class which provides:
- Enhanced script execution environment
- Better error reporting and handling
- Integration with virtual filesystem
- Support for script arguments and environment

## Implementation Notes

- Creates new `ScriptRunner` instance for execution
- Processes each script file individually
- Collects all results and errors for combined output
- Uses exception handling for robust error reporting

## Use Cases

**Automated deployment:**
```bash
script prepare.sh deploy.sh verify.sh       # Multi-step deployment
```

**System setup:**
```bash
script install_deps.sh configure.sh test.sh # Setup and validation
```

**Batch processing:**
```bash
script process_data1.sh process_data2.sh    # Process multiple datasets
```

**Development workflow:**
```bash
script build.sh test.sh package.sh          # Build pipeline
```

## Output Format

Results from all scripts are concatenated:
```
[output from script1]
[output from script2]
Error running script 'failed_script.sh': [error details]
[output from script3]
```

## Comparison with Other Commands

**vs `sh`:**
- `script`: Uses dedicated script runner, better error handling
- `sh`: Direct shell execution, more basic

**vs direct execution:**
- `script`: Enhanced environment and error reporting
- Direct: Basic execution without runner framework

## Script Requirements

Scripts should be:
- Readable by the virtual filesystem
- Properly formatted shell scripts
- Executable within the virtual environment

## Error Recovery

- Failed scripts are reported but don't stop processing
- Each script error includes script name and details
- Successful scripts still produce their normal output

## See Also

- [`sh`](sh.md) - Execute shell commands and scripts
- [`python`](python.md) - Execute Python scripts
- [Script runner](../../README.md#script-runner) - Script execution framework
- [Shell scripting](../../README.md#scripting) - Writing effective scripts