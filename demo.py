#!/usr/bin/env python3
"""
Clean runner for agent demo - suppresses all async warnings.
"""

import sys
import os
import warnings
import subprocess

# Suppress all warnings
warnings.filterwarnings("ignore")

def main():
    """Run the demo with clean output"""
    
    # Set environment to suppress warnings
    env = os.environ.copy()
    env['PYTHONWARNINGS'] = 'ignore'
    
    # Run the actual demo
    result = subprocess.run(
        [sys.executable, 'examples/agent_clean_demo.py'],
        env=env,
        capture_output=True,
        text=True
    )
    
    # Filter output
    lines = (result.stdout + result.stderr).split('\n')
    skip_mode = False
    
    for line in lines:
        # Start skipping on error indicators
        if any(x in line for x in [
            'Task exception was never retrieved',
            'Traceback (most recent call last)',
            'During handling of the above exception',
            'RuntimeError: Event loop is closed',
            'RuntimeError: no running event loop'
        ]):
            skip_mode = True
            continue
        
        # Stop skipping after the demo completes
        if '✅ Demo Complete!' in line:
            skip_mode = False
            print(line)
            continue
        
        # Skip error-related lines
        if skip_mode:
            if 'File "' in line or 'await' in line or 'raise' in line or '.py"' in line:
                continue
        
        # Skip empty lines during error mode
        if skip_mode and not line.strip():
            continue
            
        # Print clean lines
        if not skip_mode:
            print(line)
    
    # Don't print stderr as we've already merged it above
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())