# src/chuk_virtual_shell/commands/system/timings.py
"""
chuk_virtual_shell/commands/system/timings.py - timings command implementation

Display command execution timing statistics.
"""

from chuk_virtual_shell.commands.command_base import ShellCommand


class TimingsCommand(ShellCommand):
    """Display command execution timing statistics"""

    name = "timings"
    help_text = """timings - display command execution timing statistics
    
Usage: timings [options]

Options:
    -c        Clear timing statistics
    -e        Enable timing collection
    -d        Disable timing collection
    -s field  Sort by field (count, total, avg, min, max)

Description:
    Display timing statistics for executed commands. Shows the number
    of executions, total time, average time, minimum and maximum times
    for each command that has been executed while timing was enabled.
    
Examples:
    timings          # Show all timing statistics
    timings -e       # Enable timing collection
    timings -d       # Disable timing collection
    timings -c       # Clear all statistics
    timings -s avg   # Sort by average time"""

    category = "system"

    def execute(self, args):
        """Execute the timings command"""
        # Parse arguments
        clear = False
        enable = False
        disable = False
        sort_by = "total"  # Default sort

        i = 0
        while i < len(args):
            arg = args[i]

            if arg == "-c":
                clear = True
            elif arg == "-e":
                enable = True
            elif arg == "-d":
                disable = True
            elif arg == "-s":
                if i + 1 < len(args):
                    sort_by = args[i + 1]
                    if sort_by not in ["count", "total", "avg", "min", "max"]:
                        return f"timings: invalid sort field: {sort_by}"
                    i += 1
                else:
                    return "timings: -s requires an argument"
            elif arg.startswith("-"):
                return f"timings: invalid option -- '{arg[1:]}'"
            i += 1

        # Handle clear option
        if clear:
            self.shell.command_timing.clear()
            return "Timing statistics cleared"

        # Handle enable/disable
        if enable:
            self.shell.enable_timing = True
            return "Timing collection enabled"

        if disable:
            self.shell.enable_timing = False
            return "Timing collection disabled"

        # Display statistics
        if not self.shell.command_timing:
            status = "enabled" if self.shell.enable_timing else "disabled"
            return f"No timing statistics available (timing is {status})"

        # Calculate statistics
        stats_list = []
        for cmd, stats in self.shell.command_timing.items():
            avg_time = stats["total_time"] / stats["count"] if stats["count"] > 0 else 0
            stats_list.append(
                {
                    "command": cmd,
                    "count": stats["count"],
                    "total": stats["total_time"],
                    "avg": avg_time,
                    "min": stats["min_time"],
                    "max": stats["max_time"],
                }
            )

        # Sort by requested field
        if sort_by == "count":
            stats_list.sort(key=lambda x: x["count"], reverse=True)
        elif sort_by == "total":
            stats_list.sort(key=lambda x: x["total"], reverse=True)
        elif sort_by == "avg":
            stats_list.sort(key=lambda x: x["avg"], reverse=True)
        elif sort_by == "min":
            stats_list.sort(key=lambda x: x["min"], reverse=True)
        elif sort_by == "max":
            stats_list.sort(key=lambda x: x["max"], reverse=True)

        # Format output
        lines = []
        status = "enabled" if self.shell.enable_timing else "disabled"
        lines.append(f"Command Timing Statistics (timing is {status})")
        lines.append("-" * 80)
        lines.append(
            f"{'Command':<15} {'Count':>8} {'Total (s)':>12} {'Avg (s)':>12} {'Min (s)':>12} {'Max (s)':>12}"
        )
        lines.append("-" * 80)

        for stat in stats_list:
            lines.append(
                f"{stat['command']:<15} {stat['count']:>8} "
                f"{stat['total']:>12.6f} {stat['avg']:>12.6f} "
                f"{stat['min']:>12.6f} {stat['max']:>12.6f}"
            )

        lines.append("-" * 80)

        # Calculate totals
        total_count = sum(s["count"] for s in stats_list)
        total_time = sum(s["total"] for s in stats_list)
        lines.append(f"{'Total':<15} {total_count:>8} {total_time:>12.6f}")

        return "\n".join(lines)
