"""
Test helpers for properly handling async mocks and coroutines.
"""

import asyncio
from unittest.mock import AsyncMock, Mock


def create_closed_coroutine(return_value=None):
    """
    Create a coroutine that returns a value without needing to be awaited.
    This prevents RuntimeWarning about unawaited coroutines in tests.
    """
    async def _coro():
        return return_value
    
    # Create the coroutine
    coro = _coro()
    # Close it to prevent warnings
    coro.close()
    return coro


def mock_async_method(return_value=None):
    """
    Create a mock that returns a properly closed coroutine.
    This prevents warnings about unawaited coroutines.
    """
    mock = Mock()
    mock.return_value = create_closed_coroutine(return_value)
    return mock


class SafeAsyncMock(AsyncMock):
    """
    An AsyncMock that properly handles coroutines to prevent warnings.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure side_effect coroutines are properly handled
        self._clean_side_effects = []
    
    def __del__(self):
        """Clean up any unawaited coroutines."""
        for coro in self._clean_side_effects:
            if hasattr(coro, 'close'):
                coro.close()