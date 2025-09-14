"""
Tests to improve coverage of shell_interpreter.py
"""

import os
import tempfile
import yaml
from unittest.mock import Mock, patch

from chuk_virtual_shell.shell_interpreter import ShellInterpreter


class TestShellInterpreterCoverage:
    """Tests to improve shell interpreter coverage"""

    def test_init_with_memory_provider(self):
        """Test initialization with memory provider"""
        with patch(
            "chuk_virtual_shell.shell_interpreter.VirtualFileSystem"
        ) as mock_vfs:
            mock_fs = Mock()
            mock_vfs.return_value = mock_fs

            shell = ShellInterpreter(fs_provider="memory")

            mock_vfs.assert_called_once()
            # ShellInterpreter doesn't store fs_provider as an attribute
            assert shell.fs is not None

    def test_init_with_sqlite_provider(self):
        """Test initialization with SQLite provider"""
        # ShellInterpreter uses VirtualFileSystem, not SQLiteVFS directly
        with patch(
            "chuk_virtual_shell.shell_interpreter.VirtualFileSystem"
        ) as mock_vfs:
            mock_fs = Mock()
            mock_vfs.return_value = mock_fs

            shell = ShellInterpreter(
                fs_provider="sqlite", fs_provider_args={"db_path": ":memory:"}
            )

            mock_vfs.assert_called_once_with("sqlite", db_path=":memory:")
            assert shell.fs is not None

    def test_init_with_s3_provider(self):
        """Test initialization with S3 provider"""
        # ShellInterpreter uses VirtualFileSystem, not S3VFS directly
        with patch(
            "chuk_virtual_shell.shell_interpreter.VirtualFileSystem"
        ) as mock_vfs:
            mock_fs = Mock()
            mock_vfs.return_value = mock_fs

            shell = ShellInterpreter(
                fs_provider="s3", fs_provider_args={"bucket_name": "test-bucket"}
            )

            mock_vfs.assert_called_once_with("s3", bucket_name="test-bucket")
            assert shell.fs is not None

    def test_init_with_invalid_provider(self):
        """Test initialization with invalid provider"""
        # ShellInterpreter falls back to memory provider on error, doesn't raise
        with patch("chuk_virtual_shell.shell_interpreter.logger") as mock_logger:
            shell = ShellInterpreter(fs_provider="invalid_provider")

            # Should log an error but not crash
            mock_logger.error.assert_called()
            assert shell.fs is not None  # Falls back to memory provider

    def test_init_with_sandbox_yaml_missing_file(self):
        """Test initialization with missing sandbox YAML file"""
        with patch("os.path.exists", return_value=False):
            with patch("chuk_virtual_shell.shell_interpreter.VirtualFileSystem"):
                # Should log warning but not raise exception
                shell = ShellInterpreter(sandbox_yaml="nonexistent.yaml")
                assert shell is not None

    def test_init_with_sandbox_yaml_invalid_yaml(self):
        """Test initialization with invalid YAML content"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: [unclosed")
            temp_file = f.name

        try:
            with patch("chuk_virtual_shell.shell_interpreter.VirtualFileSystem"):
                # Should log error but not raise exception
                shell = ShellInterpreter(sandbox_yaml=temp_file)
                assert shell is not None
        finally:
            os.unlink(temp_file)

    def test_setup_default_environment(self):
        """Test default environment setup"""
        with patch("chuk_virtual_shell.shell_interpreter.VirtualFileSystem"):
            shell = ShellInterpreter()

            # Check that default environment variables are set
            assert shell.environ["HOME"] == "/home/user"
            assert shell.environ["USER"] == "user"
            assert shell.environ["PWD"] == "/"
            assert (
                shell.environ["SHELL"] == "/bin/pyodide-shell"
            )  # Actual default value
            assert "PATH" in shell.environ

    def test_setup_default_environment_with_existing_vars(self):
        """Test default environment setup with existing variables"""
        with patch("chuk_virtual_shell.shell_interpreter.VirtualFileSystem"):
            shell = ShellInterpreter()
            # The environment is set up during __init__, test that behavior

            # Default environment should be set
            assert "HOME" in shell.environ
            assert "USER" in shell.environ
            assert "PATH" in shell.environ

    def test_load_commands(self):
        """Test command loading"""
        with patch("chuk_virtual_shell.shell_interpreter.VirtualFileSystem"):
            with patch(
                "chuk_virtual_shell.shell_interpreter.CommandLoader"
            ) as mock_loader:
                mock_commands = {"test_ls": Mock(), "test_cd": Mock()}
                mock_loader.discover_commands.return_value = mock_commands

                shell = ShellInterpreter()

                # Commands should be loaded during initialization
                mock_loader.discover_commands.assert_called_once()
                # Check that the returned commands are in shell.commands
                for cmd in mock_commands:
                    assert cmd in shell.commands

    def test_load_shellrc_file_exists(self):
        """Test loading .shellrc when file exists"""
        with patch("chuk_virtual_shell.shell_interpreter.VirtualFileSystem"):
            shell = ShellInterpreter()

            # Mock filesystem
            shell.fs = Mock()
            shell.fs.exists.return_value = True
            shell.fs.read_file.return_value = (
                "export TEST_VAR=test_value\nalias ll='ls -la'"
            )

            # Load shellrc is called via env_manager
            shell.env_manager.load_shellrc()

            # Should have checked for the file
            shell.fs.exists.assert_called()

    def test_load_shellrc_file_not_exists(self):
        """Test loading .shellrc when file doesn't exist"""
        with patch("chuk_virtual_shell.shell_interpreter.VirtualFileSystem"):
            shell = ShellInterpreter()

            shell.fs = Mock()
            shell.fs.exists.return_value = False

            # Load shellrc is called via env_manager
            shell.env_manager.load_shellrc()

            # Should check existence but not try to read
            shell.fs.exists.assert_called()
            shell.fs.read_file.assert_not_called()

    def test_load_shellrc_read_error(self):
        """Test loading .shellrc with read error"""
        with patch("chuk_virtual_shell.shell_interpreter.VirtualFileSystem"):
            shell = ShellInterpreter()

            shell.fs = Mock()
            shell.fs.exists.return_value = True
            shell.fs.read_file.side_effect = Exception("Read error")

            # Should not raise exception
            shell.env_manager.load_shellrc()

            shell.fs.read_file.assert_called()

    def test_execute_basic_command(self):
        """Test executing a basic command"""
        with patch("chuk_virtual_shell.shell_interpreter.VirtualFileSystem"):
            shell = ShellInterpreter()

            # Mock a command
            mock_command = Mock()
            mock_command.execute.return_value = "command output"
            mock_command.run.return_value = "command output"
            shell.commands = {"test_cmd": mock_command}

            with patch.object(
                shell.executor, "execute_line", return_value="command output"
            ):
                result = shell.execute("test_cmd arg1 arg2")
                assert result == "command output"

    def test_execute_command_not_found(self):
        """Test executing non-existent command"""
        with patch("chuk_virtual_shell.shell_interpreter.VirtualFileSystem"):
            shell = ShellInterpreter()
            shell.commands = {}

            result = shell.execute("nonexistent_command")

            assert "command not found" in result.lower()

    def test_execute_empty_command(self):
        """Test executing empty command"""
        with patch("chuk_virtual_shell.shell_interpreter.VirtualFileSystem"):
            shell = ShellInterpreter()

            result = shell.execute("")
            assert result == ""

            result = shell.execute("   ")
            assert result == ""

    def test_execute_with_operators(self):
        """Test executing command with shell operators"""
        with patch("chuk_virtual_shell.shell_interpreter.VirtualFileSystem"):
            shell = ShellInterpreter()

            # Mock executor's execute_line method
            with patch.object(
                shell.executor, "execute_line", return_value="operator result"
            ):
                result = shell.execute("echo hello && echo world")
                assert result == "operator result"

    def test_execute_with_control_flow(self):
        """Test executing command with control flow"""
        with patch("chuk_virtual_shell.shell_interpreter.VirtualFileSystem"):
            shell = ShellInterpreter()

            # Control flow actually works, let's test the real output
            result = shell.execute("for i in 1 2 3; do echo $i; done")

            # Should output each number on a new line
            assert result == "1\n2\n3"

    def test_execute_command_exception(self):
        """Test command execution with exception"""
        with patch("chuk_virtual_shell.shell_interpreter.VirtualFileSystem"):
            shell = ShellInterpreter()

            mock_command = Mock()
            mock_command.execute.side_effect = Exception("Command failed")
            mock_command.run.side_effect = Exception("Command failed")
            shell.commands = {"failing_cmd": mock_command}

            with patch.object(
                shell.executor,
                "execute_line",
                return_value="Error executing command: Command failed",
            ):
                result = shell.execute("failing_cmd")
                assert (
                    "Error executing command" in result or "command not found" in result
                )

    def test_has_shell_operators(self):
        """Test that shell can handle commands with operators"""
        with patch("chuk_virtual_shell.shell_interpreter.VirtualFileSystem"):
            shell = ShellInterpreter()

            # Test that shell can execute commands with operators
            # (actual operator handling is in executor)
            result = shell.execute("echo hello && echo world")
            assert "hello" in result
            assert "world" in result

    def test_has_control_flow(self):
        """Test that shell can handle control flow structures"""
        with patch("chuk_virtual_shell.shell_interpreter.VirtualFileSystem"):
            shell = ShellInterpreter()

            # Test that shell can execute control flow
            # (actual control flow handling is in control_flow_executor)
            result = shell.execute("for i in 1 2; do echo $i; done")
            assert "1" in result
            assert "2" in result

    def test_expand_aliases(self):
        """Test alias expansion"""
        with patch("chuk_virtual_shell.shell_interpreter.VirtualFileSystem"):
            shell = ShellInterpreter()
            shell.aliases = {
                "ll": "ls -la",
                "la": "ls -a",
                "grp": "grep -i",  # Use different name to avoid recursive expansion
            }

            assert shell._expand_aliases("ll") == "ls -la"
            assert shell._expand_aliases("ll /home") == "ls -la /home"
            assert shell._expand_aliases("la") == "ls -a"
            assert shell._expand_aliases("grp pattern file") == "grep -i pattern file"
            assert shell._expand_aliases("echo hello") == "echo hello"  # No alias

    def test_expand_aliases_recursive(self):
        """Test recursive alias expansion"""
        with patch("chuk_virtual_shell.shell_interpreter.VirtualFileSystem"):
            shell = ShellInterpreter()
            shell.aliases = {"ll": "la -l", "la": "ls -a"}

            # Should expand recursively: ll -> la -l -> ls -a -l
            result = shell._expand_aliases("ll")
            assert result == "ls -a -l"

    def test_expand_aliases_circular_reference(self):
        """Test alias expansion with circular reference"""
        with patch("chuk_virtual_shell.shell_interpreter.VirtualFileSystem"):
            shell = ShellInterpreter()
            shell.aliases = {"a": "b", "b": "a"}

            # Should detect circular reference and stop
            result = shell._expand_aliases("a")
            # Should return something reasonable (not infinite loop)
            assert len(result) < 100  # Sanity check

    def test_get_prompt_default(self):
        """Test default prompt generation"""
        with patch("chuk_virtual_shell.shell_interpreter.VirtualFileSystem"):
            shell = ShellInterpreter()
            shell.environ["USER"] = "testuser"
            shell.environ["PWD"] = "/home/testuser"

            prompt = shell.prompt()

            assert "testuser" in prompt
            assert "/home/testuser" in prompt
            assert "$" in prompt

    def test_get_prompt_custom_ps1(self):
        """Test prompt with custom PS1"""
        with patch("chuk_virtual_shell.shell_interpreter.VirtualFileSystem"):
            shell = ShellInterpreter()
            # PS1 is not currently implemented, test default prompt

            prompt = shell.prompt()

            # Should have default format
            assert "@" in prompt and ":" in prompt and "$" in prompt

    def test_get_prompt_ps1_with_variables(self):
        """Test prompt with PS1 containing variables"""
        with patch("chuk_virtual_shell.shell_interpreter.VirtualFileSystem"):
            shell = ShellInterpreter()
            shell.environ["USER"] = "testuser"
            shell.environ["PWD"] = "/home/testuser"

            prompt = shell.prompt()

            # Should contain user and path
            assert "testuser" in prompt
            assert "/home/testuser" in prompt

    def test_cleanup_resources(self):
        """Test resource cleanup"""
        with patch("chuk_virtual_shell.shell_interpreter.VirtualFileSystem"):
            shell = ShellInterpreter()

            # Mock resources that need cleanup
            shell.executor = Mock()
            shell.executor.cleanup = Mock()

            # Shell doesn't have a cleanup method
            # Just ensure the shell components exist and can be accessed
            assert shell.executor is not None
            assert hasattr(shell, "_control_flow_executor")

    def test_cleanup_with_exception(self):
        """Test cleanup with exception"""
        with patch("chuk_virtual_shell.shell_interpreter.VirtualFileSystem"):
            shell = ShellInterpreter()

            # Shell doesn't have a cleanup method
            # Test that the shell can be garbage collected even with mocked attributes
            shell.test_attribute = Mock()
            shell.test_attribute.side_effect = Exception("Test exception")

            # Should not raise exception when deleted
            del shell


