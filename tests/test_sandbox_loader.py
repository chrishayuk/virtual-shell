"""
tests/test_sandbox_loader.py - Test sandbox configuration loading
"""
import os
import tempfile
import yaml
import pytest
from unittest.mock import patch, MagicMock

# virtual file system imports
from chuk_virtual_fs import VirtualFileSystem

# virtual shell imports
from chuk_virtual_shell.sandbox_loader import (
    load_sandbox_config,
    find_sandbox_config,
    list_available_configs,
    list_available_templates,
    create_filesystem_from_config,
    get_environment_from_config,
    _execute_initialization,
    _ensure_directory,
    _find_filesystem_template  # for patching in tests
)

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
    "filesystem-template": {
        "name": "python_project",
        "variables": {
            "project_name": "test_project",
            "project_description": "A test project",
            "project_version": "0.1.0"
        }
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
        
        # Create a sample filesystem template
        self.template_dir = tempfile.TemporaryDirectory()
        template_path = os.path.join(self.template_dir.name, "python_project.yaml")
        template_data = {
            "directories": [
                "/home/${project_name}",
                "/home/${project_name}/src",
                "/home/${project_name}/tests"
            ],
            "files": [
                {
                    "path": "/home/${project_name}/README.md",
                    "content": "# ${project_name}\n\n${project_description}"
                },
                {
                    "path": "/home/${project_name}/src/main.py",
                    "content": "def main():\n    print('Hello, ${project_name}!')"
                }
            ]
        }
        with open(template_path, 'w') as f:
            yaml.safe_dump(template_data, f)
            
    def teardown_method(self):
        """Clean up after test"""
        self.temp_dir.cleanup()
        self.template_dir.cleanup()
        
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
        with patch('chuk_virtual_shell.sandbox_loader.os.getcwd', return_value=self.temp_dir.name):
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
        with patch('chuk_virtual_shell.sandbox_loader.os.getcwd', return_value=self.temp_dir.name):
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
        # Call the function and verify it returns a VirtualFileSystem instance
        fs = create_filesystem_from_config(test_config)
        assert isinstance(fs, VirtualFileSystem)
            
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
        # "mkdir -p" should ensure directory exists without calling mkdir,
        # while "mkdir /test/dir2" calls mkdir.
        assert mock_fs.mkdir.call_count == 1
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
        assert mock_fs.mkdir.call_count == 3
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
    
    def test_load_sandbox_config_with_template(self):
        """Test loading a sandbox configuration with a filesystem template"""
        config = load_sandbox_config(self.config_path)
        
        assert "filesystem-template" in config
        assert config["filesystem-template"]["name"] == "python_project"
        assert config["filesystem-template"]["variables"]["project_name"] == "test_project"
        
    def test_create_filesystem_from_config_with_template(self):
        """Test creating a filesystem from a configuration with a template"""
        # Patch _find_filesystem_template to return a known path.
        template_file_path = os.path.join(self.template_dir.name, "python_project.yaml")
        with patch('chuk_virtual_shell.sandbox_loader._find_filesystem_template', return_value=template_file_path):
            with patch('chuk_virtual_shell.sandbox_loader.TemplateLoader') as mock_template_loader:
                mock_loader_instance = MagicMock()
                mock_template_loader.return_value = mock_loader_instance
                
                # Temporarily add the template directory to the environment
                with patch('chuk_virtual_shell.sandbox_loader.os.environ', 
                           {**os.environ, 'CHUK_VIRTUAL_SHELL_TEMPLATE_DIR': self.template_dir.name}):
                    fs = create_filesystem_from_config(SAMPLE_CONFIG)
                    
                    # Verify the TemplateLoader was instantiated once
                    mock_template_loader.assert_called_once()
                    
                    # Verify load_template was called once with expected arguments
                    mock_loader_instance.load_template.assert_called_once()
                    args, kwargs = mock_loader_instance.load_template.call_args
                    # Expect variables passed in kwargs
                    assert 'variables' in kwargs
                    assert kwargs['variables']['project_name'] == 'test_project'
                    # The first argument should be our template file path with basename 'python_project.yaml'
                    assert os.path.basename(args[0]) == 'python_project.yaml'
    
    def test_list_available_templates(self):
        """Test listing available filesystem templates"""
        # Patch os.listdir and os.path.exists to simulate our template directory contents.
        with patch('chuk_virtual_shell.sandbox_loader.os.environ', 
                   {**os.environ, 'CHUK_VIRTUAL_SHELL_TEMPLATE_DIR': self.template_dir.name}):
            with patch('chuk_virtual_shell.sandbox_loader.os.path.exists', return_value=True):
                with patch('chuk_virtual_shell.sandbox_loader.os.listdir', return_value=["python_project.yaml"]):
                    templates = list_available_templates()
                    assert "python_project" in templates
    
    def test_template_with_missing_name(self):
        """Test handling of configuration with missing template name"""
        # Create a config without a template name
        config_copy = SAMPLE_CONFIG.copy()
        del config_copy['filesystem-template']['name']
        
        # Patch logger.warning instead of print since warnings are logged
        with patch('chuk_virtual_shell.sandbox_loader.logger.warning') as mock_warning:
            fs = create_filesystem_from_config(config_copy)
            mock_warning.assert_called_with("Filesystem template name not specified")
    
    def test_template_with_nonexistent_template(self):
        """Test handling of configuration with a non-existent template"""
        # Create a config with a non-existent template
        config_copy = SAMPLE_CONFIG.copy()
        config_copy['filesystem-template']['name'] = 'nonexistent_template'
        
        with patch('chuk_virtual_shell.sandbox_loader.logger.warning') as mock_warning:
            fs = create_filesystem_from_config(config_copy)
            mock_warning.assert_called_with("Filesystem template nonexistent_template not found")
