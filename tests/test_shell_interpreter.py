"""
tests/chuk_virtual_shell/test_shell_interpreter.py
"""

import pytest

# virtual shell imports
from chuk_virtual_shell.shell_interpreter import ShellInterpreter


# A dummy command for testing purposes.
class DummyCommand:
    name = "dummy"
    help_text = "dummy help"
    category = "test"

    def __init__(self, shell_context):
        self.shell = shell_context

    def execute(self, args):
        return "dummy executed"

    # Add the run method to support the new shell interpreter
    def run(self, args):
        return self.execute(args)


@pytest.fixture
def shell_interpreter(monkeypatch):
    # Patch the CommandLoader.discover_commands to return a controlled set of commands.
    from chuk_virtual_shell.commands.command_loader import CommandLoader

    monkeypatch.setattr(
        CommandLoader, "discover_commands", lambda shell: {"dummy": DummyCommand(shell)}
    )
    si = ShellInterpreter()
    return si


# Test parsing an empty command line returns (None, [])
def test_parse_command_empty():
    si = ShellInterpreter()
    cmd, args = si.parse_command("")
    assert cmd is None
    assert args == []


# Test parsing a single-word command
def test_parse_command_simple():
    si = ShellInterpreter()
    cmd, args = si.parse_command("ls")
    assert cmd == "ls"
    assert args == []


# Test parsing a command with multiple arguments
def test_parse_command_multiple():
    si = ShellInterpreter()
    cmd, args = si.parse_command("echo hello world")
    assert cmd == "echo"
    assert args == ["hello", "world"]


# Test executing a known command registered by the loader (dummy command)
def test_execute_known_command(shell_interpreter):
    output = shell_interpreter.execute("dummy")
    assert output == "dummy executed"


# Test executing an unknown command returns an error message.
def test_execute_unknown_command(shell_interpreter):
    output = shell_interpreter.execute("unknown")
    assert output == "unknown: command not found"


# Test that the shell prompt reflects the environment variables.
def test_prompt(shell_interpreter):
    shell_interpreter.environ["USER"] = "tester"
    shell_interpreter.environ["PWD"] = "/home/tester"
    prompt = shell_interpreter.prompt()
    expected = "tester@pyodide:/home/tester$ "
    assert prompt == expected


# Test that _register_command correctly adds a new command.
def test_register_command(shell_interpreter):
    # Define another dummy command.
    class AnotherDummy:
        name = "another"
        help_text = "another help"
        category = "test"

        def __init__(self, shell_context):
            self.shell = shell_context

        def execute(self, args):
            return "another executed"

        # Add the run method to support the new shell interpreter
        def run(self, args):
            return self.execute(args)

    # Register the new command.
    shell_interpreter._register_command(AnotherDummy(shell_interpreter))
    # Execute the newly registered command.
    output = shell_interpreter.execute("another")
    assert output == "another executed"
