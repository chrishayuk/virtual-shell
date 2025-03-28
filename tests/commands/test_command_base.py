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
