"""
tests/test_sandbox_loader.py - Test sandbox configuration loading
"""
import os
import tempfile
import yaml
import pytest
from unittest.mock import patch, MagicMock

from virtual_shell.sandbox_loader import (
    load_sandbox_config,
    find_sandbox_config,
    list_available_configs,
    create_filesystem_from_config,
    get_environment_from_config,
    _execute_initialization,
    _ensure_directory
)
from virtual_shell.filesystem import VirtualFileSystem


# Sample configuration for testing
SAMPLE_CONFIG = {
    "name": "test_sandbox",
    "description": "Test sandbox configuration",
    "security": {
        "profile": "default",
        "read_only": False,
        "max_file_size": 1024 * 1024,
        "allowed_paths": ["/test"]
    },
    "filesystem": {
        "provider": "memory",
        "provider_args": {"compression_threshold": 1024}
    },
    "environment": {
        "HOME": "/test/home",
        "USER": "tester",
        "PATH": "/bin:/usr/bin"
    },
    "initialization": [
        "mkdir -p /test/home",
        "echo 'Test content' > /test/home/test.txt"
    ]
}


class TestSandboxLoader:
    """Tests for sandbox_loader module"""
    
    def setup_method(self):
        """Set up test environment"""
        # Create a temporary directory for test configs
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # Create a sample YAML configuration
        self.config_path = os.path.join(self.temp_dir.name, "test_sandbox.yaml")
        with open(self.config_path, 'w') as f:
            yaml.dump(SAMPLE_CONFIG, f)
            
        # Create another configuration for testing find function
        self.named_config_path = os.path.join(self.temp_dir.name, "named_config.yaml")
        named_config = SAMPLE_CONFIG.copy()
        named_config["name"] = "named_config"
        with open(self.named_config_path, 'w') as f:
            yaml.dump(named_config, f)
            
    def teardown_method(self):
        """Clean up after test"""
        self.temp_dir.cleanup()
        
    def test_load_sandbox_config(self):
        """Test loading a sandbox configuration from a YAML file"""
        config = load_sandbox_config(self.config_path)
        
        assert config["name"] == "test_sandbox"
        assert config["security"]["profile"] == "default"
        assert config["environment"]["HOME"] == "/test/home"
        
    def test_load_sandbox_config_file_not_found(self):
        """Test loading a non-existent configuration file"""
        with pytest.raises(FileNotFoundError):
            load_sandbox_config("/nonexistent/path.yaml")
            
    def test_find_sandbox_config(self):
        """Test finding a sandbox configuration by name"""
        # Mock the search paths to include our temporary directory
        with patch('virtual_shell.sandbox_loader.os.getcwd', return_value=self.temp_dir.name):
            # Should find the named_config.yaml
            path = find_sandbox_config("named_config")
            assert path is not None
            assert "named_config.yaml" in path
            
            # Should not find a non-existent configuration
            path = find_sandbox_config("nonexistent")
            assert path is None
            
    def test_list_available_configs(self):
        """Test listing available sandbox configurations"""
        # Mock the search paths to include our temporary directory
        with patch('virtual_shell.sandbox_loader.os.getcwd', return_value=self.temp_dir.name):
            configs = list_available_configs()
            assert "test_sandbox" in configs
            assert "named_config" in configs
            
    def test_create_filesystem_from_config(self):
        """Test creating a filesystem from a sandbox configuration"""
        # Create a minimal test configuration
        test_config = {
            "filesystem": {
                "provider": "memory"
            },
            "security": {
                "profile": "default"
            }
        }
        
        # Mock the VirtualFileSystem
        with patch('virtual_shell.sandbox_loader.VirtualFileSystem') as mock_fs:
            mock_instance = MagicMock()
            mock_fs.return_value = mock_instance
            
            # Create filesystem
            fs = create_filesystem_from_config(test_config)
            
            # Verify VirtualFileSystem was called with correct parameters
            mock_fs.assert_called_once_with(
                provider_name="memory",
                security_profile="default"
            )
            
    def test_get_environment_from_config(self):
        """Test getting environment variables from a sandbox configuration"""
        # Test with environment section
        env = get_environment_from_config(SAMPLE_CONFIG)
        assert env["HOME"] == "/test/home"
        assert env["USER"] == "tester"
        
        # Test with empty environment section
        empty_config = {"name": "empty"}
        env = get_environment_from_config(empty_config)
        assert env == {}
        
    def test_execute_initialization(self):
        """Test executing initialization commands"""
        # Create a mock filesystem
        mock_fs = MagicMock(spec=VirtualFileSystem)
        
        # Test initialization commands
        commands = [
            "mkdir -p /test/dir1",
            "mkdir /test/dir2",
            "echo 'Test content' > /test/file.txt"
        ]
        
        _execute_initialization(mock_fs, commands)
        
        # Verify mkdir commands
        assert mock_fs.mkdir.call_count == 1  # Only for the non -p version
        mock_fs.mkdir.assert_called_with("/test/dir2")
        
        # Verify write_file command
        mock_fs.write_file.assert_called_once_with("/test/file.txt", "Test content")
        
    def test_ensure_directory(self):
        """Test ensuring a directory exists"""
        # Create a mock filesystem
        mock_fs = MagicMock(spec=VirtualFileSystem)
        
        # Configure get_node_info to return None (directory doesn't exist)
        mock_fs.get_node_info.return_value = None
        
        # Ensure directory
        _ensure_directory(mock_fs, "/test/dir1/dir2")
        
        # Verify mkdir calls for each component
        assert mock_fs.mkdir.call_count == 3  # Should create /test, /test/dir1, /test/dir1/dir2
        mock_fs.mkdir.assert_any_call("/test")
        mock_fs.mkdir.assert_any_call("/test/dir1")
        mock_fs.mkdir.assert_any_call("/test/dir1/dir2")
    
    def test_integration(self):
        """Integration test for sandbox loader"""
        # Load the configuration
        config = load_sandbox_config(self.config_path)
        
        # Create a real VirtualFileSystem
        fs = VirtualFileSystem()
        
        # Execute initialization commands
        _execute_initialization(fs, config["initialization"])
        
        # Verify the filesystem state
        assert fs.get_node_info("/test/home") is not None
        assert fs.read_file("/test/home/test.txt") == "Test content"