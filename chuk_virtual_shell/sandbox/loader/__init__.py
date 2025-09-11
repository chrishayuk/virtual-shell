"""
Sandbox loader module for chuk_virtual_shell
"""

from .sandbox_config_loader import (
    load_config_file as load_sandbox_config,
    find_config_file as find_sandbox_config,
)

from .filesystem_initializer import (
    create_filesystem as create_filesystem_from_config,
)

from .environment_loader import (
    load_environment as get_environment_from_config,
)

# For list_available_configs, we need to implement it
import os
from typing import List


def list_available_configs() -> List[str]:
    """List all available sandbox configurations"""
    configs = []

    # Check user config directory
    home_dir = os.path.expanduser("~")
    user_config_dir = os.path.join(home_dir, ".chuk_virtual_shell", "sandboxes")

    if os.path.exists(user_config_dir):
        for file in os.listdir(user_config_dir):
            if file.endswith((".yaml", ".yml", ".json")):
                configs.append(file)

    return configs


__all__ = [
    "load_sandbox_config",
    "find_sandbox_config",
    "list_available_configs",
    "create_filesystem_from_config",
    "get_environment_from_config",
]
