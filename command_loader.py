"""
command_loader.py - Dynamically load commands from the commands directory
"""
import os
import importlib
import inspect
from command_base import ShellCommand

class CommandLoader:
    """Utility class for dynamically loading shell commands"""
    
    @staticmethod
    def discover_commands(shell_context):
        """
        Discover and instantiate all command classes in the commands directory
        
        Args:
            shell_context: The shell interpreter instance
            
        Returns:
            dict: Dictionary of command instances (name -> command)
        """
        commands = {}
        
        # In a real filesystem, we would use os.walk and importlib
        # For our virtual environment, we'll simulate this with a predefined list
        # of modules to load from the commands package
        
        # Navigation commands
        from commands.navigation.ls import LsCommand
        from commands.navigation.cd import CdCommand
        from commands.navigation.pwd import PwdCommand
        
        # File commands
        from commands.filesystem.mkdir import MkdirCommand
        from commands.filesystem.touch import TouchCommand
        from commands.filesystem.cat import CatCommand
        from commands.filesystem.echo import EchoCommand
        from commands.filesystem.rm import RmCommand
        from commands.filesystem.rmdir import RmdirCommand
        from commands.filesystem.more import MoreCommand
        
        # Environment commands
        from commands.environment.env import EnvCommand
        from commands.environment.export import ExportCommand
        
        # System commands
        from commands.system.clear import ClearCommand
        from commands.system.exit import ExitCommand
        from commands.system.help import HelpCommand
        from commands.system.script import ScriptCommand
        
        # Command classes to instantiate
        command_classes = [
            LsCommand, CdCommand, PwdCommand,
            MkdirCommand, TouchCommand, CatCommand, EchoCommand, RmCommand, RmdirCommand, MoreCommand,
            EnvCommand, ExportCommand,
            ClearCommand, ExitCommand, HelpCommand, ScriptCommand
        ]
        
        # Instantiate each command with the shell context
        for cmd_class in command_classes:
            cmd = cmd_class(shell_context)
            commands[cmd.name] = cmd
            
        return commands
    
    @staticmethod
    def load_commands_from_path(shell_context, path):
        """
        Load commands from a specific directory path
        
        This would be used in a real filesystem environment to dynamically
        load commands from an external directory
        
        Args:
            shell_context: The shell interpreter instance
            path: Directory path to load commands from
            
        Returns:
            dict: Dictionary of command instances (name -> command)
        """
        commands = {}
        
        # In a real filesystem, we would:
        # 1. Scan the directory for .py files
        # 2. Import each module
        # 3. Find classes that inherit from ShellCommand
        # 4. Instantiate them with the shell context
        
        # For our virtual environment, this is a placeholder
        # that would be implemented in a real system
        
        # Example implementation for a real filesystem:
        """
        for file in os.listdir(path):
            if file.endswith('.py') and not file.startswith('__'):
                module_name = file[:-3]  # Remove .py extension
                try:
                    # Import the module
                    module = importlib.import_module(f"{path.replace('/', '.')}.{module_name}")
                    
                    # Find command classes in the module
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            issubclass(obj, ShellCommand) and 
                            obj != ShellCommand):
                            
                            # Instantiate the command
                            cmd = obj(shell_context)
                            commands[cmd.name] = cmd
                            
                except (ImportError, AttributeError) as e:
                    print(f"Error loading command module {module_name}: {e}")
        """
                
        return commands