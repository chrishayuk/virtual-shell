"""
Cleanup utilities for agent processes.
"""

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
    warnings.filterwarnings("ignore", message=".*Event loop is closed.*")
    warnings.filterwarnings("ignore", message=".*Task was destroyed.*")

    if not _background_tasks:
        return

    # Simply cancel tasks without trying to wait for them
    # At exit time, it's better to just cancel and let the interpreter handle cleanup
    for task in list(_background_tasks):
        try:
            if not task.done() and not task.cancelled():
                task.cancel()
        except Exception:
            pass  # Ignore tasks that are already gone

    # Clear the set without trying to wait for completion
    _background_tasks.clear()


def suppress_cleanup_warnings():
    """Suppress all async cleanup warnings"""
    import sys

    # Suppress specific warnings
    warnings.filterwarnings("ignore", message=".*Task was destroyed.*")
    warnings.filterwarnings("ignore", message=".*Event loop is closed.*")
    warnings.filterwarnings("ignore", message=".*coroutine.*was never awaited.*")
    warnings.filterwarnings("ignore", category=RuntimeWarning)

    # Also configure logging
    logging.getLogger("asyncio").setLevel(logging.ERROR)
    logging.getLogger("httpx").setLevel(logging.ERROR)
    logging.getLogger("httpcore").setLevel(logging.ERROR)

    # Suppress stderr warnings at the interpreter level
    original_stderr = sys.stderr

    class FilteredStderr:
        def __init__(self, original):
            self.original = original

        def write(self, text):
            # Filter out asyncio cleanup warnings
            if any(
                msg in text
                for msg in [
                    "Task was destroyed",
                    "Event loop is closed",
                    "coroutine",
                    "was never awaited",
                    "RuntimeWarning",
                ]
            ):
                return  # Suppress these messages
            return self.original.write(text)

        def flush(self):
            return self.original.flush()

        def __getattr__(self, name):
            return getattr(self.original, name)

    sys.stderr = FilteredStderr(original_stderr)
