"""
tests/conftest.py - Pytest configuration and shared fixtures
"""

import os
import sys
import pytest

# Add parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


# Shared fixtures that may be needed across multiple test modules
@pytest.fixture
def temp_file_path():
    """
    Fixture that returns a temporary file path and cleans it up after the test
    """
    import tempfile

    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        file_path = tmp.name

    # Provide the path to the test
    yield file_path

    # Clean up after the test
    if os.path.exists(file_path):
        os.unlink(file_path)


@pytest.fixture
def temp_dir_path():
    """
    Fixture that returns a temporary directory path and cleans it up after the test
    """
    import tempfile
    import shutil

    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()

    # Provide the path to the test
    yield temp_dir

    # Clean up after the test
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture(autouse=True)
def patch_shell_command():
    """
    This fixture runs automatically for all tests and patches
    the ShellCommand.run method to make it compatible with older
    tests that don't have it.
    """
    try:
        from chuk_virtual_shell.commands.command_base import ShellCommand

        # Define a simple run method that just calls execute
        def simple_run(self, args):
            return self.execute(args)

        # Save the original run method if it exists
        if hasattr(ShellCommand, "run"):
            original_run = ShellCommand.run
        else:
            original_run = None

        # Patch the run method
        ShellCommand.run = simple_run

        # Let the test run
        yield

        # Restore the original method after the test
        if original_run:
            ShellCommand.run = original_run
        else:
            delattr(ShellCommand, "run")
    except ImportError:
        # If ShellCommand can't be imported, just skip the patching
        yield
