#!/bin/bash
# Run agent demo with clean output

# Run the Python script and filter out async warnings
python -W ignore::RuntimeWarning examples/agent_clean_demo.py 2>&1 | \
    grep -v "Task exception was never retrieved" | \
    grep -v "RuntimeError: no running event loop" | \
    grep -v "RuntimeError: Event loop is closed" | \
    grep -v "Traceback (most recent call last):" | \
    grep -v "File \"" | \
    grep -v "await self" | \
    grep -v "raise RuntimeError" | \
    grep -v "During handling of the above exception"