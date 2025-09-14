# src/chuk_virtual_shell/core/environment.py
"""
chuk_virtual_shell/core/environment.py - Environment and initialization management

Manages shell environment variables, initialization, and configuration loading.
"""

import logging
from typing import Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from chuk_virtual_shell.shell_interpreter import ShellInterpreter

logger = logging.getLogger(__name__)


class EnvironmentManager:
    """Manages shell environment variables and initialization."""
    
    def __init__(self, shell: 'ShellInterpreter'):
        self.shell = shell
        self.environ = {}
        self.setup_default_environment()
    
    def setup_default_environment(self) -> None:
        """Set up default environment variables."""
        self.environ = {
            "HOME": "/home/user",
            "PATH": "/bin:/usr/bin",
            "USER": "user",
            "SHELL": "/bin/pyodide-shell",
            "PWD": "/",
            "OLDPWD": "/",
            "TERM": "xterm",
        }
    
    def load_from_sandbox(self, config: dict) -> None:
        """
        Load environment from sandbox configuration.
        
        Args:
            config: Sandbox configuration dictionary
        """
        from chuk_virtual_shell.sandbox.loader.environment_loader import load_environment
        self.environ = load_environment(config)
        logger.debug(f"Loaded sandbox environment variables: HOME={self.environ.get('HOME')}, USER={self.environ.get('USER')}")
    
    def ensure_home_directory(self) -> None:
        """Ensure home directory exists and is accessible."""
        home_dir = self.environ.get("HOME", "/home/user")
        try:
            resolved_home_dir = self.shell.fs.resolve_path(home_dir)
            existing_node = self.shell.fs.get_node_info(resolved_home_dir)
            
            if not existing_node:
                if not self.shell.fs.mkdir(resolved_home_dir):
                    logger.warning(f"Could not create home directory {resolved_home_dir}")
            elif not existing_node.is_dir:
                logger.warning(f"Home path {resolved_home_dir} exists but is not a directory")
            
            # Try to change to home directory
            if not self.shell.fs.cd(home_dir):
                logger.warning(f"Could not change to home directory {home_dir}")
                
        except Exception as e:
            logger.error(f"Error setting up home directory {home_dir}: {e}")
    
    def load_shellrc(self) -> None:
        """Load and execute .shellrc file if it exists."""
        shellrc_paths = [
            f"{self.environ.get('HOME', '/home/user')}/.shellrc",
            "/.shellrc",
        ]
        
        for rc_path in shellrc_paths:
            try:
                if self.shell.fs.exists(rc_path) and self.shell.fs.is_file(rc_path):
                    content = self.shell.fs.read_file(rc_path)
                    if content:
                        logger.info(f"Loading shell configuration from {rc_path}")
                        self._execute_shellrc(content)
                        break  # Only load the first found .shellrc
            except Exception as e:
                logger.debug(f"Could not load {rc_path}: {e}")
    
    def _execute_shellrc(self, content: str) -> None:
        """
        Execute the contents of a .shellrc file.
        
        Args:
            content: Content of the .shellrc file
        """
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
                        if "alias" in self.shell.commands:
                            self.shell.commands["alias"].execute([parts])
                    else:
                        # Execute the command normally
                        result = self.shell.execute(line)
                        # Check if command was not found
                        if result and "command not found" in result.lower():
                            logger.warning(f"Error executing .shellrc line '{line}': {result}")
                except Exception as e:
                    logger.warning(f"Error executing .shellrc line '{line}': {e}")
    
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get an environment variable value.
        
        Args:
            key: Variable name
            default: Default value if not found
            
        Returns:
            Variable value or default
        """
        return self.environ.get(key, default)
    
    def set(self, key: str, value: str) -> None:
        """
        Set an environment variable.
        
        Args:
            key: Variable name
            value: Variable value
        """
        self.environ[key] = value
    
    def unset(self, key: str) -> None:
        """
        Unset an environment variable.
        
        Args:
            key: Variable name to remove
        """
        if key in self.environ:
            del self.environ[key]
    
    def export_dict(self) -> Dict[str, str]:
        """
        Export environment as a dictionary.
        
        Returns:
            Copy of environment variables
        """
        return self.environ.copy()