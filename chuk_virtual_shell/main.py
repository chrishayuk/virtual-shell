"""
chuk_virtual_shell/main.py - Main entry point for PyodideShell
"""
import sys
import os
import argparse
import asyncio
import json
import logging

# virtual filesystem imports
from chuk_virtual_fs.providers import list_providers

# virtual shell imports
from chuk_virtual_shell.script_runner import ScriptRunner
from chuk_virtual_shell.shell_interpreter import ShellInterpreter
from chuk_virtual_shell.telnet_server import TelnetServer

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

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
            logger.info(f"Using sandbox YAML configuration: {sandbox_yaml}")
        elif provider:
            logger.info(f"Using filesystem provider: {shell.fs.get_provider_name()}")
            
        while shell.running:
            prompt = shell.prompt()
            sys.stdout.write(prompt)
            sys.stdout.flush()
            
            cmd_line = input()
            try:
                result = shell.execute(cmd_line)
                if result:
                    print(result)
            except Exception as e:
                # Log the exception with traceback for debugging.
                logger.exception("Error executing command in interactive shell")
                
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt. Exiting...")
    except EOFError:
        logger.info("Received EOF. Exiting...")
    except Exception as e:
        logger.exception("Uncaught error in interactive shell")

async def run_telnet_server(provider=None, provider_args=None, sandbox_yaml=None):
    """Run PyodideShell in telnet server mode"""
    server = TelnetServer(fs_provider=provider, fs_provider_args=provider_args, 
                          sandbox_yaml=sandbox_yaml)
    await server.start()

def run_script(script_path, provider=None, provider_args=None, sandbox_yaml=None):
    """Run a script file in the virtual shell."""
    shell = create_shell_interpreter(provider, provider_args, sandbox_yaml)
    runner = ScriptRunner(shell)
    
    try:
        with open(script_path, 'r') as f:
            script_content = f.read()
        
        virtual_path = f"/tmp/{os.path.basename(script_path)}"
        shell.fs.write_file(virtual_path, script_content)
        
        result = runner.run_script(virtual_path)
        if result:
            print(result)
    except FileNotFoundError:
        logger.error(f"script: cannot open '{script_path}': No such file or directory")
    except Exception as e:
        logger.exception(f"Error running script '{script_path}'")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='PyodideShell - A virtual shell with pluggable storage')
    
    parser.add_argument('--telnet', action='store_true', help='Run as telnet server')
    parser.add_argument('--script', type=str, help='Script file to run')
    
    # Sandbox configuration
    parser.add_argument('--sandbox', type=str, help='Sandbox configuration to use (YAML file or name)')
    parser.add_argument('--list-sandboxes', action='store_true', help='List available sandbox configurations')
    
    # Provider options
    parser.add_argument('--fs-provider', type=str, default='memory', 
                        help='Filesystem provider to use (memory, sqlite, s3, etc.)')
    parser.add_argument('--fs-provider-args', type=str,
                        help='Arguments for the filesystem provider (JSON or key=value,key2=value2)')
    
    parser.add_argument('script_path', nargs='?', help='Script file to run')

    # Attempt to parse args
    try:
        if len(sys.argv) > 1:
            args = parser.parse_args()
        else:
            # Fallback for Pyodide or no args
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
        # If argparse tries to exit but we're in Pyodide
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
            return
    
    if args.list_sandboxes:
        from chuk_virtual_shell.sandbox_loader import list_available_configs
        configs = list_available_configs()
        print("Available sandbox configurations:")
        for name in configs:
            print(f"  {name}")
        return
    
    provider_args = parse_provider_args(args.fs_provider_args) if args.fs_provider_args else {}
    
    if args.fs_provider == 'list':
        logger.info("Available filesystem providers:")
        for name in list_providers():
            logger.info(f"  {name}")
        return
    
    # Determine operation mode
    if args.telnet:
        logger.info("Starting telnet server...")
        asyncio.run(run_telnet_server(args.fs_provider, provider_args, args.sandbox))
    elif args.script or args.script_path:
        script = args.script or args.script_path
        logger.info(f"Running script: {script}")
        run_script(script, args.fs_provider, provider_args, args.sandbox)
    elif 'pyodide' in sys.modules:
        logger.info("Detected Pyodide environment. Starting interactive shell...")
        run_interactive_shell(args.fs_provider, provider_args, args.sandbox)
    else:
        logger.info("Starting interactive shell...")
        run_interactive_shell(args.fs_provider, provider_args, args.sandbox)

if __name__ == "__main__":
    main()