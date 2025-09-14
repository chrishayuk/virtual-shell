# POSIX Compatibility Matrix

## Overview

This document provides a comprehensive comparison between Chuk Virtual Shell and POSIX.1-2017 (IEEE Std 1003.1-2017) specifications. While Chuk Virtual Shell is designed as an **agent-optimized virtual environment** rather than a POSIX-compliant shell, this matrix helps users understand which POSIX features are available.

**Compatibility Levels:**
- ✅ **Full**: Complete POSIX-compliant implementation
- ⚡ **Partial**: Works but with limitations or differences
- 🔄 **Alternative**: Different implementation achieving similar goals
- ❌ **Not Supported**: Not implemented (may be planned)
- 🚫 **Not Applicable**: Feature doesn't apply to virtual environment

## Shell Command Language (POSIX.1-2017 Chapter 2)

### 2.2 Quoting

| Feature | POSIX Requirement | Chuk Virtual Shell | Status | Notes |
|---------|-------------------|-------------------|--------|--------|
| Escape Character (`\`) | Preserves literal value of next character | Partial implementation | ⚡ | Basic escaping works |
| Single Quotes (`'`) | Preserves literal value of all characters | Expansions still occur | ⚡ | Known limitation |
| Double Quotes (`"`) | Preserves literal except `$`, `` ` ``, `\`, `!` | Variable expansion works | ⚡ | Partial compliance |
| Dollar Single Quote (`$'...'`) | ANSI-C quoting | Not supported | ❌ | Not implemented |

### 2.3 Token Recognition

| Feature | POSIX Requirement | Chuk Virtual Shell | Status | Notes |
|---------|-------------------|-------------------|--------|--------|
| Operator Recognition | `|`, `&`, `;`, `<`, `>`, `(`, `)` | Most operators supported | ⚡ | No `()` subshells yet |
| Word Recognition | Unquoted character sequences | Fully supported | ✅ | |
| Alias Substitution | Replace alias with value | Fully supported | ✅ | |
| Reserved Words | `if`, `then`, `else`, `for`, etc. | Fully supported | ✅ | |

### 2.4 Reserved Words

| Word | POSIX Purpose | Chuk Virtual Shell | Status |
|------|---------------|-------------------|--------|
| `!` | Pipeline negation | Not supported | ❌ |
| `{` `}` | Brace group | Not supported | ❌ |
| `case` `esac` | Pattern matching | Fully supported | ✅ |
| `do` `done` | Loop body | Fully supported | ✅ |
| `elif` | Else-if | Fully supported | ✅ |
| `else` | Conditional else | Fully supported | ✅ |
| `fi` | End if | Fully supported | ✅ |
| `for` | For loop | Fully supported | ✅ |
| `if` | Conditional | Fully supported | ✅ |
| `in` | For loop list | Fully supported | ✅ |
| `then` | If body | Fully supported | ✅ |
| `until` | Until loop | Fully supported | ✅ |
| `while` | While loop | Fully supported | ✅ |

### 2.5 Parameters and Variables

| Feature | POSIX Requirement | Chuk Virtual Shell | Status | Notes |
|---------|-------------------|-------------------|--------|--------|
| Positional Parameters | `$1`, `$2`, ... `$9`, `${10}` | Not supported | ❌ | No script arguments |
| Special Parameters | | | | |
| `$@` | All positional parameters | Not supported | ❌ | |
| `$*` | All positional parameters as string | Not supported | ❌ | |
| `$#` | Number of positional parameters | Not supported | ❌ | |
| `$?` | Exit status of last command | Fully supported | ✅ | |
| `$-` | Current option flags | Not supported | ❌ | |
| `$$` | Process ID of shell | Returns simulated PID | 🔄 | Virtual PID |
| `$!` | Process ID of last background command | Not supported | ❌ | No background jobs |
| `$0` | Name of shell or script | Partially supported | ⚡ | |
| Shell Variables | | | | |
| `HOME` | Home directory | Fully supported | ✅ | |
| `PATH` | Command search path | Fully supported | ✅ | |
| `PWD` | Current working directory | Fully supported | ✅ | |
| `OLDPWD` | Previous working directory | Fully supported | ✅ | |
| `IFS` | Field separator | Not supported | ❌ | |
| `PS1` | Primary prompt | Not configurable | ❌ | |
| `PS2` | Secondary prompt | Not supported | ❌ | |

### 2.6 Word Expansions

| Expansion Type | POSIX Requirement | Chuk Virtual Shell | Status | Notes |
|----------------|-------------------|-------------------|--------|--------|
| Tilde Expansion | `~` → `$HOME` | Fully supported | ✅ | |
| Parameter Expansion | `${parameter}` | Basic support | ⚡ | |
| `${parameter:-word}` | Use default | Not supported | ❌ | |
| `${parameter:=word}` | Assign default | Not supported | ❌ | |
| `${parameter:?word}` | Error if null | Not supported | ❌ | |
| `${parameter:+word}` | Use alternative | Not supported | ❌ | |
| `${#parameter}` | String length | Not supported | ❌ | |
| `${parameter%pattern}` | Remove suffix | Not supported | ❌ | |
| `${parameter#pattern}` | Remove prefix | Not supported | ❌ | |
| Command Substitution | `$(command)` or `` `command` `` | Fully supported | ✅ | Both forms work |
| Arithmetic Expansion | `$((expression))` | Not supported | ❌ | Planned |
| Field Splitting | Split on IFS | Not configurable | ❌ | |
| Pathname Expansion | `*`, `?`, `[...]` | Fully supported | ✅ | |
| Quote Removal | Remove quotes after expansion | Partial | ⚡ | |

### 2.7 Redirection

| Operator | POSIX Purpose | Chuk Virtual Shell | Status | Notes |
|----------|---------------|-------------------|--------|--------|
| `<` | Input redirection | Fully supported | ✅ | |
| `>` | Output redirection | Fully supported | ✅ | |
| `>|` | Output (override noclobber) | Not supported | ❌ | No noclobber |
| `>>` | Append output | Fully supported | ✅ | |
| `<&` | Duplicate input FD | Not supported | ❌ | |
| `>&` | Duplicate output FD | Not supported | ❌ | |
| `<<` | Here-document | Script runner only | ⚡ | |
| `<<-` | Here-document (strip tabs) | Script runner only | ⚡ | |
| `<>` | Open for reading and writing | Not supported | ❌ | |
| `2>` | Stderr redirection | Parser ready | 🔄 | Integration pending |
| `2>&1` | Merge stderr to stdout | Parser ready | 🔄 | Integration pending |

### 2.8 Exit Status

| Range | POSIX Meaning | Chuk Virtual Shell | Status |
|-------|---------------|-------------------|--------|
| 0 | Success | Fully supported | ✅ |
| 1-125 | Command-specific error | Fully supported | ✅ |
| 126 | Command found but not executable | Returns 127 | ⚡ |
| 127 | Command not found | Fully supported | ✅ |
| 128+n | Terminated by signal n | Not applicable | 🚫 |

### 2.9 Shell Commands

| Command Type | POSIX Requirement | Chuk Virtual Shell | Status | Notes |
|--------------|-------------------|-------------------|--------|--------|
| Simple Commands | Command with arguments | Fully supported | ✅ | |
| Pipelines | `cmd1 | cmd2` | Fully supported | ✅ | Multi-stage |
| Lists | `&&`, `||`, `;` | Fully supported | ✅ | |
| Compound Commands | | | | |
| Brace Group `{ }` | Group commands | Not supported | ❌ | |
| Subshell `( )` | Run in subshell | Not supported | ❌ | |
| `for` loop | Iteration | Fully supported | ✅ | |
| `case` statement | Pattern matching | Fully supported | ✅ | |
| `if` statement | Conditional | Fully supported | ✅ | |
| `while` loop | While condition | Fully supported | ✅ | |
| `until` loop | Until condition | Fully supported | ✅ | |
| Function Definition | `name() { ... }` | Not supported | ❌ | Planned |

### 2.10 Pattern Matching

| Pattern | POSIX Meaning | Chuk Virtual Shell | Status |
|---------|---------------|-------------------|--------|
| `*` | Match any string | Fully supported | ✅ |
| `?` | Match any character | Fully supported | ✅ |
| `[...]` | Match character class | Fully supported | ✅ |
| `[!...]` | Match negated class | Fully supported | ✅ |
| `[[:class:]]` | POSIX character class | Not supported | ❌ |

## Shell Built-in Utilities (POSIX.1-2017)

### Special Built-ins

| Command | POSIX Purpose | Chuk Virtual Shell | Status | Notes |
|---------|---------------|-------------------|--------|--------|
| `break` | Exit from loop | Fully supported | ✅ | |
| `colon` `:` | Null command | Fully supported | ✅ | |
| `continue` | Next loop iteration | Fully supported | ✅ | |
| `dot` `.` | Source script | Not supported | ❌ | |
| `eval` | Evaluate arguments | Not supported | ❌ | |
| `exec` | Replace shell | Not applicable | 🚫 | Virtual env |
| `exit` | Exit shell | Fully supported | ✅ | |
| `export` | Export variables | Fully supported | ✅ | |
| `readonly` | Make variable readonly | Not supported | ❌ | |
| `return` | Return from function | Not supported | ❌ | No functions |
| `set` | Set options | Partial | ⚡ | Limited options |
| `shift` | Shift parameters | Not supported | ❌ | No parameters |
| `times` | Process times | Not applicable | 🚫 | |
| `trap` | Signal handling | Not supported | ❌ | |
| `unset` | Unset variables | Fully supported | ✅ | |

### Regular Built-ins

| Command | POSIX Purpose | Chuk Virtual Shell | Status | Notes |
|---------|---------------|-------------------|--------|--------|
| `alias` | Define alias | Fully supported | ✅ | |
| `bg` | Background job | Not supported | ❌ | No job control |
| `cd` | Change directory | Fully supported | ✅ | |
| `command` | Execute command | Not supported | ❌ | |
| `false` | Return false | Fully supported | ✅ | |
| `fc` | Fix command | Not supported | ❌ | |
| `fg` | Foreground job | Not supported | ❌ | No job control |
| `getopts` | Parse options | Not supported | ❌ | |
| `hash` | Remember commands | Not supported | ❌ | |
| `jobs` | List jobs | Not supported | ❌ | No job control |
| `kill` | Terminate process | Not applicable | 🚫 | Virtual env |
| `newgrp` | Change group | Not applicable | 🚫 | |
| `pwd` | Print working directory | Fully supported | ✅ | |
| `read` | Read input | Not supported | ❌ | |
| `true` | Return true | Fully supported | ✅ | |
| `type` | Display command type | Similar to `which` | 🔄 | |
| `ulimit` | Resource limits | Not applicable | 🚫 | |
| `umask` | File creation mask | Not supported | ❌ | |
| `unalias` | Remove alias | Fully supported | ✅ | |
| `wait` | Wait for process | Not applicable | 🚫 | |

## Standard Utilities (Selection)

### File and Directory Operations

| Command | POSIX Purpose | Chuk Virtual Shell | Status | Notes |
|---------|---------------|-------------------|--------|--------|
| `basename` | Strip directory | Fully supported | ✅ | |
| `cat` | Concatenate files | Fully supported | ✅ | |
| `chmod` | Change permissions | Not supported | ❌ | No permissions |
| `chown` | Change ownership | Not supported | ❌ | No ownership |
| `cp` | Copy files | Fully supported | ✅ | `-r`, `-f`, `-n` |
| `dirname` | Strip filename | Fully supported | ✅ | |
| `find` | Find files | Fully supported | ✅ | Many options |
| `ln` | Create links | Not supported | ❌ | No links |
| `ls` | List directory | Fully supported | ✅ | `-l`, `-a`, `-h` |
| `mkdir` | Make directories | Fully supported | ✅ | `-p` option |
| `mv` | Move files | Fully supported | ✅ | |
| `rm` | Remove files | Fully supported | ✅ | `-r`, `-f` |
| `rmdir` | Remove directory | Fully supported | ✅ | |
| `touch` | Update timestamp | Fully supported | ✅ | |

### Text Processing

| Command | POSIX Purpose | Chuk Virtual Shell | Status | Notes |
|---------|---------------|-------------------|--------|--------|
| `awk` | Pattern processing | Fully supported | ✅ | |
| `cut` | Extract columns | Fully supported | ✅ | |
| `diff` | Compare files | Basic support | ⚡ | |
| `echo` | Display text | Fully supported | ✅ | |
| `grep` | Search patterns | Fully supported | ✅ | `-i`, `-v`, `-n` |
| `head` | Display first lines | Fully supported | ✅ | |
| `more` | Page through text | Basic support | ⚡ | |
| `printf` | Formatted output | Partial | ⚡ | Basic formats |
| `sed` | Stream editor | Fully supported | ✅ | |
| `sort` | Sort lines | Fully supported | ✅ | |
| `tail` | Display last lines | Fully supported | ✅ | |
| `tr` | Translate characters | Fully supported | ✅ | |
| `uniq` | Report unique lines | Fully supported | ✅ | |
| `wc` | Word count | Fully supported | ✅ | |

### System Information

| Command | POSIX Purpose | Chuk Virtual Shell | Status | Notes |
|---------|---------------|-------------------|--------|--------|
| `date` | Display date | Simulated | 🔄 | Returns current date |
| `env` | Environment | Fully supported | ✅ | |
| `id` | User identity | Not supported | ❌ | No users |
| `locale` | Locale settings | Not supported | ❌ | |
| `logname` | Login name | Returns USER | 🔄 | |
| `sleep` | Delay execution | Not supported | ❌ | |
| `tty` | Terminal name | Not applicable | 🚫 | |
| `uname` | System name | Not supported | ❌ | |
| `who` | Who is logged in | Not applicable | 🚫 | |

## Shell Execution Environment

### Process Environment

| Feature | POSIX Requirement | Chuk Virtual Shell | Status | Notes |
|---------|-------------------|-------------------|--------|--------|
| Process ID | Unique PID | Simulated | 🔄 | Virtual PID |
| Parent Process | PPID | Not supported | ❌ | |
| Process Groups | Job control | Not supported | ❌ | |
| Sessions | Terminal sessions | Not applicable | 🚫 | |
| Controlling Terminal | TTY control | Not applicable | 🚫 | |
| Signal Handling | Trap signals | Not supported | ❌ | |
| File Descriptors | 0=stdin, 1=stdout, 2=stderr | Partial | ⚡ | Virtual FDs |
| Current Working Directory | PWD tracking | Fully supported | ✅ | |
| File Creation Mask | umask | Not supported | ❌ | |
| Resource Limits | ulimit | Not applicable | 🚫 | |

### Shell Options

| Option | POSIX Purpose | Chuk Virtual Shell | Status | Notes |
|--------|---------------|-------------------|--------|--------|
| `-a` allexport | Export all variables | Not supported | ❌ | |
| `-b` notify | Async job notification | Not applicable | 🚫 | |
| `-C` noclobber | Prevent overwrite | Not supported | ❌ | |
| `-e` errexit | Exit on error | Not supported | ❌ | |
| `-f` noglob | Disable pathname expansion | Not supported | ❌ | |
| `-h` hashall | Hash commands | Not applicable | 🚫 | |
| `-m` monitor | Job control | Not applicable | 🚫 | |
| `-n` noexec | Read but don't execute | Not supported | ❌ | |
| `-o` option | Set option | Partial | ⚡ | |
| `-u` nounset | Error on unset variable | Not supported | ❌ | |
| `-v` verbose | Print input | Not supported | ❌ | |
| `-x` xtrace | Trace execution | Not supported | ❌ | |

## File System and Permissions

| Feature | POSIX Requirement | Chuk Virtual Shell | Status | Notes |
|---------|-------------------|-------------------|--------|--------|
| File Types | Regular, directory, etc. | Regular & directory only | ⚡ | |
| Permissions | rwx for ugo | Not implemented | ❌ | Virtual FS |
| Ownership | User and group | Not implemented | ❌ | Virtual FS |
| Hard Links | Multiple names | Not supported | ❌ | |
| Symbolic Links | Soft links | Not supported | ❌ | |
| Special Files | Device files | Not applicable | 🚫 | |
| File Times | atime, mtime, ctime | mtime only | ⚡ | |

## Summary

### Compliance Statistics

| Category | Full | Partial | Alternative | Not Supported | Not Applicable |
|----------|------|---------|-------------|---------------|----------------|
| Shell Language | 15 | 12 | 2 | 25 | 0 |
| Built-in Commands | 18 | 3 | 2 | 15 | 8 |
| Standard Utilities | 25 | 5 | 2 | 10 | 3 |
| Environment | 2 | 3 | 2 | 8 | 10 |
| **Total** | **60** | **23** | **8** | **58** | **21** |

### Key Differences from POSIX

1. **Virtual Environment**: No real processes, signals, or job control
2. **Security Model**: Simplified permissions for sandboxed execution
3. **Agent-Optimized**: Designed for AI agents, not interactive users
4. **Deterministic**: Reproducible execution with state management
5. **Cross-Platform**: Consistent behavior across all operating systems

### Recommendations for POSIX Users

- ✅ **Best For**: File operations, text processing, control flow, pipelines
- ⚡ **Limited**: Quoting, parameter expansion, advanced redirection
- ❌ **Avoid**: Job control, signal handling, process management
- 🔄 **Different**: Session-based state management instead of processes

### Future POSIX Compliance Goals

**High Priority:**
- Complete quoting implementation (single quotes blocking expansion)
- Stderr redirection integration (2>, 2>&1)
- Parameter expansion operators (${var:-default})
- Arithmetic expansion $(())

**Medium Priority:**
- Shell functions
- Here-documents in interactive mode
- More POSIX utilities (sleep, diff, etc.)
- Advanced glob patterns

**Low Priority:**
- Job control (not applicable to virtual environment)
- Signal handling (limited use in virtual environment)
- File permissions (simplified model sufficient)