import pytest
from chuk_virtual_shell.commands.system.help import HelpCommand
from tests.dummy_shell import DummyShell


# A simple dummy command to simulate help output.
class DummyCommand:
    def __init__(self, name, help_text):
        self.name = name
        self.help_text = help_text

    def get_help(self):
        return self.help_text


# Fixture to create a HelpCommand with a dummy shell as the shell_context.
@pytest.fixture
def help_command():
    dummy_shell = DummyShell({})
    # Populate a commands dictionary with dummy commands.
    # Predefined categories:
    #   Navigation: cd, pwd, ls
    #   File: cat, echo, touch, mkdir, rm, rmdir
    #   Environment: env, export
    #   System: help, exit, clear
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
        # Extra command outside the predefined categories.
        "foo": DummyCommand("foo", "foo help text"),
    }
    command = HelpCommand(shell_context=dummy_shell)
    return command


def test_help_with_valid_argument(help_command):
    """
    Test that calling help with a valid command argument returns its specific help text.
    """
    output = help_command.execute(["cat"])
    assert output == "cat help text"


def test_help_with_invalid_argument(help_command):
    """
    Test that calling help with an invalid command argument returns an appropriate error message.
    """
    output = help_command.execute(["nonexistent"])
    assert output == "help: no help found for 'nonexistent'"


def test_help_no_arguments(help_command):
    """
    Test that calling help without arguments returns a categorized help summary.
    This summary should include headers for Navigation, File, Environment, System,
    and also list any extra commands under 'Other commands', plus a final help prompt.
    """
    output = help_command.execute([])
    # Verify that each expected category header is present.
    assert "Navigation commands:" in output
    assert "File commands:" in output
    assert "Environment commands:" in output
    assert "System commands:" in output
    # Check that extra commands are listed.
    assert "Other commands:" in output
    # Check that a final help prompt is included.
    assert "Type 'help [command]' for more information" in output
