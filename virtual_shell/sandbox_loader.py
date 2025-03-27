"""
virtual_shell/sandbox_loader.py - Load and apply sandbox configurations from YAML files
"""
import os
import yaml
from typing import Dict, Any, Optional, List

from virtual_shell.filesystem import VirtualFileSystem


def load_sandbox_config(config_path: str) -> Dict[str, Any]:
    """
    Load a sandbox configuration from a YAML file
    
    Args:
        config_path: Path to the YAML configuration file
        
    Returns:
        Configuration dictionary
        
    Raises:
        FileNotFoundError: If the configuration file doesn't exist
        yaml.YAMLError: If the YAML file is invalid
    """
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    return config


def find_sandbox_config(name: str) -> Optional[str]:
    """
    Find a sandbox configuration file by name
    
    Args:
        name: Name of the sandbox configuration
        
    Returns:
        Path to the configuration file or None if not found
    """
    # Look in standard locations for configuration files
    search_paths = [
        # Current directory
        os.getcwd(),
        # Config directory in the current path
        os.path.join(os.getcwd(), 'config'),
        # User config directory
        os.path.expanduser("~/.config/pyodide-shell"),
        # System config directory
        "/etc/pyodide-shell",
    ]
    
    # Check if PYODIDE_SHELL_CONFIG_DIR environment variable is set
    if 'PYODIDE_SHELL_CONFIG_DIR' in os.environ:
        search_paths.insert(0, os.environ['PYODIDE_SHELL_CONFIG_DIR'])
    
    # Try different filename patterns
    file_patterns = [
        f"{name}_sandbox_config.yaml",
        f"{name}_config.yaml",
        f"{name}.yaml",
        f"sandbox_{name}.yaml"
    ]
    
    for path in search_paths:
        if not os.path.exists(path):
            continue
            
        for pattern in file_patterns:
            config_path = os.path.join(path, pattern)
            if os.path.exists(config_path):
                return config_path
    
    return None


def list_available_configs() -> List[str]:
    """
    List all available sandbox configurations
    
    Returns:
        List of configuration names
    """
    configs = []
    search_paths = [
        # Current directory
        os.getcwd(),
        # Config directory in the current path
        os.path.join(os.getcwd(), 'config'),
        # User config directory
        os.path.expanduser("~/.config/pyodide-shell"),
        # System config directory
        "/etc/pyodide-shell",
    ]
    
    # Check if PYODIDE_SHELL_CONFIG_DIR environment variable is set
    if 'PYODIDE_SHELL_CONFIG_DIR' in os.environ:
        search_paths.insert(0, os.environ['PYODIDE_SHELL_CONFIG_DIR'])
    
    for path in search_paths:
        if not os.path.exists(path):
            continue
            
        for filename in os.listdir(path):
            if filename.endswith(('.yaml', '.yml')):
                # Check if it's a sandbox config
                try:
                    config_path = os.path.join(path, filename)
                    with open(config_path, 'r') as f:
                        config = yaml.safe_load(f)
                    
                    if isinstance(config, dict) and 'name' in config:
                        if config['name'] not in configs:
                            configs.append(config['name'])
                except Exception:
                    # Skip invalid configs
                    pass
    
    return configs


def create_filesystem_from_config(config: Dict[str, Any]) -> VirtualFileSystem:
    """
    Create a filesystem from a sandbox configuration
    
    Args:
        config: Sandbox configuration dictionary
        
    Returns:
        Configured VirtualFileSystem instance
        
    Raises:
        ValueError: If the configuration is invalid
    """
    # Extract filesystem settings
    fs_config = config.get('filesystem', {})
    provider_name = fs_config.get('provider', 'memory')
    provider_args = fs_config.get('provider_args', {})
    
    # Extract security settings
    security_config = config.get('security', {})
    security_profile = security_config.get('profile')
    
    # Create filesystem with security profile
    fs = VirtualFileSystem(
        provider_name=provider_name,
        security_profile=security_profile,
        **provider_args
    )
    
    # Apply additional security settings if provided
    if security_config and hasattr(fs, 'provider') and hasattr(fs.provider, '_in_setup'):
        # Temporarily disable security for setup
        fs.provider._in_setup = True
        
        # Apply security overrides
        for key, value in security_config.items():
            if key != 'profile' and hasattr(fs.provider, key):
                setattr(fs.provider, key, value)
    
    # Execute initialization commands
    init_commands = config.get('initialization', [])
    if init_commands:
        _execute_initialization(fs, init_commands)
    
    # Re-enable security if it was temporarily disabled
    if hasattr(fs, 'provider') and hasattr(fs.provider, '_in_setup'):
        fs.provider._in_setup = False
    
    return fs


def get_environment_from_config(config: Dict[str, Any]) -> Dict[str, str]:
    """
    Get environment variables from a sandbox configuration
    
    Args:
        config: Sandbox configuration dictionary
        
    Returns:
        Dictionary of environment variables
    """
    return config.get('environment', {})


def _execute_initialization(fs: VirtualFileSystem, commands: List[str]) -> None:
    """
    Execute initialization commands on the filesystem
    
    Args:
        fs: Filesystem instance
        commands: List of initialization commands
    """
    for command in commands:
        # Very simple command interpreter for initialization
        parts = command.split(maxsplit=1)
        cmd = parts[0]
        
        if cmd == "mkdir":
            # Handle mkdir command
            if len(parts) > 1:
                args = parts[1].strip()
                if args.startswith("-p "):
                    # Create parent directories
                    path = args[3:].strip()
                    _ensure_directory(fs, path)
                else:
                    # Create single directory
                    fs.mkdir(args)
        
        elif cmd == "echo":
            # Handle echo command
            if len(parts) > 1 and ">" in parts[1]:
                # Echo with redirection
                content, path = parts[1].split(">", 1)
                # Clean up content (remove quotes)
                content = content.strip()
                if content.startswith("'") and content.endswith("'"):
                    content = content[1:-1]
                elif content.startswith('"') and content.endswith('"'):
                    content = content[1:-1]
                
                # Clean up path
                path = path.strip()
                
                # Ensure parent directory exists
                parent_dir = os.path.dirname(path)
                if parent_dir:
                    _ensure_directory(fs, parent_dir)
                
                # Write to file
                fs.write_file(path, content)


def _ensure_directory(fs: VirtualFileSystem, path: str) -> None:
    """
    Ensure a directory exists, creating parent directories as needed
    
    Args:
        fs: Filesystem instance
        path: Directory path to create
    """
    # Split path into components
    components = path.strip('/').split('/')
    current_path = "/"
    
    for component in components:
        if not component:
            continue
        
        current_path = current_path.rstrip('/') + '/' + component
        
        # Check if directory exists
        info = fs.get_node_info(current_path)
        if not info:
            # Create directory
            fs.mkdir(current_path)
        elif not info.is_dir:
            # Path exists but is not a directory
            raise ValueError(f"Path {current_path} exists but is not a directory")