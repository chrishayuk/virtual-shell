# chuk_virtual_shell/sandbox/loader/filesystem_initializer.py
import os
import traceback
import logging
import re
from typing import Dict, Any

from chuk_virtual_fs import VirtualFileSystem  # type: ignore
from chuk_virtual_fs.template_loader import TemplateLoader  # type: ignore

logger = logging.getLogger(__name__)


def compile_denied_patterns(patterns: list) -> list:
    compiled = []
    for pattern in patterns:
        try:
            compiled.append(re.compile(pattern))
        except re.error as e:
            logger.warning(f"Invalid regex pattern '{pattern}': {e}")
    return compiled


def create_filesystem(config: Dict[str, Any]) -> VirtualFileSystem:
    """
    Create a VirtualFileSystem instance based on the sandbox config.
    """
    logger.debug("Creating filesystem from config")

    security_config = config.get("security", {})
    if "denied_patterns" in security_config:
        security_config["denied_patterns"] = compile_denied_patterns(
            security_config["denied_patterns"]
        )

    fs_config = config.get("filesystem", {})
    provider_name = fs_config.get("provider", "memory")
    provider_args = fs_config.get("provider_args", {})

    security_profile = security_config.get("profile")

    logger.debug(f"Creating filesystem with provider {provider_name}")
    fs = VirtualFileSystem(
        provider_name=provider_name, security_profile=security_profile, **provider_args
    )

    # Apply additional security settings
    if (
        security_config
        and hasattr(fs, "provider")
        and hasattr(fs.provider, "_in_setup")
    ):
        fs.provider._in_setup = True
        for key, value in security_config.items():
            if key != "profile" and hasattr(fs.provider, key):
                setattr(fs.provider, key, value)

    # Handle filesystem template if specified
    if "filesystem-template" in config:
        template_config = config["filesystem-template"]
        if "name" not in template_config:
            logger.warning("Filesystem template name not specified in config.")
        else:
            template_name = template_config["name"]
            template_variables = template_config.get("variables", {})
            template_loader = TemplateLoader(fs)
            try:
                template_path = _find_template(template_name)
                if template_path:
                    template_loader.load_template(
                        template_path, variables=template_variables
                    )
                else:
                    logger.warning(f"Filesystem template '{template_name}' not found.")
            except Exception as e:
                logger.error(
                    f"Error applying filesystem template '{template_name}': {e}"
                )
                traceback.print_exc()

    if hasattr(fs, "provider") and hasattr(fs.provider, "_in_setup"):
        fs.provider._in_setup = False

    return fs


def _find_template(name: str) -> str:
    """
    Helper function to search standard directories for a template file.
    """
    search_paths = [
        os.getcwd(),
        os.path.join(os.getcwd(), "templates"),
        os.path.expanduser("~/.chuk_virtual_shell/templates"),
        "/usr/share/virtual-shell/templates",
    ]

    if "CHUK_VIRTUAL_SHELL_TEMPLATE_DIR" in os.environ:
        search_paths.insert(0, os.environ["CHUK_VIRTUAL_SHELL_TEMPLATE_DIR"])

    file_patterns = [
        f"{name}.yaml",
        f"{name}.yml",
        f"{name}_template.yaml",
        f"{name}_template.yml",
        f"{name}.json",
    ]

    for path in search_paths:
        if not os.path.exists(path):
            continue
        for pattern in file_patterns:
            template_path = os.path.join(path, pattern)
            logger.debug(f"Checking for template at {template_path}")
            if os.path.exists(template_path):
                logger.debug(f"Found template at {template_path}")
                return template_path
    return ""
