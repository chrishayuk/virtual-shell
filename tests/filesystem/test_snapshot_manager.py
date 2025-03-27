"""
tests/test_snapshot_manager.py - Test suite for snapshot manager functionality
"""
import os
import json
import pytest
import tempfile
import time
from unittest.mock import patch, MagicMock

from virtual_shell.filesystem import VirtualFileSystem
from virtual_shell.filesystem.snapshot_manager import SnapshotManager

def diagnose_filesystem(fs, path="/home"):
    """
    Diagnose filesystem issues by printing detailed information about paths
    
    Args:
        fs: VirtualFileSystem instance to diagnose
        path: Path to examine
    """
    print(f"\n--- Filesystem Diagnostic for {path} ---")
    
    # Check if path exists
    node_info = fs.get_node_info(path)
    if node_info is None:
        print(f"Path does not exist: {path}")
        
        # Check parent path
        parent_path = os.path.dirname(path)
        parent_info = fs.get_node_info(parent_path)
        if parent_info is None:
            print(f"Parent path does not exist: {parent_path}")
        else:
            print(f"Parent path exists: {parent_path}")
            print(f"Parent info: {parent_info.__dict__}")
            
            # List contents of parent
            contents = fs.ls(parent_path)
            print(f"Contents of {parent_path}: {contents}")
        
    else:
        # Path exists, print info
        print(f"Path exists: {path}")
        print(f"Path info: {node_info.__dict__}")
        
        if node_info.is_dir:
            # List contents
            contents = fs.ls(path)
            print(f"Contents: {contents}")
            
    # Try mkdir operation to see errors
    try:
        result = fs.mkdir(path)
        print(f"Attempt to mkdir({path}): {result}")
    except Exception as e:
        print(f"Error during mkdir({path}): {e}")
        
    # Try examine storage provider
    try:
        provider_name = fs.get_provider_name()
        print(f"Provider: {provider_name}")
        
        storage_stats = fs.get_storage_stats()
        print(f"Storage stats: {storage_stats}")
    except Exception as e:
        print(f"Error getting provider info: {e}")
        
    print("--- End Diagnostic ---\n")

