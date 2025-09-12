"""
chuk_virtual_shell/shell_interpreter.py - Core shell interpreter for PyodideShell

This module implements the ShellInterpreter class which initializes the virtual
filesystem, loads environment variables (optionally from a YAML sandbox configuration),
and dynamically discovers and registers shell commands. It also provides methods
for parsing, executing commands, and managing the shell state.

This enhanced version adds support for asynchronous command execution.
"""

import logging
import traceback
import time
import inspect
from typing import Optional, Tuple

# virtual file system imports
from chuk_virtual_fs import VirtualFileSystem  # type: ignore
from chuk_virtual_shell.commands.command_loader import CommandLoader
from chuk_virtual_shell.filesystem_compat import FileSystemCompat

# Configure module-level logger.
logger = logging.getLogger(__name__)


class ShellInterpreter:
    def __init__(self, fs_provider=None, fs_provider_args=None, sandbox_yaml=None):
        """
        Initialize the shell interpreter.

        Args:
            fs_provider (str, optional): Filesystem provider name.
            fs_provider_args (dict, optional): Arguments for the filesystem provider.
            sandbox_yaml (str, optional): Path or name of a YAML sandbox configuration.
        """
        # Initialize filesystem and environment.
        if sandbox_yaml:
            self._initialize_from_sandbox(sandbox_yaml)
        elif fs_provider:
            self._initialize_with_provider(fs_provider, fs_provider_args)
        else:
            raw_fs = VirtualFileSystem()
            self.fs = FileSystemCompat(raw_fs)
            self._setup_default_environment()

        # Initialize history, running flag, and return code.
        self.history = []
        self.running = True
        self.return_code = 0

        # Record start time (useful for uptime commands).
        self.start_time = time.time()

        # Command timing statistics
        self.command_timing = {}
        self.enable_timing = False

        # Set current_user based on environment.
        self.current_user = self.environ.get("USER", "user")

        # Provide a resolve_path method that delegates to the filesystem.
        self.resolve_path = lambda path: self.fs.resolve_path(path)

        # Dynamically load commands.
        self.commands = {}
        self._load_commands()

        # Initialize MCP servers list if not already set
        if not hasattr(self, "mcp_servers"):
            self.mcp_servers = []

        # Initialize aliases dictionary
        if not hasattr(self, "aliases"):
            self.aliases = {}

        # Load .shellrc file if it exists
        self._load_shellrc()

    def _initialize_from_sandbox(self, sandbox_yaml: str) -> None:
        """Initialize filesystem and environment using a YAML sandbox configuration."""
        # Import the modularized loader functions.
        from chuk_virtual_shell.sandbox.loader.sandbox_config_loader import (
            load_config_file,
            find_config_file,
        )
        from chuk_virtual_shell.sandbox.loader.filesystem_initializer import (
            create_filesystem,
        )
        from chuk_virtual_shell.sandbox.loader.environment_loader import (
            load_environment,
        )
        from chuk_virtual_shell.sandbox.loader.initialization_executor import (
            execute_initialization,
        )
        from chuk_virtual_shell.sandbox.loader.mcp_loader import load_mcp_servers

        try:
            # Resolve configuration file path.
            if not sandbox_yaml.endswith((".yaml", ".yml")) and "/" not in sandbox_yaml:
                config_path = find_config_file(sandbox_yaml)
                if not config_path:
                    raise ValueError(
                        f"Sandbox configuration '{sandbox_yaml}' not found"
                    )
            else:
                config_path = sandbox_yaml

            # Load the sandbox configuration.
            config = load_config_file(config_path)

            # Create and configure the filesystem.
            raw_fs = create_filesystem(config)
            self.fs = FileSystemCompat(raw_fs)

            # Set up the environment.
            self.environ = load_environment(config)

            # Ensure the home directory exists.
            self._ensure_home_directory(self.environ["HOME"])

            # Execute initialization commands.
            init_commands = config.get("initialization", [])
            if init_commands:
                execute_initialization(self.fs, init_commands)

            logger.info(f"Using sandbox configuration: {config.get('name', 'custom')}")
            logger.info(f"Home directory set to: {self.environ['HOME']}")
            logger.info("Environment variables:")
            for key, value in self.environ.items():
                logger.info(f"  {key}: {value}")

            # Load MCP server configurations.
            self.mcp_servers = load_mcp_servers(config)
            if self.mcp_servers:
                print(
                    f"MCP servers loaded: {[s.get('server_name') for s in self.mcp_servers]}"
                )

        except Exception as e:
            logger.error(f"Error loading sandbox configuration '{sandbox_yaml}': {e}")
            traceback.print_exc()
            logger.info("Falling back to default configuration.")
            raw_fs = VirtualFileSystem()
            self.fs = FileSystemCompat(raw_fs)
            self._setup_default_environment()

    def _initialize_with_provider(
        self, fs_provider: str, fs_provider_args: dict
    ) -> None:
        """Initialize filesystem using the specified provider and arguments."""
        try:
            raw_fs = VirtualFileSystem(fs_provider, **(fs_provider_args or {}))
            self.fs = FileSystemCompat(raw_fs)
            self._setup_default_environment()
        except Exception as e:
            logger.error(f"Error initializing filesystem provider '{fs_provider}': {e}")
            logger.info("Falling back to memory provider.")
            raw_fs = VirtualFileSystem()
            self.fs = FileSystemCompat(raw_fs)
            self._setup_default_environment()

    def _setup_default_environment(self) -> None:
        """Set up default environment variables and create a default home directory."""
        default_home = "/home/user"
        try:
            resolved_home_dir = self.fs.resolve_path(default_home)
            existing_node = self.fs.get_node_info(resolved_home_dir)
            if not existing_node:
                if not self.fs.mkdir(resolved_home_dir):
                    logger.debug(f"Could not create home directory {resolved_home_dir}")
            elif not existing_node.is_dir:
                logger.debug(
                    f"Home path {resolved_home_dir} exists but is not a directory"
                )
        except Exception as mkdir_error:
            logger.error(
                f"Error processing home directory {default_home}: {mkdir_error}"
            )

        self.environ = {
            "HOME": default_home,
            "PATH": "/bin:/usr/bin",
            "USER": "user",
            "SHELL": "/bin/pyodide-shell",
            "PWD": "/",
            "OLDPWD": "/",
            "TERM": "xterm",
        }

    def _ensure_home_directory(self, home_dir: str) -> None:
        """Ensure that the specified home directory exists and is accessible."""
        try:
            resolved_home_dir = self.fs.resolve_path(home_dir)
            existing_node = self.fs.get_node_info(resolved_home_dir)
            if not existing_node:
                if not self.fs.mkdir(resolved_home_dir):
                    logger.warning(
                        f"Could not create home directory {resolved_home_dir}"
                    )
            elif not existing_node.is_dir:
                logger.warning(
                    f"Home path {resolved_home_dir} exists but is not a directory"
                )
        except Exception as e:
            logger.error(f"Error processing home directory {home_dir}: {e}")

        try:
            if not self.fs.cd(home_dir):
                logger.warning(f"Could not change to home directory {home_dir}")
        except Exception as e:
            logger.error(f"Error changing to home directory {home_dir}: {e}")

    def _load_commands(self) -> None:
        """Dynamically load all available commands using the command loader."""
        discovered_commands = CommandLoader.discover_commands(self)
        self.commands.update(discovered_commands)

    def parse_command(self, cmd_line: str) -> Tuple[Optional[str], list]:
        """Parse a command line into the command name and arguments, respecting quotes."""
        if not cmd_line or not cmd_line.strip():
            return None, []

        # Use shlex to properly handle quoted strings
        import shlex

        try:
            parts = shlex.split(cmd_line.strip())
        except ValueError:
            # Fallback to simple split if shlex fails (e.g., unclosed quotes)
            parts = cmd_line.strip().split()

        if not parts:
            return None, []

        return parts[0], parts[1:]

    def execute(self, cmd_line: str) -> str:
        """
        Execute a command line synchronously, supporting pipes and redirection.

        Args:
            cmd_line (str): The full command line string.

        Returns:
            str: The output from the command execution.
        """
        cmd_line = cmd_line.strip()
        if not cmd_line:
            return ""

        # Store original for history before any expansions
        original_cmd_line = cmd_line

        # Handle command substitution $(command) and backticks
        cmd_line = self._expand_command_substitution(cmd_line)

        # Handle alias expansion
        cmd_line = self._expand_aliases(cmd_line)

        self.history.append(original_cmd_line)
        if cmd_line == "exit":
            self.running = False
            return "Goodbye!"

        # Check for logical operators (&&, ||) and command separator (;)
        if any(op in cmd_line for op in ["&&", "||", ";"]) and not self._contains_quoted_operator(cmd_line):
            return self._execute_with_operators(cmd_line)

        # Check for pipes (but not within quotes)
        if "|" in cmd_line and not self._is_quoted(cmd_line, cmd_line.index("|")):
            return self._execute_pipeline(cmd_line)

        # Apply expansions for simple commands (no operators)
        cmd_line = self._expand_variables(cmd_line)
        cmd_line = self._expand_globs(cmd_line)
        cmd_line = self._expand_tilde(cmd_line)

        # Check for input/output redirection
        redirect_out_file = None
        redirect_in_file = None
        append_mode = False

        # First, handle input redirection (<)
        if "<" in cmd_line:
            pos = cmd_line.index("<")
            if not self._is_quoted(cmd_line, pos):
                # Split command and input file
                cmd_part = cmd_line[:pos].strip()
                input_part = cmd_line[pos + 1 :].strip()

                # Check if there's also output redirection after input
                if ">>" in input_part:
                    pos2 = input_part.index(">>")
                    if not self._is_quoted(input_part, pos2):
                        redirect_in_file = input_part[:pos2].strip()
                        redirect_out_file = input_part[pos2 + 2 :].strip()
                        append_mode = True
                elif ">" in input_part:
                    pos2 = input_part.index(">")
                    if not self._is_quoted(input_part, pos2):
                        redirect_in_file = input_part[:pos2].strip()
                        redirect_out_file = input_part[pos2 + 1 :].strip()
                        append_mode = False
                else:
                    redirect_in_file = input_part

                # Parse the input file (might be quoted)
                if redirect_in_file:
                    import shlex

                    try:
                        parts = shlex.split(redirect_in_file)
                        if parts:
                            redirect_in_file = parts[0]
                            cmd_line = cmd_part
                    except ValueError:
                        redirect_in_file = None

                # Parse output file if present
                if redirect_out_file:
                    try:
                        parts = shlex.split(redirect_out_file)
                        if parts:
                            redirect_out_file = parts[0]
                    except ValueError:
                        redirect_out_file = None

        # If no input redirection, check for output redirection only
        if not redirect_in_file:
            # Look for >> first (append mode)
            if ">>" in cmd_line:
                pos = cmd_line.index(">>")
                if not self._is_quoted(cmd_line, pos):
                    # Split command and redirect file
                    cmd_part = cmd_line[:pos].strip()
                    redirect_part = cmd_line[pos + 2 :].strip()
                    if redirect_part:
                        # Parse the redirect file (might be quoted)
                        import shlex

                        try:
                            parts = shlex.split(redirect_part)
                            if parts:
                                redirect_out_file = parts[0]
                                append_mode = True
                                cmd_line = cmd_part
                        except ValueError:
                            pass
            # Look for > (overwrite mode)
            elif ">" in cmd_line:
                pos = cmd_line.index(">")
                if not self._is_quoted(cmd_line, pos):
                    # Split command and redirect file
                    cmd_part = cmd_line[:pos].strip()
                    redirect_part = cmd_line[pos + 1 :].strip()
                    if redirect_part:
                        # Parse the redirect file (might be quoted)
                        import shlex

                        try:
                            parts = shlex.split(redirect_part)
                            if parts:
                                redirect_out_file = parts[0]
                                append_mode = False
                                cmd_line = cmd_part
                        except ValueError:
                            pass

        # Handle input redirection
        if redirect_in_file:
            # Read the input file content
            input_content = self.fs.read_file(redirect_in_file)
            if input_content is None:
                return f"bash: {redirect_in_file}: No such file or directory"
            # Set stdin buffer for the command
            self._stdin_buffer = input_content

        # Execute the command
        cmd, args = self.parse_command(cmd_line)
        if not cmd:
            return ""

        if cmd in self.commands:
            try:
                # Track command timing if enabled
                start_time = time.time() if self.enable_timing else None

                # Use run() instead of execute() to handle async commands properly
                result = self.commands[cmd].run(args)

                # Record timing statistics
                if self.enable_timing and start_time:
                    elapsed = time.time() - start_time
                    if cmd not in self.command_timing:
                        self.command_timing[cmd] = {
                            "count": 0,
                            "total_time": 0.0,
                            "min_time": float("inf"),
                            "max_time": 0.0,
                        }
                    stats = self.command_timing[cmd]
                    stats["count"] += 1
                    stats["total_time"] += elapsed
                    stats["min_time"] = min(stats["min_time"], elapsed)
                    stats["max_time"] = max(stats["max_time"], elapsed)

                if cmd == "cd":
                    self.environ["PWD"] = self.fs.pwd()

                # Clear stdin buffer after command execution
                if hasattr(self, "_stdin_buffer"):
                    del self._stdin_buffer

                # Handle output redirection
                if redirect_out_file:
                    if append_mode:
                        # Append to file
                        existing = self.fs.read_file(redirect_out_file) or ""
                        if existing and not existing.endswith("\n"):
                            content = existing + "\n" + result
                        elif existing:
                            content = existing + result
                        else:
                            content = result
                        self.fs.write_file(redirect_out_file, content)
                    else:
                        # Overwrite file
                        self.fs.write_file(redirect_out_file, result)
                    return ""  # No output to terminal when redirecting

                return result
            except Exception as e:
                logger.error(f"Error executing command '{cmd}': {e}")
                return f"Error executing command: {e}"
        else:
            return f"{cmd}: command not found"

    def _expand_command_substitution(self, cmd_line: str, depth: int = 0) -> str:
        """
        Expand command substitutions in the form $(command) and `command`.

        Args:
            cmd_line: Command line potentially containing substitutions
            depth: Recursion depth to prevent infinite loops

        Returns:
            Command line with substitutions expanded
        """
        # Prevent infinite recursion
        if depth > 5:
            return cmd_line

        import re

        def substitute(match):
            # Execute the command and return its output
            command = match.group(1)
            # Execute without substitution to avoid recursion
            result = self._execute_without_substitution(command)
            # Remove trailing newline for substitution
            if result and result.endswith("\n"):
                result = result[:-1]
            return result

        # Find and replace $(command) patterns
        cmd_line = re.sub(r"\$\(([^)]+)\)", substitute, cmd_line)
        
        # Find and replace `command` patterns (backticks)
        cmd_line = re.sub(r"`([^`]+)`", substitute, cmd_line)
        
        return cmd_line

    def _execute_without_substitution(self, cmd_line: str) -> str:
        """Execute a command without expanding substitutions (to avoid recursion)."""
        cmd_line = cmd_line.strip()
        if not cmd_line:
            return ""

        # Check for pipes (but not within quotes)
        if "|" in cmd_line and not self._is_quoted(cmd_line, cmd_line.index("|")):
            return self._execute_pipeline(cmd_line)

        # Check for input/output redirection (rest of execute logic)
        # (Copy the rest of the execute method logic here but without the substitution call)
        redirect_out_file = None
        redirect_in_file = None
        append_mode = False

        # Handle input redirection
        if "<" in cmd_line:
            pos = cmd_line.index("<")
            if not self._is_quoted(cmd_line, pos):
                cmd_part = cmd_line[:pos].strip()
                input_part = cmd_line[pos + 1 :].strip()

                if ">>" in input_part:
                    pos2 = input_part.index(">>")
                    if not self._is_quoted(input_part, pos2):
                        redirect_in_file = input_part[:pos2].strip()
                        redirect_out_file = input_part[pos2 + 2 :].strip()
                        append_mode = True
                elif ">" in input_part:
                    pos2 = input_part.index(">")
                    if not self._is_quoted(input_part, pos2):
                        redirect_in_file = input_part[:pos2].strip()
                        redirect_out_file = input_part[pos2 + 1 :].strip()
                        append_mode = False
                else:
                    redirect_in_file = input_part

                if redirect_in_file:
                    import shlex

                    try:
                        parts = shlex.split(redirect_in_file)
                        if parts:
                            redirect_in_file = parts[0]
                    except ValueError:
                        pass

                    content = self.fs.read_file(redirect_in_file)
                    if content is None:
                        return f"{redirect_in_file}: No such file or directory"
                    self._stdin_buffer = content

                cmd_line = cmd_part

        # Handle output redirection
        if not redirect_out_file:
            if ">>" in cmd_line:
                pos = cmd_line.index(">>")
                if not self._is_quoted(cmd_line, pos):
                    cmd_line = cmd_line[:pos].strip()
                    redirect_out_file = cmd_line[pos + 2 :].strip()
                    append_mode = True
            elif ">" in cmd_line:
                pos = cmd_line.index(">")
                if not self._is_quoted(cmd_line, pos):
                    redirect_out_file = cmd_line[pos + 1 :].strip()
                    cmd_line = cmd_line[:pos].strip()
                    append_mode = False

        # Parse and execute command
        cmd, args = self.parse_command(cmd_line)
        if not cmd:
            return ""

        if cmd in self.commands:
            try:
                result = self.commands[cmd].run(args)
                if cmd == "cd":
                    self.environ["PWD"] = self.fs.pwd()

                if hasattr(self, "_stdin_buffer"):
                    del self._stdin_buffer

                if redirect_out_file:
                    if append_mode:
                        existing = self.fs.read_file(redirect_out_file) or ""
                        if existing and not existing.endswith("\n"):
                            content = existing + "\n" + result
                        elif existing:
                            content = existing + result
                        else:
                            content = result
                        self.fs.write_file(redirect_out_file, content)
                    else:
                        self.fs.write_file(redirect_out_file, result)
                    return ""

                return result
            except Exception as e:
                return f"Error executing command: {e}"
        else:
            return f"{cmd}: command not found"

    def _is_quoted(self, text: str, position: int) -> bool:
        """Check if a position in text is within quotes."""
        in_single = False
        in_double = False
        escaped = False

        for i, char in enumerate(text):
            if i >= position:
                return in_single or in_double

            if escaped:
                escaped = False
                continue

            if char == "\\":
                escaped = True
            elif char == '"' and not in_single:
                in_double = not in_double
            elif char == "'" and not in_double:
                in_single = not in_single

        return False

    def _execute_pipeline(self, cmd_line: str) -> str:
        """Execute a pipeline of commands connected by pipes."""
        # Apply expansions to the whole pipeline
        cmd_line = self._expand_variables(cmd_line)
        cmd_line = self._expand_globs(cmd_line)
        cmd_line = self._expand_tilde(cmd_line)
        
        # Check if the last command has redirection
        redirect_file = None
        append_mode = False
        input_file = None

        # First check for input redirection in the first command
        if "<" in cmd_line:
            # Find the first pipe
            pipe_pos = cmd_line.index("|") if "|" in cmd_line else len(cmd_line)
            first_cmd = cmd_line[:pipe_pos]

            if "<" in first_cmd:
                pos = first_cmd.index("<")
                if not self._is_quoted(first_cmd, pos):
                    # Extract input file
                    before_input = first_cmd[:pos].strip()
                    after_input = first_cmd[pos + 1 :].strip()

                    import shlex

                    try:
                        parts = shlex.split(after_input)
                        if parts:
                            input_file = parts[0]
                            # Reconstruct command line without input redirection
                            if pipe_pos < len(cmd_line):
                                cmd_line = before_input + cmd_line[pipe_pos:]
                            else:
                                cmd_line = before_input
                    except ValueError:
                        pass

        # Look for output redirection in the whole pipeline
        if ">>" in cmd_line:
            pos = cmd_line.rfind(">>")  # Find last occurrence
            if not self._is_quoted(cmd_line, pos):
                # Split at the last >>
                pipeline_part = cmd_line[:pos].strip()
                redirect_part = cmd_line[pos + 2 :].strip()
                if redirect_part:
                    import shlex

                    try:
                        parts = shlex.split(redirect_part)
                        if parts:
                            redirect_file = parts[0]
                            append_mode = True
                            cmd_line = pipeline_part
                    except ValueError:
                        pass
        elif ">" in cmd_line:
            pos = cmd_line.rfind(">")  # Find last occurrence
            if not self._is_quoted(cmd_line, pos):
                # Split at the last >
                pipeline_part = cmd_line[:pos].strip()
                redirect_part = cmd_line[pos + 1 :].strip()
                if redirect_part:
                    import shlex

                    try:
                        parts = shlex.split(redirect_part)
                        if parts:
                            redirect_file = parts[0]
                            append_mode = False
                            cmd_line = pipeline_part
                    except ValueError:
                        pass

        # Now execute the pipeline
        commands = cmd_line.split("|")
        result = ""

        for i, cmd_str in enumerate(commands):
            cmd_str = cmd_str.strip()
            if not cmd_str:
                continue

            # Parse the command
            cmd, args = self.parse_command(cmd_str)
            if not cmd:
                continue

            if cmd not in self.commands:
                return f"{cmd}: command not found"

            try:
                # Set stdin buffer for commands that support it
                if i == 0 and input_file:
                    # Read input file for the first command
                    content = self.fs.read_file(input_file)
                    if content is None:
                        return f"{input_file}: No such file or directory"
                    self._stdin_buffer = content
                elif i > 0 and result:
                    # Store the previous command's output as stdin for this command
                    self._stdin_buffer = result

                # Execute the command
                result = self.commands[cmd].run(args)

                # Clear stdin buffer
                if hasattr(self, "_stdin_buffer"):
                    del self._stdin_buffer

                # Check if the command returned an error
                if result and (
                    result.startswith(f"{cmd}: ")
                    and ("No such file" in result or "error" in result.lower())
                ):
                    # Error occurred, stop pipeline and return error
                    return result

            except Exception as e:
                logger.error(f"Error executing command '{cmd}' in pipeline: {e}")
                return f"Error executing command in pipeline: {e}"

        # Handle output redirection if specified
        if redirect_file:
            if append_mode:
                # Append to file
                existing = self.fs.read_file(redirect_file) or ""
                if existing and not existing.endswith("\n"):
                    content = existing + "\n" + result
                elif existing:
                    content = existing + result
                else:
                    content = result
                self.fs.write_file(redirect_file, content)
            else:
                # Overwrite file
                self.fs.write_file(redirect_file, result)
            return ""  # No output to terminal when redirecting

        return result

    async def execute_async(self, cmd_line: str) -> str:
        """
        Execute a command line asynchronously.

        Args:
            cmd_line (str): The full command line string.

        Returns:
            str: The output from the command execution.
        """
        cmd_line = cmd_line.strip()
        if not cmd_line:
            return ""
        self.history.append(cmd_line)
        if cmd_line == "exit":
            self.running = False
            return "Goodbye!"
        cmd, args = self.parse_command(cmd_line)
        if not cmd:
            return ""
        if cmd in self.commands:
            try:
                command = self.commands[cmd]
                # Check if command supports async execution
                if hasattr(command, "execute_async") and inspect.iscoroutinefunction(
                    command.execute_async
                ):
                    result = await command.execute_async(args)
                else:
                    # Fall back to synchronous execution for backward compatibility
                    result = command.execute(args)

                if cmd == "cd":
                    self.environ["PWD"] = self.fs.pwd()
                return result
            except Exception as e:
                logger.error(f"Error executing command '{cmd}' asynchronously: {e}")
                return f"Error executing command: {e}"
        else:
            return f"{cmd}: command not found"

    def prompt(self) -> str:
        """Return the formatted command prompt."""
        username = self.environ.get("USER", "user")
        hostname = "pyodide"
        pwd = self.environ.get("PWD", "/")
        return f"{username}@{hostname}:{pwd}$ "

    def complete(self, text: str, state: int) -> Optional[str]:
        """Stub for tab completion (to be implemented)."""
        return None

    def _load_shellrc(self):
        """Load and execute .shellrc file if it exists."""
        shellrc_paths = [
            f"{self.environ.get('HOME', '/home/user')}/.shellrc",
            "/.shellrc",
        ]

        for rc_path in shellrc_paths:
            try:
                if self.fs.exists(rc_path) and self.fs.is_file(rc_path):
                    content = self.fs.read_file(rc_path)
                    if content:
                        logger.info(f"Loading shell configuration from {rc_path}")
                        # Execute each line in the .shellrc file
                        for line in content.splitlines():
                            line = line.strip()
                            # Skip comments and empty lines
                            if line and not line.startswith("#"):
                                try:
                                    # For alias commands, don't expand variables
                                    # They should be expanded when the alias is used
                                    if line.startswith("alias "):
                                        # Parse and execute alias directly
                                        parts = line[6:].strip()  # Remove "alias "
                                        if "alias" in self.commands:
                                            self.commands["alias"].execute([parts])
                                    else:
                                        # Execute the command normally
                                        result = self.execute(line)
                                        # Check if command was not found
                                        if result and "command not found" in result.lower():
                                            logger.warning(
                                                f"Error executing .shellrc line '{line}': {result}"
                                            )
                                except Exception as e:
                                    logger.warning(
                                        f"Error executing .shellrc line '{line}': {e}"
                                    )
                        break  # Only load the first found .shellrc
            except Exception as e:
                logger.debug(f"Could not load {rc_path}: {e}")

    def _expand_aliases(self, cmd_line):
        """Expand aliases in the command line."""
        if not hasattr(self, "aliases") or not self.aliases:
            return cmd_line

        # Split the command line to get the first word (command)
        import shlex

        try:
            parts = shlex.split(cmd_line)
            if not parts:
                return cmd_line
        except ValueError:
            # If shlex fails, try simple split
            parts = cmd_line.split()
            if not parts:
                return cmd_line

        # Check if the first word is an alias
        cmd = parts[0]
        if cmd in self.aliases:
            # Replace with alias value
            alias_value = self.aliases[cmd]
            if len(parts) > 1:
                # Append remaining arguments
                expanded = alias_value + " " + " ".join(parts[1:])
            else:
                expanded = alias_value

            # Prevent infinite recursion by tracking expansion depth
            if not hasattr(self, "_alias_depth"):
                self._alias_depth = 0

            self._alias_depth += 1
            if self._alias_depth < 10:  # Max recursion depth
                # Recursively expand in case alias contains other aliases
                expanded = self._expand_aliases(expanded)

            self._alias_depth -= 1
            if self._alias_depth == 0:
                del self._alias_depth

            return expanded

        return cmd_line

    # Helper methods.
    def user_exists(self, target: str) -> bool:
        """Return True if the target user exists, otherwise False."""
        return target == self.environ.get("USER", "user")

    def group_exists(self, target: str) -> bool:
        """Return True if the target group exists, otherwise False."""
        return target == "staff"

    def exists(self, path: str) -> bool:
        """Return True if a node exists at the given path, otherwise False."""
        try:
            return self.get_node_info(path) is not None
        except Exception:
            return False

    def get_node_info(self, path: str) -> Optional[object]:
        """
        Return node information for the given path using the provider, or None if not found.
        """
        resolved_path = self.resolve_path(path)
        return self.fs.provider.get_node_info(resolved_path)

    def _register_command(self, command):
        """Register a single command with the shell."""
        self.commands[command.name] = command

    def _expand_variables(self, cmd_line: str) -> str:
        """
        Expand environment variables in the command line.
        Supports $VAR and ${VAR} syntax.
        """
        import re

        # Special variables
        cmd_line = cmd_line.replace("$?", str(self.return_code))
        cmd_line = cmd_line.replace("$$", str(id(self)))
        cmd_line = cmd_line.replace("$#", "0")

        # Expand ${VAR} format
        def expand_braces(match):
            var_name = match.group(1)
            return self.environ.get(var_name, "")

        cmd_line = re.sub(r"\$\{([^}]+)\}", expand_braces, cmd_line)

        # Expand $VAR format - but only if VAR starts with letter/underscore
        # and consists of alphanumeric/underscore chars
        def expand_simple(match):
            var_name = match.group(1)
            # Don't expand single lowercase letters (like $d in sed)
            # These are often special patterns in commands
            if len(var_name) == 1 and var_name.islower():
                return match.group(0)  # Keep original
            # Always expand to the value (empty string if not found)
            return self.environ.get(var_name, "")

        # Match $VARNAME where VARNAME is alphanumeric starting with letter/underscore
        cmd_line = re.sub(r"\$([A-Za-z_][A-Za-z0-9_]*)", expand_simple, cmd_line)

        return cmd_line

    def _expand_globs(self, cmd_line: str) -> str:
        """
        Expand glob patterns (wildcards) in the command line.
        Supports *, ?, and [].
        """
        import glob as glob_module
        import shlex

        try:
            # Parse the command line preserving quotes
            parts = shlex.split(cmd_line)
        except ValueError:
            # If shlex fails, return as-is
            return cmd_line

        expanded_parts = []
        for part in parts:
            # Check if this part contains glob characters
            if any(char in part for char in ["*", "?", "["]):
                # Try to expand the glob pattern
                # Convert virtual FS paths to match against
                if part.startswith("/"):
                    # Absolute path
                    base_path = "/"
                    pattern = part[1:] if len(part) > 1 else ""
                else:
                    # Relative path
                    base_path = self.fs.pwd()
                    pattern = part

                matches = self._match_glob_pattern(base_path, pattern)
                if matches:
                    expanded_parts.extend(matches)
                else:
                    # No matches, keep the pattern as-is
                    expanded_parts.append(part)
            else:
                expanded_parts.append(part)

        # Reconstruct the command line, preserving empty strings
        result_parts = []
        for part in expanded_parts:
            if part == "":
                # Preserve empty strings with quotes
                result_parts.append('""')
            elif " " in part:
                result_parts.append(shlex.quote(part))
            else:
                result_parts.append(part)
        return " ".join(result_parts)

    def _match_glob_pattern(self, base_path: str, pattern: str) -> list:
        """
        Match glob pattern against files in the virtual filesystem.
        """
        import fnmatch
        import os

        matches = []
        
        # Handle absolute vs relative patterns
        if pattern.startswith("/"):
            search_path = "/"
            pattern = pattern[1:]
        else:
            search_path = base_path

        # Get the directory to search in
        if "/" in pattern:
            # Pattern includes directory
            dir_parts = pattern.rsplit("/", 1)
            search_dir = os.path.join(search_path, dir_parts[0])
            file_pattern = dir_parts[1]
        else:
            # Pattern is just for files in current/base directory
            search_dir = search_path
            file_pattern = pattern

        # List files in the search directory
        try:
            entries = self.fs.ls(search_dir)
            if entries:
                for entry in entries:
                    # Skip . and ..
                    if entry in [".", ".."]:
                        continue
                    
                    # Check if the entry matches the pattern
                    if fnmatch.fnmatch(entry, file_pattern):
                        # For relative patterns, return just the filename
                        # For absolute patterns, return the full path
                        if search_path == base_path and not pattern.startswith("/"):
                            # Relative pattern in current directory
                            matches.append(entry)
                        else:
                            # Absolute pattern or pattern with directory
                            if search_dir == "/":
                                full_path = "/" + entry
                            else:
                                full_path = os.path.join(search_dir, entry).replace("\\", "/")
                            matches.append(full_path)
        except:
            pass

        return sorted(matches)

    def _expand_tilde(self, cmd_line: str) -> str:
        """
        Expand tilde (~) to home directory.
        """
        import shlex

        try:
            parts = shlex.split(cmd_line)
        except ValueError:
            parts = cmd_line.split()

        expanded_parts = []
        home = self.environ.get("HOME", "/home/user")

        for part in parts:
            if part == "~":
                expanded_parts.append(home)
            elif part.startswith("~/"):
                expanded_parts.append(home + part[1:])
            else:
                expanded_parts.append(part)

        # Reconstruct the command line, preserving empty strings
        result_parts = []
        for part in expanded_parts:
            if part == "":
                # Preserve empty strings with quotes
                result_parts.append('""')
            elif " " in part:
                result_parts.append(shlex.quote(part))
            else:
                result_parts.append(part)
        return " ".join(result_parts)

    def _contains_quoted_operator(self, cmd_line: str) -> bool:
        """
        Check if logical operators or semicolons are within quotes.
        """
        for op in ["&&", "||", ";"]:
            if op in cmd_line:
                idx = cmd_line.index(op)
                if self._is_quoted(cmd_line, idx):
                    return True
        return False

    def _execute_with_operators(self, cmd_line: str) -> str:
        """
        Execute command line with logical operators (&&, ||) and semicolon separator.
        """
        import re

        # Split by operators while preserving them
        parts = re.split(r'(&&|\|\||;)', cmd_line)
        
        results = []
        i = 0
        skip_next = False
        
        while i < len(parts):
            if i % 2 == 0:  # Command part
                cmd = parts[i].strip()
                if cmd and not skip_next:
                    # Execute the individual command
                    result = self._execute_single_command(cmd)
                    
                    # Store the result if there's output
                    if result:
                        results.append(result)
                    
                    # Check the next operator to determine flow
                    if i + 1 < len(parts):
                        operator = parts[i + 1].strip()
                        
                        if operator == "&&":
                            # Continue only if command succeeded (return code 0)
                            if self.return_code != 0:
                                skip_next = True
                        elif operator == "||":
                            # Continue only if command failed (return code != 0)
                            if self.return_code == 0:
                                skip_next = True
                        elif operator == ";":
                            # Always continue with semicolon
                            skip_next = False
                else:
                    skip_next = False
            i += 1
        
        return "\n".join(results)

    def _execute_single_command(self, cmd_line: str) -> str:
        """
        Execute a single command (no operators, but may have pipes/redirects).
        """
        cmd_line = cmd_line.strip()
        if not cmd_line:
            return ""

        # Apply expansions now that we're executing a single command
        cmd_line = self._expand_variables(cmd_line)
        cmd_line = self._expand_globs(cmd_line)
        cmd_line = self._expand_tilde(cmd_line)

        # Check for pipes
        if "|" in cmd_line and not self._is_quoted(cmd_line, cmd_line.index("|")):
            return self._execute_pipeline(cmd_line)

        # Handle regular command with possible redirection
        return self._execute_command_with_redirect(cmd_line)

    def _execute_command_with_redirect(self, cmd_line: str) -> str:
        """
        Execute a command with possible input/output redirection.
        This is the core single command execution logic extracted from execute().
        """
        # Check for input/output redirection
        redirect_out_file = None
        redirect_in_file = None
        append_mode = False

        # First, handle input redirection (<)
        if "<" in cmd_line:
            pos = cmd_line.index("<")
            if not self._is_quoted(cmd_line, pos):
                # Split command and input file
                cmd_part = cmd_line[:pos].strip()
                input_part = cmd_line[pos + 1 :].strip()

                # Check if there's also output redirection after input
                if ">>" in input_part:
                    pos2 = input_part.index(">>")
                    if not self._is_quoted(input_part, pos2):
                        redirect_in_file = input_part[:pos2].strip()
                        redirect_out_file = input_part[pos2 + 2 :].strip()
                        append_mode = True
                elif ">" in input_part:
                    pos2 = input_part.index(">")
                    if not self._is_quoted(input_part, pos2):
                        redirect_in_file = input_part[:pos2].strip()
                        redirect_out_file = input_part[pos2 + 1 :].strip()
                        append_mode = False
                else:
                    redirect_in_file = input_part

                # Parse the input file (might be quoted)
                if redirect_in_file:
                    import shlex

                    try:
                        parts = shlex.split(redirect_in_file)
                        if parts:
                            redirect_in_file = parts[0]
                            cmd_line = cmd_part
                    except ValueError:
                        redirect_in_file = None

                # Parse output file if present
                if redirect_out_file:
                    try:
                        parts = shlex.split(redirect_out_file)
                        if parts:
                            redirect_out_file = parts[0]
                    except ValueError:
                        redirect_out_file = None

        # If no input redirection, check for output redirection only
        if not redirect_in_file:
            # Look for >> first (append mode)
            if ">>" in cmd_line:
                pos = cmd_line.index(">>")
                if not self._is_quoted(cmd_line, pos):
                    # Split command and redirect file
                    cmd_part = cmd_line[:pos].strip()
                    redirect_part = cmd_line[pos + 2 :].strip()
                    if redirect_part:
                        # Parse the redirect file (might be quoted)
                        import shlex

                        try:
                            parts = shlex.split(redirect_part)
                            if parts:
                                redirect_out_file = parts[0]
                                append_mode = True
                                cmd_line = cmd_part
                        except ValueError:
                            pass
            # Look for > (overwrite mode)
            elif ">" in cmd_line:
                pos = cmd_line.index(">")
                if not self._is_quoted(cmd_line, pos):
                    # Split command and redirect file
                    cmd_part = cmd_line[:pos].strip()
                    redirect_part = cmd_line[pos + 1 :].strip()
                    if redirect_part:
                        # Parse the redirect file (might be quoted)
                        import shlex

                        try:
                            parts = shlex.split(redirect_part)
                            if parts:
                                redirect_out_file = parts[0]
                                append_mode = False
                                cmd_line = cmd_part
                        except ValueError:
                            pass

        # Handle input redirection
        if redirect_in_file:
            # Read the input file content
            input_content = self.fs.read_file(redirect_in_file)
            if input_content is None:
                self.return_code = 1
                return f"bash: {redirect_in_file}: No such file or directory"
            # Set stdin buffer for the command
            self._stdin_buffer = input_content

        # Execute the command
        cmd, args = self.parse_command(cmd_line)
        if not cmd:
            return ""

        if cmd in self.commands:
            try:
                # Track command timing if enabled
                start_time = time.time() if self.enable_timing else None

                # Use run() instead of execute() to handle async commands properly
                result = self.commands[cmd].run(args)
                self.return_code = 0  # Success

                # Record timing statistics
                if self.enable_timing and start_time:
                    elapsed = time.time() - start_time
                    if cmd not in self.command_timing:
                        self.command_timing[cmd] = {
                            "count": 0,
                            "total_time": 0.0,
                            "min_time": float("inf"),
                            "max_time": 0.0,
                        }
                    stats = self.command_timing[cmd]
                    stats["count"] += 1
                    stats["total_time"] += elapsed
                    stats["min_time"] = min(stats["min_time"], elapsed)
                    stats["max_time"] = max(stats["max_time"], elapsed)

                if cmd == "cd":
                    self.environ["PWD"] = self.fs.pwd()

                # Clear stdin buffer after command execution
                if hasattr(self, "_stdin_buffer"):
                    del self._stdin_buffer

                # Handle output redirection
                if redirect_out_file:
                    if append_mode:
                        # Append to file
                        existing = self.fs.read_file(redirect_out_file) or ""
                        if existing and not existing.endswith("\n"):
                            content = existing + "\n" + result
                        elif existing:
                            content = existing + result
                        else:
                            content = result
                        self.fs.write_file(redirect_out_file, content)
                    else:
                        # Overwrite file
                        self.fs.write_file(redirect_out_file, result)
                    return ""  # No output to terminal when redirecting

                return result
            except Exception as e:
                logger.error(f"Error executing command '{cmd}': {e}")
                self.return_code = 1
                return f"Error executing command: {e}"
        else:
            self.return_code = 127  # Command not found
            return f"{cmd}: command not found"
