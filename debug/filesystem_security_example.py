"""
security_example.py - Example showing security features of the virtual filesystem
"""
from virtual_shell.filesystem import (
    VirtualFileSystem,
    create_secure_provider,
    get_available_profiles,
    get_profile_settings
)


def security_profiles_demo():
    """Demonstrate available security profiles"""
    print("\n===== SECURITY PROFILES =====")
    profiles = get_available_profiles()
    for profile in profiles:
        settings = get_profile_settings(profile)
        print(f"\n{profile.upper()} Profile:")
        print(f"  Max File Size: {settings['max_file_size'] / 1024 / 1024:.1f} MB")
        print(f"  Max Total Size: {settings['max_total_size'] / 1024 / 1024:.1f} MB")
        print(f"  Read Only: {settings['read_only']}")
        print(f"  Max Files: {settings['max_files']}")
        print(f"  Max Path Depth: {settings['max_path_depth']}")
        if 'allowed_paths' in settings:
            print(f"  Allowed Paths: {settings['allowed_paths']}")


def default_security_example():
    """Example using the default security profile"""
    print("\n===== DEFAULT SECURITY PROFILE =====")
    fs = VirtualFileSystem(security_profile="default")
    
    # Create test files
    print("Creating test directories and files...")
    fs.mkdir("/home/user")
    fs.write_file("/home/user/test.txt", "Hello, secure world!")
    print("Created /home/user/test.txt successfully")
    
    # Show filesystem stats
    stats = fs.get_storage_stats()
    print(f"Storage stats: {stats}")
    
    # Try to create a file in a denied path (should fail)
    print("\nAttempting to write to denied path /etc/passwd...")
    result = fs.write_file("/etc/passwd", "root:x:0:0:")
    print(f"Write to /etc/passwd: {'Success' if result else 'Failed (as expected)'}")
    
    # Try to create a file with a denied pattern
    print("\nAttempting to create file with denied pattern '..'...")
    result = fs.touch("/home/user/..hidden")
    print(f"Create file with '..' pattern: {'Success' if result else 'Failed (as expected)'}")
    
    # View security violations
    violations = fs.get_security_violations()
    print(f"\nSecurity violations detected: {len(violations)}")
    for i, violation in enumerate(violations):
        print(f"  {i+1}. {violation['operation']} on {violation['path']}: {violation['reason']}")


def readonly_example():
    """Example using the readonly security profile"""
    print("\n===== READ-ONLY SECURITY PROFILE =====")
    
    # Create a filesystem and populate it
    print("Creating filesystem with sample data...")
    fs = VirtualFileSystem()
    fs.mkdir("/home/user")
    fs.write_file("/home/user/important.txt", "Important read-only data")
    print("Created /home/user/important.txt successfully")
    
    # Now apply read-only security
    print("\nApplying read-only security profile...")
    fs.apply_security("readonly")
    print("Security profile applied")
    
    # Attempt to modify (should fail)
    print("\nAttempting to modify file in read-only filesystem...")
    result = fs.write_file("/home/user/important.txt", "Modified data")
    print(f"Write to file: {'Success' if result else 'Failed (as expected)'}")
    
    # Attempt to create new file (should fail)
    print("\nAttempting to create new file in read-only filesystem...")
    result = fs.touch("/home/user/newfile.txt")
    print(f"Create new file: {'Success' if result else 'Failed (as expected)'}")
    
    # Reading should still work
    print("\nAttempting to read file in read-only filesystem...")
    content = fs.read_file("/home/user/important.txt")
    print(f"Read content: '{content}'")
    
    # View security violations
    violations = fs.get_security_violations()
    print(f"\nSecurity violations detected: {len(violations)}")
    for i, violation in enumerate(violations):
        print(f"  {i+1}. {violation['operation']} on {violation['path']}: {violation['reason']}")


