"""
tests/chuk_virtual_shell/commands/text/test_sed_command.py
"""

import pytest
from chuk_virtual_shell.commands.text.sed import SedCommand
from tests.dummy_shell import DummyShell


@pytest.fixture
def sed_command():
    # Setup a dummy file system with sample files
    files = {
        "file1.txt": "Hello world\nThis is a test\nHello again",
        "file2.txt": "Line 1\nLine 2\nLine 3",
        "numbers.txt": "1. First\n2. Second\n3. Third\n4. Fourth",
    }
    dummy_shell = DummyShell(files)
    command = SedCommand(shell_context=dummy_shell)
    return command


def test_sed_missing_script(sed_command):
    output = sed_command.execute([])
    assert output == "sed: missing script"


def test_sed_basic_substitution(sed_command):
    output = sed_command.execute(["s/Hello/Hi/", "file1.txt"])
    assert "Hi world" in output
    assert "Hi again" in output


def test_sed_global_substitution(sed_command):
    sed_command.shell.fs.write_file("test.txt", "foo bar foo baz foo")
    output = sed_command.execute(["s/foo/XXX/g", "test.txt"])
    assert output == "XXX bar XXX baz XXX"


def test_sed_case_insensitive(sed_command):
    sed_command.shell.fs.write_file("test.txt", "Hello HELLO hello")
    output = sed_command.execute(["s/hello/hi/gi", "test.txt"])
    assert output == "hi hi hi"


def test_sed_delete_pattern(sed_command):
    output = sed_command.execute(["/Hello/d", "file1.txt"])
    assert "Hello" not in output
    assert "This is a test" in output


def test_sed_delete_first_line(sed_command):
    output = sed_command.execute(["1d", "file2.txt"])
    assert "Line 1" not in output
    assert "Line 2" in output
    assert "Line 3" in output


def test_sed_delete_last_line(sed_command):
    output = sed_command.execute(["$d", "file2.txt"])
    assert "Line 1" in output
    assert "Line 2" in output
    assert "Line 3" not in output


def test_sed_delete_range(sed_command):
    output = sed_command.execute(["2,3d", "numbers.txt"])
    lines = output.splitlines()
    assert "1. First" in lines[0]
    assert "4. Fourth" in lines[1]
    assert len(lines) == 2


def test_sed_in_place_edit(sed_command):
    # Create a test file
    sed_command.shell.fs.write_file("edit.txt", "Original content")

    # Edit in place
    output = sed_command.execute(["-i", "s/Original/Modified/", "edit.txt"])
    assert output == ""  # No output for in-place edit

    # Check file was modified
    content = sed_command.shell.fs.read_file("edit.txt")
    assert content == "Modified content"


def test_sed_quiet_mode_with_print(sed_command):
    output = sed_command.execute(["-n", "/Hello/p", "file1.txt"])
    assert "Hello world" in output
    assert "Hello again" in output
    assert "This is a test" not in output


def test_sed_multiple_scripts(sed_command):
    output = sed_command.execute(
        ["-e", "s/Hello/Hi/", "-e", "s/world/Earth/", "file1.txt"]
    )
    assert "Hi Earth" in output


def test_sed_stdin_processing(sed_command):
    # Simulate stdin
    sed_command.shell._stdin_buffer = "Input text\nAnother line"
    output = sed_command.execute(["s/Input/Output/"])
    assert "Output text" in output


def test_sed_file_not_found(sed_command):
    output = sed_command.execute(["s/a/b/", "nonexistent.txt"])
    assert "No such file or directory" in output


def test_sed_different_delimiter(sed_command):
    sed_command.shell.fs.write_file("path.txt", "/usr/local/bin")
    output = sed_command.execute(["s#/usr/local#/opt#", "path.txt"])
    assert output == "/opt/bin"


@pytest.mark.skip(reason="Backreference support not yet implemented")
def test_sed_backreference(sed_command):
    sed_command.shell.fs.write_file("test.txt", "Hello World")
    sed_command.execute([r"s/\(.*\) \(.*\)/\2 \1/", "test.txt"])
    # Note: Basic regex support for backreferences would need enhancement
    # This test documents expected behavior
