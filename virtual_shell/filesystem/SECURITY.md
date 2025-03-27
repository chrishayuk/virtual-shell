# Security Features for Virtual Filesystem

The Virtual Filesystem includes robust security features designed for AI sandbox environments, allowing you to apply resource limits, path restrictions, and access controls.

## Basic Usage

```python
from virtual_shell.filesystem import VirtualFileSystem

# Create a filesystem with default security profile
fs = VirtualFileSystem(security_profile="default")

# Or apply security to an existing filesystem
fs = VirtualFileSystem()
fs.apply_security("strict")

# Create custom security settings
fs = VirtualFileSystem(
    security_profile="default",
    security_max_file_size=5 * 1024 * 1024,  # 5MB
    security_denied_paths=["/etc", "/var", "/usr"]
)
```

## Available Security Profiles

The system comes with predefined security profiles:

| Profile    | Description                                            |
|------------|--------------------------------------------------------|
| default    | Balanced security for general use                      |
| strict     | Limited paths and sizes for untrusted code             |
| readonly   | Prevents all write operations                          |
| untrusted  | Very limited access for high-risk environments         |
| testing    | Relaxed limits for testing purposes                    |

## Security Features

### Resource Limits

- **File Size Limits**: Prevent creation of excessively large files
- **Total Storage Quota**: Limit overall storage usage
- **File Count Limits**: Restrict the total number of files

### Path Restrictions

- **Allowed Paths**: Restrict filesystem access to specific directories
- **Denied Paths**: Block access to sensitive locations
- **Path Depth Limit**: Prevent deeply nested directory structures

### Content Controls

- **Denied Patterns**: Block files matching specific patterns
- **Read-Only Mode**: Prevent all modifications

### Monitoring

- **Security Violation Logging**: Track all security violations
- **Enhanced Statistics**: View quota usage and limits

## Checking Security Violations

```python
# Get security violations
violations = fs.get_security_violations()
for violation in violations:
    print(f"{violation['operation']} on {violation['path']}: {violation['reason']}")
```

## Read-Only Mode

```python
# Check if filesystem is read-only
if fs.is_read_only():
    print("Filesystem is in read-only mode")

# Switch to read-only mode
fs.set_read_only(True)
```

## Creating Custom Security Profiles

```python
from virtual_shell.filesystem import create_custom_security_profile

# Define a custom profile
create_custom_security_profile("ai_sandbox", {
    "max_file_size": 2 * 1024 * 1024,  # 2MB
    "max_total_size": 50 * 1024 * 1024,  # 50MB
    "read_only": False,
    "allowed_paths": ["/workspace", "/tmp"],
    "denied_paths": ["/etc", "/usr", "/bin"],
    "denied_patterns": [r"\.env", r"\.config", r"\.ssh"],
    "max_path_depth": 5,
    "max_files": 200
})

# Use the custom profile
fs = VirtualFileSystem(security_profile="ai_sandbox")
```

## Security Wrapper Implementation

For advanced use cases, you can directly use the `SecurityWrapper` class:

```python
from virtual_shell.filesystem import SecurityWrapper, get_provider

# Create a base provider
provider = get_provider("memory")

# Wrap it with security settings
secure_provider = SecurityWrapper(
    provider,
    max_file_size=1024 * 1024,
    read_only=True,
    denied_patterns=[r"\.exe$", r"\.sh$"]
)

# Use in a VirtualFileSystem
fs = VirtualFileSystem(secure_provider)
```

## Best Practices for AI Sandboxes

1. **Default to strict profiles**: Start with the "strict" or "untrusted" profile for AI-generated code
2. **Enable read-only when possible**: If the AI only needs to read files, use the "readonly" profile
3. **Set tight resource limits**: Limit file sizes based on expected output size
4. **Restrict paths**: Only allow access to specific directories
5. **Log and review violations**: Monitor security violations to identify potential issues
6. **Sandbox initialization**: Set up the filesystem with necessary files before applying security

## Security Considerations

- The security wrapper operates at the provider API level, not at the OS level
- For stronger isolation, combine with container-level sandboxing (Docker, etc.)
- Security violations are logged but do not halt execution
- Path validation handles normalization to prevent path traversal attacks

## Customizing Security Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| max_file_size | Maximum size of individual files | 10MB |
| max_total_size | Maximum total storage size | 100MB |
| read_only | Whether to prevent all write operations | false |
| allowed_paths | List of allowed path prefixes | ["/"] |
| denied_paths | List of denied path prefixes | ["/etc/passwd", "/etc/shadow"] |
| denied_patterns | List of regex patterns for denied filenames | [r"\.\.", r"\.env"] |
| max_path_depth | Maximum directory nesting depth | 10 |
| max_files | Maximum number of files allowed | 1000 |