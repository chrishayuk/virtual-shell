import pytest
from chuk_virtual_shell.commands.system.script import ScriptCommand
from tests.dummy_shell import DummyShell


# A dummy ScriptRunner to simulate script execution.
class DummyScriptRunner:
    def __init__(self, shell):
        self.shell = shell

    def run_script(self, script_path):
        # Simulate running a script by returning a message.
        return f"Ran {script_path}"


# Fixture to create a ScriptCommand with a dummy shell as the shell_context.
@pytest.fixture
def script_command(monkeypatch):
    # Monkey-patch ScriptRunner in the module where it's used so that it uses our dummy runner.
    monkeypatch.setattr(
        "chuk_virtual_shell.commands.system.script.ScriptRunner", DummyScriptRunner
    )

    # Setup a dummy file system; its contents are not used by ScriptCommand.
    dummy_shell = DummyShell({})
    dummy_shell.environ = {}
    command = ScriptCommand(shell_context=dummy_shell)
    return command


def test_script_missing_operand(script_command):
    """
    Test that executing the script command without a filename returns the expected error message.
    """
    output = script_command.execute([])
    assert output == "script: missing operand"


def test_script_execution(script_command):
    """
    Test that the script command correctly delegates to ScriptRunner and returns the simulated message.
    """
    # Execute the command with a filename argument.
    output = script_command.execute(["myscript.sh"])
    # Expect the dummy ScriptRunner to return a specific message.
    assert output == "Ran myscript.sh"
