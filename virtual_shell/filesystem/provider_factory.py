"""
virtual_shell/filesystem/provider_factory.py - Factory for creating storage providers
"""
from typing import Dict, Any, Optional

from virtual_shell.filesystem.provider_base import StorageProvider
from virtual_shell.filesystem.providers import get_provider, list_providers


class ProviderFactory:
    """
    Factory for creating and managing filesystem storage providers
    """
    
    @staticmethod
    def create(provider_name: str = "memory", **kwargs) -> Optional[StorageProvider]:
        """
        Create a storage provider instance
        
        Args:
            provider_name: Name of the provider to create
            **kwargs: Arguments to pass to the provider constructor
        
        Returns:
            Provider instance or None if provider not found
        """
        provider = get_provider(provider_name, **kwargs)
        if provider and hasattr(provider, 'initialize'):
            provider.initialize()
        return provider
    
    @staticmethod
    def get_available_providers() -> Dict[str, Any]:
        """
        Get all available providers
        
        Returns:
            Dictionary of provider names and classes
        """
        return list_providers()
    
    @staticmethod
    def is_provider_available(name: str) -> bool:
        """
        Check if a provider is available
        
        Args:
            name: Name of the provider to check
        
        Returns:
            True if provider is available, False otherwise
        """
        providers = list_providers()
        return name.lower() in providers
    
    @staticmethod
    def provider_metadata() -> Dict[str, Dict[str, Any]]:
        """
        Get metadata for all available providers
        
        Returns:
            Dictionary of provider metadata
        """
        providers = list_providers()
        metadata = {}
        
        for name, provider_class in providers.items():
            # Get provider description from docstring
            description = provider_class.__doc__ or "No description available"
            description = description.strip().split('\n')[0]
            
            # Get provider parameters from init method
            import inspect
            signature = inspect.signature(provider_class.__init__)
            params = []
            
            for param_name, param in signature.parameters.items():
                if param_name == 'self':
                    continue
                    
                param_info = {
                    'name': param_name,
                    'required': param.default == inspect.Parameter.empty,
                    'default': None if param.default == inspect.Parameter.empty else param.default
                }
                params.append(param_info)
            
            metadata[name] = {
                'description': description,
                'parameters': params,
                'class': provider_class.__name__
            }
            
        return metadata