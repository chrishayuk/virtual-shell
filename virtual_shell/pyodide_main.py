"""
pyodide_main.py - Pyodide-compatible main entry point for PyodideShell
"""
import sys
import os
import json
from virtual_shell.shell_interpreter import ShellInterpreter

def pyodide_main():
    """Run an interactive shell in the Pyodide environment"""
    print("Starting PyodideShell in Pyodide environment...")
    
    # Create shell interpreter with memory provider
    shell = ShellInterpreter()
    
    # Print provider info
    print(f"Using filesystem provider: {shell.fs.get_provider_name()}")
    
    # Synchronous shell loop for Pyodide
    while shell.running:
        # Print prompt
        prompt = shell.prompt()
        sys.stdout.write(prompt)
        sys.stdout.flush()
        
        # Run a special version of input that works with Pyodide
        cmd_line = input()
        
        # Echo the typed command so you can see it
        print(cmd_line)
        
        # Make sure cmd_line is actually a string
        if hasattr(cmd_line, 'strip'):
            cmd_line = cmd_line.strip()
        else:
            # Debug the object type
            print(f"DEBUG: cmd_line is type {type(cmd_line)}")
            # Try to convert it to a string
            try:
                cmd_line = str(cmd_line)
            except:
                cmd_line = ""
        
        # Execute command
        try:
            result = shell.execute(cmd_line)
            if result:
                print(result)
        except Exception as e:
            print(f"Error executing command: {e}")
    
    print("Goodbye from PyodideShell!")

if __name__ == "__main__":
    pyodide_main()
