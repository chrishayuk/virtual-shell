"""
chuk_virtual_shell/main.py - Main entry point for PyodideShell
"""

import sys
import os
import argparse
import asyncio
import json
import logging
from dotenv import load_dotenv

# virtual filesystem imports
from chuk_virtual_fs.providers import list_providers  # type: ignore

# virtual shell imports
from chuk_virtual_shell.script_runner import ScriptRunner
from chuk_virtual_shell.shell_interpreter import ShellInterpreter
from chuk_virtual_shell.telnet_server import TelnetServer
from chuk_virtual_shell.sandbox.loader.mcp_loader import initialize_mcp


# Load environment variables (for E2B API keys if needed)
load_dotenv()

# logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)


def parse_provider_args(provider_args_str):
    """Parse provider arguments from a string, with environment variable expansion"""
    if not provider_args_str:
        return {}

    # Expand environment variables in the arguments string
    provider_args_str = os.path.expandvars(provider_args_str)

    try:
        # Try to parse as JSON
        args = json.loads(provider_args_str)
    except json.JSONDecodeError:
        # If not valid JSON, try to parse as key=value pairs
        args = {}
        for arg_pair in provider_args_str.split(","):
            if "=" in arg_pair:
                key, value = arg_pair.split("=", 1)
                args[key.strip()] = value.strip()
    
    # Note: S3-specific environment variable handling moved to main() function
    # to avoid adding S3 args to non-S3 providers
    
    return args


def convert_dict_to_object(d):
    """Convert a dictionary to an object with attributes"""

    class ConfigObject:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    return ConfigObject(**d)


async def initialize_shell_mcp(shell):
    """Initialize MCP servers for a shell instance"""
    if hasattr(shell, "mcp_servers") and shell.mcp_servers:
        logger.info(
            f"Initializing MCP servers: {[s.get('server_name') if isinstance(s, dict) else s.server_name for s in shell.mcp_servers]}"
        )

        # Convert dictionary MCP configs to objects with attributes if needed
        if shell.mcp_servers and isinstance(shell.mcp_servers[0], dict):
            logger.debug("Converting MCP server dictionaries to objects")
            shell.mcp_servers = [
                convert_dict_to_object(server) for server in shell.mcp_servers
            ]

        try:
            # Initialize MCP commands
            result = await initialize_mcp(shell)
            if result:
                logger.error(f"MCP initialization error: {result}")
            else:
                # List registered MCP commands
                mcp_commands = []
                for name, cmd in shell.commands.items():
                    if hasattr(cmd, "get_category") and cmd.get_category() == "mcp":
                        mcp_commands.append(name)

                if mcp_commands:
                    logger.info(f"Registered MCP commands: {', '.join(mcp_commands)}")
                else:
                    logger.warning("No MCP commands were registered")
        except Exception as e:
            logger.exception(f"Error during MCP initialization: {e}")
    else:
        logger.debug("No MCP servers configured, skipping initialization")


def create_shell_interpreter(provider=None, provider_args=None, sandbox_yaml=None):
    """Create a shell interpreter with the specified provider or sandbox"""
    if sandbox_yaml:
        shell = ShellInterpreter(sandbox_yaml=sandbox_yaml)
    else:
        shell = ShellInterpreter(fs_provider=provider, fs_provider_args=provider_args)
    return shell


async def setup_shell_with_mcp(provider=None, provider_args=None, sandbox_yaml=None):
    """Create and setup a shell interpreter with MCP initialization"""
    shell = create_shell_interpreter(provider, provider_args, sandbox_yaml)

    # Initialize MCP if available
    await initialize_shell_mcp(shell)

    return shell


def run_interactive_shell(provider=None, provider_args=None, sandbox_yaml=None):
    """Run PyodideShell in interactive mode"""
    # Create shell and initialize MCP asynchronously
    shell = asyncio.run(setup_shell_with_mcp(provider, provider_args, sandbox_yaml))

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
            except Exception:
                # Log the exception with traceback for debugging.
                logger.exception("Error executing command in interactive shell")

    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt. Exiting...")
    except EOFError:
        logger.info("Received EOF. Exiting...")
    except Exception:
        logger.exception("Uncaught error in interactive shell")


async def run_telnet_server(provider=None, provider_args=None, sandbox_yaml=None, host="0.0.0.0", port=8023):
    """Run PyodideShell in telnet server mode"""
    # Create and start telnet server (it will create its own shell instances per connection)
    server = TelnetServer(
        host=host, 
        port=port, 
        fs_provider=provider, 
        fs_provider_args=provider_args
    )
    await server.start()


def run_script(script_path, provider=None, provider_args=None, sandbox_yaml=None):
    """Run a script file in the virtual shell."""
    # Create shell and initialize MCP asynchronously
    shell = asyncio.run(setup_shell_with_mcp(provider, provider_args, sandbox_yaml))
    runner = ScriptRunner(shell)

    try:
        # Check if file exists in real filesystem
        if os.path.exists(script_path):
            with open(script_path, "r") as f:
                script_content = f.read()

            # Create /tmp directory in virtual filesystem if it doesn't exist
            shell.execute("mkdir -p /tmp")

            virtual_path = f"/tmp/{os.path.basename(script_path)}"
            shell.fs.write_file(virtual_path, script_content)

            result = runner.run_script(virtual_path)
            if result:
                print(result)
        else:
            print(f"script: cannot open '{script_path}': No such file or directory")
    except Exception:
        logger.exception(f"Error running script '{script_path}'")


