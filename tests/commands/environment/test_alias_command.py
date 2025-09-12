"""Tests for the alias and unalias commands."""

import pytest
from chuk_virtual_shell.shell_interpreter import ShellInterpreter
from chuk_virtual_shell.commands.environment.alias import AliasCommand
from chuk_virtual_shell.commands.environment.unalias import UnaliasCommand


@pytest.fixture
def shell():
    """Create a shell instance for testing."""
    return ShellInterpreter()


class TestAliasCommand:
    """Test cases for the alias command."""

    def test_alias_no_arguments(self, shell):
        """Test listing all aliases when no arguments given."""
        alias_cmd = AliasCommand(shell)
        shell.aliases = {}

        # Empty aliases
        result = alias_cmd.execute([])
        assert result == ""

        # With some aliases
        shell.aliases = {"ll": "ls -la", "la": "ls -a"}
        result = alias_cmd.execute([])
        assert "alias ll='ls -la'" in result
        assert "alias la='ls -a'" in result

    def test_alias_create_simple(self, shell):
        """Test creating a simple alias."""
        alias_cmd = AliasCommand(shell)
        shell.aliases = {}

        result = alias_cmd.execute(["ll=ls -la"])
        assert result == ""
        assert shell.aliases["ll"] == "ls -la"

    def test_alias_create_with_quotes(self, shell):
        """Test creating alias with quotes."""
        alias_cmd = AliasCommand(shell)
        shell.aliases = {}

        # Single quotes
        alias_cmd.execute(["ll='ls -la'"])
        assert shell.aliases["ll"] == "ls -la"

        # Double quotes
        alias_cmd.execute(['la="ls -a"'])
        assert shell.aliases["la"] == "ls -a"

    def test_alias_display_specific(self, shell):
        """Test displaying a specific alias."""
        alias_cmd = AliasCommand(shell)
        shell.aliases = {"ll": "ls -la", "la": "ls -a"}

        result = alias_cmd.execute(["ll"])
        assert result == "alias ll='ls -la'"

        result = alias_cmd.execute(["nonexistent"])
        assert "not found" in result

    def test_alias_multiple_definitions(self, shell):
        """Test defining multiple aliases at once."""
        alias_cmd = AliasCommand(shell)
        shell.aliases = {}

        alias_cmd.execute(["ll=ls -la", "la=ls -a", "l=ls"])
        assert shell.aliases["ll"] == "ls -la"
        assert shell.aliases["la"] == "ls -a"
        assert shell.aliases["l"] == "ls"

    def test_alias_overwrite(self, shell):
        """Test overwriting an existing alias."""
        alias_cmd = AliasCommand(shell)
        shell.aliases = {"ll": "ls -l"}

        alias_cmd.execute(["ll=ls -la"])
        assert shell.aliases["ll"] == "ls -la"

    def test_alias_complex_value(self, shell):
        """Test alias with complex value."""
        alias_cmd = AliasCommand(shell)
        shell.aliases = {}

        alias_cmd.execute(["gitlog=git log --oneline --graph --all"])
        assert shell.aliases["gitlog"] == "git log --oneline --graph --all"

    def test_alias_empty_value(self, shell):
        """Test alias with empty value."""
        alias_cmd = AliasCommand(shell)
        shell.aliases = {}

        alias_cmd.execute(["empty="])
        assert shell.aliases["empty"] == ""

    def test_alias_special_characters(self, shell):
        """Test alias with special characters in value."""
        alias_cmd = AliasCommand(shell)
        shell.aliases = {}

        alias_cmd.execute(["search='grep -r \"pattern\"'"])
        assert shell.aliases["search"] == 'grep -r "pattern"'


