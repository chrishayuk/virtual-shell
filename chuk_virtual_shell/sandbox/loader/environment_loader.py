# chuk_virtual_shell/sandbox/loader/environment_loader.py
from typing import Dict, Any

def load_environment(config: Dict[str, Any]) -> Dict[str, str]:
    """
    Extract environment variables from the sandbox configuration.
    
    Args:
        config: The sandbox configuration dictionary.
    
    Returns:
        A dictionary of environment variables.
    """
    env_config = config.get('environment', {})
    environment = {
        "HOME": env_config.get('HOME', '/sandbox'),
        "PATH": env_config.get('PATH', '/bin'),
        "USER": env_config.get('USER', 'ai'),
        "SHELL": env_config.get('SHELL', '/bin/pyodide-shell'),
        "TERM": env_config.get('TERM', 'xterm'),
        "PWD": "/"
    }
    for key, value in env_config.items():
        if key not in environment:
            environment[key] = value

    # return the environment
    return environment
