"""
Cleanup utilities for agent processes.
"""

import asyncio
import atexit
import warnings
import logging

logger = logging.getLogger(__name__)

# Track all background tasks
_background_tasks = set()
_cleanup_registered = False


def track_task(task):
    """Track a background task for cleanup"""
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)
    _register_cleanup()


def _register_cleanup():
    """Register cleanup handler once"""
    global _cleanup_registered
    if not _cleanup_registered:
        atexit.register(_cleanup_all)
        _cleanup_registered = True


def _cleanup_all():
    """Clean up all background tasks on exit"""
    # Suppress warnings during cleanup
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    warnings.filterwarnings("ignore", message=".*Task.*")
    
    if _background_tasks:
        # Cancel all tasks
        for task in _background_tasks:
            if not task.done():
                task.cancel()
        
        # Try to run cleanup if event loop exists
        try:
            loop = asyncio.get_event_loop()
            if loop and not loop.is_closed():
                # Create a cleanup coroutine
                async def cleanup():
                    await asyncio.gather(*_background_tasks, return_exceptions=True)
                
                # Run cleanup with timeout
                loop.run_until_complete(
                    asyncio.wait_for(cleanup(), timeout=1.0)
                )
        except:
            pass  # Ignore all cleanup errors
        
        _background_tasks.clear()


def suppress_cleanup_warnings():
    """Suppress all async cleanup warnings"""
    import sys
    import io
    
    # Suppress specific warnings
    warnings.filterwarnings("ignore", message=".*Task was destroyed.*")
    warnings.filterwarnings("ignore", message=".*Event loop is closed.*")
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    
    # Also configure logging
    logging.getLogger("asyncio").setLevel(logging.ERROR)
    logging.getLogger("httpx").setLevel(logging.ERROR)
    logging.getLogger("httpcore").setLevel(logging.ERROR)