# chuk_virtual_shell/sandbox/loader/environment_loader.py
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def load_environment(config: Dict[str, Any]) -> Dict[str, str]:
    """
    Extract environment variables from the sandbox configuration.

    Args:
        config: The sandbox configuration dictionary.

    Returns:
        A dictionary of environment variables.
    """
    env_config = config.get("environment", {})

    # Default environment values
    defaults = {
        "HOME": "/sandbox",
        "PATH": "/bin",
        "USER": "ai",
        "SHELL": "/bin/pyodide-shell",
        "TERM": "xterm",
        "PWD": "/",
    }

    # Merge user environment settings with defaults
    environment = {**defaults, **env_config}

    # Just a sanity/logging example: ensure we at least have HOME defined
    if not environment.get("HOME"):
        logger.warning("HOME environment variable not specified; using /sandbox")

    return environment
