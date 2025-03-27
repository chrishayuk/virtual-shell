"""
commands/system/script.py - Run shell scripts command
"""
from command_base import ShellCommand
from script_runner import ScriptRunner

class ScriptCommand(ShellCommand):
    name = "script"
    help_text = "script - Run a shell script\nUsage: script [filename]"
    category = "system"
    
    def execute(self, args):
        if not args:
            return "script: missing operand"
            
        script_path = args[0]
        
        # Create a script runner instance
        runner = ScriptRunner(self.shell)
        
        # Run the script
        return runner.run_script(script_path)