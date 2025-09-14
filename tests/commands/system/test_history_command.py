"""Tests for the history command."""

import pytest
from chuk_virtual_shell.shell_interpreter import ShellInterpreter
from chuk_virtual_shell.commands.system.history import HistoryCommand


@pytest.fixture
def shell():
    """Create a shell instance for testing."""
    return ShellInterpreter()


class TestHistoryCommand:
    """Test cases for the history command."""

    def test_history_empty(self, shell):
        """Test history when no commands have been run."""
        history_cmd = HistoryCommand(shell)
        shell.history = []

        result = history_cmd.execute([])
        assert result == ""

    def test_history_display_all(self, shell):
        """Test displaying all history."""
        history_cmd = HistoryCommand(shell)
        shell.history = ["ls", "cd /home", "pwd", "echo test"]

        result = history_cmd.execute([])
        assert "1  ls" in result
        assert "2  cd /home" in result
        assert "3  pwd" in result
        assert "4  echo test" in result

    def test_history_display_count(self, shell):
        """Test displaying last N commands."""
        history_cmd = HistoryCommand(shell)
        shell.history = ["ls", "cd /home", "pwd", "echo test", "cat file"]

        result = history_cmd.execute(["3"])
        assert "ls" not in result
        assert "cd /home" not in result
        assert "3  pwd" in result
        assert "4  echo test" in result
        assert "5  cat file" in result

    def test_history_search_pattern(self, shell):
        """Test searching history by pattern."""
        history_cmd = HistoryCommand(shell)
        shell.history = ["ls /home", "cd /tmp", "echo test", "ls -la", "echo hello"]

        # Search for 'echo'
        result = history_cmd.execute(["echo"])
        assert "3  echo test" in result
        assert "5  echo hello" in result
        assert "ls" not in result
        assert "cd" not in result

    def test_history_clear(self, shell):
        """Test clearing history."""
        history_cmd = HistoryCommand(shell)
        shell.history = ["ls", "cd", "pwd"]

        result = history_cmd.execute(["-c"])
        assert result == ""
        assert len(shell.history) == 0

    def test_history_delete_entry(self, shell):
        """Test deleting specific history entry."""
        history_cmd = HistoryCommand(shell)
        shell.history = ["ls", "cd", "pwd", "echo"]

        # Delete entry 2 (cd)
        result = history_cmd.execute(["-d", "2"])
        assert result == ""
        assert shell.history == ["ls", "pwd", "echo"]

    def test_history_delete_invalid_offset(self, shell):
        """Test deleting with invalid offset."""
        history_cmd = HistoryCommand(shell)
        shell.history = ["ls", "cd"]

        # Out of range
        result = history_cmd.execute(["-d", "10"])
        assert "out of range" in result

        # Non-numeric
        result = history_cmd.execute(["-d", "abc"])
        assert "numeric argument required" in result

    def test_history_no_numbers(self, shell):
        """Test displaying history without line numbers."""
        history_cmd = HistoryCommand(shell)
        shell.history = ["ls", "cd", "pwd"]

        result = history_cmd.execute(["-n"])
        lines = result.split("\n")
        assert lines[0] == "ls"
        assert lines[1] == "cd"
        assert lines[2] == "pwd"

    def test_history_reverse_order(self, shell):
        """Test displaying history in reverse order."""
        history_cmd = HistoryCommand(shell)
        shell.history = ["first", "second", "third"]

        result = history_cmd.execute(["-r"])
        lines = result.split("\n")
        assert "3  third" in lines[0]
        assert "2  second" in lines[1]
        assert "1  first" in lines[2]

    def test_history_add_without_execute(self, shell):
        """Test adding to history without executing."""
        history_cmd = HistoryCommand(shell)
        shell.history = ["ls"]

        result = history_cmd.execute(["-s", "git commit -m 'test'"])
        assert result == ""
        assert "git commit -m 'test'" in shell.history
        assert len(shell.history) == 2

    def test_history_add_without_argument(self, shell):
        """Test -s option without argument."""
        history_cmd = HistoryCommand(shell)

        result = history_cmd.execute(["-s"])
        assert "option requires an argument" in result

    def test_history_invalid_option(self, shell):
        """Test with invalid option."""
        history_cmd = HistoryCommand(shell)

        result = history_cmd.execute(["-x"])
        assert "invalid option" in result

    def test_history_case_insensitive_search(self, shell):
        """Test that pattern search is case-insensitive."""
        history_cmd = HistoryCommand(shell)
        shell.history = ["ECHO TEST", "echo hello", "Echo world"]

        result = history_cmd.execute(["echo"])
        assert "1  ECHO TEST" in result
        assert "2  echo hello" in result
        assert "3  Echo world" in result

    def test_history_combined_options(self, shell):
        """Test combining multiple options."""
        history_cmd = HistoryCommand(shell)
        shell.history = ["ls", "cd", "pwd", "echo", "cat"]

        # Reverse order with limit
        result = history_cmd.execute(["-r", "3"])
        lines = result.split("\n")
        assert "5  cat" in lines[0]
        assert "4  echo" in lines[1]
        assert "3  pwd" in lines[2]
        assert "ls" not in result

    def test_history_line_number_alignment(self, shell):
        """Test that line numbers are properly aligned."""
        history_cmd = HistoryCommand(shell)
        # Create history with different number widths
        shell.history = ["cmd" + str(i) for i in range(1, 12)]

        result = history_cmd.execute([])
        lines = result.split("\n")

        # Check alignment for single digit
        assert " 1  cmd1" in lines[0]
        # Check alignment for double digit
        assert "11  cmd11" in lines[10]

    def test_history_empty_search_result(self, shell):
        """Test searching with no matches."""
        history_cmd = HistoryCommand(shell)
        shell.history = ["ls", "cd", "pwd"]

        result = history_cmd.execute(["nonexistent"])
        assert result == ""
