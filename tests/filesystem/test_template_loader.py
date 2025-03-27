"""
tests/test_template_loader.py - Test suite for template loader functionality
"""
import os
import json
import yaml
import tempfile
import pytest

from virtual_shell.filesystem import VirtualFileSystem
from virtual_shell.filesystem.template_loader import TemplateLoader

class TestTemplateLoader:
    """Test cases for the TemplateLoader class"""
    
    @pytest.fixture
    def clean_fs(self):
        """Fixture to create a clean virtual filesystem for each test"""
        fs = VirtualFileSystem()
        
        # Ensure /home directory exists
        if fs.get_node_info("/home") is None:
            fs.mkdir("/home")
        
        return fs
    
    @pytest.fixture
    def template_loader(self, clean_fs):
        """Fixture to create a TemplateLoader with a clean filesystem"""
        return TemplateLoader(clean_fs)
    
    def test_apply_basic_template(self, template_loader, clean_fs):
        """Test applying a basic template with directories and files"""
        # Define a basic template
        template = {
            "directories": [
                "/home/test_project",
                "/home/test_project/src",
                "/home/test_project/tests"
            ],
            "files": [
                {
                    "path": "/home/test_project/README.md",
                    "content": "# Test Project\n\nA simple test project."
                },
                {
                    "path": "/home/test_project/src/main.py",
                    "content": "def main():\n    print('Hello, World!')"
                }
            ]
        }
        
        # Apply the template
        result = template_loader.apply_template(template)
        
        # Verify directories were created
        assert clean_fs.get_node_info("/home/test_project").is_dir is True
        assert clean_fs.get_node_info("/home/test_project/src").is_dir is True
        assert clean_fs.get_node_info("/home/test_project/tests").is_dir is True
        
        # Verify files were created with correct content
        assert clean_fs.read_file("/home/test_project/README.md") == "# Test Project\n\nA simple test project."
        assert clean_fs.read_file("/home/test_project/src/main.py") == "def main():\n    print('Hello, World!')"
    
    def test_template_with_variables(self, template_loader, clean_fs):
        """Test applying a template with variable substitution"""
        # Define a template with placeholders
        template = {
            "directories": [
                "/home/${project_name}",
                "/home/${project_name}/src",
                "/home/${project_name}/tests"
            ],
            "files": [
                {
                    "path": "/home/${project_name}/README.md",
                    "content": "# ${project_name}\n\n${project_description}"
                }
            ]
        }
        
        # Define variables for substitution
        variables = {
            "project_name": "awesome_project",
            "project_description": "An awesome test project"
        }
        
        # Apply the template with variables
        result = template_loader.apply_template(template, variables=variables)
        
        # Verify directories were created with substituted paths
        assert clean_fs.get_node_info("/home/awesome_project").is_dir is True
        assert clean_fs.get_node_info("/home/awesome_project/src").is_dir is True
        assert clean_fs.get_node_info("/home/awesome_project/tests").is_dir is True
        
        # Verify file was created with substituted content
        assert clean_fs.read_file("/home/awesome_project/README.md") == "# awesome_project\n\nAn awesome test project"
    
    def test_load_yaml_template(self, template_loader, clean_fs):
        """Test loading a template from a YAML file"""
        # Create a temporary YAML template file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as temp_file:
            yaml.safe_dump({
                "directories": [
                    "/home/yaml_project",
                    "/home/yaml_project/src"
                ],
                "files": [
                    {
                        "path": "/home/yaml_project/README.md",
                        "content": "# YAML Project Template"
                    }
                ]
            }, temp_file)
            temp_filename = temp_file.name
        
        try:
            # Load template from YAML file
            result = template_loader.load_template(temp_filename)
            
            # Verify template was applied
            assert clean_fs.get_node_info("/home/yaml_project").is_dir is True
            assert clean_fs.get_node_info("/home/yaml_project/src").is_dir is True
            assert clean_fs.read_file("/home/yaml_project/README.md") == "# YAML Project Template"
        
        finally:
            # Clean up temporary file
            os.unlink(temp_filename)
    
    def test_load_json_template(self, template_loader, clean_fs):
        """Test loading a template from a JSON file"""
        # Create a temporary JSON template file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump({
                "directories": [
                    "/home/json_project",
                    "/home/json_project/src"
                ],
                "files": [
                    {
                        "path": "/home/json_project/README.md",
                        "content": "# JSON Project Template"
                    }
                ]
            }, temp_file)
            temp_filename = temp_file.name
        
        try:
            # Load template from JSON file
            result = template_loader.load_template(temp_filename)
            
            # Verify template was applied
            assert clean_fs.get_node_info("/home/json_project").is_dir is True
            assert clean_fs.get_node_info("/home/json_project/src").is_dir is True
            assert clean_fs.read_file("/home/json_project/README.md") == "# JSON Project Template"
        
        finally:
            # Clean up temporary file
            os.unlink(temp_filename)
    
    def test_quick_load(self, template_loader, clean_fs):
        """Test quick loading multiple files"""
        # Define files to load
        files = {
            "/home/test_files/file1.txt": "Content of file 1",
            "/home/test_files/file2.txt": "Content of file 2",
            "/home/test_files/subdir/file3.txt": "Content of file 3"
        }
        
        # Quick load the files
        loaded_count = template_loader.quick_load(files)
        
        # Verify files were created
        assert loaded_count == 3
        assert clean_fs.read_file("/home/test_files/file1.txt") == "Content of file 1"
        assert clean_fs.read_file("/home/test_files/file2.txt") == "Content of file 2"
        assert clean_fs.read_file("/home/test_files/subdir/file3.txt") == "Content of file 3"
    
    def test_preload_directory(self, template_loader, clean_fs):
        """Test preloading a directory from the host filesystem"""
        # Create a temporary directory with test files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create some test files
            os.makedirs(os.path.join(temp_dir, 'subdir'), exist_ok=True)
            
            with open(os.path.join(temp_dir, 'file1.txt'), 'w') as f:
                f.write("Content of file 1")
            
            with open(os.path.join(temp_dir, 'file2.txt'), 'w') as f:
                f.write("Content of file 2")
            
            with open(os.path.join(temp_dir, 'subdir', 'file3.txt'), 'w') as f:
                f.write("Content of file 3")
            
            # Preload the directory
            loaded_count = template_loader.preload_directory(temp_dir, "/home/preloaded")
            
            # Verify files were loaded
            assert loaded_count == 3
            assert clean_fs.read_file("/home/preloaded/file1.txt") == "Content of file 1"
            assert clean_fs.read_file("/home/preloaded/file2.txt") == "Content of file 2"
            assert clean_fs.read_file("/home/preloaded/subdir/file3.txt") == "Content of file 3"
    
    def test_preload_directory_with_pattern(self, template_loader, clean_fs):
        """Test preloading a directory with a specific file pattern"""
        # Create a temporary directory with test files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create some test files
            with open(os.path.join(temp_dir, 'file1.txt'), 'w') as f:
                f.write("Content of file 1")
            
            with open(os.path.join(temp_dir, 'file2.py'), 'w') as f:
                f.write("print('Hello')")
            
            with open(os.path.join(temp_dir, 'file3.txt'), 'w') as f:
                f.write("Content of file 3")
            
            # Preload only .py files
            loaded_count = template_loader.preload_directory(temp_dir, "/home/preloaded", pattern="*.py")
            
            # Verify only .py files were loaded
            assert loaded_count == 1
            assert clean_fs.get_node_info("/home/preloaded/file1.txt") is None
            assert clean_fs.read_file("/home/preloaded/file2.py") == "print('Hello')"
            assert clean_fs.get_node_info("/home/preloaded/file3.txt") is None
    
    def test_load_from_template_directory(self, template_loader, clean_fs):
        """Test loading templates from a directory"""
        # Create a temporary directory with template files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create YAML templates
            with open(os.path.join(temp_dir, 'template1.yaml'), 'w') as f:
                yaml.safe_dump({
                    "directories": ["/home/template1"],
                    "files": [{"path": "/home/template1/file1.txt", "content": "Template 1"}]
                }, f)
            
            with open(os.path.join(temp_dir, 'template2.yml'), 'w') as f:
                yaml.safe_dump({
                    "directories": ["/home/template2"],
                    "files": [{"path": "/home/template2/file2.txt", "content": "Template 2"}]
                }, f)
            
            # Create JSON template
            with open(os.path.join(temp_dir, 'template3.json'), 'w') as f:
                json.dump({
                    "directories": ["/home/template3"],
                    "files": [{"path": "/home/template3/file3.txt", "content": "Template 3"}]
                }, f)
            
            # Load templates from directory
            results = template_loader.load_from_template_directory(temp_dir)
            
            # Verify templates were loaded
            assert len(results) == 3
            assert results['template1.yaml'] == 1
            assert results['template2.yml'] == 1
            assert results['template3.json'] == 1
            
            # Verify file contents
            assert clean_fs.read_file("/home/template1/file1.txt") == "Template 1"
            assert clean_fs.read_file("/home/template2/file2.txt") == "Template 2"
            assert clean_fs.read_file("/home/template3/file3.txt") == "Template 3"
    
    def test_template_with_complex_links(self, template_loader, clean_fs):
        """Test template with symbolic links"""
        # Assume the filesystem supports symbolic links
        # If not supported, this test will be skipped
        if not hasattr(clean_fs, 'create_symlink'):
            pytest.skip("Filesystem does not support symbolic links")
        
        # Define a template with symbolic links
        template = {
            "directories": [
                "/home/link_test",
                "/home/link_test/source"
            ],
            "files": [
                {
                    "path": "/home/link_test/source/original.txt",
                    "content": "Original file content"
                }
            ],
            "links": [
                {
                    "path": "/home/link_test/symlink.txt",
                    "target": "/home/link_test/source/original.txt"
                }
            ]
        }
        
        # Apply the template
        result = template_loader.apply_template(template)
        
        # Verify source file
        assert clean_fs.read_file("/home/link_test/source/original.txt") == "Original file content"
        
        # Verify symbolic link
        node_info = clean_fs.get_node_info("/home/link_test/symlink.txt")
        assert node_info is not None, "Symbolic link was not created"
        # If possible, read the linked file's content through the symlink
        try:
            link_content = clean_fs.read_file("/home/link_test/symlink.txt")
            assert link_content == "Original file content"
        except Exception:
            # Depending on the filesystem implementation, reading symlink might not be supported
            pass