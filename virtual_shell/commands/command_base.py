"""
virtual_shell/command_base.py - base class for all shell commands
"""
class ShellCommand:
    """Base class for all shell commands"""
    name = ""
    help_text = ""
    category = ""  # For better organization: 'navigation', 'file', 'environment', 'system'
    
    def __init__(self, shell_context):
        self.shell = shell_context
    
    def execute(self, args):
        """Execute the command with given arguments"""
        raise NotImplementedError("Subclasses must implement execute()")
    
    def get_help(self):
        """Return help text for the command"""
        return self.help_text
        
    def get_category(self):
        """Return the command category"""
        return self.category