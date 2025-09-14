"""
tests/interpreters/test_bash_interpreter.py - Tests for bash script interpreter
"""

import pytest
from chuk_virtual_shell.interpreters.bash_interpreter import VirtualBashInterpreter
from chuk_virtual_shell.commands.system.sh import ShCommand
from tests.dummy_shell import DummyShell


@pytest.fixture
def bash_setup():
    # Create shell with some test files
    files = {
        "test.txt": "Hello World",
        "data.txt": "Line 1\nLine 2\nLine 3",
        "script.sh": "#!/bin/sh\necho Hello\necho World",
    }
    shell = DummyShell(files)
    interpreter = VirtualBashInterpreter(shell)
    sh_command = ShCommand(shell_context=shell)
    return interpreter, sh_command, shell


@pytest.mark.asyncio
async def test_variable_assignment(bash_setup):
    interpreter, _, _ = bash_setup

    result = await interpreter.execute_line("NAME=John")
    assert result == ""
    assert interpreter.variables["NAME"] == "John"

    result = await interpreter.execute_line('MESSAGE="Hello World"')
    assert interpreter.variables["MESSAGE"] == "Hello World"


@pytest.mark.asyncio
async def test_variable_expansion(bash_setup):
    interpreter, _, _ = bash_setup
    interpreter.variables["NAME"] = "Alice"

    expanded = interpreter._expand_variables("Hello $NAME")
    assert expanded == "Hello Alice"

    expanded = interpreter._expand_variables("Hello ${NAME}")
    assert expanded == "Hello Alice"


@pytest.mark.asyncio
async def test_export_command(bash_setup):
    interpreter, _, shell = bash_setup

    await interpreter.execute_line("export PATH=/usr/bin")
    assert shell.environ["PATH"] == "/usr/bin"

    interpreter.variables["VAR"] = "value"
    await interpreter.execute_line("export VAR")
    assert shell.environ["VAR"] == "value"


@pytest.mark.asyncio
async def test_command_execution(bash_setup):
    interpreter, _, shell = bash_setup

    # Test echo command
    result = await interpreter.execute_line("echo Hello")
    assert "Hello" in result

    # Test with variable
    interpreter.variables["MSG"] = "Test"
    result = await interpreter.execute_line("echo $MSG")
    assert "Test" in result


@pytest.mark.asyncio
async def test_pipeline(bash_setup):
    interpreter, _, shell = bash_setup

    # Create test commands in shell
    shell.fs.write_file("names.txt", "Alice\nBob\nCarol")

    # Test pipe (simplified - would need grep command implemented)
    result = await interpreter.execute_line("cat names.txt")
    assert "Alice" in result
    assert "Bob" in result


@pytest.mark.asyncio
async def test_output_redirection(bash_setup):
    interpreter, _, shell = bash_setup

    # Test > redirection
    await interpreter.execute_line("echo Hello > output.txt")
    content = shell.fs.read_file("output.txt")
    assert "Hello" in content

    # Test >> redirection
    await interpreter.execute_line("echo World >> output.txt")
    content = shell.fs.read_file("output.txt")
    assert "Hello" in content
    assert "World" in content


@pytest.mark.asyncio
async def test_input_redirection(bash_setup):
    interpreter, _, shell = bash_setup

    # Test < redirection
    shell.fs.write_file("input.txt", "Test Input")
    result = await interpreter.execute_line("cat < input.txt")
    assert "Test Input" in result


@pytest.mark.asyncio
async def test_logical_operators(bash_setup):
    interpreter, _, shell = bash_setup

    # Test && operator
    result = await interpreter.execute_line("echo First && echo Second")
    assert "First" in result
    # Note: Full implementation would show both outputs

    # Test || operator
    result = await interpreter.execute_line("false || echo Fallback")
    # Note: Would need false command implemented


@pytest.mark.asyncio
async def test_for_loop(bash_setup):
    interpreter, _, shell = bash_setup

    # Test simple for loop
    script = "for i in 1 2 3; do echo Number $i; done"
    result = await interpreter.execute_line(script)
    assert "Number 1" in result
    assert "Number 2" in result
    assert "Number 3" in result


@pytest.mark.asyncio
async def test_if_statement(bash_setup):
    interpreter, _, shell = bash_setup

    # Test file existence check
    shell.fs.write_file("exists.txt", "content")
    result = await interpreter.execute_line("if [ -f exists.txt ]; then echo Found; fi")
    assert "Found" in result

    # Test string comparison
    interpreter.variables["VAR"] = "test"
    result = await interpreter.execute_line(
        'if [ "$VAR" = "test" ]; then echo Match; fi'
    )
    assert "Match" in result


@pytest.mark.asyncio
async def test_script_execution(bash_setup):
    interpreter, _, shell = bash_setup

    # Create a test script
    script_content = """#!/bin/sh
NAME="Script Test"
echo "Hello from $NAME"
echo "Current directory: $(pwd)"
"""
    shell.fs.write_file("test_script.sh", script_content)

    result = await interpreter.run_script("test_script.sh")
    assert "Hello from Script Test" in result


@pytest.mark.asyncio
async def test_special_variables(bash_setup):
    interpreter, _, shell = bash_setup

    # Test $? (exit code)
    result = interpreter._expand_variables("Exit code: $?")
    assert "Exit code: 0" in result

    # Test $$ (process ID simulation)
    result = interpreter._expand_variables("PID: $$")
    assert "PID:" in result


def test_sh_command_basic(bash_setup):
    _, sh_command, shell = bash_setup

    # Test executing a simple command
    result = sh_command.execute(["-c", "echo Hello"])
    assert "Hello" in result


def test_sh_command_script(bash_setup):
    _, sh_command, shell = bash_setup

    # Create a test script
    shell.fs.write_file("hello.sh", "echo Hello\necho World")

    result = sh_command.execute(["hello.sh"])
    assert "Hello" in result
    assert "World" in result


def test_sh_command_errors(bash_setup):
    _, sh_command, shell = bash_setup

    # Test missing file
    result = sh_command.execute(["nonexistent.sh"])
    assert "No such file or directory" in result

    # Test -c without argument
    result = sh_command.execute(["-c"])
    assert "requires an argument" in result


@pytest.mark.asyncio
async def test_variable_default_values(bash_setup):
    interpreter, _, shell = bash_setup

    # Test ${VAR:-default}
    result = interpreter._expand_variables("${UNDEFINED:-default}")
    assert result == "default"

    interpreter.variables["DEFINED"] = "value"
    result = interpreter._expand_variables("${DEFINED:-default}")
    assert result == "value"

    # Test ${VAR:=default}
    result = interpreter._expand_variables("${NEW_VAR:=assigned}")
    assert result == "assigned"
    assert interpreter.variables["NEW_VAR"] == "assigned"
