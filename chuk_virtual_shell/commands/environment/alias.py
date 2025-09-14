# src/chuk_virtual_shell/commands/environment/alias.py
"""
chuk_virtual_shell/commands/environment/alias.py - alias command implementation

Creates command aliases for the shell.
"""

from chuk_virtual_shell.commands.command_base import ShellCommand


class AliasCommand(ShellCommand):
    """Define or display command aliases"""

    name = "alias"
    help_text = """alias - define or display aliases
    
Usage: alias [name[=value] ...]

Description:
    Without arguments, alias prints the list of aliases in the form
    alias name=value on standard output.
    
    When arguments are supplied, an alias is defined for each name
    whose value is given. A trailing space in value causes the next
    word to be checked for alias substitution.
    
Examples:
    alias                      # List all aliases
    alias ll='ls -la'         # Create an alias
    alias rm='rm -i'          # Override command with alias
    alias grep='grep --color' # Add default options"""

    category = "environment"

    def execute(self, args):
        """Execute the alias command"""
        # Initialize aliases dict if it doesn't exist
        if not hasattr(self.shell, "aliases"):
            self.shell.aliases = {}

        if not args:
            # Display all aliases
            if not self.shell.aliases:
                return ""

            results = []
            for name, value in sorted(self.shell.aliases.items()):
                results.append(f"alias {name}='{value}'")
            return "\n".join(results)

        # Process alias definitions
        results = []
        for arg in args:
            if "=" in arg:
                # Define an alias
                name, value = arg.split("=", 1)
                # Remove quotes if present
                if value.startswith(("'", '"')) and value.endswith(value[0]):
                    value = value[1:-1]
                self.shell.aliases[name] = value
            else:
                # Display specific alias
                if arg in self.shell.aliases:
                    results.append(f"alias {arg}='{self.shell.aliases[arg]}'")
                else:
                    results.append(f"alias: {arg}: not found")

        return "\n".join(results) if results else ""