def main():
    parser = argparse.ArgumentParser(
        description="PyodideShell - A virtual shell with pluggable storage"
    )

    parser.add_argument("--telnet", action="store_true", help="Run as telnet server")
    parser.add_argument("--port", type=int, default=8023, help="Port for telnet server (default: 8023)")
    parser.add_argument("--script", type=str, help="Script file to run")

    # Sandbox configuration
    parser.add_argument(
        "--sandbox", type=str, help="Sandbox configuration to use (YAML file or name)"
    )
    parser.add_argument(
        "--list-sandboxes",
        action="store_true",
        help="List available sandbox configurations",
    )

    # Provider options
    parser.add_argument(
        "--fs-provider",
        type=str,
        default="memory",
        help="Filesystem provider to use (memory, sqlite, s3, etc.)",
    )
    parser.add_argument(
        "--fs-provider-args",
        type=str,
        help="Arguments for the filesystem provider (JSON or key=value,key2=value2)",
    )

    # MCP options
    parser.add_argument(
        "--no-mcp", action="store_true", help="Disable MCP initialization"
    )

    parser.add_argument("script_path", nargs="?", help="Script file to run")

    # Attempt to parse args
    try:
        if len(sys.argv) > 1:
            args = parser.parse_args()
        else:
            # Fallback for Pyodide or no args
            args = argparse.Namespace(
                telnet=False,
                port=8023,
                script=None,
                script_path=None,
                fs_provider="memory",
                fs_provider_args=None,
                sandbox=None,
                list_sandboxes=False,
                no_mcp=False,
            )
    except SystemExit:
        if "pyodide" in sys.modules:
            args = argparse.Namespace(
                telnet=False,
                port=8023,
                script=None,
                script_path=None,
                fs_provider="memory",
                fs_provider_args=None,
                sandbox=None,
                list_sandboxes=False,
                no_mcp=False,
            )
        else:
            return

    # Handle list commands first (before sandbox checks)
    if args.list_sandboxes:
        from chuk_virtual_shell.sandbox.loader import list_available_configs

        configs = list_available_configs()
        print("Available sandbox configurations:")
        for name in configs:
            print(f"  {name}")
        return

    provider_args = (
        parse_provider_args(args.fs_provider_args) if args.fs_provider_args else {}
    )
    
    # For S3 provider, auto-populate from environment if no args provided  
    if args.fs_provider == 's3' and not provider_args:
        if 'S3_BUCKET_NAME' in os.environ:
            provider_args['bucket_name'] = os.environ['S3_BUCKET_NAME'].strip('"')
            
            # Auto-detect region
            if 'AWS_DEFAULT_REGION' in os.environ:
                provider_args['region_name'] = os.environ['AWS_DEFAULT_REGION']
            elif 'AWS_REGION' in os.environ:
                provider_args['region_name'] = os.environ['AWS_REGION']
                
            # Auto-detect S3 endpoint URL (for S3-compatible services like Tigris)
            if 'AWS_ENDPOINT_URL_S3' in os.environ:
                provider_args['endpoint_url'] = os.environ['AWS_ENDPOINT_URL_S3']
                logger.info(f"Using S3-compatible endpoint: {provider_args['endpoint_url']}")
                
            logger.info(f"Using S3 bucket from environment: {provider_args['bucket_name']}")
        else:
            logger.error("S3 provider requires bucket_name. Set S3_BUCKET_NAME environment variable or use --fs-provider-args")
            return

    if args.fs_provider == "list":
        print("Available filesystem providers:")
        for name in list_providers():
            print(f"  {name}")
        return

    # If the user just runs `chuk-virtual-shell` with no --sandbox, fall back to default.yaml
    if not args.sandbox:
        # Construct a path to default.yaml (adjust as needed for your project structure)
        default_config_path = os.path.join(
            os.path.dirname(__file__), "config", "default.yaml"
        )
        if os.path.exists(default_config_path):
            args.sandbox = default_config_path
            logger.info(f"No sandbox specified, defaulting to {args.sandbox}")
        else:
            logger.warning(
                "No sandbox specified, and default.yaml not found. Proceeding without a sandbox config."
            )

    # Modify initialize_shell_mcp function to respect --no-mcp flag
    original_initialize_shell_mcp = initialize_shell_mcp

    if args.no_mcp:

        async def disabled_initialize_shell_mcp(shell):
            logger.info("MCP initialization disabled by --no-mcp flag")
            return

        globals()["initialize_shell_mcp"] = disabled_initialize_shell_mcp

    # Determine operation mode
    if args.telnet:
        logger.info(f"Starting telnet server on port {args.port}...")
        asyncio.run(run_telnet_server(args.fs_provider, provider_args, args.sandbox, port=args.port))
    elif args.script or args.script_path:
        script = args.script or args.script_path
        logger.info(f"Running script: {script}")
        run_script(script, args.fs_provider, provider_args, args.sandbox)
    elif "pyodide" in sys.modules:
        logger.info("Detected Pyodide environment. Starting interactive shell...")
        run_interactive_shell(args.fs_provider, provider_args, args.sandbox)
    else:
        logger.info("Starting interactive shell...")
        run_interactive_shell(args.fs_provider, provider_args, args.sandbox)

    # Restore original function if it was replaced
    if args.no_mcp:
        globals()["initialize_shell_mcp"] = original_initialize_shell_mcp


if __name__ == "__main__":
    main()