def quota_example():
    """Example demonstrating storage quotas"""
    print("\n===== STORAGE QUOTA EXAMPLE =====")
    
    # Create a filesystem with a very small quota
    # Note: With improvements, allowed paths are created automatically
    print("Creating filesystem with 'untrusted' security profile (tight limits)...")
    fs = VirtualFileSystem(security_profile="untrusted")
    
    # Show quota limits
    stats = fs.get_storage_stats()
    print(f"Max file size: {stats['max_file_size'] / 1024:.1f} KB")
    print(f"Max total size: {stats['max_total_size'] / 1024:.1f} KB")
    print(f"Allowed paths: {stats.get('allowed_paths', ['all'])}")
    
    # The /sandbox directory should now exist automatically
    print("\nVerifying that sandbox directory exists...")
    sandbox_exists = fs.get_node_info("/sandbox") is not None
    print(f"Sandbox directory exists: {'Yes' if sandbox_exists else 'No'}")
    
    # Try to write a small file (should succeed)
    small_data = "x" * 1000  # 1KB
    print("\nWriting 1KB file (should succeed)...")
    result = fs.write_file("/sandbox/small.txt", small_data)
    print(f"Write 1KB file: {'Success' if result else 'Failed'}")
    
    # Try to write a file exceeding the max file size
    large_data = "x" * (600 * 1024)  # 600KB
    print("\nAttempting to write 600KB file (should fail due to file size limit)...")
    result = fs.write_file("/sandbox/large.txt", large_data)
    print(f"Write 600KB file: {'Success' if result else 'Failed (as expected)'}")
    
    # Try to write to a path outside allowed paths
    print("\nAttempting to write to path outside allowed area...")
    result = fs.write_file("/home/test.txt", "Outside sandbox")
    print(f"Write outside allowed path: {'Success' if result else 'Failed (as expected)'}")
    
    # View security violations
    violations = fs.get_security_violations()
    print(f"\nSecurity violations detected: {len(violations)}")
    for i, violation in enumerate(violations):
        print(f"  {i+1}. {violation['operation']} on {violation['path']}: {violation['reason']}")


def custom_security_example():
    """Example with custom security settings"""
    print("\n===== CUSTOM SECURITY EXAMPLE =====")
    
    # Create filesystem with custom security settings and automatic path creation
    print("Creating filesystem with custom security settings...")
    fs = VirtualFileSystem(
        security_profile="default",
        security_max_file_size=50 * 1024,  # 50KB
        security_allowed_paths=["/projects", "/data"],
        security_denied_patterns=[r".*\.exe", r".*\.sh", r".*\.zip"]
    )
    
    # Verify allowed directories are created automatically
    print("\nVerifying allowed directories were automatically created...")
    projects_exists = fs.get_node_info("/projects") is not None
    data_exists = fs.get_node_info("/data") is not None
    print(f"Projects directory exists: {'Yes' if projects_exists else 'No'}")
    print(f"Data directory exists: {'Yes' if data_exists else 'No'}")
    
    # Write to allowed path
    print("\nWriting to allowed path...")
    result = fs.write_file("/projects/notes.txt", "Project notes")
    print(f"Write to allowed path: {'Success' if result else 'Failed'}")
    
    # Try to write to non-allowed path
    print("\nAttempting to write to non-allowed path...")
    result = fs.write_file("/home/user.txt", "Test")
    print(f"Write to non-allowed path: {'Success' if result else 'Failed (as expected)'}")
    
    # Try to create denied file type
    print("\nAttempting to create denied file type...")
    result = fs.touch("/projects/script.sh")
    print(f"Create denied file type: {'Success' if result else 'Failed (as expected)'}")
    
    # Test clearing violations
    print("\nClearing security violations...")
    fs.provider.clear_violations()
    violations = fs.get_security_violations()
    print(f"Violations after clearing: {len(violations)}")
    
    # Generate a new violation
    print("\nGenerating new violation after clearing...")
    fs.touch("/projects/archive.zip")
    new_violations = fs.get_security_violations()
    print(f"New violations count: {len(new_violations)}")
    if new_violations:
        print(f"  Latest violation: {new_violations[0]['operation']} on {new_violations[0]['path']}")
    
    # Show filesystem info with security details
    print("\nFilesystem info with security details:")
    info = fs.get_fs_info()
    print(f"  Provider: {info['provider_name']}")
    print(f"  Current directory: {info['current_directory']}")
    if 'security' in info:
        print(f"  Read-only: {info['security']['read_only']}")
        print(f"  Security violations: {info['security']['violations']}")
        
    # Get storage stats with security info
    stats = fs.get_storage_stats()
    print("\nStorage stats with security info:")
    print(f"  Max file size: {stats['max_file_size'] / 1024:.1f} KB")
    print(f"  Total used: {stats['total_size_bytes']} bytes")
    print(f"  File count: {stats['file_count']} / {stats['max_files']}")


if __name__ == "__main__":
    print("==================================================")
    print(" VIRTUAL FILESYSTEM SECURITY FEATURES DEMONSTRATION")
    print("==================================================")
    
    security_profiles_demo()
    default_security_example()
    readonly_example()
    quota_example()
    custom_security_example()
    
    print("\n==================================================")
    print(" SECURITY DEMONSTRATION COMPLETE")
    print("==================================================")