"""
virtual_shell/filesystem/providers/__init__.py - Provider registry and factory
"""
from typing import Dict, Type, Optional

from virtual_shell.filesystem.provider_base import StorageProvider

# Registry of available providers
_PROVIDERS: Dict[str, Type[StorageProvider]] = {}


def register_provider(name: str, provider_class: Type[StorageProvider]) -> None:
    """Register a storage provider class with a name"""
    _PROVIDERS[name] = provider_class


def get_provider(name: str, **kwargs) -> Optional[StorageProvider]:
    """
    Create a provider instance by name with given arguments
    
    Args:
        name: The registered name of the provider
        **kwargs: Arguments to pass to the provider constructor
        
    Returns:
        An instance of the requested provider or None if not found
    """
    provider_class = _PROVIDERS.get(name)
    if not provider_class:
        return None
    
    return provider_class(**kwargs)


def list_providers() -> Dict[str, str]:
    """
    List all registered providers with their descriptions
    
    Returns:
        Dictionary of provider names to their descriptions
    """
    return {name: provider_class.__doc__ for name, provider_class in _PROVIDERS.items()}


# Import all provider modules to register them
from virtual_shell.filesystem.providers.memory import MemoryStorageProvider
register_provider("memory", MemoryStorageProvider)

# Optional imports based on available dependencies
try:
    from virtual_shell.filesystem.providers.sqlite import SqliteStorageProvider
    register_provider("sqlite", SqliteStorageProvider)
except ImportError:
    pass  # SQLite not available

try:
    from virtual_shell.filesystem.providers.s3 import S3StorageProvider
    register_provider("s3", S3StorageProvider)
except ImportError:
    pass  # S3 dependencies not available

try:
    from virtual_shell.filesystem.providers.pyodide import PyodideStorageProvider
    register_provider("pyodide", PyodideStorageProvider)
except ImportError:
    pass  # pyodite storage provider not available