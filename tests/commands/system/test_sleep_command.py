"""
Test cases for the sleep command.
"""

import pytest
import time
from chuk_virtual_shell.shell_interpreter import ShellInterpreter


class TestSleepCommand:
    """Test the sleep command functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.shell = ShellInterpreter()

    def test_sleep_basic(self):
        """Test basic sleep functionality."""
        start = time.time()
        result = self.shell.execute("sleep 0.1")
        elapsed = time.time() - start
        
        assert result == ""
        assert self.shell.return_code == 0
        # Allow some tolerance for timing
        assert elapsed >= 0.09  # Should sleep at least 0.09 seconds
        assert elapsed < 0.3    # But not too long

    def test_sleep_integer(self):
        """Test sleep with integer seconds."""
        start = time.time()
        result = self.shell.execute("sleep 1")
        elapsed = time.time() - start
        
        assert result == ""
        assert self.shell.return_code == 0
        assert elapsed >= 0.9
        assert elapsed < 1.5

    def test_sleep_decimal(self):
        """Test sleep with decimal seconds."""
        start = time.time()
        result = self.shell.execute("sleep 0.5")
        elapsed = time.time() - start
        
        assert result == ""
        assert self.shell.return_code == 0
        assert elapsed >= 0.4
        assert elapsed < 0.8

    def test_sleep_zero(self):
        """Test sleep with zero duration."""
        start = time.time()
        result = self.shell.execute("sleep 0")
        elapsed = time.time() - start
        
        assert result == ""
        assert self.shell.return_code == 0
        assert elapsed < 0.1  # Should return immediately

    def test_sleep_missing_argument(self):
        """Test sleep without argument."""
        result = self.shell.execute("sleep")
        assert "missing operand" in result

    def test_sleep_invalid_argument(self):
        """Test sleep with invalid argument."""
        result = self.shell.execute("sleep abc")
        assert "invalid time interval" in result
        
        result = self.shell.execute("sleep -5")
        assert "invalid time interval" in result

    def test_sleep_in_pipeline(self):
        """Test sleep in a command pipeline."""
        start = time.time()
        result = self.shell.execute("echo start && sleep 0.2 && echo end")
        elapsed = time.time() - start
        
        assert "start" in result
        assert "end" in result
        assert elapsed >= 0.15  # Should have slept

    def test_sleep_with_timing(self):
        """Test sleep with command timing enabled."""
        self.shell.execute("timings -e")
        
        # Execute sleep
        self.shell.execute("sleep 0.1")
        
        # Check timing was recorded
        if "sleep" in self.shell.command_timing:
            stats = self.shell.command_timing["sleep"]
            assert stats["count"] == 1
            assert stats["total_time"] >= 0.09