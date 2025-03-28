"""
chuk_virtual_shell/sandbox_loader.py - Load and apply sandbox configurations from YAML files
"""
import os
import json
import traceback
import yaml
from typing import Dict, Any, Optional, List

# virtual filesystem imports
from chuk_virtual_fs import VirtualFileSystem
from chuk_virtual_fs.template_loader import TemplateLoader

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
    # Look in standard locations for configuration files
    search_paths = [
        os.getcwd(),
        os.path.join(os.getcwd(), 'config'),
        os.path.expanduser("~/.config/virtual-shell"),
        "/etc/virtual-shell",
    ]
    
    # Check if environment variable for config directory is set (try both variants)
    env_config_dir = os.environ.get("CHUK_VIRTUAL_SHELL_CONFIG_DIR") or os.environ.get("chuk_virtual_shell_CONFIG_DIR")
    if env_config_dir:
        search_paths.insert(0, env_config_dir)
    
    print("Debug: Searching for sandbox config in:")
    for sp in search_paths:
        print("  ", sp)
    
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
            print(f"Debug: Checking {config_path}")
            if os.path.exists(config_path):
                print(f"Debug: Found config at {config_path}")
                return config_path
    
    return None

def _find_filesystem_template(name: str) -> Optional[str]:
    """
    Find a filesystem template file by name
    
    Args:
        name: Name of the filesystem template
        
    Returns:
        Path to the template file or None if not found
    """
    # If no template specified, return None
    if not name:
        return None
    
    # Look in standard locations for template files
    search_paths = [
        # Current directory
        os.getcwd(),
        # Templates directory in the current path
        os.path.join(os.getcwd(), 'templates'),
        # User templates directory
        os.path.expanduser("~/.chuk_virtual_shell/templates"),
        # System templates directory
        "/usr/share/virtual-shell/templates",
    ]
    
    # Check if CHUK_VIRTUAL_SHELL_TEMPLATE_DIR environment variable is set
    if 'CHUK_VIRTUAL_SHELL_TEMPLATE_DIR' in os.environ:
        search_paths.insert(0, os.environ['CHUK_VIRTUAL_SHELL_TEMPLATE_DIR'])
    
    # Try different filename patterns
    file_patterns = [
        f"{name}.yaml",
        f"{name}.yml",
        f"{name}_template.yaml",
        f"{name}_template.yml",
        f"{name}.json"
    ]
    
    for path in search_paths:
        if not os.path.exists(path):
            continue
            
        for pattern in file_patterns:
            template_path = os.path.join(path, pattern)
            if os.path.exists(template_path):
                return template_path
    
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
        os.path.expanduser("~/.config/virtual-shell"),
        # System config directory
        "/etc/virtual-shell",
    ]
    
    # Check if chuk_virtual_shell_CONFIG_DIR environment variable is set
    if 'chuk_virtual_shell_CONFIG_DIR' in os.environ:
        search_paths.insert(0, os.environ['chuk_virtual_shell_CONFIG_DIR'])
    
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


def list_available_templates() -> List[str]:
    """
    List all available filesystem templates
    
    Returns:
        List of template names
    """
    templates = []
    search_paths = [
        # Current directory
        os.getcwd(),
        # Templates directory in the current path
        os.path.join(os.getcwd(), 'templates'),
        # User templates directory
        os.path.expanduser("~/.chuk_virtual_shell/templates"),
        # System templates directory
        "/usr/share/virtual-shell/templates",
    ]
    
    # Check if CHUK_VIRTUAL_SHELL_TEMPLATE_DIR environment variable is set
    if 'CHUK_VIRTUAL_SHELL_TEMPLATE_DIR' in os.environ:
        search_paths.insert(0, os.environ['CHUK_VIRTUAL_SHELL_TEMPLATE_DIR'])
    
    for path in search_paths:
        if not os.path.exists(path):
            continue
            
        for filename in os.listdir(path):
            if filename.endswith(('.yaml', '.yml', '.json')):
                try:
                    template_path = os.path.join(path, filename)
                    with open(template_path, 'r') as f:
                        if filename.endswith('.json'):
                            template_data = json.load(f)
                        else:
                            template_data = yaml.safe_load(f)
                    
                    # Validate template structure
                    if isinstance(template_data, dict) and 'directories' in template_data:
                        template_name = filename.split('.')[0]
                        if template_name not in templates:
                            templates.append(template_name)
                except Exception:
                    # Skip invalid templates
                    pass
    
    return templates


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
    print("Debug: Creating filesystem from config")
    print("Debug: Config contents:", config)
    
    # Extract filesystem settings
    fs_config = config.get('filesystem', {})
    provider_name = fs_config.get('provider', 'memory')
    provider_args = fs_config.get('provider_args', {})
    
    # Extract security settings
    security_config = config.get('security', {})
    security_profile = security_config.get('profile')
    
    # Create filesystem with security profile
    print(f"Debug: Creating filesystem with provider {provider_name}")
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
    
    # Handle filesystem template
    # Remove this section if it's causing issues
    if 'filesystem-template' in config:
        print("Debug: Filesystem template found in config")
        # Get template details
        template_config = config['filesystem-template']
        
        # Check if template name is specified
        if 'name' not in template_config:
            print("Warning: Filesystem template name not specified")
        else:
            template_name = template_config['name']
            template_variables = template_config.get('variables', {})
            
            # Create template loader
            template_loader = TemplateLoader(fs)
            
            try:
                # Find the template file
                template_path = _find_filesystem_template(template_name)
                
                if template_path:
                    # Apply the template with variables
                    template_loader.load_template(
                        template_path, 
                        variables=template_variables
                    )
                else:
                    print(f"Warning: Filesystem template {template_name} not found")
            
            except Exception as e:
                print(f"Error applying filesystem template: {e}")
                traceback.print_exc()
    
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