"""
tests/chuk_virtual_shell/test_script_runner.py
"""

import pytest

# virtual shell imports
from chuk_virtual_shell.script_runner import ScriptRunner


# Dummy file system for our dummy shell.
class DummyFS:
    def __init__(self, files):
        self.files = files

    def read_file(self, path):
        return self.files.get(path, None)


# Dummy shell that provides an fs, an execute() method, and a running flag.
class DummyShell:
    def __init__(self, files):
        self.fs = DummyFS(files)
        self.running = True
        self.executed_commands = []  # Keep track of executed commands for verification

    def execute(self, cmd_line):
        # Record the command that was executed.
        self.executed_commands.append(cmd_line.strip())
        # Simulate command execution:
        # If the command is "exit", simulate a shell exit.
        if cmd_line.strip() == "exit":
            self.running = False
            return "Goodbye!"
        # Otherwise, return a dummy result.
        return f"result: {cmd_line.strip()}"


# Fixture to provide a new dummy shell for each test.
@pytest.fixture
def dummy_shell():
    # Initialize with an empty file dictionary.
    return DummyShell({})


def test_run_script_file_not_found(dummy_shell):
    runner = ScriptRunner(dummy_shell)
    # Attempt to run a script that does not exist.
    output = runner.run_script("nonexistent.sh")
    assert output == "script: cannot open 'nonexistent.sh': No such file"


def test_run_script_content_single_command(dummy_shell):
    runner = ScriptRunner(dummy_shell)
    # Provide a simple script with one command.
    script_content = "echo hello"
    output = runner.run_script_content(script_content)
    # Expect the dummy shell to process the command.
    assert output == "result: echo hello"


def test_run_script_content_multiple_commands(dummy_shell):
    runner = ScriptRunner(dummy_shell)
    # Create a script with multiple commands, including empty lines and comments.
    script_content = """
# This is a comment line that should be skipped
echo hello

echo world
"""
    output = runner.run_script_content(script_content)
    # Expected execution of "echo hello" and "echo world" only.
    expected = "result: echo hello\nresult: echo world"
    assert output == expected


def test_run_script_stop_on_exit(dummy_shell):
    runner = ScriptRunner(dummy_shell)
    # Script containing an "exit" command should stop further execution.
    script_content = """
echo first
exit
echo second
"""
    output = runner.run_script_content(script_content)
    # Expected output: "echo first" then "exit" returns "Goodbye!" and stops execution.
    expected = "result: echo first\nGoodbye!"
    assert output == expected
    # Also, verify that "echo second" was never executed.
    assert "echo second" not in dummy_shell.executed_commands
