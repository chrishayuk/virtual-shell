"""
Enhanced Pyodide-Compatible Async Shell using Pyodide provider (with debug)
"""
import sys
import asyncio

async def safe_async_input(prompt=""):
    """
    Async input gathering with improved handling
    """
    try:
        import nodepy
        
        # Use await to ensure we get the full input
        full_input = await nodepy.input(prompt)
        
        # Additional handling for edge cases
        return full_input.strip() if full_input is not None else ""
    except Exception as e:
        print(f"Input error: {e}")
        return ""

async def run_pyodide_shell():
    """
    Async shell main loop with optimized input and error handling
    """
    try:
        # Import the provider manager and the shell interpreter
        from virtual_shell.filesystem.provider_manager import ProviderManager
        from virtual_shell.shell_interpreter import ShellInterpreter

        # Debug: List available providers
        try:
            from virtual_shell.filesystem.providers import list_providers
            providers = list_providers()
        except Exception as e:
            pass

        # Create and initialize the Pyodide provider via the factory
        provider = ProviderManager.create_provider("pyodide")
        if not provider:
            raise Exception("Failed to create Pyodide provider")
        
        # Check provider initialization status
        if not provider.initialize():
            raise Exception("Provider initialization failed")

        # Pass the provider to the shell interpreter (assuming it accepts one)
        shell = ShellInterpreter(provider)

        while shell.running:
            # Prepare prompt
            prompt = shell.prompt()
            sys.stdout.write(prompt)
            sys.stdout.flush()

            try:
                # Await input with minimal overhead
                cmd_line = await safe_async_input("")
                
                # Exit conditions
                if cmd_line.lower() in {'exit', 'quit', 'q'}:
                    break
                
                # Skip empty lines
                if not cmd_line:
                    continue
                
                # Execute command
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
        # Create an async main function
        async def main():
            await run_pyodide_shell()
        
        # Get or create event loop
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    
    except Exception as main_error:
        print(f"Fatal error: {main_error}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    pyodide_main()
