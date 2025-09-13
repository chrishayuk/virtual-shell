# src/chuk_virtual_shell/commands/environment/unalias.py
"""
chuk_virtual_shell/commands/environment/unalias.py - unalias command implementation

Removes command aliases from the shell.
"""

from chuk_virtual_shell.commands.command_base import ShellCommand


class UnaliasCommand(ShellCommand):
    """Remove command aliases"""

    name = "unalias"
    help_text = """unalias - remove alias definitions
    
Usage: unalias [-a] name [name ...]

Options:
    -a    Remove all alias definitions

Description:
    The unalias command removes alias definitions from the shell.
    Each name is an alias that is removed from the list of defined aliases.
    
Examples:
    unalias ll           # Remove the ll alias
    unalias rm grep     # Remove multiple aliases
    unalias -a          # Remove all aliases"""

    category = "environment"

    def execute(self, args):
        """Execute the unalias command"""
        # Initialize aliases dict if it doesn't exist
        if not hasattr(self.shell, "aliases"):
            self.shell.aliases = {}

        if not args:
            return "unalias: usage: unalias [-a] name [name ...]"

        # Check for -a flag
        if "-a" in args:
            self.shell.aliases.clear()
            return ""

        # Remove specific aliases
        not_found = []
        for name in args:
            if name.startswith("-") and name != "-a":
                return f"unalias: {name}: invalid option\nunalias: usage: unalias [-a] name [name ...]"

            if name in self.shell.aliases:
                del self.shell.aliases[name]
            else:
                not_found.append(f"unalias: {name}: not found")

        return "\n".join(not_found) if not_found else ""
