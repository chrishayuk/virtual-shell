"""
chuk_virtual_shell/sandbox_loader.py - Load and apply sandbox configurations from YAML files

This module loads sandbox configuration from YAML files, locates configuration and template files
in standard directories, and creates/configures a VirtualFileSystem instance according to the sandbox
settings, including applying security and initialization commands.
"""

import os
import json
import traceback
import logging
import re
import yaml
from typing import Dict, Any, Optional, List

# Virtual filesystem imports
from chuk_virtual_fs import VirtualFileSystem
from chuk_virtual_fs.template_loader import TemplateLoader

# Configure module-level logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

# Set the security wrapper logger to only log errors (suppress warnings and info messages)
logging.getLogger("chuk_virtual_fs.security_wrapper").setLevel(logging.CRITICAL)

def load_sandbox_config(config_path: str) -> Dict[str, Any]:
    """
    Load a sandbox configuration from a YAML file.

    Args:
        config_path: Path to the YAML configuration file.

    Returns:
        Configuration dictionary.

    Raises:
        FileNotFoundError: If the configuration file doesn't exist.
        yaml.YAMLError: If the YAML file is invalid.
    """
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


def find_sandbox_config(name: str) -> Optional[str]:
    """
    Search for a sandbox configuration file in standard directories.

    Args:
        name: Sandbox name (or part of the filename).

    Returns:
        Full path to the configuration file if found, else None.
    """
    search_paths = [
        os.getcwd(),
        os.path.join(os.getcwd(), 'config'),
        os.path.expanduser("~/.config/virtual-shell"),
        "/etc/virtual-shell",
    ]
    
    env_config_dir = os.environ.get("CHUK_VIRTUAL_SHELL_CONFIG_DIR") or os.environ.get("chuk_virtual_shell_CONFIG_DIR")
    if env_config_dir:
        search_paths.insert(0, env_config_dir)
    
    logger.debug("Searching for sandbox config in:")
    for sp in search_paths:
        logger.debug(f"  {sp}")
    
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
            logger.debug(f"Checking {config_path}")
            if os.path.exists(config_path):
                logger.debug(f"Found config at {config_path}")
                return config_path
    return None