class TestSnapshotManager:
    """Test cases for the SnapshotManager class"""
    
    @pytest.fixture
    def clean_fs(self):
        """Fixture to create a clean virtual filesystem for each test"""
        # Create a fresh filesystem
        fs = VirtualFileSystem()
        
        # Check if the /home directory already exists
        home_info = fs.get_node_info("/home")
        if home_info is None:
            # Create it if needed
            fs.mkdir("/home")
        
        # Return the prepared filesystem
        return fs
    
    @pytest.fixture
    def fs(self, clean_fs):
        """Fixture to create a filesystem with basic directories"""
        fs = clean_fs
        
        # Check if /home/user already exists
        user_info = fs.get_node_info("/home/user")
        if user_info is None:
            # Create /home/user if it doesn't exist
            fs.mkdir("/home/user")
        
        return fs
    
    @pytest.fixture
    def populated_fs(self, fs):
        """Fixture to create a populated filesystem with test content"""
        # First check if /home/user exists
        user_info = fs.get_node_info("/home/user")
        if user_info is None:
            fs.mkdir("/home/user")
            
        # Then check and create subdirectories if needed
        docs_info = fs.get_node_info("/home/user/docs")
        if docs_info is None:
            fs.mkdir("/home/user/docs")
            
        projects_info = fs.get_node_info("/home/user/projects")
        if projects_info is None:
            fs.mkdir("/home/user/projects")
            
        test_info = fs.get_node_info("/home/user/projects/test")
        if test_info is None:
            fs.mkdir("/home/user/projects/test")
        
        # Create files if they don't exist
        hello_info = fs.get_node_info("/home/user/hello.txt")
        if hello_info is None:
            fs.write_file("/home/user/hello.txt", "Hello World")
            
        main_info = fs.get_node_info("/home/user/projects/test/main.py")
        if main_info is None:
            fs.write_file("/home/user/projects/test/main.py", "print('Test')")
            
        readme_info = fs.get_node_info("/home/user/docs/readme.md")
        if readme_info is None:
            fs.write_file("/home/user/docs/readme.md", "# Documentation")
        
        # Verify file content
        assert fs.read_file("/home/user/hello.txt") == "Hello World"
        assert fs.read_file("/home/user/projects/test/main.py") == "print('Test')"
        assert fs.read_file("/home/user/docs/readme.md") == "# Documentation"
        
        return fs
    
    @pytest.fixture
    def snapshot_manager(self, populated_fs):
        """Fixture to create a SnapshotManager with populated filesystem"""
        return SnapshotManager(populated_fs)
    
    def test_create_snapshot(self, snapshot_manager):
        """Test creating a named snapshot"""
        # Create a snapshot
        snapshot_name = snapshot_manager.create_snapshot("test_snapshot", "Test snapshot")
        
        # Verify snapshot was created
        assert snapshot_name == "test_snapshot"
        assert "test_snapshot" in snapshot_manager.snapshots
        assert "test_snapshot" in snapshot_manager.snapshot_metadata
        assert snapshot_manager.snapshot_metadata["test_snapshot"]["description"] == "Test snapshot"
    
    def test_create_snapshot_auto_name(self, snapshot_manager):
        """Test creating a snapshot with auto-generated name"""
        # Create a snapshot without providing a name
        snapshot_name = snapshot_manager.create_snapshot(description="Auto-named snapshot")
        
        # Verify snapshot was created with auto-generated name
        assert snapshot_name is not None
        assert snapshot_name.startswith("snapshot_")
        assert snapshot_name in snapshot_manager.snapshots
        assert snapshot_manager.snapshot_metadata[snapshot_name]["description"] == "Auto-named snapshot"
    
    def test_restore_snapshot(self, populated_fs, snapshot_manager):
        """Test restoring from a snapshot"""
        # First verify the required file exists and has expected content
        assert populated_fs.read_file("/home/user/hello.txt") == "Hello World"
        
        # Create initial snapshot
        snapshot_name = snapshot_manager.create_snapshot("initial")
        
        # Modify filesystem
        assert populated_fs.write_file("/home/user/hello.txt", "Modified content")
        assert populated_fs.mkdir("/home/user/new_dir")
        assert populated_fs.write_file("/home/user/new_file.txt", "New file")
        
        # Verify modification
        assert populated_fs.read_file("/home/user/hello.txt") == "Modified content"
        assert populated_fs.get_node_info("/home/user/new_dir") is not None
        
        # Check existing state
        fs_contents = populated_fs.find("/home/user", recursive=True)
        print(f"Contents before restore: {fs_contents}")
        
        # Restore snapshot
        result = snapshot_manager.restore_snapshot(snapshot_name)
        
        # Verify restore was successful
        assert result is True
        
        # Check restored state
        fs_contents = populated_fs.find("/home/user", recursive=True)
        print(f"Contents after restore: {fs_contents}")
        
        # Verify filesystem state after restore
        assert populated_fs.read_file("/home/user/hello.txt") == "Hello World"
        assert populated_fs.get_node_info("/home/user/new_dir") is None, "Directory was not removed during restore"
        assert populated_fs.get_node_info("/home/user/new_file.txt") is None, "File was not removed during restore"
    
    def test_restore_nonexistent_snapshot(self, snapshot_manager):
        """Test restoring a snapshot that doesn't exist"""
        result = snapshot_manager.restore_snapshot("nonexistent")
        assert result is False
    
    def test_delete_snapshot(self, snapshot_manager):
        """Test deleting a snapshot"""
        # Create a snapshot
        snapshot_name = snapshot_manager.create_snapshot("to_delete")
        
        # Verify snapshot exists
        assert snapshot_name in snapshot_manager.snapshots
        
        # Delete snapshot
        result = snapshot_manager.delete_snapshot(snapshot_name)
        
        # Verify deletion
        assert result is True
        assert snapshot_name not in snapshot_manager.snapshots
        assert snapshot_name not in snapshot_manager.snapshot_metadata
    
    def test_delete_nonexistent_snapshot(self, snapshot_manager):
        """Test deleting a snapshot that doesn't exist"""
        result = snapshot_manager.delete_snapshot("nonexistent")
        assert result is False
    
    def test_list_snapshots(self, snapshot_manager):
        """Test listing available snapshots"""
        # Create multiple snapshots
        snapshot_manager.create_snapshot("first", "First snapshot")
        # Add a small delay to ensure timestamps differ
        time.sleep(0.001)
        snapshot_manager.create_snapshot("second", "Second snapshot")
        
        # List snapshots
        snapshots = snapshot_manager.list_snapshots()
        
        # Verify list
        assert len(snapshots) == 2
        snapshot_names = [s["name"] for s in snapshots]
        assert "first" in snapshot_names
        assert "second" in snapshot_names
        
        # Verify snapshots are sorted by creation time (newest first)
        assert snapshots[0]["name"] == "second"  # Most recent first
        assert snapshots[1]["name"] == "first"
    
    def test_export_import_snapshot(self, snapshot_manager, populated_fs):
        """Test exporting and importing a snapshot"""
        # First verify the file exists with expected content
        assert populated_fs.read_file("/home/user/hello.txt") == "Hello World"
        
        # Create a temporary file for the snapshot
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_file:
            export_path = temp_file.name
        
        try:
            # Create and export a snapshot
            snapshot_name = snapshot_manager.create_snapshot("export_test", "Snapshot for export")
            export_result = snapshot_manager.export_snapshot(snapshot_name, export_path)
            
            # Verify export
            assert export_result is True
            assert os.path.exists(export_path)
            
            # Modify filesystem
            assert populated_fs.write_file("/home/user/hello.txt", "Modified for import test")
            assert populated_fs.read_file("/home/user/hello.txt") == "Modified for import test"
            
            # Delete the original snapshot
            snapshot_manager.delete_snapshot(snapshot_name)
            
            # Import the snapshot with a new name
            imported_name = snapshot_manager.import_snapshot(export_path, "imported_snapshot")
            
            # Verify import
            assert imported_name == "imported_snapshot"
            assert "imported_snapshot" in snapshot_manager.snapshots
            
            # Restore the imported snapshot
            restore_result = snapshot_manager.restore_snapshot(imported_name)
            
            # Verify restore from imported snapshot
            assert restore_result is True
            assert populated_fs.read_file("/home/user/hello.txt") == "Hello World"
            
        finally:
            # Clean up temporary file
            if os.path.exists(export_path):
                os.unlink(export_path)
    
    def test_serialize_filesystem(self, populated_fs, snapshot_manager):
        """Test serializing filesystem state"""
        # Verify the test files and directories exist first
        assert populated_fs.get_node_info("/home/user/docs") is not None
        assert populated_fs.get_node_info("/home/user/projects/test") is not None
        assert populated_fs.read_file("/home/user/hello.txt") == "Hello World"
        
        # Serialize the filesystem
        fs_data = snapshot_manager._serialize_filesystem()
        
        # Verify serialized data structure
        assert "version" in fs_data
        assert "timestamp" in fs_data
        assert "directories" in fs_data
        assert "files" in fs_data
        
        # Verify directories
        directories = fs_data["directories"]
        assert "/home/user/docs" in directories
        assert "/home/user/projects" in directories
        assert "/home/user/projects/test" in directories
        
        # Verify files
        files = fs_data["files"]
        assert "/home/user/hello.txt" in files
        assert "/home/user/projects/test/main.py" in files
        assert "/home/user/docs/readme.md" in files
        
        # Verify file content
        assert files["/home/user/hello.txt"]["content"] == "Hello World"
        assert files["/home/user/projects/test/main.py"]["content"] == "print('Test')"
    
    def test_deserialize_filesystem(self, clean_fs, snapshot_manager):
        """Test deserializing filesystem state"""
        # Create test data to deserialize
        fs_data = {
            "version": 1,
            "timestamp": 1234567890,
            "provider": "MemoryStorageProvider",
            "directories": {
                "/test": {"name": "test", "parent": "/"},
                "/test/subdir": {"name": "subdir", "parent": "/test"}
            },
            "files": {
                "/test/file.txt": {
                    "name": "file.txt", 
                    "parent": "/test",
                    "content": "Test file content"
                },
                "/test/subdir/nested.txt": {
                    "name": "nested.txt", 
                    "parent": "/test/subdir",
                    "content": "Nested file content"
                }
            }
        }
        
        # Replace snapshot_manager's filesystem with our clean filesystem
        original_fs = snapshot_manager.fs
        snapshot_manager.fs = clean_fs
        
        try:
            # Deserialize the test data
            result = snapshot_manager._deserialize_filesystem(fs_data)
            
            # Verify deserialization result
            assert result is True
            
            # Verify filesystem state after deserialization
            assert clean_fs.get_node_info("/test").is_dir is True
            assert clean_fs.get_node_info("/test/subdir").is_dir is True
            assert clean_fs.get_node_info("/test/file.txt").is_dir is False
            assert clean_fs.get_node_info("/test/subdir/nested.txt").is_dir is False
            
            # Verify file contents
            assert clean_fs.read_file("/test/file.txt") == "Test file content"
            assert clean_fs.read_file("/test/subdir/nested.txt") == "Nested file content"
        
        finally:
            # Restore original filesystem
            snapshot_manager.fs = original_fs
    
    @patch('time.time', return_value=1234567890)
    def test_snapshot_metadata(self, mock_time, populated_fs, snapshot_manager):
        """Test that snapshot metadata is correctly recorded"""
        # Create a snapshot
        snapshot_name = snapshot_manager.create_snapshot("metadata_test", "Testing metadata")
        
        # Verify metadata
        metadata = snapshot_manager.snapshot_metadata[snapshot_name]
        assert metadata["created"] == 1234567890
        assert metadata["description"] == "Testing metadata"
        assert metadata["fs_provider"] == populated_fs.get_provider_name()
        assert "stats" in metadata
    
    def test_multiple_snapshots_independence(self, populated_fs, snapshot_manager):
        """Test that multiple snapshots maintain independent states"""
        # Verify initial state
        assert populated_fs.read_file("/home/user/hello.txt") == "Hello World"
        
        # Create initial snapshot
        first_snapshot = snapshot_manager.create_snapshot("first_state")
        
        # Modify filesystem
        assert populated_fs.write_file("/home/user/hello.txt", "Modified content")
        assert populated_fs.mkdir("/home/user/snapshot_test")
        
        # Verify modified state
        assert populated_fs.read_file("/home/user/hello.txt") == "Modified content"
        assert populated_fs.get_node_info("/home/user/snapshot_test") is not None
        
        # Create second snapshot
        second_snapshot = snapshot_manager.create_snapshot("second_state")
        
        # Further modify filesystem
        assert populated_fs.write_file("/home/user/hello.txt", "Further modified")
        assert populated_fs.write_file("/home/user/snapshot_test/test.txt", "Test file")
        
        # Verify further modified state
        assert populated_fs.read_file("/home/user/hello.txt") == "Further modified"
        assert populated_fs.read_file("/home/user/snapshot_test/test.txt") == "Test file"
        
        # Check current state
        fs_contents = populated_fs.find("/home/user", recursive=True)
        print(f"Contents before first restore: {fs_contents}")
        
        # Restore to first snapshot
        restore_result = snapshot_manager.restore_snapshot(first_snapshot)
        assert restore_result is True
        
        # Check restored state
        fs_contents = populated_fs.find("/home/user", recursive=True)
        print(f"Contents after first restore: {fs_contents}")
        
        # Verify first snapshot state
        assert populated_fs.read_file("/home/user/hello.txt") == "Hello World"
        assert populated_fs.get_node_info("/home/user/snapshot_test") is None, "Directory was not removed during restore"
        
        # Restore to second snapshot
        restore_result = snapshot_manager.restore_snapshot(second_snapshot)
        assert restore_result is True
        
        # Check second restored state
        fs_contents = populated_fs.find("/home/user", recursive=True)
        print(f"Contents after second restore: {fs_contents}")
        
        # Verify second snapshot state
        assert populated_fs.read_file("/home/user/hello.txt") == "Modified content"
        assert populated_fs.get_node_info("/home/user/snapshot_test") is not None
        assert populated_fs.get_node_info("/home/user/snapshot_test/test.txt") is None

    def test_snapshot_with_complex_directory_structure(self, clean_fs, snapshot_manager):
        """Test snapshot with a more complex directory structure"""
        # Replace snapshot_manager's filesystem with our clean filesystem
        original_fs = snapshot_manager.fs
        snapshot_manager.fs = clean_fs
        
        try:
            # Verify home directory exists
            home_info = clean_fs.get_node_info("/home")
            assert home_info is not None, "/home directory doesn't exist"
            
            # Verify user directory exists
            user_info = clean_fs.get_node_info("/home/user")
            assert user_info is not None, "/home/user directory doesn't exist"
            
            # Check and create /home/user/projects if needed
            projects_info = clean_fs.get_node_info("/home/user/projects")
            if projects_info is None:
                assert clean_fs.mkdir("/home/user/projects") is True
            
            # Check and create app directory if needed
            app_path = "/home/user/projects/app"
            app_info = clean_fs.get_node_info(app_path)
            if app_info is None:
                assert clean_fs.mkdir(app_path) is True
            
            # Create or verify subdirectories
            subdirs = ["src", "tests", "docs"]
            for subdir in subdirs:
                subdir_path = f"{app_path}/{subdir}"
                if clean_fs.get_node_info(subdir_path) is None:
                    assert clean_fs.mkdir(subdir_path) is True
                assert clean_fs.get_node_info(subdir_path) is not None
            
            # Create files at different levels (overwrite if they exist)
            files = {
                f"{app_path}/README.md": "# App README",
                f"{app_path}/src/main.py": "print('Main app')",
                f"{app_path}/tests/test_main.py": "# Test cases",
                f"{app_path}/src/utils.py": "# Utility functions",
                f"{app_path}/src/config.py": "# Configuration"
            }
            
            # Write all files
            for path, content in files.items():
                assert clean_fs.write_file(path, content) is True
            
            # Verify files were created with correct content
            for path, content in files.items():
                assert clean_fs.read_file(path) == content
            
            # Create a snapshot
            snapshot_name = snapshot_manager.create_snapshot("complex_structure")
            
            # Track the original state
            original_paths = set(clean_fs.find("/home/user/projects/app", recursive=True))
            print(f"Original paths: {original_paths}")
            
            # Modify filesystem extensively
            assert clean_fs.rm(f"{app_path}/src/utils.py") is True
            assert clean_fs.rm(f"{app_path}/tests/test_main.py") is True
            
            # Create build directory if it doesn't exist
            build_path = f"{app_path}/build"
            if clean_fs.get_node_info(build_path) is None:
                assert clean_fs.mkdir(build_path) is True
            
            # Write new/modified files
            assert clean_fs.write_file(f"{build_path}/output.log", "Build output") is True
            assert clean_fs.write_file(f"{app_path}/src/main.py", "# Modified main app") is True
            
            # Verify modifications
            assert clean_fs.get_node_info(f"{app_path}/src/utils.py") is None
            assert clean_fs.get_node_info(build_path) is not None
            assert clean_fs.read_file(f"{app_path}/src/main.py") == "# Modified main app"
            
            # Track the modified state
            modified_paths = set(clean_fs.find("/home/user/projects/app", recursive=True))
            print(f"Modified paths: {modified_paths}")
            
            # Restore snapshot
            restore_result = snapshot_manager.restore_snapshot(snapshot_name)
            
            # Track the restored state
            restored_paths = set(clean_fs.find("/home/user/projects/app", recursive=True))
            print(f"Restored paths: {restored_paths}")
            
            # Verify restore
            assert restore_result is True
            assert clean_fs.get_node_info(f"{app_path}/src/utils.py") is not None
            assert clean_fs.get_node_info(f"{app_path}/tests/test_main.py") is not None
            assert clean_fs.get_node_info(build_path) is None
            assert clean_fs.read_file(f"{app_path}/src/main.py") == "print('Main app')"
            
            # Verify full restoration by comparing path sets
            assert restored_paths == original_paths, f"Restored paths don't match original paths: \nOriginal: {original_paths}\nRestored: {restored_paths}"
            
        finally:
            # Restore original filesystem
            snapshot_manager.fs = original_fs
                        
    def test_incremental_changes(self, populated_fs, snapshot_manager):
        """Test incremental changes across multiple snapshots"""
        # Create base snapshot
        base_snapshot = snapshot_manager.create_snapshot("base")
        
        # Make a series of incremental changes with snapshots
        # Change 1
        populated_fs.write_file("/home/user/change1.txt", "Change 1")
        snapshot1 = snapshot_manager.create_snapshot("snapshot1")
        
        # Change 2
        populated_fs.write_file("/home/user/change2.txt", "Change 2")
        snapshot2 = snapshot_manager.create_snapshot("snapshot2")
        
        # Change 3
        populated_fs.write_file("/home/user/change3.txt", "Change 3")
        snapshot3 = snapshot_manager.create_snapshot("snapshot3")
        
        # Verify all changes exist
        assert populated_fs.read_file("/home/user/change1.txt") == "Change 1"
        assert populated_fs.read_file("/home/user/change2.txt") == "Change 2"
        assert populated_fs.read_file("/home/user/change3.txt") == "Change 3"
        
        # Restore to base
        snapshot_manager.restore_snapshot(base_snapshot)
        
        # Verify no changes exist
        assert populated_fs.get_node_info("/home/user/change1.txt") is None
        assert populated_fs.get_node_info("/home/user/change2.txt") is None
        assert populated_fs.get_node_info("/home/user/change3.txt") is None
        
        # Restore to snapshot 2
        snapshot_manager.restore_snapshot(snapshot2)
        
        # Verify only changes 1 and 2 exist
        assert populated_fs.read_file("/home/user/change1.txt") == "Change 1"
        assert populated_fs.read_file("/home/user/change2.txt") == "Change 2"
        assert populated_fs.get_node_info("/home/user/change3.txt") is None