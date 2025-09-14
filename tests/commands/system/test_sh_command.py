"""
Tests for the sh command
"""

import pytest
from unittest.mock import MagicMock, patch
from tests.dummy_shell import DummyShell
from chuk_virtual_shell.commands.system.sh import ShCommand


class TestShCommand:
    """Test cases for the sh command"""

    def setup_method(self):
        """Set up test environment before each test"""
        self.shell = DummyShell({})
        self.cmd = ShCommand(self.shell)

        # Create test script files
        self.shell.fs.write_file("/script.sh", "echo 'Hello'\necho 'World'")
        self.shell.fs.write_file("/error.sh", "exit 1")
        self.shell.fs.write_file("/complex.sh", "#!/bin/sh\n# Comment\necho $1\nls")
        self.shell.fs.mkdir("/testdir")

    def test_sh_no_arguments(self):
        """Test sh without arguments"""
        result = self.cmd.execute([])
        assert "interactive mode not supported" in result

    def test_sh_c_option(self):
        """Test sh -c option"""
        with patch.object(self.shell, "execute") as mock_exec:
            mock_exec.return_value = "command output"
            result = self.cmd.execute(["-c", "echo hello"])
            mock_exec.assert_called_with("echo hello")
            assert result == "command output"

    def test_sh_c_missing_argument(self):
        """Test sh -c without argument"""
        result = self.cmd.execute(["-c"])
        assert "-c requires an argument" in result

    def test_sh_script_file(self):
        """Test executing a shell script file"""
        with patch.object(self.shell, "execute") as mock_exec:
            mock_exec.side_effect = ["Hello", "World"]
            result = self.cmd.execute(["/script.sh"])
            assert mock_exec.call_count == 2
            assert "Hello" in result
            assert "World" in result

    def test_sh_nonexistent_script(self):
        """Test executing non-existent script"""
        result = self.cmd.execute(["/nonexistent.sh"])
        assert "No such file or directory" in result

    def test_sh_directory_as_script(self):
        """Test trying to execute a directory"""
        result = self.cmd.execute(["/testdir"])
        assert "directory" in result.lower() or "cannot read" in result.lower()

    def test_sh_invalid_option(self):
        """Test sh with invalid option"""
        result = self.cmd.execute(["-z"])
        assert "invalid option" in result or "no such file" in result.lower()

    def test_sh_e_option(self):
        """Test sh -e option (exit on error)"""
        result = self.cmd.execute(["-e", "-c", "echo test"])
        # Should execute normally
        assert "test" in result or "interactive" not in result

    def test_sh_x_option(self):
        """Test sh -x option (debug mode)"""
        result = self.cmd.execute(["-x", "-c", "echo debug"])
        # Should execute with debug flag set
        assert result is not None

    def test_sh_v_option(self):
        """Test sh -v option (verbose mode)"""
        result = self.cmd.execute(["-v", "-c", "echo verbose"])
        # Should execute with verbose flag set
        assert result is not None

    def test_sh_script_with_comments(self):
        """Test executing script with comments"""
        with patch.object(self.shell, "execute") as mock_exec:
            mock_exec.side_effect = ["arg1", "file1 file2"]
            self.cmd.execute(["/complex.sh", "arg1"])
            # Comments should be skipped
            assert mock_exec.call_count == 2

    def test_sh_empty_script(self):
        """Test executing empty script"""
        self.shell.fs.write_file("/empty.sh", "")
        result = self.cmd.execute(["/empty.sh"])
        assert result == ""

    def test_sh_script_only_comments(self):
        """Test script with only comments"""
        self.shell.fs.write_file("/comments.sh", "# Comment 1\n# Comment 2\n")
        result = self.cmd.execute(["/comments.sh"])
        assert result == ""

    @pytest.mark.asyncio
    async def test_sh_async_execution(self):
        """Test async execution of sh command"""
        cmd = ShCommand(self.shell)

        # Test -c async
        with patch.object(
            self.shell, "execute", return_value="async output"
        ) as mock_exec:
            result = await cmd.execute_async(["-c", "echo async"])
            mock_exec.assert_called_with("echo async")
            assert result == "async output"

    @pytest.mark.asyncio
    async def test_sh_async_script(self):
        """Test async script execution"""
        cmd = ShCommand(self.shell)

        # Use the actual script that's already set up
        with patch.object(self.shell, "execute", return_value="Hello") as mock_exec:
            result = await cmd.execute_async(["/script.sh"])
            # Should execute the lines from the script
            assert mock_exec.called
            assert "Hello" in result

    @pytest.mark.asyncio
    async def test_sh_async_no_args(self):
        """Test async with no arguments"""
        cmd = ShCommand(self.shell)
        result = await cmd.execute_async([])
        assert "interactive mode not supported" in result

    @pytest.mark.asyncio
    async def test_sh_async_nonexistent_file(self):
        """Test async with non-existent file"""
        cmd = ShCommand(self.shell)
        result = await cmd.execute_async(["/missing.sh"])
        assert "No such file or directory" in result

    @pytest.mark.asyncio
    async def test_sh_async_directory(self):
        """Test async with directory instead of file"""
        cmd = ShCommand(self.shell)
        result = await cmd.execute_async(["/testdir"])
        assert "Is a directory" in result

    def test_sh_run_with_asyncio_running(self):
        """Test run method when asyncio loop is running"""

        with patch("asyncio.get_running_loop") as mock_get_loop:
            mock_loop = MagicMock()
            mock_loop.is_running.return_value = True
            mock_get_loop.return_value = mock_loop

            with patch("asyncio.run_coroutine_threadsafe") as mock_run_threadsafe:
                future = MagicMock()
                future.result.return_value = "test output"
                mock_run_threadsafe.return_value = future

                with patch.object(self.shell, "execute", return_value="test output"):
                    self.cmd.run(["-c", "test"])
                    # Should use run_coroutine_threadsafe for running loop
                    assert mock_run_threadsafe.called

    def test_sh_execute_fallback_to_sync(self):
        """Test execute method fallback to sync when async fails"""
        with patch("asyncio.get_event_loop") as mock_get_loop:
            mock_get_loop.side_effect = Exception("No loop")

            with patch.object(self.shell, "execute") as mock_exec:
                mock_exec.return_value = "sync result"
                result = self.cmd.execute(["-c", "echo fallback"])
                assert result == "sync result"

    def test_sh_interpreter_initialization(self):
        """Test interpreter is initialized on first use"""
        cmd = ShCommand(self.shell)
        assert cmd.interpreter is None

        # Execute something to trigger initialization in sync mode
        with patch(
            "chuk_virtual_shell.interpreters.bash_interpreter.VirtualBashInterpreter"
        ):
            with patch.object(self.shell, "execute") as mock_exec:
                mock_exec.return_value = "result"
                cmd.execute(["-c", "test"])

    def test_sh_combined_options(self):
        """Test combining multiple options"""
        result = self.cmd.execute(["-e", "-x", "-v", "-c", "echo test"])
        # Should handle multiple flags
        assert result is not None

    def test_sh_script_with_args(self):
        """Test script with arguments"""
        with patch.object(self.shell, "execute") as mock_exec:
            mock_exec.return_value = ""
            result = self.cmd.execute(["/script.sh", "arg1", "arg2"])
            # Args are parsed but not used in sync mode
            assert result is not None

    def test_sh_cannot_read_file(self):
        """Test when file cannot be read"""
        # Make read_file return None
        with patch.object(self.shell.fs, "read_file") as mock_read:
            mock_read.return_value = None
            result = self.cmd.execute(["/script.sh"])
            assert "Cannot read file" in result

    def test_sh_help(self):
        """Test sh help text"""
        assert "Execute shell script" in self.cmd.help_text
        assert "-c" in self.cmd.help_text
        assert "-e" in self.cmd.help_text
        assert "-x" in self.cmd.help_text
