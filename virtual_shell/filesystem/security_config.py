"""
virtual_shell/filesystem/security_config.py - Security configuration helpers
"""
from typing import Dict, List, Optional, Any

from virtual_shell.filesystem.provider_base import StorageProvider
from virtual_shell.filesystem.security_wrapper import SecurityWrapper


# Default security profiles
SECURITY_PROFILES = {
    "default": {
        "max_file_size": 10 * 1024 * 1024,  # 10MB
        "max_total_size": 100 * 1024 * 1024,  # 100MB
        "read_only": False,
        "allowed_paths": ["/"],
        "denied_paths": ["/etc/passwd", "/etc/shadow", "/etc/ssh"],
        "denied_patterns": [r"\.\.", r"\.env", r"\.ssh", r"\.aws", r"\.config"],
        "max_path_depth": 10,
        "max_files": 1000
    },
    "strict": {
        "max_file_size": 1 * 1024 * 1024,  # 1MB
        "max_total_size": 20 * 1024 * 1024,  # 20MB
        "read_only": False,
        "allowed_paths": ["/home", "/tmp"],
        "denied_paths": ["/etc", "/bin", "/sbin", "/usr", "/var", "/root"],
        "denied_patterns": [r"\.\.", r"\.", r"\..*", r".*\.exe", r".*\.sh"],
        "max_path_depth": 5,
        "max_files": 100
    },
    "readonly": {
        "max_file_size": 10 * 1024 * 1024,  # 10MB
        "max_total_size": 100 * 1024 * 1024,  # 100MB
        "read_only": True,
        "allowed_paths": ["/"],
        "denied_paths": [],
        "denied_patterns": [],
        "max_path_depth": 15,
        "max_files": 5000
    },
    "untrusted": {
        "max_file_size": 512 * 1024,  # 512KB
        "max_total_size": 5 * 1024 * 1024,  # 5MB
        "read_only": False,
        "allowed_paths": ["/sandbox"],
        "denied_paths": ["/etc", "/bin", "/home", "/usr"],  # Removed "/" to allow creation of allowed paths
        "denied_patterns": [r"\.\.", r"^\.", r".*\.(exe|sh|bat|cmd|py|rb|pl)$"],  # Only block specific extensions
        "max_path_depth": 3,
        "max_files": 50
    },
    "testing": {
        "max_file_size": 100 * 1024 * 1024,  # 100MB
        "max_total_size": 1024 * 1024 * 1024,  # 1GB
        "read_only": False,
        "allowed_paths": ["/"],
        "denied_paths": [],
        "denied_patterns": [r".*\.malicious"],
        "max_path_depth": 20,
        "max_files": 10000
    }
}


def create_secure_provider(
    provider: StorageProvider,
    profile: str = "default",
    setup_allowed_paths: bool = True,
    **overrides
) -> SecurityWrapper:
    """
    Create a security-wrapped provider using a predefined profile
    
    Args:
        provider: Base storage provider to wrap
        profile: Security profile name ("default", "strict", "readonly", "untrusted", "testing")
        setup_allowed_paths: Whether to automatically create allowed paths
        **overrides: Override specific security settings
        
    Returns:
        SecurityWrapper instance with the specified profile
    """
    # Get profile settings
    if profile not in SECURITY_PROFILES:
        raise ValueError(f"Unknown security profile: {profile}")
        
    settings = SECURITY_PROFILES[profile].copy()
    
    # Apply any overrides
    settings.update(overrides)
    
    # Add setup_allowed_paths parameter
    settings['setup_allowed_paths'] = setup_allowed_paths
    
    # Create and return the wrapped provider
    return SecurityWrapper(provider, **settings)


def create_custom_security_profile(
    name: str,
    settings: Dict[str, Any]
) -> None:
    """
    Create a custom security profile
    
    Args:
        name: Name for the new profile
        settings: Security settings dictionary
    """
    if name in SECURITY_PROFILES:
        raise ValueError(f"Profile '{name}' already exists")
        
    # Validate required settings
    required_settings = [
        "max_file_size", "max_total_size", "read_only"
    ]
    for setting in required_settings:
        if setting not in settings:
            raise ValueError(f"Missing required setting: {setting}")
            
    # Add the new profile
    SECURITY_PROFILES[name] = settings.copy()


def get_available_profiles() -> List[str]:
    """
    Get the list of available security profiles
    
    Returns:
        List of profile names
    """
    return list(SECURITY_PROFILES.keys())


def get_profile_settings(profile: str) -> Dict[str, Any]:
    """
    Get the settings for a specific profile
    
    Args:
        profile: Profile name
        
    Returns:
        Dictionary of profile settings
    """
    if profile not in SECURITY_PROFILES:
        raise ValueError(f"Unknown security profile: {profile}")
        
    return SECURITY_PROFILES[profile].copy()


def setup_profile_paths(provider: StorageProvider, profile: str) -> bool:
    """
    Set up required paths for a security profile
    
    This can be used to prepare a filesystem before applying security restrictions.
    
    Args:
        provider: Storage provider to set up
        profile: Security profile name
        
    Returns:
        True if setup was successful
    """
    if profile not in SECURITY_PROFILES:
        return False
        
    settings = SECURITY_PROFILES[profile]
    allowed_paths = settings.get('allowed_paths', ["/"])
    
    # Create a temporary security wrapper just for setup
    temp_wrapper = SecurityWrapper(
        provider,
        allowed_paths=allowed_paths,
        setup_allowed_paths=True
    )
    
    # The wrapper will automatically set up paths
    return True