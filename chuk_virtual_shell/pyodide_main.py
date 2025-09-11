"""
Enhanced Pyodide-Compatible Async Shell with YAML Sandbox Configuration
"""

import sys
import asyncio
import os

# Default sandbox configuration to use
DEFAULT_SANDBOX = "ai_sandbox"


async def safe_async_input(prompt=""):
    """
    Async input gathering with improved handling
    """
    try:
        import nodepy  # type: ignore

        # Use await to ensure we get the full input
        full_input = await nodepy.input(prompt)

        # Additional handling for edge cases
        return full_input.strip() if full_input is not None else ""
    except Exception as e:
        print(f"Input error: {e}")
        return ""


async def run_pyodide_shell():
    """
    Async shell main loop with YAML sandbox configuration
    """
    try:
        # Import the new modularized sandbox config loader and shell interpreter.
        from chuk_virtual_shell.sandbox.loader.sandbox_config_loader import (
            find_config_file,
        )
        from chuk_virtual_shell.shell_interpreter import ShellInterpreter

        # Check for environment variables that might specify a sandbox.
        sandbox_yaml = os.environ.get("PYODIDE_SANDBOX", DEFAULT_SANDBOX)

        # If sandbox specified by name, try to find its config file.
        if not sandbox_yaml.endswith((".yaml", ".yml")) and "/" not in sandbox_yaml:
            config_path = find_config_file(sandbox_yaml)
            if config_path:
                sandbox_yaml = config_path
            else:
                print(
                    f"Warning: Sandbox configuration '{sandbox_yaml}' not found, falling back to default"
                )
                # Try to find the default sandbox.
                default_path = find_config_file(DEFAULT_SANDBOX)
                if default_path:
                    sandbox_yaml = default_path
                else:
                    sandbox_yaml = None

        print(
            f"Initializing shell with sandbox configuration: {sandbox_yaml or 'default'}"
        )

        # Create shell with the specified sandbox configuration.
        shell = ShellInterpreter(sandbox_yaml=sandbox_yaml)

        # Print sandbox info.
        print("Shell initialized with the following environment:")
        print(f"Home directory: {shell.environ.get('HOME', '/home/user')}")
        print(f"User: {shell.environ.get('USER', 'user')}")

        # Welcome message.
        fs_info = shell.fs.get_fs_info()
        if "security" in fs_info:
            security = fs_info["security"]
            read_only = security.get("read_only", False)
            print(f"Security mode: {'Read-only' if read_only else 'Restricted write'}")

        print("\nType 'help' for a list of available commands.")
        print("Type 'exit' to quit the shell.")
        print("-" * 60)

        while shell.running:
            # Prepare prompt.
            prompt = shell.prompt()
            sys.stdout.write(prompt)
            sys.stdout.flush()

            try:
                # Await input with minimal overhead.
                cmd_line = await safe_async_input("")

                # Exit conditions.
                if cmd_line.lower() in {"exit", "quit", "q"}:
                    break

                # Skip empty lines.
                if not cmd_line:
                    continue

                # Execute command.
                result = shell.execute(cmd_line)
                if result:
                    print(result)

            except KeyboardInterrupt:
                print("^C")
                continue
            except Exception as e:
                print(f"Execution Error: {e}")

    except ImportError as import_error:
        print(f"Import error: {import_error}")
    except Exception as e:
        print(f"Shell error: {e}")
    finally:
        print("PyodideShell session ended.")


def pyodide_main():
    """
    Robust entry point for Pyodide shell
    """
    try:
        # Print startup banner.
        print("=" * 60)
        print("PyodideShell - Secure Virtual Environment")
        print("=" * 60)

        # Create an async main function.
        async def main():
            await run_pyodide_shell()

        # Get or create event loop.
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())

    except Exception as main_error:
        print(f"Fatal error: {main_error}")
        import traceback

        traceback
