# src/chuk_virtual_shell/commands/system/date.py
"""
Date command implementation for virtual shell
"""

from datetime import datetime
from chuk_virtual_shell.commands.command_base import ShellCommand


class DateCommand(ShellCommand):
    """Display the current date and time"""

    name = "date"
    help_text = """date - Display the current date and time
Usage: date [OPTIONS]
Options:
  (no options)  Display current date and time
  +FORMAT       Display date in custom format (limited support)
Examples:
  date              Display current date/time
  date +%Y-%m-%d    Display date in YYYY-MM-DD format"""
    category = "system"

    def execute(self, args):
        """Execute the date command"""
        now = datetime.now()

        # Check for format string
        if args and args[0].startswith("+"):
            format_str = args[0][1:]  # Remove the + prefix
            try:
                # Basic format string replacements
                format_map = {
                    "%Y": now.strftime("%Y"),  # Year
                    "%m": now.strftime("%m"),  # Month
                    "%d": now.strftime("%d"),  # Day
                    "%H": now.strftime("%H"),  # Hour
                    "%M": now.strftime("%M"),  # Minute
                    "%S": now.strftime("%S"),  # Second
                    "%a": now.strftime("%a"),  # Weekday abbreviated
                    "%A": now.strftime("%A"),  # Weekday full
                    "%b": now.strftime("%b"),  # Month abbreviated
                    "%B": now.strftime("%B"),  # Month full
                    "%Y-%m-%d": now.strftime("%Y-%m-%d"),
                    "%H:%M:%S": now.strftime("%H:%M:%S"),
                }

                result = format_str
                for fmt, value in format_map.items():
                    result = result.replace(fmt, value)
                return result
            except Exception:
                # If format fails, return default
                pass

        # Default format: Day Mon DD HH:MM:SS TIMEZONE YYYY
        # Example: Thu Sep 11 13:45:00 PDT 2025
        return now.strftime("%a %b %d %H:%M:%S %Z %Y").strip()
