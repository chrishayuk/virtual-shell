"""
commands/system/help.py - Help command
"""

from command_base import ShellCommand

class HelpCommand(ShellCommand):
    name = "help"
    help_text = "help - Display help for commands\nUsage: help [command]"
    category = "system"
    
    def execute(self, args):
        if args:
            cmd_name = args[0]
            if cmd_name in self.shell.commands:
                cmd = self.shell.commands[cmd_name]
                return cmd.get_help()
            else:
                return f"help: no help found for '{cmd_name}'"
        
        # Group commands by category
        navigation_cmds = ["cd", "pwd", "ls"]
        file_cmds = ["cat", "echo", "touch", "mkdir", "rm", "rmdir"]
        env_cmds = ["env", "export"]
        system_cmds = ["help", "exit", "clear"]
        
        # Filter available commands
        nav_available = [cmd for cmd in navigation_cmds if cmd in self.shell.commands]
        file_available = [cmd for cmd in file_cmds if cmd in self.shell.commands]
        env_available = [cmd for cmd in env_cmds if cmd in self.shell.commands]
        sys_available = [cmd for cmd in system_cmds if cmd in self.shell.commands]
        
        # Get any other commands not in the predefined categories
        all_cmds = set(self.shell.commands.keys())
        categorized = set(navigation_cmds + file_cmds + env_cmds + system_cmds)
        other_cmds = sorted(list(all_cmds - categorized))
        
        result = []
        
        if nav_available:
            result.append("Navigation commands: " + ", ".join(sorted(nav_available)))
        if file_available:
            result.append("File commands: " + ", ".join(sorted(file_available)))
        if env_available:
            result.append("Environment commands: " + ", ".join(sorted(env_available)))
        if sys_available:
            result.append("System commands: " + ", ".join(sorted(sys_available)))
        if other_cmds:
            result.append("Other commands: " + ", ".join(other_cmds))
            
        result.append("Type 'help [command]' for more information")
        
        return "\n".join(result)