def _find_filesystem_template(name: str) -> Optional[str]:
    """
    Find a filesystem template file by name.

    Args:
        name: Name of the filesystem template.

    Returns:
        Path to the template file or None if not found.
    """
    if not name:
        return None
    
    search_paths = [
        os.getcwd(),
        os.path.join(os.getcwd(), 'templates'),
        os.path.expanduser("~/.chuk_virtual_shell/templates"),
        "/usr/share/virtual-shell/templates",
    ]
    
    if 'CHUK_VIRTUAL_SHELL_TEMPLATE_DIR' in os.environ:
        search_paths.insert(0, os.environ['CHUK_VIRTUAL_SHELL_TEMPLATE_DIR'])
    
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
    List all available sandbox configurations.

    Returns:
        List of configuration names.
    """
    configs = []
    search_paths = [
        os.getcwd(),
        os.path.join(os.getcwd(), 'config'),
        os.path.expanduser("~/.config/virtual-shell"),
        "/etc/virtual-shell",
    ]
    
    if 'chuk_virtual_shell_CONFIG_DIR' in os.environ:
        search_paths.insert(0, os.environ['chuk_virtual_shell_CONFIG_DIR'])
    
    for path in search_paths:
        if not os.path.exists(path):
            continue
        for filename in os.listdir(path):
            if filename.endswith(('.yaml', '.yml')):
                try:
                    config_path = os.path.join(path, filename)
                    with open(config_path, 'r') as f:
                        config = yaml.safe_load(f)
                    if isinstance(config, dict) and 'name' in config:
                        if config['name'] not in configs:
                            configs.append(config['name'])
                except Exception:
                    pass
    return configs


def list_available_templates() -> List[str]:
    """
    List all available filesystem templates.

    Returns:
        List of template names.
    """
    templates = []
    search_paths = [
        os.getcwd(),
        os.path.join(os.getcwd(), 'templates'),
        os.path.expanduser("~/.chuk_virtual_shell/templates"),
        "/usr/share/virtual-shell/templates",
    ]
    
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
                    if isinstance(template_data, dict) and 'directories' in template_data:
                        template_name = filename.split('.')[0]
                        if template_name not in templates:
                            templates.append(template_name)
                except Exception:
                    pass
    return templates


def compile_denied_patterns(patterns: List[str]) -> List[re.Pattern]:
    """
    Compile a list of string patterns into regular expression objects.

    Args:
        patterns: List of regex pattern strings.

    Returns:
        List of compiled regex objects.
    """
    compiled = []
    for pattern in patterns:
        try:
            compiled.append(re.compile(pattern))
        except re.error as e:
            logger.warning(f"Invalid regex pattern '{pattern}': {e}")
    return compiled

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
    logger.debug("Creating filesystem from config")
    logger.debug("Config contents: %s", config)
    
    # Before anything else, compile denied patterns if present.
    security_config = config.get('security', {})
    if 'denied_patterns' in security_config:
        patterns = security_config['denied_patterns']
        # Replace the string patterns with compiled regex objects.
        security_config['denied_patterns'] = compile_denied_patterns(patterns)
    
    # Extract filesystem settings
    fs_config = config.get('filesystem', {})
    provider_name = fs_config.get('provider', 'memory')
    provider_args = fs_config.get('provider_args', {})
    
    # Extract security settings (security_config is updated now)
    security_profile = security_config.get('profile')
    
    logger.debug(f"Creating filesystem with provider {provider_name}")
    fs = VirtualFileSystem(
        provider_name=provider_name,
        security_profile=security_profile,
        **provider_args
    )
    
    # Apply additional security settings if provided
    if security_config and hasattr(fs, 'provider') and hasattr(fs.provider, '_in_setup'):
        fs.provider._in_setup = True
        
        # Apply security overrides
        for key, value in security_config.items():
            if key != 'profile' and hasattr(fs.provider, key):
                setattr(fs.provider, key, value)
    
    # Handle filesystem template
    if 'filesystem-template' in config:
        logger.debug("Filesystem template found in config")
        template_config = config['filesystem-template']
        if 'name' not in template_config:
            logger.warning("Filesystem template name not specified")
        else:
            template_name = template_config['name']
            template_variables = template_config.get('variables', {})
            template_loader = TemplateLoader(fs)
            try:
                template_path = _find_filesystem_template(template_name)
                if template_path:
                    template_loader.load_template(template_path, variables=template_variables)
                else:
                    logger.warning(f"Filesystem template {template_name} not found")
            except Exception as e:
                logger.error(f"Error applying filesystem template: {e}")
                traceback.print_exc()
    
    # Execute initialization commands
    init_commands = config.get('initialization', [])
    if init_commands:
        _execute_initialization(fs, init_commands)
    
    if hasattr(fs, 'provider') and hasattr(fs.provider, '_in_setup'):
        fs.provider._in_setup = False
    
    return fs


def get_environment_from_config(config: Dict[str, Any]) -> Dict[str, str]:
    """
    Extract environment variables from a sandbox configuration.

    Args:
        config: Sandbox configuration dictionary.

    Returns:
        Dictionary of environment variables.
    """
    return config.get('environment', {})


def _execute_initialization(fs: VirtualFileSystem, commands: List[str]) -> None:
    """
    Execute initialization commands on the filesystem.

    Args:
        fs: Filesystem instance.
        commands: List of initialization commands.
    """
    for command in commands:
        parts = command.split(maxsplit=1)
        cmd = parts[0]
        
        if cmd == "mkdir":
            if len(parts) > 1:
                args = parts[1].strip()
                if args.startswith("-p "):
                    path = args[3:].strip()
                    _ensure_directory(fs, path)
                else:
                    fs.mkdir(args)
        
        elif cmd == "echo":
            if len(parts) > 1 and ">" in parts[1]:
                content, path = parts[1].split(">", 1)
                content = content.strip()
                if (content.startswith("'") and content.endswith("'")) or \
                   (content.startswith('"') and content.endswith('"')):
                    content = content[1:-1]
                path = path.strip()
                parent_dir = os.path.dirname(path)
                if parent_dir:
                    _ensure_directory(fs, parent_dir)
                fs.write_file(path, content)


def _ensure_directory(fs: VirtualFileSystem, path: str) -> None:
    """
    Ensure a directory exists, creating any missing parent directories as needed.

    Args:
        fs: Filesystem instance.
        path: Directory path to create.
    """
    components = path.strip('/').split('/')
    current_path = "/"
    for component in components:
        if not component:
            continue
        current_path = current_path.rstrip('/') + '/' + component
        info = fs.get_node_info(current_path)
        if not info:
            fs.mkdir(current_path)
        elif not info.is_dir:
            raise ValueError(f"Path {current_path} exists but is not a directory")
