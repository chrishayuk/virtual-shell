"""
tests/virtual_shell/commands/system/test_help_command.py
"""
import pytest
from virtual_shell.commands.system.help import HelpCommand
from tests.dummy_shell import DummyShell

# A simple dummy command to simulate help output.
class DummyCommand:
    def __init__(self, name, help_text):
        self.name = name
        self.help_text = help_text

    def get_help(self):
        return self.help_text

# Fixture to create a HelpCommand with a dummy shell as the shell_context
@pytest.fixture
def help_command():
    dummy_shell = DummyShell({})
    # Create a commands dictionary with some dummy commands.
    # These commands fall into the predefined categories:
    # Navigation commands: cd, pwd, ls
    # File commands: cat, echo, touch, mkdir, rm, rmdir
    # Environment commands: env, export
    # System commands: help, exit, clear
    dummy_shell.commands = {
        "cd": DummyCommand("cd", "cd help text"),
        "pwd": DummyCommand("pwd", "pwd help text"),
        "ls": DummyCommand("ls", "ls help text"),
        "cat": DummyCommand("cat", "cat help text"),
        "echo": DummyCommand("echo", "echo help text"),
        "touch": DummyCommand("touch", "touch help text"),
        "mkdir": DummyCommand("mkdir", "mkdir help text"),
        "rm": DummyCommand("rm", "rm help text"),
        "rmdir": DummyCommand("rmdir", "rmdir help text"),
        "env": DummyCommand("env", "env help text"),
        "export": DummyCommand("export", "export help text"),
        "help": DummyCommand("help", "help help text"),
        "exit": DummyCommand("exit", "exit help text"),
        "clear": DummyCommand("clear", "clear help text"),
        # An extra command that is not in a predefined category.
        "foo": DummyCommand("foo", "foo help text"),
    }
    command = HelpCommand(shell_context=dummy_shell)
    return command

# Test help with a specific command argument returns its help text.
def test_help_with_valid_argument(help_command):
    output = help_command.execute(["cat"])
    # Expect to receive the help text of the 'cat' command.
    assert output == "cat help text"

# Test help with an invalid command argument returns the appropriate error message.
def test_help_with_invalid_argument(help_command):
    output = help_command.execute(["nonexistent"])
    assert output == "help: no help found for 'nonexistent'"

# Test help with no arguments returns a categorized help summary.
def test_help_no_arguments(help_command):
    output = help_command.execute([])
    # Check that the output includes the expected category headers.
    assert "Navigation commands:" in output
    assert "File commands:" in output
    assert "Environment commands:" in output
    assert "System commands:" in output
    # Also check that extra commands (not in predefined categories) are listed.
    assert "Other commands:" in output
    # And check that the final message is appended.
    assert "Type 'help [command]' for more information" in output
