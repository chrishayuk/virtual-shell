"""
main.py - Main entry point for PyodideShell
"""
import sys
import os  # Add this missing import for os.path.basename
import asyncio
from shell_interpreter import ShellInterpreter
from telnet_server import TelnetServer

def run_interactive_shell():
    """Run PyodideShell in interactive mode"""
    shell = ShellInterpreter()
    
    try:
        while shell.running:
            # Print prompt
            prompt = shell.prompt()
            sys.stdout.write(prompt)
            sys.stdout.flush()
            
            # Read command
            cmd_line = input()
            
            # Execute command
            result = shell.execute(cmd_line)
            if result:
                print(result)
                
    except KeyboardInterrupt:
        print("\nReceived keyboard interrupt. Exiting...")
    except EOFError:
        print("\nReceived EOF. Exiting...")
    except Exception as e:
        print(f"Error in interactive shell: {e}")  # Debug any errors
    
    print("Goodbye!")

async def run_telnet_server():
    """Run PyodideShell in telnet server mode"""
    server = TelnetServer()
    await server.start()

def run_script(script_path):
    """Run a shell script"""
    from script_runner import ScriptRunner
    
    shell = ShellInterpreter()
    runner = ScriptRunner(shell)
    
    try:
        # Since we're in a real filesystem rather than our virtual one,
        # we need to read the file from the real filesystem
        with open(script_path, 'r') as f:
            script_content = f.read()
        
        # Create the script in the virtual filesystem
        virtual_path = f"/tmp/{os.path.basename(script_path)}"
        shell.fs.write_file(virtual_path, script_content)
        
        # Run the script
        result = runner.run_script(virtual_path)
        if result:
            print(result)
    except FileNotFoundError:
        print(f"script: cannot open '{script_path}': No such file or directory")
    except Exception as e:
        print(f"Error running script: {e}")

def main():
    """Main entry point"""
    print("Starting main function...")  # Debug message
    if len(sys.argv) > 1:
        print(f"Command line argument detected: {sys.argv[1]}")  # Debug message
        if sys.argv[1] == "--telnet":
            # Run as telnet server
            print("Starting telnet server...")  # Debug message
            asyncio.run(run_telnet_server())
        elif sys.argv[1] == "--script" and len(sys.argv) > 2:
            # Run a script
            print(f"Running script: {sys.argv[2]}")  # Debug message
            run_script(sys.argv[2])
        elif not sys.argv[1].startswith("--"):
            # Assume it's a script path
            print(f"Running script: {sys.argv[1]}")  # Debug message
            run_script(sys.argv[1])
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Usage: python main.py [--telnet|--script <script_path>|<script_path>]")
    elif 'pyodide' in sys.modules:
        # Running in Pyodide/browser - interactive shell
        print("Detected Pyodide environment")  # Debug message
        run_interactive_shell()
    else:
        # Running in regular Python environment - interactive shell
        print("Starting default interactive shell...")  # Debug message
        run_interactive_shell()

# Make sure to actually call the main function
if __name__ == "__main__":
    # start main
    main()