"""
tests/chuk_virtual_shell/commands/test_command_base.py
"""

import pytest
from chuk_virtual_shell.commands.command_base import ShellCommand


# A dummy subclass that properly implements execute()
class DummyCommand(ShellCommand):
    name = "dummy"
    help_text = "Dummy help text"
    category = "dummy"

    def execute(self, args):
        return "dummy executed"


# An incomplete subclass that does not override execute()
class IncompleteCommand(ShellCommand):
    pass


# Test that get_help() returns the defined help_text.
def test_get_help():
    dummy = DummyCommand(shell_context={})
    assert dummy.get_help() == "Dummy help text"


# Test that get_category() returns the defined category.
def test_get_category():
    dummy = DummyCommand(shell_context={})
    assert dummy.get_category() == "dummy"


# Test that calling execute() on the DummyCommand returns the expected output.
def test_execute_dummy_command():
    dummy = DummyCommand(shell_context={})
    result = dummy.execute(["arg1", "arg2"])
    assert result == "dummy executed"


# Test that calling execute() on an incomplete command raises NotImplementedError.
def test_execute_not_implemented():
    incomplete = IncompleteCommand(shell_context={})
    with pytest.raises(NotImplementedError):
        incomplete.execute([])


# Test execute_async default implementation
def test_execute_async_default():
    dummy = DummyCommand(shell_context={})
    # Default async implementation should call synchronous execute
    import asyncio

    result = asyncio.run(dummy.execute_async(["test"]))
    assert result == "dummy executed"


# Test run method with synchronous command
def test_run_synchronous_command():
    dummy = DummyCommand(shell_context={})
    result = dummy.run(["test"])
    assert result == "dummy executed"


# Test async command implementation
class AsyncCommand(ShellCommand):
    name = "async"
    help_text = "Async test command"
    category = "test"

    def execute(self, args):
        return "sync executed"

    async def execute_async(self, args):
        # Custom async implementation
        import asyncio

        await asyncio.sleep(0.001)  # Simulate async work
        return "async executed"


def test_run_async_command():
    async_cmd = AsyncCommand(shell_context={})
    result = async_cmd.run(["test"])
    assert result == "async executed"


# Test async command error handling
class FailingAsyncCommand(ShellCommand):
    name = "failing"
    help_text = "Failing async command"
    category = "test"

    async def execute_async(self, args):
        raise Exception("Async command failed")


def test_run_async_command_with_error():
    failing_cmd = FailingAsyncCommand(shell_context={})
    result = failing_cmd.run(["test"])
    assert "Error executing command 'failing'" in result


# Test async command with timeout scenario (simulate long-running task)
class LongRunningAsyncCommand(ShellCommand):
    name = "longrunning"
    help_text = "Long running async command"
    category = "test"

    async def execute_async(self, args):
        import asyncio

        await asyncio.sleep(0.1)  # Short enough to not timeout
        return "long running completed"


def test_run_long_running_async_command():
    long_cmd = LongRunningAsyncCommand(shell_context={})
    result = long_cmd.run(["test"])
    assert result == "long running completed"


# Test event loop creation scenario
def test_run_async_no_existing_loop():
    # This test runs outside an event loop to test loop creation
    async_cmd = AsyncCommand(shell_context={})
    result = async_cmd.run(["test"])
    assert result == "async executed"


# Test hasattr checks for async detection
def test_async_detection_logic():
    # Test with synchronous command
    dummy = DummyCommand(shell_context={})
    has_custom_async = (
        hasattr(dummy, "execute_async")
        and dummy.execute_async.__func__ is not ShellCommand.execute_async
    )
    assert not has_custom_async

    # Test with async command
    async_cmd = AsyncCommand(shell_context={})
    has_custom_async = (
        hasattr(async_cmd, "execute_async")
        and async_cmd.execute_async.__func__ is not ShellCommand.execute_async
    )
    assert has_custom_async


# Test command with neither execute nor custom execute_async
class AsyncOnlyCommand(ShellCommand):
    name = "asynconly"
    help_text = "Async only command"
    category = "test"

    async def execute_async(self, args):
        return "async only"


def test_async_only_command():
    async_only_cmd = AsyncOnlyCommand(shell_context={})
    result = async_only_cmd.run(["test"])
    assert result == "async only"


# Test base class attributes
def test_base_class_attributes():
    incomplete = IncompleteCommand(shell_context={})
    assert incomplete.name == ""
    assert incomplete.help_text == ""
    assert incomplete.category == ""


def test_command_initialization():
    shell_context = {"test": "context"}
    dummy = DummyCommand(shell_context=shell_context)
    assert dummy.shell == shell_context
