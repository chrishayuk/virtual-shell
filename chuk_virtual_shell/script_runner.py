"""
chuk_virtual_shell/script_runner.py - Execute shell scripts in PyodideShell
"""
class ScriptRunner:
    """Utility class for running shell scripts"""
    
    def __init__(self, shell):
        """
        Initialize the script runner
        
        Args:
            shell: The shell interpreter instance
        """
        self.shell = shell
    
    def run_script(self, script_path):
        """
        Run a shell script from a file path
        
        Args:
            script_path: Path to the script file
            
        Returns:
            str: Output from the script execution
        """
        # Read script content
        script_content = self.shell.fs.read_file(script_path)
        
        if script_content is None:
            return f"script: cannot open '{script_path}': No such file"
        
        return self.run_script_content(script_content)
    
    def run_script_content(self, script_content):
        """
        Run a shell script from a string
        
        Args:
            script_content: String containing the script commands
            
        Returns:
            str: Output from the script execution
        """
        # Split the script into lines
        lines = script_content.splitlines()
        
        # Process each line
        results = []
        for line in lines:
            # Skip empty lines and comments
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            # Execute the command
            result = self.shell.execute(line)
            if result:
                results.append(result)
            
            # Stop execution if the shell is no longer running
            if not self.shell.running:
                break
        
        # Return the combined results
        return "\n".join(results)