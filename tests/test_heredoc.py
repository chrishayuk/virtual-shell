"""Tests for heredoc support in script runner"""

import pytest
from chuk_virtual_shell.shell_interpreter import ShellInterpreter
from chuk_virtual_shell.script_runner import ScriptRunner


@pytest.fixture
def shell_with_runner():
    """Create a shell with script runner"""
    shell = ShellInterpreter()
    shell.execute("mkdir /tmp")
    runner = ScriptRunner(shell)
    return shell, runner


def test_simple_heredoc(shell_with_runner):
    """Test a simple heredoc"""
    shell, runner = shell_with_runner

    script = """
cat > /tmp/test.txt << EOF
Hello World
This is a test
EOF
"""
    runner.run_script_content(script)

    # Verify file was created with correct content
    content = shell.fs.read_file("/tmp/test.txt")
    assert content == "Hello World\nThis is a test"


def test_heredoc_with_variables(shell_with_runner):
    """Test heredoc with shell-like content"""
    shell, runner = shell_with_runner

    script = """
cat > /tmp/data.csv << DATA
Alice,30,Engineer
Bob,25,Designer
Charlie,35,Manager
DATA
"""
    runner.run_script_content(script)

    content = shell.fs.read_file("/tmp/data.csv")
    assert "Alice,30,Engineer" in content
    assert "Bob,25,Designer" in content
    assert "Charlie,35,Manager" in content


def test_heredoc_append(shell_with_runner):
    """Test heredoc with append mode"""
    shell, runner = shell_with_runner

    # Create initial file
    shell.fs.write_file("/tmp/append.txt", "Initial content")

    script = """
cat >> /tmp/append.txt << END
Additional line 1
Additional line 2
END
"""
    runner.run_script_content(script)

    content = shell.fs.read_file("/tmp/append.txt")
    assert "Initial content" in content
    assert "Additional line 1" in content
    assert "Additional line 2" in content


def test_heredoc_with_special_characters(shell_with_runner):
    """Test heredoc with special characters"""
    shell, runner = shell_with_runner

    script = """
cat > /tmp/special.txt << DELIMITER
Line with $variable
Line with "quotes"
Line with 'single quotes'
Line with special chars: !@#$%^&*()
DELIMITER
"""
    runner.run_script_content(script)

    content = shell.fs.read_file("/tmp/special.txt")
    assert "$variable" in content
    assert '"quotes"' in content
    assert "'single quotes'" in content
    assert "!@#$%^&*()" in content


def test_multiple_heredocs(shell_with_runner):
    """Test multiple heredocs in one script"""
    shell, runner = shell_with_runner

    script = """
cat > /tmp/file1.txt << EOF1
Content for file 1
EOF1

cat > /tmp/file2.txt << EOF2
Content for file 2
EOF2
"""
    runner.run_script_content(script)

    content1 = shell.fs.read_file("/tmp/file1.txt")
    content2 = shell.fs.read_file("/tmp/file2.txt")
    assert content1 == "Content for file 1"
    assert content2 == "Content for file 2"


def test_heredoc_with_indentation(shell_with_runner):
    """Test heredoc preserves indentation"""
    shell, runner = shell_with_runner

    script = """
cat > /tmp/indented.txt << EOF
    Indented line
        More indentation
    Back to first level
EOF
"""
    runner.run_script_content(script)

    content = shell.fs.read_file("/tmp/indented.txt")
    lines = content.split("\n")
    assert lines[0] == "    Indented line"
    assert lines[1] == "        More indentation"
    assert lines[2] == "    Back to first level"


def test_heredoc_empty_content(shell_with_runner):
    """Test heredoc with empty content"""
    shell, runner = shell_with_runner

    script = """
cat > /tmp/empty.txt << EOF
EOF
"""
    runner.run_script_content(script)

    content = shell.fs.read_file("/tmp/empty.txt")
    assert content == ""


def test_heredoc_with_commands_after(shell_with_runner):
    """Test commands after heredoc work correctly"""
    shell, runner = shell_with_runner

    script = """
cat > /tmp/test.txt << EOF
Test content
EOF
echo "Command after heredoc" > /tmp/after.txt
"""
    runner.run_script_content(script)

    content1 = shell.fs.read_file("/tmp/test.txt")
    content2 = shell.fs.read_file("/tmp/after.txt")
    assert content1 == "Test content"
    assert content2 == "Command after heredoc"


def test_heredoc_cat_without_redirect(shell_with_runner):
    """Test heredoc with cat (no redirection)"""
    shell, runner = shell_with_runner

    script = """
cat << EOF
This should be output
directly to stdout
EOF
"""
    result = runner.run_script_content(script)

    assert "This should be output" in result
    assert "directly to stdout" in result
