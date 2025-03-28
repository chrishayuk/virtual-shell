# Environment Commands

This document describes the environment-related commands available in the Chuk Virtual Shell.

## Available Commands

### env

The `env` command displays environment variables currently set in the shell.

#### Usage

```
env [filter]
```

#### Arguments

- `filter` (optional): If provided, only environment variables containing this substring in their names will be displayed.

#### Examples

Display all environment variables:
```
$ env
PATH=/usr/local/bin:/usr/bin:/bin
HOME=/home/user
USER=chuck
SHELL=/bin/bash
```

Display only environment variables containing "PATH" in their name:
```
$ env PATH
PATH=/usr/local/bin:/usr/bin:/bin
CLASSPATH=/usr/lib/java
```

### export

The `export` command sets environment variables in the current shell session.

#### Usage

```
export KEY=VALUE [KEY2=VALUE2 ...]
```

#### Arguments

- `KEY=VALUE`: One or more assignments in the format KEY=VALUE.

#### Examples

Set a single environment variable:
```
$ export DEBUG=true
```

Set multiple environment variables:
```
$ export LANG=en_US.UTF-8 EDITOR=vim
```

#### Error Handling

The `export` command will report errors for:
- Missing '=' in assignments
- Missing variable names

Example error messages:
```
$ export DEBUG
export: invalid assignment 'DEBUG' (expected KEY=VALUE)

$ export =true
export: missing variable name
```

## Implementation Details

Both commands are implemented as Python classes that inherit from the `ShellCommand` base class. They use the `argparse` module for parsing command-line arguments and interact with the shell's environment variables through the `self.shell.environ` dictionary.

## Integration with the Shell

These commands can be used to view and modify the environment variables that affect the behavior of other commands in the Chuk Virtual Shell. Environment variables set using `export` will be available to subsequent commands run in the same shell session.