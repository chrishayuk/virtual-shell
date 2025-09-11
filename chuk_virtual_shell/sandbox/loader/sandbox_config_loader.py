# chuk_virtual_shell/sandbox/loader/sandbox_config_loader.py
import os
import yaml  # type: ignore
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def load_config_file(config_path: str) -> Dict[str, Any]:
    """
    Load a sandbox configuration from a YAML file.

    Args:
        config_path: Path to the YAML configuration file.

    Returns:
        Configuration dictionary.
    """
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config


def find_config_file(name: str) -> Optional[str]:
    """
    Search standard directories for a sandbox configuration file by name.

    Args:
        name: The sandbox name (or part of the filename).

    Returns:
        The full path to the configuration file if found, else None.
    """
    search_paths = [
        os.getcwd(),
        os.path.join(os.getcwd(), "config"),
        os.path.expanduser("~/.config/virtual-shell"),
        "/etc/virtual-shell",
    ]

    env_config_dir = os.environ.get("CHUK_VIRTUAL_SHELL_CONFIG_DIR") or os.environ.get(
        "chuk_virtual_shell_CONFIG_DIR"
    )
    if env_config_dir:
        search_paths.insert(0, env_config_dir)

    file_patterns = [
        f"{name}_sandbox_config.yaml",
        f"{name}_config.yaml",
        f"{name}.yaml",
        f"sandbox_{name}.yaml",
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
