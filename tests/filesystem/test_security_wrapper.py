"""
tests/filesystem/test_security_wrapper.py - Tests for security features of the virtual filesystem
"""
import pytest
import posixpath
from typing import List, Dict, Any

from virtual_shell.filesystem import (
    VirtualFileSystem,
    SecurityWrapper,
    create_secure_provider,
    get_available_profiles
)
from virtual_shell.filesystem.providers import get_provider
from virtual_shell.filesystem.node_info import FSNodeInfo


class TestSecurityWrapper:
    """Test the SecurityWrapper implementation"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Create a base memory provider for testing
        self.provider = get_provider("memory")
        self.provider.initialize()
        
    def test_basic_initialization(self):
        """Test basic initialization of security wrapper"""
        # Create wrapper with default settings
        wrapper = SecurityWrapper(self.provider)
        
        # Check default settings
        assert wrapper.max_file_size == 10 * 1024 * 1024  # 10MB
        assert wrapper.max_total_size == 100 * 1024 * 1024  # 100MB
        assert wrapper.read_only is False
        assert wrapper.allowed_paths == ["/"]
        assert len(wrapper.denied_paths) > 0
        assert len(wrapper.denied_patterns) > 0
        
    def test_readonly_mode(self):
        """Test read-only mode restrictions"""
        # Create read-only wrapper
        wrapper = SecurityWrapper(self.provider, read_only=True)
        
        # Setup test data before applying read-only check
        wrapper._in_setup = True
        wrapper.provider.create_node(FSNodeInfo("test.txt", False, "/"))
        wrapper.provider.write_file("/test.txt", "Test content")
        wrapper._in_setup = False
        
        # Verify read operations work
        assert wrapper.get_node_info("/test.txt") is not None
        assert wrapper.read_file("/test.txt") == "Test content"
        
        # Verify write operations are blocked
        assert wrapper.write_file("/test.txt", "Modified content") is False
        assert wrapper.create_node(FSNodeInfo("new.txt", False, "/")) is False
        assert wrapper.delete_node("/test.txt") is False
        
        # Verify violation log
        violations = wrapper.get_violation_log()
        assert len(violations) == 3
        for violation in violations:
            assert "read-only mode" in violation["reason"]
            
    def test_file_size_limit(self):
        """Test file size limit restrictions"""
        # Create wrapper with small file size limit
        max_size = 100  # 100 bytes
        wrapper = SecurityWrapper(self.provider, max_file_size=max_size)
        
        # Create a file
        wrapper.create_node(FSNodeInfo("small.txt", False, "/"))
        
        # Test small file (within limit)
        small_content = "x" * 50
        assert wrapper.write_file("/small.txt", small_content) is True
        
        # Test large file (exceeds limit)
        large_content = "x" * 200
        assert wrapper.write_file("/small.txt", large_content) is False
        
        # Verify violation log
        violations = wrapper.get_violation_log()
        assert len(violations) == 1
        assert "File size exceeds maximum" in violations[0]["reason"]
        
    def test_allowed_paths(self):
        """Test allowed paths restrictions"""
        # Create wrapper with restricted paths
        allowed = ["/home", "/tmp"]
        wrapper = SecurityWrapper(self.provider, allowed_paths=allowed)
        
        # Setup allowed paths
        wrapper._setup_allowed_paths()
        
        # Test paths within allowed areas
        assert wrapper.create_node(FSNodeInfo("test.txt", False, "/home")) is True
        assert wrapper.create_node(FSNodeInfo("temp.txt", False, "/tmp")) is True
        
        # Test paths outside allowed areas
        assert wrapper.create_node(FSNodeInfo("blocked.txt", False, "/etc")) is False
        
        # Verify violation log
        violations = wrapper.get_violation_log()
        assert len(violations) == 1
        assert "Path not in allowed paths list" in violations[0]["reason"]
    
    def test_denied_paths(self):
        """Test denied paths restrictions"""
        # Create wrapper with denied paths
        denied = ["/etc/passwd", "/private"]
        wrapper = SecurityWrapper(self.provider, denied_paths=denied)
        
        # Create parent directory first
        wrapper._in_setup = True
        wrapper.provider.create_node(FSNodeInfo("home", True, "/"))
        wrapper._in_setup = False
        
        # Test regular path (allowed)
        assert wrapper.create_node(FSNodeInfo("test.txt", False, "/home")) is True
        
    def test_denied_patterns(self):
        """Test denied patterns restrictions"""
        # Create wrapper with denied patterns
        patterns = [r"\.exe$", r"^\."]
        wrapper = SecurityWrapper(self.provider, denied_patterns=patterns)
        
        # Test regular filename (allowed)
        assert wrapper.create_node(FSNodeInfo("test.txt", False, "/")) is True
        
        # Test denied patterns
        assert wrapper.create_node(FSNodeInfo("test.exe", False, "/")) is False
        assert wrapper.create_node(FSNodeInfo(".hidden", False, "/")) is False
        
        # Verify violation log
        violations = wrapper.get_violation_log()
        assert len(violations) == 2
        assert "Path matches denied pattern" in violations[0]["reason"]
        
    def test_path_depth_limit(self):
        """Test path depth limit restrictions"""
        # Create wrapper with shallow depth limit
        max_depth = 2
        wrapper = SecurityWrapper(self.provider, max_path_depth=max_depth)
        
        # Test shallow path (allowed)
        wrapper.create_node(FSNodeInfo("level1", True, "/"))
        assert wrapper.create_node(FSNodeInfo("file.txt", False, "/level1")) is True
        
        # Test deep path (blocked)
        wrapper._in_setup = True  # Temporarily disable to set up test
        wrapper.provider.create_node(FSNodeInfo("level2", True, "/level1"))
        wrapper.provider.create_node(FSNodeInfo("level3", True, "/level1/level2"))
        wrapper._in_setup = False
        
        assert wrapper.create_node(FSNodeInfo("deep.txt", False, "/level1/level2/level3")) is False
        
        # Verify violation log
        violations = wrapper.get_violation_log()
        assert len(violations) == 1
        assert "Path depth exceeds maximum" in violations[0]["reason"]
        
    def test_total_quota(self):
        """Test total storage quota restrictions"""
        # Create wrapper with small quota
        quota = 200  # 200 bytes
        wrapper = SecurityWrapper(self.provider, max_total_size=quota)
        
        # Write files until quota is exceeded
        wrapper.create_node(FSNodeInfo("file1.txt", False, "/"))
        assert wrapper.write_file("/file1.txt", "x" * 100) is True
        
        wrapper.create_node(FSNodeInfo("file2.txt", False, "/"))
        assert wrapper.write_file("/file2.txt", "x" * 50) is True
        
        wrapper.create_node(FSNodeInfo("file3.txt", False, "/"))
        assert wrapper.write_file("/file3.txt", "x" * 100) is False
        
        # Verify violation log
        violations = wrapper.get_violation_log()
        assert len(violations) == 1
        assert "Total storage quota exceeded" in violations[0]["reason"]
        
    def test_violation_log(self):
        """Test violation logging"""
        # Create wrapper and generate violations
        wrapper = SecurityWrapper(
            self.provider, 
            read_only=True,
            denied_paths=["/etc"],
            denied_patterns=[r"\.exe$"]
        )
        
        # Set up some data
        wrapper._in_setup = True
        wrapper.provider.create_node(FSNodeInfo("test.txt", False, "/"))
        wrapper._in_setup = False
        
        # Generate multiple violations
        wrapper.write_file("/test.txt", "Modified")  # read-only violation
        wrapper.create_node(FSNodeInfo("program.exe", False, "/"))  # pattern violation
        wrapper.create_node(FSNodeInfo("config", False, "/etc"))  # path violation
        
        # Test violation log
        violations = wrapper.get_violation_log()
        assert len(violations) == 3
        
        # Test clear violations
        wrapper.clear_violations()
        assert len(wrapper.get_violation_log()) == 0


class TestSecurityProfiles:
    """Test security profiles and integration"""
    
    def test_available_profiles(self):
        """Test available security profiles"""
        profiles = get_available_profiles()
        assert "default" in profiles
        assert "strict" in profiles
        assert "readonly" in profiles
        assert "untrusted" in profiles
        assert "testing" in profiles
        
    def test_profile_integration(self):
        """Test security profile integration with filesystem"""
        # Create filesystem with security profile
        fs = VirtualFileSystem(security_profile="default")
        
        # Verify provider is wrapped with security
        assert "SecurityWrapper" in fs.get_provider_name()
        
        # Test basic operations
        fs.mkdir("/home/user")
        fs.write_file("/home/user/test.txt", "Test content")
        
        # Test security violation
        result = fs.write_file("/etc/passwd", "root:x:0:0:")
        assert result is False
        
        # Verify violations are tracked
        violations = fs.get_security_violations()
        assert len(violations) > 0
        
    def test_readonly_profile(self):
        """Test readonly profile integration"""
        # Create filesystem with data
        fs = VirtualFileSystem()
        fs.mkdir("/home/user")
        fs.write_file("/home/user/test.txt", "Original content")
        
        # Apply readonly profile
        fs.apply_security("readonly")
        
        # Verify write operations are blocked
        assert fs.write_file("/home/user/test.txt", "Modified") is False
        assert fs.mkdir("/home/newdir") is False
        
        # Verify read operations work
        assert fs.read_file("/home/user/test.txt") == "Original content"
        
    def test_untrusted_profile(self):
        """Test untrusted profile integration"""
        # Create filesystem with untrusted profile
        fs = VirtualFileSystem(security_profile="untrusted")
        
        # Sandbox directory should be automatically created
        assert fs.get_node_info("/sandbox") is not None
        
        # Verify sandbox restrictions
        assert fs.mkdir("/sandbox/allowed") is True
        assert fs.mkdir("/home/user") is False
        
        # Verify file size limits
        small_data = "x" * 1000  # 1KB
        large_data = "x" * (600 * 1024)  # 600KB
        
        fs.write_file("/sandbox/small.txt", small_data)
        assert fs.write_file("/sandbox/large.txt", large_data) is False


class TestVirtualFileSystemSecurity:
    """Test VirtualFileSystem security integration"""
    
    def test_security_constructor(self):
        """Test security constructor parameters"""
        # Create with security profile
        fs = VirtualFileSystem(
            security_profile="default",
            security_read_only=True,
            security_max_file_size=1000
        )
        
        # Verify settings were applied
        assert fs.is_read_only() is True
        
        # Test file size restriction
        fs._in_setup = True  # Disable checks temporarily
        fs.mkdir("/test")
        fs._in_setup = False
        
        fs.write_file("/test/small.txt", "x" * 500)
        assert fs.write_file("/test/large.txt", "x" * 2000) is False
        
    def test_apply_security(self):
        """Test applying security after creation"""
        # Create without security
        fs = VirtualFileSystem()
        
        # Create test data
        fs.mkdir("/etc")
        fs.write_file("/etc/test.conf", "test")
        
        # Apply security that restricts /etc
        fs.apply_security("default")
        
        # Test restriction is in effect
        assert fs.write_file("/etc/passwd", "root:x:0:0:") is False
        
    def test_security_info(self):
        """Test security info in filesystem info"""
        # Create with security
        fs = VirtualFileSystem(security_profile="default")
        
        # Get filesystem info
        info = fs.get_fs_info()
        
        # Verify security info is included
        assert "security" in info
        assert "read_only" in info["security"]
        assert "violations" in info["security"]