# chuk_virtual_shell/command_loader.py
import os
import importlib
import inspect
import logging
from typing import Dict, Any
from chuk_virtual_shell.commands.command_base import ShellCommand

logger = logging.getLogger(__name__)


class CommandLoader:
    """Utility class for dynamically loading shell commands"""

    @staticmethod
    def discover_commands(shell_context) -> dict:
        """
        Discover and instantiate all command classes in the commands package recursively.

        Args:
            shell_context: The shell interpreter instance.

        Returns:
            dict: Dictionary of command instances (name -> command)
        """
        commands: Dict[str, Any] = {}
        # Determine the root directory for the commands package.
        # __file__ refers to this file: chuk_virtual_shell/commands/command_loader.py
        base_dir = os.path.dirname(__file__)
        # The base package name for commands
        base_package = "chuk_virtual_shell.commands"

        # Walk through the commands package recursively.
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if file.endswith(".py") and not file.startswith("__"):
                    # Compute module name from file path.
                    module_path = os.path.join(root, file)
                    rel_path = os.path.relpath(module_path, base_dir)
                    module_name = rel_path[:-3].replace(os.sep, ".")
                    full_module_name = f"{base_package}.{module_name}"
                    try:
                        module = importlib.import_module(full_module_name)
                    except Exception as e:
                        # Only log MCP-related imports at debug level since MCP is optional
                        if "mcp" in full_module_name.lower():
                            logger.debug(
                                f"Optional module not available: {full_module_name}"
                            )
                        else:
                            logger.warning(
                                f"Error importing module {full_module_name}: {e}"
                            )
                        continue

                    # Inspect module for command classes.
                    for _, obj in inspect.getmembers(module, inspect.isclass):
                        if issubclass(obj, ShellCommand) and obj is not ShellCommand:
                            try:
                                cmd_instance = obj(shell_context)
                                commands[cmd_instance.name] = cmd_instance
                            except Exception as e:
                                print(
                                    f"Error instantiating command {obj.__name__} "
                                    f"from module {full_module_name}: {e}"
                                )
        return commands

    @staticmethod
    def load_commands_from_path(shell_context, path: str) -> dict:
        """
        Load commands from a specific directory path.

        This would be used in a real filesystem environment to dynamically
        load commands from an external directory.

        Args:
            shell_context: The shell interpreter instance.
            path: Directory path to load commands from.

        Returns:
            dict: Dictionary of command instances (name -> command)
        """
        commands: Dict[str, Any] = {}
        if not os.path.exists(path):
            return commands

        for file in os.listdir(path):
            if file.endswith(".py") and not file.startswith("__"):
                module_name = file[:-3]
                try:
                    module = importlib.import_module(module_name)
                    for _, obj in inspect.getmembers(module, inspect.isclass):
                        if issubclass(obj, ShellCommand) and obj is not ShellCommand:
                            cmd_instance = obj(shell_context)
                            commands[cmd_instance.name] = cmd_instance
                except Exception as e:
                    print(f"Error loading command module {module_name}: {e}")
        return commands
