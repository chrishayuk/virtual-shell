#!/usr/bin/env python
"""
Run demonstration scripts in the virtual shell
"""
import sys
from chuk_virtual_shell.shell_interpreter import ShellInterpreter
from chuk_virtual_shell.script_runner import ScriptRunner

def run_demo(script_path):
    """Run a demonstration script in the virtual shell"""
    # Create shell and script runner
    shell = ShellInterpreter()
    runner = ScriptRunner(shell)
    
    # Read the script from the real filesystem
    try:
        with open(script_path, 'r') as f:
            script_content = f.read()
    except FileNotFoundError:
        print(f"Error: Script not found: {script_path}")
        return 1
    
    # Copy script to virtual filesystem
    virtual_path = f"/tmp/{script_path.split('/')[-1]}"
    shell.fs.write_file(virtual_path, script_content)
    
    # Run the script
    print(f"Running {script_path} in virtual shell...")
    print("=" * 50)
    result = runner.run_script(virtual_path)
    print(result)
    
    return 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: uv run python run_demo.py <script_path>")
        print("Example: uv run python run_demo.py examples/redirection_pipeline_demo.sh")
        sys.exit(1)
    
    sys.exit(run_demo(sys.argv[1]))