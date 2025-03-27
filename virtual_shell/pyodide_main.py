"""
pyodide_main.py - Event Loop Aware PyodideShell
"""
import sys
import os
import asyncio
import traceback
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pyodide_shell_debug.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('PyodideShell')

def create_debug_file(content):
    """
    Create a debug file with given content
    """
    try:
        with open('pyodide_shell_debug.txt', 'w') as f:
            f.write(str(content))
    except Exception as e:
        print(f"Failed to write debug file: {e}")

async def safe_async_input(prompt=""):
    """
    Safe async input method for Pyodide environment
    """
    logger.debug(f"Attempting to get input with prompt: {prompt}")
    
    try:
        import nodepy
        
        try:
            # Await input 
            input_result = await nodepy.input(prompt)
            
            # Convert and log result
            result_str = str(input_result).strip()
            logger.debug(f"Input result: {result_str}")
            
            return result_str
        
        except Exception as input_error:
            logger.error(f"Async input error: {input_error}")
            return ""
    
    except Exception as e:
        logger.error(f"Nodepy input initialization error: {e}")
        return ""

async def run_pyodide_shell():
    """
    Async shell loop designed for Pyodide environment
    """
    logger.info("Starting PyodideShell interactive loop")
    
    try:
        from virtual_shell.shell_interpreter import ShellInterpreter
        
        # Create shell interpreter
        shell = ShellInterpreter()
        
        # Log filesystem provider
        logger.info(f"Filesystem Provider: {shell.fs.get_provider_name()}")
        
        # Interactive shell loop
        while shell.running:
            try:
                # Generate prompt
                prompt = shell.prompt()
                logger.debug(f"Generated prompt: {prompt}")
                
                # Get input asynchronously
                cmd_line = await safe_async_input(prompt)
                logger.debug(f"Received command: {cmd_line}")
                
                # Exit conditions
                if cmd_line.lower() in ['exit', 'quit', 'q']:
                    logger.info("Exit command received")
                    break
                
                # Skip empty commands
                if not cmd_line:
                    continue
                
                # Execute command
                try:
                    result = shell.execute(cmd_line)
                    
                    # Log and print result
                    if result:
                        logger.info(f"Command result: {result}")
                        print(result)
                
                except Exception as exec_error:
                    logger.error(f"Command execution error: {exec_error}")
                    print(f"Error: {exec_error}")
            
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received")
                break
            except Exception as loop_error:
                logger.error(f"Shell loop error: {loop_error}")
                print(f"Error: {loop_error}")
                break
    
    except ImportError as import_error:
        logger.error(f"Failed to import ShellInterpreter: {import_error}")
        print(f"Import error: {import_error}")
    except Exception as init_error:
        logger.error(f"Shell initialization failed: {init_error}")
        print(f"Initialization error: {init_error}")
    finally:
        logger.info("PyodideShell session ended.")
        print("PyodideShell session ended.")

def pyodide_main():
    """
    Main entry point for Pyodide shell
    """
    try:
        # Get current event loop or create a new one
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Run the shell coroutine
        loop.run_until_complete(run_pyodide_shell())
    
    except Exception as main_error:
        logger.error(f"Fatal shell error: {main_error}")
        print(f"Fatal error: {main_error}")
        traceback.print_exc()

if __name__ == "__main__":
    pyodide_main()