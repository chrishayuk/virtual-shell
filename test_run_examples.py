#!/usr/bin/env python
"""
Test runner to demonstrate executing example scripts in the virtual shell.
Run this to see the virtual shell in action with the new commands and interpreters.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chuk_virtual_shell.shell_interpreter import ShellInterpreter
from chuk_virtual_shell.commands.text.grep import GrepCommand
from chuk_virtual_shell.commands.text.sed import SedCommand
from chuk_virtual_shell.commands.text.awk import AwkCommand
from chuk_virtual_shell.commands.text.head import HeadCommand
from chuk_virtual_shell.commands.text.tail import TailCommand
from chuk_virtual_shell.commands.text.sort import SortCommand
from chuk_virtual_shell.commands.text.uniq import UniqCommand
from chuk_virtual_shell.commands.text.wc import WcCommand
from chuk_virtual_shell.commands.system.sh import ShCommand
from chuk_virtual_shell.commands.system.python import PythonCommand, Python3Command

def register_new_commands(shell):
    """Register all the new commands with the shell"""
    # Text processing commands
    shell.commands['grep'] = GrepCommand(shell_context=shell)
    shell.commands['sed'] = SedCommand(shell_context=shell)
    shell.commands['awk'] = AwkCommand(shell_context=shell)
    shell.commands['head'] = HeadCommand(shell_context=shell)
    shell.commands['tail'] = TailCommand(shell_context=shell)
    shell.commands['sort'] = SortCommand(shell_context=shell)
    shell.commands['uniq'] = UniqCommand(shell_context=shell)
    shell.commands['wc'] = WcCommand(shell_context=shell)
    
    # Script execution commands
    shell.commands['sh'] = ShCommand(shell_context=shell)
    shell.commands['python'] = PythonCommand(shell_context=shell)
    shell.commands['python3'] = Python3Command(shell_context=shell)
    
    print("✓ Registered new commands: grep, sed, awk, head, tail, sort, uniq, wc, sh, python")

def copy_example_scripts(shell):
    """Copy example scripts into the virtual filesystem"""
    examples_dir = os.path.join(os.path.dirname(__file__), 'examples')
    
    # Create examples directory in virtual FS
    shell.fs.mkdir('examples')
    
    # List of example files to copy
    example_files = [
        'hello_world.sh',
        'file_operations.sh',
        'text_processing.sh',
        'control_flow.sh',
        'hello_world.py',
        'file_operations.py',
        'data_processing.py',
        'system_interaction.py'
    ]
    
    copied = []
    for filename in example_files:
        source_path = os.path.join(examples_dir, filename)
        if os.path.exists(source_path):
            with open(source_path, 'r') as f:
                content = f.read()
            shell.fs.write_file(f'examples/{filename}', content)
            copied.append(filename)
    
    if copied:
        print(f"✓ Copied {len(copied)} example scripts to virtual filesystem")
        return True
    return False

def run_demo(shell):
    """Run demonstration commands"""
    print("\n" + "="*60)
    print("VIRTUAL SHELL DEMONSTRATION")
    print("="*60 + "\n")
    
    demos = [
        ("List example scripts", "ls examples/"),
        ("Show current directory", "pwd"),
        ("Create test file", "echo 'Hello Virtual Shell' > test.txt"),
        ("Display file content", "cat test.txt"),
        ("Word count", "wc test.txt"),
        ("Pattern search", "echo 'Line 1\\nLine 2\\nLine 3' > lines.txt && grep '2' lines.txt"),
        ("Text substitution", "sed 's/Line/Row/g' lines.txt"),
        ("Sort demo", "echo 'banana\\napple\\ncherry' > fruits.txt && sort fruits.txt"),
        ("AWK demo", "echo 'John 25\\nAlice 30\\nBob 20' > people.txt && awk '{print $1}' people.txt"),
    ]
    
    for title, command in demos:
        print(f"\n--- {title} ---")
        print(f"$ {command}")
        result = shell.execute(command)
        if result:
            print(result)
    
    print("\n" + "="*60)
    print("RUNNING EXAMPLE SCRIPTS")
    print("="*60 + "\n")
    
    # Run a bash script
    print("\n--- Running Bash Script: hello_world.sh ---")
    print("$ sh examples/hello_world.sh")
    result = shell.execute("sh examples/hello_world.sh")
    if result:
        print(result)
    
    # Run a Python script
    print("\n--- Running Python Script: hello_world.py ---")
    print("$ python examples/hello_world.py")
    result = shell.execute("python examples/hello_world.py")
    if result:
        print(result)
    
    print("\n" + "="*60)
    print("ADVANCED EXAMPLES")
    print("="*60 + "\n")
    
    # Pipeline example
    print("\n--- Pipeline Example ---")
    command = "cat lines.txt | grep 'Line' | sed 's/Line/Item/' | sort"
    print(f"$ {command}")
    result = shell.execute(command)
    if result:
        print(result)
    
    # Text processing example
    print("\n--- Text Processing Example ---")
    shell.execute("sh examples/text_processing.sh")
    
    print("\n" + "="*60)
    print("INTERACTIVE MODE")
    print("="*60)
    print("\nYou can now interact with the virtual shell.")
    print("Try commands like:")
    print("  - grep 'pattern' file.txt")
    print("  - sed 's/old/new/' file.txt")
    print("  - awk '{print $1}' file.txt")
    print("  - sh examples/file_operations.sh")
    print("  - python examples/data_processing.py")
    print("  - head -n 5 file.txt")
    print("  - tail -n 5 file.txt")
    print("  - sort file.txt | uniq")
    print("\nType 'exit' to quit.\n")

def main():
    """Main function to run the demonstration"""
    print("Initializing Virtual Shell with new commands...")
    
    # Create shell instance
    shell = ShellInterpreter()
    
    # Register new commands
    register_new_commands(shell)
    
    # Copy example scripts
    if copy_example_scripts(shell):
        # Run demonstrations
        run_demo(shell)
        
        # Interactive mode
        while shell.running:
            try:
                command = input(f"{shell.environ.get('USER', 'user')}@virtual:{shell.fs.cwd}$ ")
                if command.strip():
                    result = shell.execute(command)
                    if result:
                        print(result)
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit.")
            except EOFError:
                break
    else:
        print("Error: Could not find example scripts directory")
        print("Make sure you're running from the virtual-shell directory")

if __name__ == "__main__":
    main()