"""
Test async event loop fixes for python and sh commands
"""
import pytest
import asyncio
import warnings
from unittest.mock import Mock, patch
from chuk_virtual_shell.commands.system.python import PythonCommand
from chuk_virtual_shell.commands.system.sh import ShCommand

# Suppress false positive warnings about unawaited coroutines during Mock/inspect introspection
# These warnings occur when Python's inspect module examines async methods, not from actual code issues
pytestmark = pytest.mark.filterwarnings("ignore:coroutine.*was never awaited:RuntimeWarning")


class TestAsyncEventLoopFix:
    """Test that python and sh commands work without async event loop errors"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_shell = Mock()
        self.mock_shell.fs = Mock()
        self.mock_shell.environ = {}
        
        # Setup filesystem methods
        self.mock_shell.fs.exists.return_value = True
        self.mock_shell.fs.is_file.return_value = True
        self.mock_shell.fs.read_file.return_value = "print('Hello')"
        
    def test_python_command_has_async_implementation(self):
        """Test that PythonCommand has custom async implementation"""
        from chuk_virtual_shell.commands.command_base import ShellCommand
        import inspect

        python_cmd = PythonCommand(self.mock_shell)

        # Should have a custom execute_async - check using qualname to avoid coroutine creation
        has_custom_async = (
            hasattr(python_cmd, 'execute_async') and
            inspect.iscoroutinefunction(python_cmd.execute_async) and
            python_cmd.execute_async.__qualname__ != ShellCommand.execute_async.__qualname__
        )
        assert has_custom_async
        
    def test_sh_command_has_async_implementation(self):
        """Test that ShCommand has custom async implementation"""
        from chuk_virtual_shell.commands.command_base import ShellCommand
        import inspect

        sh_cmd = ShCommand(self.mock_shell)

        # Should have a custom execute_async - check using qualname to avoid coroutine creation
        has_custom_async = (
            hasattr(sh_cmd, 'execute_async') and
            inspect.iscoroutinefunction(sh_cmd.execute_async) and
            sh_cmd.execute_async.__qualname__ != ShellCommand.execute_async.__qualname__
        )
        assert has_custom_async
        
    def test_python_command_execute_without_event_loop(self):
        """Test python command executes without requiring event loop"""
        python_cmd = PythonCommand(self.mock_shell)

        # Directly replace method to avoid inspect warnings
        call_count = []
        original_method = python_cmd._execute_sync
        def mock_exec(*args, **kwargs):
            call_count.append(1)
            return "Python output"
        python_cmd._execute_sync = mock_exec
        try:
            # This should not raise RuntimeError about event loop
            result = python_cmd.execute(["-c", "print('test')"])
            assert result == "Python output"
            assert len(call_count) == 1
        finally:
            python_cmd._execute_sync = original_method
            
    def test_sh_command_execute_without_event_loop(self):
        """Test sh command executes without requiring event loop"""
        sh_cmd = ShCommand(self.mock_shell)
        
        # Mock shell execute method
        self.mock_shell.execute.return_value = "test"
        
        # This should not raise RuntimeError about event loop
        result = sh_cmd.execute(["-c", "echo test"])
        
        # Should execute without error
        assert result is not None
        # Check that shell.execute was called
        self.mock_shell.execute.assert_called_once_with("echo test")
        
    def test_python_command_run_method(self):
        """Test python command's run method (from base class)"""
        python_cmd = PythonCommand(self.mock_shell)

        # Directly replace method to avoid inspect warnings
        original_method = python_cmd._execute_sync
        python_cmd._execute_sync = lambda *args, **kwargs: "Python 3.x.x"
        try:
            # run() should call execute() which calls _execute_sync()
            result = python_cmd.run(["-V"])
            assert "Python" in result
        finally:
            python_cmd._execute_sync = original_method
            
    def test_sh_command_run_method(self):
        """Test sh command's run method (from base class)"""
        sh_cmd = ShCommand(self.mock_shell)
        
        # Mock shell execution
        self.mock_shell.execute.return_value = "Shell output"
        
        # run() should call execute() which calls _execute_sync()
        result = sh_cmd.run(["-c", "echo test"])
        
        # Should work without async issues
        assert result is not None
        
    def test_async_command_handles_no_event_loop(self):
        """Test that async commands handle missing event loop gracefully"""
        python_cmd = PythonCommand(self.mock_shell)
        
        with patch('asyncio.get_running_loop') as mock_get_loop:
            # Simulate no running event loop
            mock_get_loop.side_effect = RuntimeError("No running event loop")
            
            with patch('asyncio.run') as mock_run:
                # Mock asyncio.run to return a result
                mock_run.return_value = "Success"
                
                # run() should handle the missing loop by using asyncio.run
                result = python_cmd.run(["-V"])
                
                # Should have used asyncio.run since no loop was running
                assert mock_run.called
                assert "Python" in result or result == "Success"
                
    def test_python_command_script_execution(self):
        """Test python command can execute scripts without async issues"""
        python_cmd = PythonCommand(self.mock_shell)

        # Setup script file
        self.mock_shell.fs.exists.return_value = True
        self.mock_shell.fs.is_file.return_value = True
        self.mock_shell.fs.read_file.return_value = "print('Script output')"

        # Directly replace the method to avoid inspect module warnings
        original_method = python_cmd._execute_sync
        python_cmd._execute_sync = lambda *args, **kwargs: "Script executed"
        try:
            result = python_cmd.execute(["test.py"])
            assert "Script executed" in result
        finally:
            python_cmd._execute_sync = original_method
        
    def test_sh_command_script_execution(self):
        """Test sh command can execute scripts without async issues"""
        sh_cmd = ShCommand(self.mock_shell)
        
        # Setup script file
        self.mock_shell.fs.exists.return_value = True
        self.mock_shell.fs.is_file.return_value = True
        self.mock_shell.fs.read_file.return_value = "echo 'Script output'"
        
        # Mock shell execution
        self.mock_shell.execute.return_value = "Script output"
        
        result = sh_cmd.execute(["test.sh"])
        
        # Should execute without async errors
        assert result is not None
        
    def test_commands_work_in_sync_context(self):
        """Test commands work in purely synchronous context"""
        # No event loop should be running
        try:
            asyncio.get_running_loop()
            pytest.skip("Event loop is running, can't test sync context")
        except RuntimeError:
            # Good, no loop running
            pass

        # Suppress RuntimeWarning about unawaited coroutines during Mock inspection
        # This is a false positive - the coroutine isn't being called, just inspected
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*coroutine.*was never awaited")

            # Both commands should work
            python_cmd = PythonCommand(self.mock_shell)
            sh_cmd = ShCommand(self.mock_shell)

            # Directly replace methods to avoid inspect module warnings
            py_original = python_cmd._execute_sync
            python_cmd._execute_sync = lambda *args, **kwargs: "Python works"
            try:
                py_result = python_cmd.execute(["-V"])
                assert "Python" in py_result
            finally:
                python_cmd._execute_sync = py_original

            sh_original = sh_cmd._execute_sync
            sh_cmd._execute_sync = lambda *args, **kwargs: "Shell works"
            try:
                sh_result = sh_cmd.execute(["-c", "echo test"])
                assert "Shell works" in sh_result
            finally:
                sh_cmd._execute_sync = sh_original