# Makefile for chuk_virtual_shell and Pyodide shell

# Use system's python3 for the interactive shell targets.
PYTHON = $(shell which python3)
# Use npm for Node-related commands.
NODE = npm

# Prepend the local chuk_virtual_fs directory to PYTHONPATH (if you’re developing locally)
LOCAL_PYTHONPATH = ./chuk_virtual_fs

.PHONY: run telnet script list-sandboxes list-providers test install pyodide clean

# Run interactive shell (normal Python mode)
run:
	@echo "Starting interactive shell..."
	PYTHONPATH=$(LOCAL_PYTHONPATH):$$PYTHONPATH $(PYTHON) chuk_virtual_shell/main.py

# Run telnet server mode
telnet:
	@echo "Starting telnet server..."
	PYTHONPATH=$(LOCAL_PYTHONPATH):$$PYTHONPATH $(PYTHON) chuk_virtual_shell/main.py --telnet

# Run a script through the shell interpreter.
# Provide the script file via the SCRIPT variable:
#   make script SCRIPT=path/to/script
script:
	@if [ -z "$(SCRIPT)" ]; then \
		echo "Usage: make script SCRIPT=path/to/script"; \
		exit 1; \
	fi
	@echo "Running script $(SCRIPT)..."
	PYTHONPATH=$(LOCAL_PYTHONPATH):$$PYTHONPATH $(PYTHON) chuk_virtual_shell/main.py --script $(SCRIPT)

# List available sandbox configurations
list-sandboxes:
	@echo "Listing available sandbox configurations..."
	PYTHONPATH=$(LOCAL_PYTHONPATH):$$PYTHONPATH $(PYTHON) chuk_virtual_shell/main.py --list-sandboxes

# List available filesystem providers
list-providers:
	@echo "Listing available filesystem providers..."
	PYTHONPATH=$(LOCAL_PYTHONPATH):$$PYTHONPATH $(PYTHON) chuk_virtual_shell/main.py --fs-provider list

# Run tests (using uv-run pytest)
test:
	@echo "Running tests..."
	PYTHONPATH=$(LOCAL_PYTHONPATH):$$PYTHONPATH uv run pytest

# Install npm dependencies in the pyodide-container folder
install:
	@echo "Installing npm dependencies..."
	cd pyodide-container && $(NODE) install

# Run the Pyodide shell (via your Node entry script)
pyodide:
	@echo "Starting Pyodide shell..."
	cd pyodide-container && PYODIDE_SANDBOX=ai_sandbox CHUK_VIRTUAL_SHELL_CONFIG_DIR=./config $(NODE) start

# Clean up generated files, node_modules, __pycache__, and Pyodide main file
clean:
	@echo "Cleaning up..."
	rm -rf node_modules __pycache__ pyodide_main.py
