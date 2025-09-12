"""
Test date command implementation
"""

from datetime import datetime
from unittest.mock import Mock, patch
from chuk_virtual_shell.commands.system.date import DateCommand


class TestDateCommand:
    """Test the date command"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_shell = Mock()
        self.date_cmd = DateCommand(self.mock_shell)

    def test_date_command_exists(self):
        """Test that date command is properly defined"""
        assert self.date_cmd.name == "date"
        assert self.date_cmd.category == "system"
        assert "date" in self.date_cmd.help_text

    def test_date_default_format(self):
        """Test date command with no arguments"""
        with patch("chuk_virtual_shell.commands.system.date.datetime") as mock_datetime:
            # Mock the current time
            mock_now = Mock()
            mock_now.strftime.return_value = "Thu Sep 11 13:45:00  2025"
            mock_datetime.now.return_value = mock_now

            result = self.date_cmd.execute([])

            # Should call strftime with default format
            mock_now.strftime.assert_called_once_with("%a %b %d %H:%M:%S %Z %Y")
            assert result == "Thu Sep 11 13:45:00  2025"

    def test_date_with_year_format(self):
        """Test date command with year format"""
        with patch("chuk_virtual_shell.commands.system.date.datetime") as mock_datetime:
            # Mock the current time
            test_date = datetime(2025, 9, 11, 13, 45, 0)
            mock_datetime.now.return_value = test_date

            result = self.date_cmd.execute(["+%Y"])
            assert result == "2025"

    def test_date_with_full_date_format(self):
        """Test date command with full date format"""
        with patch("chuk_virtual_shell.commands.system.date.datetime") as mock_datetime:
            # Mock the current time
            test_date = datetime(2025, 9, 11, 13, 45, 0)
            mock_datetime.now.return_value = test_date

            result = self.date_cmd.execute(["+%Y-%m-%d"])
            assert result == "2025-09-11"

    def test_date_with_time_format(self):
        """Test date command with time format"""
        with patch("chuk_virtual_shell.commands.system.date.datetime") as mock_datetime:
            # Mock the current time
            test_date = datetime(2025, 9, 11, 13, 45, 30)
            mock_datetime.now.return_value = test_date

            result = self.date_cmd.execute(["+%H:%M:%S"])
            assert result == "13:45:30"

    def test_date_with_weekday_format(self):
        """Test date command with weekday format"""
        with patch("chuk_virtual_shell.commands.system.date.datetime") as mock_datetime:
            # Mock the current time (Thursday)
            test_date = datetime(2025, 9, 11, 13, 45, 0)
            mock_datetime.now.return_value = test_date

            # Test abbreviated weekday
            result = self.date_cmd.execute(["+%a"])
            assert result == "Thu"

            # Test full weekday
            result = self.date_cmd.execute(["+%A"])
            assert result == "Thursday"

    def test_date_with_month_format(self):
        """Test date command with month format"""
        with patch("chuk_virtual_shell.commands.system.date.datetime") as mock_datetime:
            # Mock the current time (September)
            test_date = datetime(2025, 9, 11, 13, 45, 0)
            mock_datetime.now.return_value = test_date

            # Test abbreviated month
            result = self.date_cmd.execute(["+%b"])
            assert result == "Sep"

            # Test full month
            result = self.date_cmd.execute(["+%B"])
            assert result == "September"

    def test_date_with_invalid_format(self):
        """Test date command with invalid format falls back to default"""
        with patch("chuk_virtual_shell.commands.system.date.datetime") as mock_datetime:
            # Mock the current time
            mock_now = Mock()
            mock_now.strftime.return_value = "Thu Sep 11 13:45:00  2025"
            mock_datetime.now.return_value = mock_now

            # Invalid format should fall back to default
            result = self.date_cmd.execute(["+invalid"])

            # Should still return something
            assert result is not None

    def test_date_with_mixed_format(self):
        """Test date command with mixed text and format specifiers"""
        with patch("chuk_virtual_shell.commands.system.date.datetime") as mock_datetime:
            # Mock the current time
            test_date = datetime(2025, 9, 11, 13, 45, 0)
            mock_datetime.now.return_value = test_date

            # Format with text
            result = self.date_cmd.execute(["+Today is %Y-%m-%d"])
            assert result == "Today is 2025-09-11"

    def test_date_help_text(self):
        """Test that date command has proper help text"""
        help_text = self.date_cmd.get_help()
        assert "date" in help_text
        assert "Display" in help_text
        assert "Usage:" in help_text
        assert "Examples:" in help_text
