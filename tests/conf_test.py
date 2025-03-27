"""
tests/conftest.py - Pytest configuration and shared fixtures
"""
import os
import sys
import pytest

# Add parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Shared fixtures that may be needed across multiple test modules
@pytest.fixture
def temp_file_path():
    """
    Fixture that returns a temporary file path and cleans it up after the test
    """
    import tempfile
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
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