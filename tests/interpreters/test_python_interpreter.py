"""
tests/interpreters/test_python_interpreter.py - Tests for Python script interpreter
"""

import pytest
from chuk_virtual_shell.interpreters.python_interpreter import VirtualPythonInterpreter
from chuk_virtual_shell.commands.system.python import PythonCommand
from tests.dummy_shell import DummyShell


@pytest.fixture
def python_setup():
    # Create shell with some test files
    files = {
        "/data.txt": "Hello World",
        "/numbers.txt": "1\n2\n3\n4\n5",
    }
    shell = DummyShell(files)
    interpreter = VirtualPythonInterpreter(shell)
    python_command = PythonCommand(shell_context=shell)
    return interpreter, python_command, shell


@pytest.mark.asyncio
async def test_simple_print(python_setup):
    interpreter, _, _ = python_setup

    code = "print('Hello World')"
    result = await interpreter.execute_code(code)
    assert "Hello World" in result


@pytest.mark.asyncio
async def test_variable_assignment(python_setup):
    interpreter, _, _ = python_setup

    code = """
x = 10
y = 20
print(x + y)
"""
    result = await interpreter.execute_code(code)
    assert "30" in result


@pytest.mark.asyncio
async def test_file_operations_read(python_setup):
    interpreter, _, shell = python_setup

    code = """
with open('data.txt', 'r') as f:
    content = f.read()
    print(content)
"""
    result = await interpreter.execute_code(code)
    assert "Hello World" in result


@pytest.mark.asyncio
async def test_file_operations_write(python_setup):
    interpreter, _, shell = python_setup

    code = """
with open('output.txt', 'w') as f:
    f.write('Test Output')
print('File written')
"""
    result = await interpreter.execute_code(code)
    assert "File written" in result

    # Check file was created
    content = shell.fs.read_file("/output.txt")
    assert content == "Test Output"


@pytest.mark.asyncio
async def test_file_operations_append(python_setup):
    interpreter, _, shell = python_setup

    # Create initial file
    shell.fs.write_file("/append.txt", "Initial\n")

    code = """
with open('append.txt', 'a') as f:
    f.write('Appended')
"""
    await interpreter.execute_code(code)

    content = shell.fs.read_file("/append.txt")
    assert content == "Initial\nAppended"


@pytest.mark.asyncio
async def test_os_module_operations(python_setup):
    interpreter, _, shell = python_setup

    code = """
import os
print('CWD:', os.getcwd())
print('Files:', os.listdir('.'))
"""
    result = await interpreter.execute_code(code)
    assert "CWD:" in result
    assert "Files:" in result


@pytest.mark.asyncio
async def test_os_path_operations(python_setup):
    interpreter, _, shell = python_setup

    code = """
import os
print('data.txt exists:', os.path.exists('data.txt'))
print('data.txt is file:', os.path.isfile('data.txt'))
print('nonexistent exists:', os.path.exists('nonexistent'))
"""
    result = await interpreter.execute_code(code)
    assert "data.txt exists: True" in result
    assert "data.txt is file: True" in result
    assert "nonexistent exists: False" in result


@pytest.mark.asyncio
async def test_subprocess_module(python_setup):
    interpreter, _, shell = python_setup

    code = """
import subprocess
result = subprocess.run(['echo', 'Hello'], capture_output=True, text=True)
print('Output:', result.stdout)
print('Return code:', result.returncode)
"""
    result = await interpreter.execute_code(code)
    assert "Output: Hello" in result or "Output:" in result
    assert "Return code: 0" in result


@pytest.mark.asyncio
async def test_exception_handling(python_setup):
    interpreter, _, _ = python_setup

    code = """
try:
    x = 1 / 0
except ZeroDivisionError:
    print('Caught division by zero')
"""
    result = await interpreter.execute_code(code)
    assert "Caught division by zero" in result


@pytest.mark.asyncio
async def test_syntax_error(python_setup):
    interpreter, _, _ = python_setup

    code = "print('unclosed"
    result = await interpreter.execute_code(code)
    assert "SyntaxError" in result


@pytest.mark.asyncio
async def test_runtime_error(python_setup):
    interpreter, _, _ = python_setup

    code = "undefined_variable"
    result = await interpreter.execute_code(code)
    assert "NameError" in result or "undefined_variable" in result


@pytest.mark.asyncio
async def test_script_execution(python_setup):
    interpreter, _, shell = python_setup

    # Create a Python script
    script = """
import os

def main():
    print('Script running')
    files = os.listdir('.')
    print(f'Found {len(files)} files')
    
    with open('script_output.txt', 'w') as f:
        f.write('Script was here')

if __name__ == '__main__':
    main()
"""
    shell.fs.write_file("/test_script.py", script)

    result = await interpreter.run_script("/test_script.py")
    assert "Script running" in result
    assert "Found" in result

    # Check output file
    content = shell.fs.read_file("/script_output.txt")
    assert content == "Script was here"


@pytest.mark.asyncio
async def test_script_with_arguments(python_setup):
    interpreter, _, shell = python_setup

    script = """
import sys
print('Script name:', sys.argv[0])
print('Arguments:', sys.argv[1:])
"""
    shell.fs.write_file("/args_script.py", script)

    result = await interpreter.run_script("/args_script.py", ["arg1", "arg2"])
    assert "Script name: /args_script.py" in result
    assert "['arg1', 'arg2']" in result


def test_python_command_basic(python_setup):
    _, python_command, shell = python_setup

    # Test -c option
    result = python_command.execute(["-c", "print('Hello from command')"])
    assert "Hello from command" in result


def test_python_command_script(python_setup):
    _, python_command, shell = python_setup

    # Create a test script
    shell.fs.write_file("/hello.py", "print('Hello')\nprint('World')")

    result = python_command.execute(["/hello.py"])
    assert "Hello" in result
    assert "World" in result


def test_python_command_version(python_setup):
    _, python_command, shell = python_setup

    result = python_command.execute(["-V"])
    assert "Python" in result


def test_python_command_errors(python_setup):
    _, python_command, shell = python_setup

    # Test missing file
    result = python_command.execute(["nonexistent.py"])
    assert "No such file" in result

    # Test -c without argument
    result = python_command.execute(["-c"])
    assert "requires an argument" in result


@pytest.mark.asyncio
async def test_file_iteration(python_setup):
    interpreter, _, shell = python_setup

    # Create file with multiple lines
    shell.fs.write_file("/lines.txt", "Line 1\nLine 2\nLine 3")

    code = """
with open('lines.txt', 'r') as f:
    for i, line in enumerate(f, 1):
        print(f'{i}: {line.strip()}')
"""
    result = await interpreter.execute_code(code)
    assert "1: Line 1" in result
    assert "2: Line 2" in result
    assert "3: Line 3" in result


@pytest.mark.asyncio
async def test_makedirs(python_setup):
    interpreter, _, shell = python_setup

    code = """
import os
os.makedirs('new/nested/dir', exist_ok=True)
print('Directory created')
"""
    result = await interpreter.execute_code(code)
    assert "Directory created" in result

    # Check directory was created
    assert shell.fs.is_directory("/new/nested/dir")


def test_python_sync_execution(python_setup):
    interpreter, _, shell = python_setup

    code = "print('Sync execution')"
    result = interpreter.execute_code_sync(code)
    assert "Sync execution" in result

    # Test script execution
    shell.fs.write_file("sync_test.py", "print('Sync script')")
    result = interpreter.run_script_sync("sync_test.py")
    assert "Sync script" in result
