# src/chuk_virtual_shell/shell_interpreter.py
"""
chuk_virtual_shell/shell_interpreter.py - Core shell interpreter

This module implements the ShellInterpreter class which orchestrates the virtual
shell by coordinating between specialized components for parsing, expansion,
execution, and environment management.
"""

import logging
import traceback
import time
import inspect
from typing import Optional, Tuple

# Virtual file system imports
from chuk_virtual_fs import VirtualFileSystem  # type: ignore
from chuk_virtual_shell.commands.command_loader import CommandLoader
from chuk_virtual_shell.filesystem_compat import FileSystemCompat

# Core component imports
from chuk_virtual_shell.core.expansion import ExpansionHandler
from chuk_virtual_shell.core.parser import CommandParser
from chuk_virtual_shell.core.executor import CommandExecutor
from chuk_virtual_shell.core.environment import EnvironmentManager
from chuk_virtual_shell.core.control_flow_executor import ControlFlowExecutor

# Configure module-level logger
logger = logging.getLogger(__name__)


class ShellInterpreter:
    """
    Main shell interpreter that orchestrates between components.
    
    This class serves as the central coordinator, delegating specialized
    tasks to dedicated components while maintaining the shell state.
    """
    
    def __init__(self, fs_provider=None, fs_provider_args=None, sandbox_yaml=None):
        """
        Initialize the shell interpreter.

        Args:
            fs_provider (str, optional): Filesystem provider name.
            fs_provider_args (dict, optional): Arguments for the filesystem provider.
            sandbox_yaml (str, optional): Path or name of a YAML sandbox configuration.
        """
        # Store sandbox config for later processing
        self._sandbox_yaml = sandbox_yaml
        
        # Initialize filesystem first (without sandbox environment setup)
        self._initialize_filesystem(fs_provider, fs_provider_args, None)
        
        # Initialize core components (env_manager needs filesystem)
        self.env_manager = EnvironmentManager(self)
        self.environ = self.env_manager.environ  # Compatibility alias
        
        # Now handle sandbox initialization if provided
        if sandbox_yaml:
            self._finish_sandbox_initialization(sandbox_yaml)
            # Update environ alias after sandbox loading
            self.environ = self.env_manager.environ
        else:
            self.env_manager.ensure_home_directory()
        
        self.parser = CommandParser()
        self.expansion = ExpansionHandler(self)
        self.executor = CommandExecutor(self)
        self._control_flow_executor = ControlFlowExecutor(self)
        
        # Initialize shell state
        self.history = []
        self.running = True
        self.return_code = 0
        self.start_time = time.time()
        
        # Command timing statistics
        self.command_timing = {}
        self.enable_timing = False
        
        # Set current user from environment
        self.current_user = self.environ.get("USER", "user")
        
        # Provide a resolve_path method that delegates to the filesystem
        self.resolve_path = lambda path: self.fs.resolve_path(path)
        
        # Load commands dynamically
        self.commands = {}
        self._load_commands()
        
        # Initialize optional features
        self._initialize_optional_features(sandbox_yaml)
        
        # Load shell configuration (skip in sandbox mode for security)
        if not self._sandbox_yaml:
            self.env_manager.load_shellrc()
    
    def _initialize_filesystem(self, fs_provider, fs_provider_args, sandbox_yaml):
        """Initialize the filesystem based on provided configuration."""
        if sandbox_yaml:
            self._initialize_from_sandbox(sandbox_yaml)
        elif fs_provider:
            self._initialize_with_provider(fs_provider, fs_provider_args, sandbox_yaml)
        else:
            raw_fs = VirtualFileSystem()
            self.fs = FileSystemCompat(raw_fs)
    
    def _initialize_from_sandbox(self, sandbox_yaml: str) -> None:
        """This method is no longer used - sandbox initialization moved to _finish_sandbox_initialization."""
        # This method is kept for compatibility but does nothing
        # The actual sandbox initialization happens in _finish_sandbox_initialization
        pass
    
    def _initialize_with_provider(self, fs_provider: str, fs_provider_args: dict, sandbox_yaml: str = None) -> None:
        """Initialize filesystem using the specified provider and arguments."""
        try:
            raw_fs = VirtualFileSystem(fs_provider, **(fs_provider_args or {}))
            self.fs = FileSystemCompat(raw_fs)
        except Exception as e:
            logger.error(f"Error initializing filesystem provider '{fs_provider}': {e}")
            
            # Provide helpful guidance for common provider errors
            if fs_provider == 's3':
                if 'bucket_name' in str(e):
                    logger.error("S3 provider requires a 'bucket_name' argument.")
                    logger.error("Example: --fs-provider s3 --fs-provider-args '{\"bucket_name\": \"my-bucket\"}'")
                elif '403' in str(e) or 'Forbidden' in str(e) or 'credentials' in str(e).lower() or 'Failed to initialize provider' in str(e):
                    logger.error("S3 access denied - check your AWS credentials and permissions.")
                    logger.error("Set AWS credentials using one of these methods:")
                    logger.error("  • Environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY")
                    logger.error("  • For Tigris: Set TIGRIS_ACCESS_KEY_ID and TIGRIS_SECRET_ACCESS_KEY")
                    logger.error("  • AWS CLI: aws configure")
                    logger.error("  • IAM role (if running on EC2)")
                    logger.error("  • AWS credentials file: ~/.aws/credentials")
                    if sandbox_yaml and 'tigris' in sandbox_yaml.lower():
                        logger.error("  • Tigris sandbox requires: https://console.tigris.dev/ account and API keys")
                elif '404' in str(e) or 'NoSuchBucket' in str(e):
                    logger.error("S3 bucket not found - check bucket name and region.")
                elif 'region' in str(e).lower():
                    logger.error("S3 region issue - try specifying region in provider args.")
                    logger.error("Example: --fs-provider-args '{\"bucket_name\": \"my-bucket\", \"region_name\": \"us-east-1\"}'")
                else:
                    logger.error("S3 provider initialization failed.")
                    logger.error("Check bucket name, AWS credentials, and permissions.")
            elif fs_provider == 'sqlite' and ('path' in str(e) or 'db_path' in str(e)):
                logger.error("SQLite provider may need a 'db_path' argument.")
                logger.error("Example: --fs-provider sqlite --fs-provider-args 'db_path=my_shell.db'")
            
            logger.info("Falling back to memory provider.")
            raw_fs = VirtualFileSystem()
            self.fs = FileSystemCompat(raw_fs)
    
    def _finish_sandbox_initialization(self, sandbox_yaml: str) -> None:
        """Complete sandbox initialization after env_manager is created."""
        from chuk_virtual_shell.sandbox.loader.sandbox_config_loader import (
            load_config_file, find_config_file
        )
        from chuk_virtual_shell.sandbox.loader.filesystem_initializer import (
            create_filesystem
        )
        from chuk_virtual_shell.sandbox.loader.initialization_executor import (
            execute_initialization
        )
        from chuk_virtual_shell.sandbox.loader.mcp_loader import load_mcp_servers
        
        try:
            # Resolve configuration file path
            if not sandbox_yaml.endswith((".yaml", ".yml")) and "/" not in sandbox_yaml:
                config_path = find_config_file(sandbox_yaml)
                if not config_path:
                    raise ValueError(f"Sandbox configuration '{sandbox_yaml}' not found")
            else:
                config_path = sandbox_yaml
            
            # Load the sandbox configuration
            config = load_config_file(config_path)
            
            # Replace filesystem with sandbox-configured one
            raw_fs = create_filesystem(config)
            self.fs = FileSystemCompat(raw_fs)
            
            # Set up the environment (now that env_manager exists)
            self.env_manager.load_from_sandbox(config)
            
            # Execute initialization commands
            init_commands = config.get("initialization", [])
            if init_commands:
                execute_initialization(self.fs.fs, init_commands)
            
            # Load MCP servers if specified
            if 'mcp_servers' in config:
                self.mcp_servers = load_mcp_servers(config.get('mcp_servers', []))
                
            logger.info(f"Sandbox '{config.get('name', 'unknown')}' loaded successfully")
            
        except Exception as e:
            logger.error(f"Error completing sandbox configuration '{sandbox_yaml}': {e}")
            logger.exception("Detailed sandbox error:")
            # Fall back to default environment setup
            self.env_manager.setup_default_environment()
            self.env_manager.ensure_home_directory()
    
    def _initialize_optional_features(self, sandbox_yaml):
        """Initialize optional features like MCP servers and aliases."""
        # Initialize MCP servers list if not already set
        if not hasattr(self, "mcp_servers"):
            self.mcp_servers = []
        
        # Initialize aliases dictionary
        if not hasattr(self, "aliases"):
            self.aliases = {}
    
    def _load_commands(self) -> None:
        """Dynamically load all available commands using the command loader."""
        discovered_commands = CommandLoader.discover_commands(self)
        self.commands.update(discovered_commands)
    
    def parse_command(self, cmd_line: str) -> Tuple[Optional[str], list]:
        """
        Parse a command line into the command name and arguments.
        
        Delegates to the CommandParser component.
        """
        return self.parser.parse_command(cmd_line)
    
    def execute(self, cmd_line: str) -> str:
        """
        Execute a command line synchronously.
        
        This is the main entry point for command execution. It handles:
        - Command history
        - Command substitution
        - Alias expansion
        - Delegates actual execution to CommandExecutor
        
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
        cmd_line = self.expansion.expand_command_substitution(cmd_line)
        
        # Handle alias expansion
        cmd_line = self.expansion.expand_aliases(cmd_line)
        
        # Add to history
        self.history.append(original_cmd_line)
        
        # Delegate execution to the executor
        return self.executor.execute_line(cmd_line)
    
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
                    # Fall back to synchronous execution
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
        """
        Tab completion stub.
        
        Args:
            text: Text to complete
            state: Completion state
            
        Returns:
            Completed text or None
        """
        # TODO: Implement tab completion
        return None
    
    # Helper methods for backward compatibility
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
        Return node information for the given path using the provider.
        
        Args:
            path: Path to check
            
        Returns:
            Node info or None if not found
        """
        resolved_path = self.resolve_path(path)
        return self.fs.provider.get_node_info(resolved_path)
    
    def _register_command(self, command):
        """
        Register a single command with the shell.
        
        Args:
            command: Command instance to register
        """
        self.commands[command.name] = command
    
    # Delegation methods for backward compatibility
    def _expand_variables(self, cmd_line: str) -> str:
        """Expand environment variables (delegates to ExpansionHandler)."""
        return self.expansion.expand_variables(cmd_line)
    
    def _expand_globs(self, cmd_line: str) -> str:
        """Expand glob patterns (delegates to ExpansionHandler)."""
        return self.expansion.expand_globs(cmd_line)
    
    def _expand_tilde(self, cmd_line: str) -> str:
        """Expand tildes (delegates to ExpansionHandler)."""
        return self.expansion.expand_tilde(cmd_line)
    
    def _expand_aliases(self, cmd_line: str) -> str:
        """Expand aliases (delegates to ExpansionHandler)."""
        return self.expansion.expand_aliases(cmd_line)
    
    def _is_quoted(self, text: str, position: int) -> bool:
        """Check if position is quoted (delegates to CommandParser)."""
        return self.parser.is_quoted(text, position)