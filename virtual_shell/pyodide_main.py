"""
pyodide_main.py - Pyodide-Safe Shell Initialization
"""
import sys
import traceback

def comprehensive_diagnostics():
    """
    Comprehensive system and input method diagnostics
    """
    print("\n### SYSTEM DIAGNOSTICS ###")
    
    # Python environment info
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    print(f"Current Working Directory: {sys.path}")
    
    # Check for Pyodide
    try:
        import js
        print("\nPyodide environment detected")
    except ImportError:
        print("\nStandard Python environment")
    
    # Input method investigation
    print("\n### INPUT METHOD INVESTIGATION ###")
    try:
        import nodepy
        print("Nodepy module available")
        
        print("\nNodepy module contents:")
        print(dir(nodepy))
        
        print("\nAttempting to retrieve input method details:")
        try:
            input_func = nodepy.input
            print(f"Input function: {input_func}")
            print(f"Input function type: {type(input_func)}")
        except Exception as func_error:
            print(f"Error retrieving input function: {func_error}")
    
    except ImportError:
        print("Nodepy module not found")
    except Exception as e:
        print(f"Unexpected nodepy investigation error: {e}")

def run_shell_diagnostics():
    """
    Run diagnostic checks for the shell
    """
    try:
        from virtual_shell.shell_interpreter import ShellInterpreter
        
        # Create shell interpreter
        print("\n### SHELL INTERPRETER DIAGNOSTICS ###")
        shell = ShellInterpreter()
        
        # Print filesystem provider info
        print(f"Filesystem Provider: {shell.fs.get_provider_name()}")
        
        # Investigate shell methods
        print("\nAvailable ShellInterpreter methods:")
        for method in dir(shell):
            if not method.startswith('_'):
                print(f"  - {method}")
        
        # Prompt generation test
        try:
            prompt = shell.prompt()
            print(f"\nGenerated Prompt: {prompt}")
        except Exception as prompt_error:
            print(f"Prompt generation error: {prompt_error}")
        
        # Mock input and command execution
        print("\n### COMMAND EXECUTION TEST ###")
        test_commands = ['pwd', 'ls', 'help']
        for cmd in test_commands:
            try:
                print(f"\nTesting command: {cmd}")
                result = shell.execute(cmd)
                print(f"Command result: {result}")
            except Exception as cmd_error:
                print(f"Command '{cmd}' execution error: {cmd_error}")
    
    except ImportError as import_error:
        print(f"Shell interpreter import error: {import_error}")
        traceback.print_exc()
    
    except Exception as shell_error:
        print(f"Unexpected shell error: {shell_error}")
        traceback.print_exc()

def pyodide_main():
    """
    Main entry point with comprehensive diagnostics
    """
    # Run comprehensive diagnostics
    comprehensive_diagnostics()
    
    # Run shell system checks
    run_shell_diagnostics()
    
    # Print final message
    print("\nDiagnostic complete. Please check the output for any issues.")

if __name__ == "__main__":
    pyodide_main()