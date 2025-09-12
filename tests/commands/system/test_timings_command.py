"""Tests for the timings command."""

import pytest
from chuk_virtual_shell.shell_interpreter import ShellInterpreter
from chuk_virtual_shell.commands.system.timings import TimingsCommand


@pytest.fixture
def shell():
    """Create a shell instance for testing."""
    return ShellInterpreter()


class TestTimingsCommand:
    """Test cases for the timings command."""

    def test_timings_empty(self, shell):
        """Test timings when no statistics collected."""
        timings_cmd = TimingsCommand(shell)
        shell.command_timing = {}
        shell.enable_timing = False

        result = timings_cmd.execute([])
        assert "No timing statistics available" in result
        assert "disabled" in result

    def test_timings_enable(self, shell):
        """Test enabling timing collection."""
        timings_cmd = TimingsCommand(shell)
        shell.enable_timing = False

        result = timings_cmd.execute(["-e"])
        assert result == "Timing collection enabled"
        assert shell.enable_timing is True

    def test_timings_disable(self, shell):
        """Test disabling timing collection."""
        timings_cmd = TimingsCommand(shell)
        shell.enable_timing = True

        result = timings_cmd.execute(["-d"])
        assert result == "Timing collection disabled"
        assert shell.enable_timing is False

    def test_timings_clear(self, shell):
        """Test clearing timing statistics."""
        timings_cmd = TimingsCommand(shell)
        shell.command_timing = {
            "ls": {"count": 5, "total_time": 0.5, "min_time": 0.05, "max_time": 0.15}
        }

        result = timings_cmd.execute(["-c"])
        assert result == "Timing statistics cleared"
        assert len(shell.command_timing) == 0

    def test_timings_display(self, shell):
        """Test displaying timing statistics."""
        timings_cmd = TimingsCommand(shell)
        shell.enable_timing = True
        shell.command_timing = {
            "ls": {
                "count": 3,
                "total_time": 0.003,
                "min_time": 0.0008,
                "max_time": 0.0012,
            },
            "echo": {
                "count": 5,
                "total_time": 0.001,
                "min_time": 0.0001,
                "max_time": 0.0003,
            },
        }

        result = timings_cmd.execute([])

        # Check header
        assert "Command Timing Statistics" in result
        assert "enabled" in result

        # Check column headers
        assert "Command" in result
        assert "Count" in result
        assert "Total (s)" in result
        assert "Avg (s)" in result
        assert "Min (s)" in result
        assert "Max (s)" in result

        # Check data
        assert "ls" in result
        assert "3" in result  # count
        assert "echo" in result
        assert "5" in result  # count

        # Check totals
        assert "Total" in result
        assert "8" in result  # total count (3 + 5)

    def test_timings_sort_by_count(self, shell):
        """Test sorting by count."""
        timings_cmd = TimingsCommand(shell)
        shell.enable_timing = True
        shell.command_timing = {
            "ls": {
                "count": 10,
                "total_time": 0.1,
                "min_time": 0.008,
                "max_time": 0.012,
            },
            "echo": {
                "count": 5,
                "total_time": 0.05,
                "min_time": 0.008,
                "max_time": 0.012,
            },
            "pwd": {
                "count": 15,
                "total_time": 0.15,
                "min_time": 0.008,
                "max_time": 0.012,
            },
        }

        result = timings_cmd.execute(["-s", "count"])
        lines = result.split("\n")

        # Find data lines (skip headers)
        data_lines = [
            line
            for line in lines
            if line
            and not line.startswith("-")
            and "Command" not in line
            and "Total" not in line
        ]

        # pwd (15) should come first, then ls (10), then echo (5)
        assert "pwd" in data_lines[0]
        assert "ls" in data_lines[1]
        assert "echo" in data_lines[2]

    def test_timings_sort_by_avg(self, shell):
        """Test sorting by average time."""
        timings_cmd = TimingsCommand(shell)
        shell.enable_timing = True
        shell.command_timing = {
            "slow": {"count": 2, "total_time": 2.0, "min_time": 0.9, "max_time": 1.1},
            "fast": {
                "count": 10,
                "total_time": 0.1,
                "min_time": 0.009,
                "max_time": 0.011,
            },
            "medium": {
                "count": 5,
                "total_time": 1.0,
                "min_time": 0.18,
                "max_time": 0.22,
            },
        }

        result = timings_cmd.execute(["-s", "avg"])
        lines = result.split("\n")

        # Find data lines
        data_lines = [
            line
            for line in lines
            if line
            and not line.startswith("-")
            and "Command" not in line
            and "Total" not in line
        ]

        # slow (avg=1.0) should come first, then medium (avg=0.2), then fast (avg=0.01)
        assert "slow" in data_lines[0]
        assert "medium" in data_lines[1]
        assert "fast" in data_lines[2]

    def test_timings_sort_by_total(self, shell):
        """Test sorting by total time (default)."""
        timings_cmd = TimingsCommand(shell)
        shell.enable_timing = True
        shell.command_timing = {
            "cmd1": {"count": 1, "total_time": 0.5, "min_time": 0.5, "max_time": 0.5},
            "cmd2": {
                "count": 10,
                "total_time": 1.0,
                "min_time": 0.09,
                "max_time": 0.11,
            },
            "cmd3": {
                "count": 5,
                "total_time": 0.25,
                "min_time": 0.04,
                "max_time": 0.06,
            },
        }

        result = timings_cmd.execute([])  # Default sort is by total
        lines = result.split("\n")

        # Find data lines
        data_lines = [
            line
            for line in lines
            if line
            and not line.startswith("-")
            and "Command" not in line
            and "Total" not in line
        ]

        # cmd2 (total=1.0) should come first, then cmd1 (0.5), then cmd3 (0.25)
        assert "cmd2" in data_lines[0]
        assert "cmd1" in data_lines[1]
        assert "cmd3" in data_lines[2]

    def test_timings_invalid_sort_field(self, shell):
        """Test with invalid sort field."""
        timings_cmd = TimingsCommand(shell)

        result = timings_cmd.execute(["-s", "invalid"])
        assert "invalid sort field" in result

    def test_timings_sort_missing_argument(self, shell):
        """Test -s without argument."""
        timings_cmd = TimingsCommand(shell)

        result = timings_cmd.execute(["-s"])
        assert "requires an argument" in result

    def test_timings_invalid_option(self, shell):
        """Test with invalid option."""
        timings_cmd = TimingsCommand(shell)

        result = timings_cmd.execute(["-x"])
        assert "invalid option" in result

    def test_timings_formatting(self, shell):
        """Test that timing values are properly formatted."""
        timings_cmd = TimingsCommand(shell)
        shell.enable_timing = True
        shell.command_timing = {
            "test": {
                "count": 1,
                "total_time": 0.123456789,
                "min_time": 0.123456789,
                "max_time": 0.123456789,
            }
        }

        result = timings_cmd.execute([])

        # Should format to 6 decimal places
        assert "0.123457" in result

    def test_timings_status_when_enabled(self, shell):
        """Test that status shows enabled when timing is on."""
        timings_cmd = TimingsCommand(shell)
        shell.enable_timing = True
        shell.command_timing = {
            "ls": {"count": 1, "total_time": 0.1, "min_time": 0.1, "max_time": 0.1}
        }

        result = timings_cmd.execute([])
        assert "timing is enabled" in result

    def test_timings_status_when_disabled(self, shell):
        """Test that status shows disabled when timing is off."""
        timings_cmd = TimingsCommand(shell)
        shell.enable_timing = False
        shell.command_timing = {
            "ls": {"count": 1, "total_time": 0.1, "min_time": 0.1, "max_time": 0.1}
        }

        result = timings_cmd.execute([])
        assert "timing is disabled" in result

    def test_timings_calculation_accuracy(self, shell):
        """Test that average is calculated correctly."""
        timings_cmd = TimingsCommand(shell)
        shell.enable_timing = True
        shell.command_timing = {
            "test": {"count": 4, "total_time": 2.0, "min_time": 0.4, "max_time": 0.6}
        }

        result = timings_cmd.execute([])

        # Average should be 2.0 / 4 = 0.5
        lines = result.split("\n")
        test_line = next(
            line for line in lines if "test" in line and "Command" not in line
        )
        # The average should be formatted as 0.500000
        assert "0.500000" in test_line
