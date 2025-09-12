"""
Tests for the python command
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from tests.dummy_shell import DummyShell
from chuk_virtual_shell.commands.system.python import PythonCommand, Python3Command


class TestPythonCommand:
    """Test cases for the python command"""

    def setup_method(self):
        """Set up test environment before each test"""
        self.shell = DummyShell({})
        self.cmd = PythonCommand(self.shell)

        # Create test files
        self.shell.fs.write_file("/script.py", "print('Hello')")
        self.shell.fs.write_file("/error.py", "raise ValueError('test error')")
        self.shell.fs.write_file("/args.py", "import sys; print(sys.argv)")
        self.shell.fs.mkdir("/testdir")

    def test_python_no_arguments(self):
        """Test python without arguments"""
        result = self.cmd.execute([])
        assert "interactive mode not fully supported" in result.lower()

    def test_python_version(self):
        """Test python version flag"""
        result = self.cmd.execute(["-V"])
        assert "Python 3" in result

        # Also test long form
        result2 = self.cmd.execute(["--version"])
        assert "Python 3" in result2

    def test_python_c_option(self):
        """Test python -c option"""
        with patch.object(self.cmd, "interpreter") as mock_interp:
            mock_interp.execute_code_sync.return_value = "42"
            result = self.cmd.execute(["-c", "print(6*7)"])
            mock_interp.execute_code_sync.assert_called_with("print(6*7)")
            assert result == "42"

    def test_python_c_missing_argument(self):
        """Test python -c without argument"""
        result = self.cmd.execute(["-c"])
        assert "-c requires an argument" in result

    def test_python_m_option(self):
        """Test python -m option (not fully implemented)"""
        # In sync mode, -m is treated as a script name
        result = self.cmd.execute(["-m", "json.tool"])
        assert (
            "No such file" in result
            or "module execution not fully implemented" in result
        )

    def test_python_m_missing_argument(self):
        """Test python -m without argument"""
        result = self.cmd.execute(["-m"])
        assert "No such file" in result or "requires an argument" in result

    def test_python_script_file(self):
        """Test executing a python script file"""
        with patch.object(self.cmd, "interpreter") as mock_interp:
            mock_interp.run_script_sync.return_value = "Hello"
            result = self.cmd.execute(["/script.py"])
            mock_interp.run_script_sync.assert_called_with("/script.py", [])
            assert result == "Hello"

    def test_python_script_with_args(self):
        """Test executing a python script with arguments"""
        with patch.object(self.cmd, "interpreter") as mock_interp:
            mock_interp.run_script_sync.return_value = "['/args.py', 'arg1', 'arg2']"
            self.cmd.execute(["/args.py", "arg1", "arg2"])
            mock_interp.run_script_sync.assert_called_with("/args.py", ["arg1", "arg2"])

    def test_python_nonexistent_script(self):
        """Test executing non-existent script"""
        result = self.cmd.execute(["/nonexistent.py"])
        assert "No such file or directory" in result

    def test_python_directory_as_script(self):
        """Test trying to execute a directory"""
        result = self.cmd.execute(["/testdir"])
        assert "is a directory" in result.lower() or "no such file" in result.lower()

    def test_python_invalid_option(self):
        """Test python with invalid option"""
        result = self.cmd.execute(["-x"])
        assert "invalid option" in result or "no such file" in result.lower()

    def test_python_interactive_flag(self):
        """Test python -i flag"""
        result = self.cmd.execute(["-i"])
        # In sync mode, -i is treated as a script name
        assert "No such file" in result or "interactive" in result.lower()

    @pytest.mark.asyncio
    async def test_python_async_execution(self):
        """Test async execution of python command"""
        cmd = PythonCommand(self.shell)

        # Test version async
        result = await cmd.execute_async(["-V"])
        assert "Python 3" in result

        # Test -c async
        with patch.object(cmd, "interpreter") as mock_interp:
            mock_interp.execute_code = AsyncMock(return_value="async result")
            result = await cmd.execute_async(["-c", "print('async')"])
            mock_interp.execute_code.assert_called_with("print('async')")
            assert result == "async result"

    @pytest.mark.asyncio
    async def test_python_async_script(self):
        """Test async script execution"""
        cmd = PythonCommand(self.shell)

        with patch.object(cmd, "interpreter") as mock_interp:
            mock_interp.run_script = AsyncMock(return_value="script output")
            result = await cmd.execute_async(["/script.py", "arg1"])
            mock_interp.run_script.assert_called_with("/script.py", ["arg1"])
            assert result == "script output"

    @pytest.mark.asyncio
    async def test_python_async_module(self):
        """Test async module execution"""
        cmd = PythonCommand(self.shell)
        result = await cmd.execute_async(["-m", "unittest"])
        assert "module execution not fully implemented" in result

    def test_python_run_with_asyncio_running(self):
        """Test run method when asyncio loop is running"""

        # Mock the asyncio functions
        with patch("asyncio.get_running_loop") as mock_get_loop:
            mock_loop = MagicMock()
            mock_loop.is_running.return_value = True
            mock_get_loop.return_value = mock_loop

            with patch("asyncio.run_coroutine_threadsafe") as mock_run_threadsafe:
                future = MagicMock()
                future.result.return_value = "Python 3.x.x (virtual environment)"
                mock_run_threadsafe.return_value = future

                result = self.cmd.run(["-V"])
                # Should use run_coroutine_threadsafe for running loop
                assert mock_run_threadsafe.called
                assert "Python" in result

    def test_python_execute_fallback_to_sync(self):
        """Test execute method fallback to sync when async fails"""
        with patch("asyncio.get_event_loop") as mock_get_loop:
            mock_get_loop.side_effect = Exception("No loop")

            # Should fallback to sync
            result = self.cmd.execute(["-V"])
            assert "Python 3" in result

    def test_python_interpreter_initialization(self):
        """Test interpreter is initialized on first use"""
        cmd = PythonCommand(self.shell)
        assert cmd.interpreter is None

        # Execute something to trigger initialization - test with -c that requires interpreter
        cmd._execute_sync(["-c", "print('test')"])
        # After execution, interpreter should be initialized
        assert cmd.interpreter is not None

    def test_python3_command_alias(self):
        """Test Python3Command alias"""
        cmd = Python3Command(self.shell)
        assert cmd.name == "python3"

        # Should work the same as PythonCommand
        result = cmd.execute(["-V"])
        assert "Python 3" in result

    def test_python_complex_options(self):
        """Test complex option combinations"""
        # Test -c with additional args
        with patch.object(self.cmd, "interpreter") as mock_interp:
            mock_interp.execute_code_sync.return_value = "executed"
            self.cmd.execute(["-c", "print('test')", "/script.py"])
            mock_interp.execute_code_sync.assert_called_with("print('test')")

    def test_python_help(self):
        """Test python help text"""
        assert "Execute Python scripts" in self.cmd.help_text
        assert "-c" in self.cmd.help_text
        assert "-m" in self.cmd.help_text