class TestUnaliasCommand:
    """Test cases for the unalias command."""

    def test_unalias_single(self, shell):
        """Test removing a single alias."""
        unalias_cmd = UnaliasCommand(shell)
        shell.aliases = {"ll": "ls -la", "la": "ls -a"}

        result = unalias_cmd.execute(["ll"])
        assert result == ""
        assert "ll" not in shell.aliases
        assert "la" in shell.aliases

    def test_unalias_multiple(self, shell):
        """Test removing multiple aliases."""
        unalias_cmd = UnaliasCommand(shell)
        shell.aliases = {"ll": "ls -la", "la": "ls -a", "l": "ls"}

        result = unalias_cmd.execute(["ll", "la"])
        assert result == ""
        assert "ll" not in shell.aliases
        assert "la" not in shell.aliases
        assert "l" in shell.aliases

    def test_unalias_all(self, shell):
        """Test removing all aliases with -a."""
        unalias_cmd = UnaliasCommand(shell)
        shell.aliases = {"ll": "ls -la", "la": "ls -a", "l": "ls"}

        result = unalias_cmd.execute(["-a"])
        assert result == ""
        assert len(shell.aliases) == 0

    def test_unalias_nonexistent(self, shell):
        """Test removing non-existent alias."""
        unalias_cmd = UnaliasCommand(shell)
        shell.aliases = {"ll": "ls -la"}

        result = unalias_cmd.execute(["nonexistent"])
        assert "not found" in result
        assert "ll" in shell.aliases  # Existing aliases unchanged

    def test_unalias_no_arguments(self, shell):
        """Test with no arguments."""
        unalias_cmd = UnaliasCommand(shell)

        result = unalias_cmd.execute([])
        assert "usage" in result

    def test_unalias_invalid_option(self, shell):
        """Test with invalid option."""
        unalias_cmd = UnaliasCommand(shell)

        result = unalias_cmd.execute(["-x", "ll"])
        assert "invalid option" in result

    def test_unalias_mixed_existing_nonexistent(self, shell):
        """Test removing mix of existing and non-existing aliases."""
        unalias_cmd = UnaliasCommand(shell)
        shell.aliases = {"ll": "ls -la", "la": "ls -a"}

        result = unalias_cmd.execute(["ll", "nonexistent", "la"])
        assert "nonexistent: not found" in result
        assert "ll" not in shell.aliases
        assert "la" not in shell.aliases

    def test_unalias_empty_aliases(self, shell):
        """Test unalias when no aliases defined."""
        unalias_cmd = UnaliasCommand(shell)
        shell.aliases = {}

        result = unalias_cmd.execute(["-a"])
        assert result == ""

        result = unalias_cmd.execute(["anything"])
        assert "not found" in result


class TestAliasExpansion:
    """Test alias expansion in the shell interpreter."""

    def test_alias_expansion_simple(self, shell):
        """Test simple alias expansion."""
        shell.aliases = {"ll": "ls -la"}

        expanded = shell._expand_aliases("ll /home")
        assert expanded == "ls -la /home"

    def test_alias_expansion_no_match(self, shell):
        """Test when command is not an alias."""
        shell.aliases = {"ll": "ls -la"}

        expanded = shell._expand_aliases("ls /home")
        assert expanded == "ls /home"

    def test_alias_expansion_recursive(self, shell):
        """Test recursive alias expansion."""
        shell.aliases = {"ll": "la -l", "la": "ls -a"}

        expanded = shell._expand_aliases("ll /home")
        assert expanded == "ls -a -l /home"

    def test_alias_expansion_no_infinite_loop(self, shell):
        """Test that circular aliases don't cause infinite loop."""
        shell.aliases = {"a": "b", "b": "a"}

        # Should stop after max recursion depth
        expanded = shell._expand_aliases("a test")
        # Will expand up to max depth (10) then stop
        assert expanded in ["a test", "b test"]

    def test_alias_expansion_empty_aliases(self, shell):
        """Test expansion with no aliases defined."""
        shell.aliases = {}

        expanded = shell._expand_aliases("ll /home")
        assert expanded == "ll /home"

    def test_alias_expansion_preserves_arguments(self, shell):
        """Test that alias expansion preserves original arguments."""
        shell.aliases = {"g": "grep -i"}

        expanded = shell._expand_aliases("g pattern file.txt")
        assert expanded == "grep -i pattern file.txt"
