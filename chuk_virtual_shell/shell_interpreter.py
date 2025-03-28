"""
chuk_virtual_shell/shell_interpreter.py - Core shell interpreter for PyodideShell

This module implements the ShellInterpreter class which initializes the virtual
filesystem, loads environment variables (optionally from a YAML sandbox configuration),
and dynamically discovers and registers shell commands. It also provides methods
for parsing, executing commands, and managing the shell state.
"""

import logging
import traceback
import time
from typing import Optional

from chuk_virtual_fs import VirtualFileSystem
from chuk_virtual_shell.commands.command_loader import CommandLoader

# Configure module-level logger.
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


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
            self.fs = VirtualFileSystem()
            self._setup_default_environment()

        # Initialize history, running flag, and return code.
        self.history = []
        self.running = True
        self.return_code = 0

        # Record start time (useful for uptime commands).
        self.start_time = time.time()

        # NEW: Set current_user based on environment.
        self.current_user = self.environ.get("USER", "user")

        # NEW: Provide a resolve_path method that delegates to the filesystem.
        self.resolve_path = lambda path: self.fs.resolve_path(path)

        # Dynamically load commands.
        self.commands = {}
        self._load_commands()

    def _initialize_from_sandbox(self, sandbox_yaml: str) -> None:
        """Initialize filesystem and environment using a YAML sandbox configuration."""
        from chuk_virtual_shell.sandbox_loader import (
            load_sandbox_config, create_filesystem_from_config,
            get_environment_from_config, find_sandbox_config
        )

        try:
            # Resolve configuration file path.
            if not sandbox_yaml.endswith(('.yaml', '.yml')) and '/' not in sandbox_yaml:
                config_path = find_sandbox_config(sandbox_yaml)
                if not config_path:
                    raise ValueError(f"Sandbox configuration '{sandbox_yaml}' not found")
            else:
                config_path = sandbox_yaml

            # Load configuration.
            config = load_sandbox_config(config_path)

            # Create filesystem.
            try:
                self.fs = create_filesystem_from_config(config)
            except Exception as fs_error:
                logger.error(f"Error creating filesystem: {fs_error}")
                traceback.print_exc()
                self.fs = VirtualFileSystem()

            # Set environment from config.
            env_config = config.get('environment', {})
            self.environ = {
                "HOME": env_config.get('HOME', '/sandbox'),
                "PATH": env_config.get('PATH', '/bin'),
                "USER": env_config.get('USER', 'ai'),
                "SHELL": env_config.get('SHELL', '/bin/pyodide-shell'),
                "TERM": env_config.get('TERM', 'xterm'),
                "PWD": "/"
            }
            for key, value in env_config.items():
                if key not in self.environ:
                    self.environ[key] = value

            # Ensure home directory exists and is accessible.
            self._ensure_home_directory(self.environ['HOME'])

            logger.info(f"Using sandbox configuration: {config.get('name', 'custom')}")
            logger.info(f"Home directory set to: {self.environ['HOME']}")
            logger.info("Environment variables:")
            for key, value in self.environ.items():
                logger.info(f"  {key}: {value}")
        except Exception as e:
            logger.error(f"Error loading sandbox configuration '{sandbox_yaml}': {e}")
            traceback.print_exc()
            logger.info("Falling back to default configuration.")
            self.fs = VirtualFileSystem()
            self._setup_default_environment()

    def _initialize_with_provider(self, fs_provider: str, fs_provider_args: dict) -> None:
        """Initialize filesystem using the specified provider and arguments."""
        try:
            self.fs = VirtualFileSystem(fs_provider, **(fs_provider_args or {}))
            self._setup_default_environment()
        except Exception as e:
            logger.error(f"Error initializing filesystem provider '{fs_provider}': {e}")
            logger.info("Falling back to memory provider.")
            self.fs = VirtualFileSystem()
            self._setup_default_environment()

    def _setup_default_environment(self) -> None:
        """Set up default environment variables and create a default home directory."""
        default_home = "/home/user"
        try:
            resolved_home_dir = self.fs.resolve_path(default_home)
            existing_node = self.fs.get_node_info(resolved_home_dir)
            if not existing_node:
                if not self.fs.mkdir(resolved_home_dir):
                    logger.warning(f"Could not create home directory {resolved_home_dir}")
            elif not existing_node.is_dir:
                logger.warning(f"Home path {resolved_home_dir} exists but is not a directory")
        except Exception as mkdir_error:
            logger.error(f"Error processing home directory {default_home}: {mkdir_error}")

        self.environ = {
            "HOME": default_home,
            "PATH": "/bin:/usr/bin",
            "USER": "user",
            "SHELL": "/bin/pyodide-shell",
            "PWD": "/",
            "TERM": "xterm",
        }

    def _ensure_home_directory(self, home_dir: str) -> None:
        """Ensure that the specified home directory exists and is accessible."""
        try:
            resolved_home_dir = self.fs.resolve_path(home_dir)
            existing_node = self.fs.get_node_info(resolved_home_dir)
            if not existing_node:
                if not self.fs.mkdir(resolved_home_dir):
                    logger.warning(f"Could not create home directory {resolved_home_dir}")
            elif not existing_node.is_dir:
                logger.warning(f"Home path {resolved_home_dir} exists but is not a directory")
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

    def parse_command(self, cmd_line: str) -> (str, list):
        """Parse a command line into the command name and arguments."""
        if not cmd_line or not cmd_line.strip():
            return None, []
        parts = cmd_line.strip().split()
        return parts[0], parts[1:]

    def execute(self, cmd_line: str) -> str:
        """
        Execute a command line.
        
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
                result = self.commands[cmd].execute(args)
                if cmd == "cd":
                    self.environ["PWD"] = self.fs.pwd()
                return result
            except Exception as e:
                logger.error(f"Error executing command '{cmd}': {e}")
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

    # Helper method to check if a user exists.
    def user_exists(self, target: str) -> bool:
        """Return True if the target user exists, otherwise False."""
        return target == self.environ.get("USER", "user")

    # Helper method to check if a group exists.
    def group_exists(self, target: str) -> bool:
        """Return True if the target group exists, otherwise False."""
        return target == "staff"

    # Helper method to check if a node exists at the given path.
    def exists(self, path: str) -> bool:
        """Return True if a node exists at the given path, otherwise False."""
        try:
            return self.get_node_info(path) is not None
        except Exception:
            return False

    # Get node information using the provider.
    def get_node_info(self, path: str) -> Optional[object]:
        """Return node information for the given path using the provider, or None if not found."""
        resolved_path = self.resolve_path(path)
        return self.fs.provider.get_node_info(resolved_path)

    # Internal method to register commands.
    def _register_command(self, command):
        self.commands[command.name] = command
