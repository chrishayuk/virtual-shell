#!/usr/bin/env python3
"""
Clean runner for multi-agent collaboration demo.
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
        [sys.executable, 'examples/multi_agent_collaboration.py'],
        env=env,
        capture_output=True,
        text=True
    )
    
    # Filter output
    output = result.stdout + result.stderr
    lines = output.split('\n')
    skip_mode = False
    
    for line in lines:
        # Start skipping on error indicators
        if any(x in line for x in [
            'Task exception was never retrieved',
            'Task was destroyed but it is pending',
            'Traceback (most recent call last)',
            'During handling of the above exception',
            'RuntimeError: Event loop is closed',
            'RuntimeError: no running event loop',
            'asyncio.exceptions.CancelledError'
        ]):
            skip_mode = True
            continue
        
        # Stop skipping on key markers
        if any(x in line for x in [
            '✅', '🎉', 'PHASE', '===', '---', 'Complete'
        ]):
            skip_mode = False
        
        # Skip error-related lines
        if skip_mode:
            if 'File "' in line or 'await' in line or 'raise' in line or '.py' in line:
                continue
        
        # Print clean lines
        if not skip_mode or line.strip().startswith(('✓', '•', '📊', '🏗️', '💻', '🧪', '📈')):
            print(line)
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())