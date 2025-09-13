# src/chuk_virtual_shell/commands/system/history.py
"""
chuk_virtual_shell/commands/system/history.py - history command implementation

Displays and searches command history.
"""

from chuk_virtual_shell.commands.command_base import ShellCommand


class HistoryCommand(ShellCommand):
    """Display or search command history"""

    name = "history"
    help_text = """history - display or search command history
    
Usage: history [options] [pattern]

Options:
    -c        Clear the history list
    -d offset Delete the history entry at position offset
    -n        Display history without line numbers
    -r        Display history in reverse order (newest first)
    -s string Add string to history without executing
    pattern   Search for commands containing pattern

Description:
    Display the command history list with line numbers. When a pattern
    is provided, only show commands that contain the pattern.
    
Examples:
    history              # Show all history
    history 10          # Show last 10 commands
    history grep        # Search for commands containing 'grep'
    history -c          # Clear history
    history -r          # Show history in reverse order
    history -s "cmd"    # Add 'cmd' to history without running it"""

    category = "system"

    def execute(self, args):
        """Execute the history command"""
        # Initialize history if it doesn't exist
        if not hasattr(self.shell, "history"):
            self.shell.history = []

        # Parse arguments
        clear_history = False
        delete_offset = None
        no_numbers = False
        reverse_order = False
        add_to_history = None
        pattern = None
        show_count = None

        i = 0
        while i < len(args):
            arg = args[i]

            if arg == "-c":
                clear_history = True
            elif arg == "-d":
                if i + 1 < len(args):
                    try:
                        delete_offset = int(args[i + 1])
                        i += 1
                    except ValueError:
                        return f"history: {args[i + 1]}: numeric argument required"
                else:
                    return "history: -d: option requires an argument"
            elif arg == "-n":
                no_numbers = True
            elif arg == "-r":
                reverse_order = True
            elif arg == "-s":
                if i + 1 < len(args):
                    add_to_history = args[i + 1]
                    i += 1
                else:
                    return "history: -s: option requires an argument"
            elif arg.startswith("-"):
                return f"history: {arg}: invalid option"
            else:
                # Check if it's a number (show last N commands)
                try:
                    show_count = int(arg)
                except ValueError:
                    # It's a search pattern
                    pattern = arg
            i += 1

        # Execute requested operation
        if clear_history:
            self.shell.history.clear()
            return ""

        if delete_offset is not None:
            if 1 <= delete_offset <= len(self.shell.history):
                del self.shell.history[delete_offset - 1]
                return ""
            else:
                return f"history: {delete_offset}: history position out of range"

        if add_to_history:
            self.shell.history.append(add_to_history)
            return ""

        # Prepare history for display
        history_items = list(self.shell.history)

        # Filter by pattern if provided
        if pattern:
            filtered = []
            for i, cmd in enumerate(history_items):
                if pattern.lower() in cmd.lower():
                    filtered.append((i + 1, cmd))
            history_items = filtered
        else:
            history_items = [(i + 1, cmd) for i, cmd in enumerate(history_items)]

        # Limit to last N commands if specified
        if show_count and show_count > 0:
            history_items = history_items[-show_count:]

        # Reverse order if requested
        if reverse_order:
            history_items.reverse()

        # Format output
        if not history_items:
            return ""

        results = []
        if no_numbers:
            results = [cmd for _, cmd in history_items]
        else:
            # Calculate width for line numbers
            max_num = max(num for num, _ in history_items)
            width = len(str(max_num))
            results = [f"{num:>{width}}  {cmd}" for num, cmd in history_items]

        return "\n".join(results)
