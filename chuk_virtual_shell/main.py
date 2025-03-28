"""
chuk_virtual_shell/main.py - Main entry point for PyodideShell
"""
import sys
import os
import argparse
import asyncio
import json

# virtual filesystem imports
from chuk_virtual_fs.providers import list_providers

# virtual shell imports
from chuk_virtual_shell.script_runner import ScriptRunner
from chuk_virtual_shell.shell_interpreter import ShellInterpreter
from chuk_virtual_shell.telnet_server import TelnetServer

def parse_provider_args(provider_args_str):
    """Parse provider arguments from a string"""
    if not provider_args_str:
        return {}
        
    try:
        # Try to parse as JSON
        return json.loads(provider_args_str)
    except json.JSONDecodeError:
        # If not valid JSON, try to parse as key=value pairs
        args = {}
        for arg_pair in provider_args_str.split(','):
            if '=' in arg_pair:
                key, value = arg_pair.split('=', 1)
                args[key.strip()] = value.strip()
        return args

def create_shell_interpreter(provider=None, provider_args=None, sandbox_yaml=None):
    """Create a shell interpreter with the specified provider or sandbox"""
    if sandbox_yaml:
        shell = ShellInterpreter(sandbox_yaml=sandbox_yaml)
    else:
        shell = ShellInterpreter(fs_provider=provider, fs_provider_args=provider_args)
    return shell

def run_interactive_shell(provider=None, provider_args=None, sandbox_yaml=None):
    """Run PyodideShell in interactive mode"""
    shell = create_shell_interpreter(provider, provider_args, sandbox_yaml)
    
    try:
        # Print provider info
        if sandbox_yaml:
            print(f"Using sandbox YAML configuration: {sandbox_yaml}")
        elif provider:
            print(f"Using filesystem provider: {shell.fs.get_provider_name()}")
            
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
        print(f"Error in interactive shell: {e}")

async def run_telnet_server(provider=None, provider_args=None, sandbox_yaml=None):
    """Run PyodideShell in telnet server mode"""
    server = TelnetServer(fs_provider=provider, fs_provider_args=provider_args, 
                         sandbox_yaml=sandbox_yaml)
    await server.start()

def run_script(script_path, provider=None, provider_args=None, sandbox_yaml=None):
    # create the shell interpreter
    shell = create_shell_interpreter(provider, provider_args, sandbox_yaml)

    # create the script runner
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

        # check the result
        if result:
            print(result)
    except FileNotFoundError:
        print(f"script: cannot open '{script_path}': No such file or directory")
    except Exception as e:
        print(f"Error running script: {e}")

def main():
    """Main entry point"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='PyodideShell - A virtual shell with pluggable storage')
    
    # Mode selection
    parser.add_argument('--telnet', action='store_true', help='Run as telnet server')
    parser.add_argument('--script', type=str, help='Script file to run')
    
    # Sandbox configuration
    parser.add_argument('--sandbox', type=str, help='Sandbox configuration to use (YAML file or name)')
    parser.add_argument('--list-sandboxes', action='store_true', help='List available sandbox configurations')
    
    # Provider options (used if sandbox not specified)
    parser.add_argument('--fs-provider', type=str, default='memory', 
                        help='Filesystem provider to use (memory, sqlite, s3, etc.)')
    parser.add_argument('--fs-provider-args', type=str,
                        help='Arguments for the filesystem provider (JSON or key=value,key2=value2)')
    
    # Script as positional argument
    parser.add_argument('script_path', nargs='?', help='Script file to run')
    
    # Parse args, but handle cases where we're not using argparse (like in Pyodide)
    try:
        if len(sys.argv) > 1:
            args = parser.parse_args()
        else:
            args = argparse.Namespace(
                telnet=False, 
                script=None, 
                script_path=None,
                fs_provider='memory',
                fs_provider_args=None,
                sandbox=None,
                list_sandboxes=False
            )
    except SystemExit:
        # If argparse wants to exit, just use default args in Pyodide environment
        if 'pyodide' in sys.modules:
            args = argparse.Namespace(
                telnet=False, 
                script=None, 
                script_path=None,
                fs_provider='memory',
                fs_provider_args=None,
                sandbox=None,
                list_sandboxes=False
            )
        else:
            # In a normal Python environment, let argparse handle errors
            return
    
    # List available sandboxes if requested
    if args.list_sandboxes:
        from chuk_virtual_shell.sandbox_loader import list_available_configs
        configs = list_available_configs()
        print("Available sandbox configurations:")
        for name in configs:
            print(f"  {name}")
        return
        
    # Parse provider arguments if specified
    provider_args = parse_provider_args(args.fs_provider_args) if args.fs_provider_args else {}
    
    # List available providers if requested
    if args.fs_provider == 'list':
        print("Available filesystem providers:")
        for name in list_providers():
            print(f"  {name}")
        return
    
    # Determine operation mode
    if args.telnet:
        # Run as telnet server
        print("Starting telnet server...")
        asyncio.run(run_telnet_server(args.fs_provider, provider_args, args.sandbox))
    elif args.script or args.script_path:
        # Run a script
        script = args.script or args.script_path
        print(f"Running script: {script}")
        run_script(script, args.fs_provider, provider_args, args.sandbox)
    elif 'pyodide' in sys.modules:
        # Running in Pyodide/browser - interactive shell
        print("Detected Pyodide environment")
        run_interactive_shell(args.fs_provider, provider_args, args.sandbox)
    else:
        # Running in regular Python environment - interactive shell
        print("Starting interactive shell...")
        run_interactive_shell(args.fs_provider, provider_args, args.sandbox)

# Make sure to actually call the main function
if __name__ == "__main__":
    main()