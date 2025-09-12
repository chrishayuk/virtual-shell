"""
tests/chuk_virtual_shell/commands/test_command_loader.py
"""

from chuk_virtual_shell.commands.command_loader import CommandLoader
from chuk_virtual_shell.commands.command_base import ShellCommand
from tests.dummy_shell import DummyShell


# Test for discover_commands
def test_discover_commands():
    # Create a dummy shell with an empty file system and minimal environment.
    dummy_shell = DummyShell({})
    dummy_shell.environ = {}

    # Discover commands using the CommandLoader.
    commands = CommandLoader.discover_commands(dummy_shell)

    # Expected command names as defined in CommandLoader.
    expected_commands = [
        "ls",
        "cd",
        "pwd",
        "mkdir",
        "touch",
        "cat",
        "echo",
        "rm",
        "rmdir",
        "more",
        "env",
        "export",
        "clear",
        "exit",
        "help",
        "script",
    ]

    # Verify that each expected command is present and is an instance of ShellCommand.
    for cmd_name in expected_commands:
        assert cmd_name in commands, f"Missing command: {cmd_name}"
        assert isinstance(
            commands[cmd_name], ShellCommand
        ), f"{cmd_name} is not an instance of ShellCommand"


# Test for load_commands_from_path with non-existent path
def test_load_commands_from_path_nonexistent():
    dummy_shell = DummyShell({})
    dummy_shell.environ = {}

    # Non-existent path should return an empty dict.
    commands = CommandLoader.load_commands_from_path(dummy_shell, "/nonexistent/path")
    assert commands == {}


# Test error handling during module import
def test_discover_commands_with_import_error():
    dummy_shell = DummyShell({})
    dummy_shell.environ = {}

    # Mock importlib.import_module to raise an exception for specific modules
    import importlib
    from unittest.mock import patch

    original_import = importlib.import_module

    def mock_import_module(name):
        if "failing_module" in name:
            raise ImportError("Simulated import error")
        return original_import(name)

    # Mock os.walk to include a "failing_module.py" file
    with (
        patch("os.walk") as mock_walk,
        patch("importlib.import_module", side_effect=mock_import_module),
    ):

        # Set up mock walk to return a structure with our failing module
        mock_walk.return_value = [
            ("/mock/commands", ["system"], ["failing_module.py", "working_module.py"])
        ]

        # This should not raise an error and should continue processing other modules
        commands = CommandLoader.discover_commands(dummy_shell)
        # The function should handle the error gracefully and continue
        assert isinstance(commands, dict)


# Test error handling during command instantiation
def test_discover_commands_with_instantiation_error():
    dummy_shell = DummyShell({})
    dummy_shell.environ = {}

    from unittest.mock import patch, MagicMock
    import inspect

    # Create a mock command class that raises an error during instantiation
    class FailingCommand(ShellCommand):
        name = "failing_cmd"

        def __init__(self, shell_context):
            raise ValueError("Simulated instantiation error")

        def execute(self, args):
            return "should not reach here"

    # Mock inspect.getmembers to return our failing command
    def mock_getmembers(module, predicate):
        if predicate == inspect.isclass:
            return [("FailingCommand", FailingCommand)]
        return []

    # Mock importlib to return a module with our failing command
    mock_module = MagicMock()
    mock_module.FailingCommand = FailingCommand

    with (
        patch("os.walk") as mock_walk,
        patch("importlib.import_module", return_value=mock_module),
        patch("inspect.getmembers", side_effect=mock_getmembers),
    ):

        mock_walk.return_value = [("/mock/commands", [], ["failing_command.py"])]

        # This should handle the instantiation error gracefully
        commands = CommandLoader.discover_commands(dummy_shell)
        assert isinstance(commands, dict)
        assert "failing_cmd" not in commands  # Should not be added due to error
        # The fact that this doesn't raise an exception and returns an empty dict
        # shows that the error handling path (lines 50-51) was executed


# Test load_commands_from_path with existing path and files
def test_load_commands_from_path_with_files():
    dummy_shell = DummyShell({})
    dummy_shell.environ = {}

    from unittest.mock import patch, MagicMock
    import inspect

    # Create a working command class for testing
    class TestLoadCommand(ShellCommand):
        name = "test_load_cmd"

        def __init__(self, shell_context):
            super().__init__(shell_context)

        def execute(self, args):
            return "test output"

    # Mock the module with the command class
    mock_module = MagicMock()
    # Add the TestLoadCommand to the mock module for inspect.getmembers to find
    mock_module.TestLoadCommand = TestLoadCommand

    def mock_getmembers(module, predicate):
        if predicate == inspect.isclass:
            # Return the class from our mock module
            return [("TestLoadCommand", TestLoadCommand)]
        return []

    with (
        patch("os.path.exists", return_value=True),
        patch(
            "os.listdir",
            return_value=["test_command.py", "__init__.py", "not_a_py_file.txt"],
        ),
        patch("importlib.import_module", return_value=mock_module),
        patch("inspect.getmembers", side_effect=mock_getmembers),
    ):

        commands = CommandLoader.load_commands_from_path(dummy_shell, "/mock/path")
        assert "test_load_cmd" in commands
        assert isinstance(commands["test_load_cmd"], TestLoadCommand)


# Test load_commands_from_path with import error
def test_load_commands_from_path_import_error():
    dummy_shell = DummyShell({})
    dummy_shell.environ = {}

    from unittest.mock import patch

    with (
        patch("os.path.exists", return_value=True),
        patch("os.listdir", return_value=["failing_command.py"]),
        patch("importlib.import_module", side_effect=ImportError("Module not found")),
    ):

        # Should handle import error gracefully
        commands = CommandLoader.load_commands_from_path(dummy_shell, "/mock/path")
        assert commands == {}


# Test load_commands_from_path with instantiation error
def test_load_commands_from_path_instantiation_error():
    dummy_shell = DummyShell({})
    dummy_shell.environ = {}

    from unittest.mock import patch, MagicMock
    import inspect

    # Create a command class that fails during instantiation
    class FailingLoadCommand(ShellCommand):
        name = "failing_load_cmd"

        def __init__(self, shell_context):
            raise RuntimeError("Instantiation failed")

        def execute(self, args):
            return "should not reach here"

    mock_module = MagicMock()
    mock_module.FailingLoadCommand = FailingLoadCommand

    def mock_getmembers(module, predicate):
        if predicate == inspect.isclass:
            return [("FailingLoadCommand", FailingLoadCommand)]
        return []

    with (
        patch("os.path.exists", return_value=True),
        patch("os.listdir", return_value=["failing_command.py"]),
        patch("importlib.import_module", return_value=mock_module),
        patch("inspect.getmembers", side_effect=mock_getmembers),
    ):

        # Should handle instantiation error gracefully
        commands = CommandLoader.load_commands_from_path(dummy_shell, "/mock/path")
        assert commands == {}