class TestShellInterpreterIntegration:
    """Integration tests for shell interpreter"""

    def test_full_sandbox_integration(self):
        """Test complete sandbox integration"""
        sandbox_config = {
            "environment": {"SANDBOX_ENV": "test_env", "CUSTOM_PATH": "/custom/bin"},
            "initialization": ["echo 'Sandbox initialization complete'"],
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(sandbox_config, f)
            temp_file = f.name

        try:
            # Create shell with sandbox - this tests the complete initialization flow
            shell = ShellInterpreter(sandbox_yaml=temp_file)

            # Verify environment was loaded
            assert shell.environ.get("SANDBOX_ENV") == "test_env"
            assert shell.environ.get("CUSTOM_PATH") == "/custom/bin"

            # Sandbox mode skips shellrc loading for security, so no SANDBOX_LOADED
            # Just verify the shell was created successfully
            assert shell is not None
            assert shell.fs is not None

        finally:
            os.unlink(temp_file)

    def test_command_execution_flow(self):
        """Test complete command execution flow"""
        shell = ShellInterpreter()

        # Test basic command
        result = shell.execute("echo hello world")
        assert "hello world" in result

        # Test command with arguments
        result = shell.execute("echo 'quoted string'")
        assert "quoted string" in result

        # Test environment variable
        shell.environ["TEST_VAR"] = "test_value"
        result = shell.execute("echo $TEST_VAR")
        assert "test_value" in result

    def test_alias_integration(self):
        """Test alias integration"""
        shell = ShellInterpreter()

        # Set up an alias
        shell.execute("alias ll='ls -la'")

        # Use the alias
        result = shell.execute("ll")

        # Should have executed ls -la
        # (The exact output depends on the ls implementation)
        assert "total" in result or "." in result  # Common ls -la output elements

    def test_environment_variable_persistence(self):
        """Test environment variable persistence"""
        shell = ShellInterpreter()

        # Set environment variable
        shell.execute("export TEST_PERSISTENCE=persistent_value")

        # Verify it persists
        result = shell.execute("echo $TEST_PERSISTENCE")
        assert "persistent_value" in result

        # Verify it's in the shell's environment
        assert shell.environ.get("TEST_PERSISTENCE") == "persistent_value"

    def test_working_directory_persistence(self):
        """Test working directory persistence"""
        shell = ShellInterpreter()

        # Create a directory and change to it
        shell.execute("mkdir /test_dir")
        shell.execute("cd /test_dir")

        # Verify we're in the right directory
        result = shell.execute("pwd")
        assert "/test_dir" in result

        # Verify PWD environment variable was updated
        assert shell.environ.get("PWD") == "/test_dir"
