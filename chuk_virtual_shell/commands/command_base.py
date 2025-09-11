"""
chuk_virtual_shell/command_base.py - base class for all shell commands

This updated base class adds support for asynchronous commands while
maintaining backward compatibility with existing synchronous commands.
"""

import logging
import asyncio

logger = logging.getLogger(__name__)


class ShellCommand:
    """Base class for all shell commands"""

    name = ""
    help_text = ""
    category = (
        ""  # For better organization: 'navigation', 'file', 'environment', 'system'
    )

    def __init__(self, shell_context):
        self.shell = shell_context

    def execute(self, args):
        """
        Execute the command with given arguments

        This is the primary method most commands should implement for synchronous operation.
        """
        # By default, this method raises NotImplementedError, which is what we want
        # for synchronous commands that don't implement this method
        raise NotImplementedError("Subclasses must implement execute()")

    async def execute_async(self, args):
        """
        Asynchronous command implementation

        Subclasses that need async capabilities should override this method.
        By default, it calls the synchronous execute method for compatibility.
        """
        # Default implementation calls the sync version
        return self.execute(args)

    def run(self, args):
        """
        Run the command with the appropriate execution mode (sync or async)

        This method determines whether to run the command synchronously or asynchronously
        based on if the command has overridden execute_async and handles event loop issues.

        Shell interpreters should call this method instead of execute() directly.
        """
        # Check if this command has an async implementation that's different from the base class
        has_custom_async = (
            hasattr(self, "execute_async")
            and self.execute_async.__func__ is not ShellCommand.execute_async
        )

        if has_custom_async:
            # If this command has a custom async implementation, handle it appropriately
            try:
                # Try to get the current event loop
                try:
                    loop = asyncio.get_running_loop()
                    if loop.is_running():
                        # We're in an already running event loop, create a new task
                        logger.debug(
                            f"Running command '{self.name}' in existing event loop"
                        )
                        future = asyncio.run_coroutine_threadsafe(
                            self.execute_async(args), loop
                        )
                        return future.result(timeout=30)  # Wait for up to 30 seconds
                except RuntimeError:
                    # No loop is running, create one
                    logger.debug(f"Creating new event loop for command '{self.name}'")
                    return asyncio.run(self.execute_async(args))
            except Exception as e:
                logger.exception(f"Error executing async command '{self.name}': {e}")
                return f"Error executing command '{self.name}': {e}"
        else:
            # For commands that only implement execute(), call it directly
            return self.execute(args)

    def get_help(self):
        """Return help text for the command"""
        return self.help_text

    def get_category(self):
        """Return the command category"""
        return self.category
