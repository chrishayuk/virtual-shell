"""
pyodide_main.py - Event Loop Aware PyodideShell (With Visible Prompt)
"""
import sys
import os
import asyncio
import traceback
import logging

# Configure logging (but we'll disable it anyway)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pyodide_shell_debug.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Get the PyodideShell logger and disable it
logger = logging.getLogger('PyodideShell')
logger.disabled = True

def create_debug_file(content):
    """
    Create a debug file with given content (if you ever re-enable logging).
    """
    try:
        with open('pyodide_shell_debug.txt', 'w') as f:
            f.write(str(content))
    except Exception as e:
        print(f"Failed to write debug file: {e}")

async def safe_async_input(prompt=""):
    """
    Gathers user input asynchronously via Node's raw-mode function.
    Note: The 'prompt' parameter is unused if you're printing it in Python.
    """
    try:
        import nodepy
        try:
            input_result = await nodepy.input(prompt)
            return str(input_result).strip()
        except:
            return ""
    except:
        return ""

async def run_pyodide_shell():
    """
    Main async loop: prints the prompt on Python side, reads commands asynchronously.
    """
    try:
        from virtual_shell.shell_interpreter import ShellInterpreter
        shell = ShellInterpreter()
        
        # Interactive shell loop
        while shell.running:
            try:
                # Get the prompt from the shell
                prompt = shell.prompt()

                # Print it here in Python, so user sees it immediately
                sys.stdout.write(prompt)
                sys.stdout.flush()

                # Collect user input WITHOUT re-printing the prompt on the Node side
                cmd_line = await safe_async_input("")

                # Handle exit commands
                if cmd_line.lower() in ['exit', 'quit', 'q']:
                    break
                if not cmd_line:
                    continue
                
                # Execute the command
                try:
                    result = shell.execute(cmd_line)
                    if result:
                        print(result)
                except Exception as exec_error:
                    print(f"Error: {exec_error}")
            
            except KeyboardInterrupt:
                break
            except Exception as loop_error:
                print(f"Error: {loop_error}")
                break
    
    except ImportError as import_error:
        print(f"Import error: {import_error}")
    except Exception as init_error:
        print(f"Initialization error: {init_error}")
    finally:
        print("PyodideShell session ended.")

def pyodide_main():
    """
    Entry point that runs the async shell loop until completion.
    """
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run_pyodide_shell())
    except Exception as main_error:
        print(f"Fatal error: {main_error}")
        traceback.print_exc()

if __name__ == "__main__":
    pyodide_main()
