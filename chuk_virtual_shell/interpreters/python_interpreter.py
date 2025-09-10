"""
chuk_virtual_shell/interpreters/python_interpreter.py - Execute Python scripts with virtual FS access
"""
import sys
import io
import contextlib
import types
import traceback
from typing import Dict, Any

class VirtualPythonInterpreter:
    """Execute Python scripts with virtual FS access"""
    
    def __init__(self, shell):
        self.shell = shell
        self.output_buffer = io.StringIO()
        self.namespace = self._create_namespace()
    
    def _create_namespace(self) -> Dict[str, Any]:
        """Create Python namespace with virtual FS access"""
        
        # Create virtual os module
        virtual_os = types.ModuleType('os')
        virtual_os.getcwd = lambda: self.shell.fs.cwd
        virtual_os.chdir = lambda path: self.shell.fs.chdir(path)
        virtual_os.listdir = lambda path='.': self._listdir(path)
        virtual_os.environ = self.shell.environ
        virtual_os.getenv = lambda key, default=None: self.shell.environ.get(key, default)
        virtual_os.path = types.ModuleType('path')
        virtual_os.path.exists = lambda path: self.shell.fs.exists(path)
        virtual_os.path.isfile = lambda path: self.shell.fs.is_file(path)
        virtual_os.path.isdir = lambda path: self.shell.fs.is_dir(path)
        virtual_os.path.join = lambda *parts: '/'.join(parts).replace('//', '/')
        virtual_os.path.basename = lambda path: path.split('/')[-1]
        virtual_os.path.dirname = lambda path: '/'.join(path.split('/')[:-1]) or '/'
        virtual_os.path.abspath = lambda path: self.shell.fs.resolve_path(path)
        virtual_os.makedirs = lambda path, exist_ok=False: self._makedirs(path, exist_ok)
        virtual_os.remove = lambda path: self.shell.fs.rm(path)
        virtual_os.rmdir = lambda path: self.shell.fs.rmdir(path)
        
        # Create virtual sys module
        virtual_sys = types.ModuleType('sys')
        virtual_sys.argv = ['script.py']
        virtual_sys.path = sys.path.copy()
        virtual_sys.version = sys.version
        virtual_sys.platform = sys.platform
        virtual_sys.stdout = self.output_buffer
        virtual_sys.stderr = self.output_buffer
        
        # Create virtual open function
        shell = self.shell  # Capture shell reference for closure
        
        def virtual_open(filepath, mode='r', encoding='utf-8'):
            """Virtual file open function"""
            
            class VirtualFile:
                def __init__(self, path, mode, encoding):
                    self.path = shell.fs.resolve_path(path)
                    self.mode = mode
                    self.encoding = encoding
                    self.position = 0
                    self.closed = False
                    
                    # Initialize content
                    if 'r' in mode:
                        self.content = shell.fs.read_file(self.path)
                        if self.content is None:
                            raise FileNotFoundError(f"No such file: {path}")
                        self.lines = self.content.splitlines(True)
                    elif 'w' in mode:
                        self.content = ""
                        self.lines = []
                        if 'a' not in mode:
                            # Create empty file for write mode
                            shell.fs.write_file(self.path, "")
                    elif 'a' in mode:
                        self.content = shell.fs.read_file(self.path) or ""
                        self.lines = self.content.splitlines(True)
                
                def read(self, size=-1):
                    if self.closed:
                        raise ValueError("I/O operation on closed file")
                    if 'r' not in self.mode:
                        raise IOError("File not open for reading")
                    
                    if size == -1:
                        result = self.content[self.position:]
                        self.position = len(self.content)
                    else:
                        result = self.content[self.position:self.position + size]
                        self.position += len(result)
                    return result
                
                def readline(self):
                    if self.closed:
                        raise ValueError("I/O operation on closed file")
                    if 'r' not in self.mode:
                        raise IOError("File not open for reading")
                    
                    if self.position >= len(self.content):
                        return ""
                    
                    # Find next newline
                    newline_pos = self.content.find('\n', self.position)
                    if newline_pos == -1:
                        result = self.content[self.position:]
                        self.position = len(self.content)
                    else:
                        result = self.content[self.position:newline_pos + 1]
                        self.position = newline_pos + 1
                    return result
                
                def readlines(self):
                    if self.closed:
                        raise ValueError("I/O operation on closed file")
                    if 'r' not in self.mode:
                        raise IOError("File not open for reading")
                    
                    lines = []
                    while True:
                        line = self.readline()
                        if not line:
                            break
                        lines.append(line)
                    return lines
                
                def write(self, data):
                    if self.closed:
                        raise ValueError("I/O operation on closed file")
                    if 'w' not in self.mode and 'a' not in self.mode:
                        raise IOError("File not open for writing")
                    
                    self.content += str(data)
                    shell.fs.write_file(self.path, self.content)
                    return len(data)
                
                def writelines(self, lines):
                    for line in lines:
                        self.write(line)
                
                def flush(self):
                    if 'w' in self.mode or 'a' in self.mode:
                        shell.fs.write_file(self.path, self.content)
                
                def close(self):
                    if not self.closed:
                        self.flush()
                        self.closed = True
                
                def __enter__(self):
                    return self
                
                def __exit__(self, exc_type, exc_val, exc_tb):
                    self.close()
                
                def __iter__(self):
                    return self
                
                def __next__(self):
                    line = self.readline()
                    if not line:
                        raise StopIteration
                    return line
            
            return VirtualFile(filepath, mode, encoding)
        
        # Create virtual subprocess module
        virtual_subprocess = types.ModuleType('subprocess')
        
        class CompletedProcess:
            def __init__(self, args, returncode, stdout=None, stderr=None):
                self.args = args
                self.returncode = returncode
                self.stdout = stdout
                self.stderr = stderr
        
        def virtual_run(args, shell=False, capture_output=False, text=True, **kwargs):
            """Virtual subprocess.run implementation"""
            if isinstance(args, list):
                cmd = ' '.join(args)
            else:
                cmd = args
            
            # Execute through virtual shell
            result = self.shell.execute(cmd)
            
            if capture_output:
                return CompletedProcess(args, 0, result, "")
            else:
                if result:
                    self.output_buffer.write(result + '\n')
                return CompletedProcess(args, 0)
        
        virtual_subprocess.run = virtual_run
        virtual_subprocess.CompletedProcess = CompletedProcess
        virtual_subprocess.PIPE = -1
        
        # Create namespace
        namespace = {
            '__builtins__': __builtins__,
            '__name__': '__main__',
            'os': virtual_os,
            'sys': virtual_sys,
            'open': virtual_open,
            'subprocess': virtual_subprocess,
            'print': self._virtual_print,
        }
        
        return namespace
    
    def _virtual_print(self, *args, **kwargs):
        """Custom print function that captures output"""
        output = io.StringIO()
        kwargs['file'] = output
        print(*args, **kwargs)
        result = output.getvalue()
        self.output_buffer.write(result)
        return result
    
    def _listdir(self, path):
        """List directory contents"""
        items = self.shell.fs.list_dir(path)
        return items if items is not None else []
    
    def _makedirs(self, path, exist_ok=False):
        """Create directory recursively"""
        if self.shell.fs.exists(path):
            if not exist_ok:
                raise FileExistsError(f"Directory exists: {path}")
            return
        
        # Create parent directories if needed
        parts = path.split('/')
        current = ''
        for part in parts:
            if part:
                current = current + '/' + part if current else part
                if not self.shell.fs.exists(current):
                    self.shell.fs.mkdir(current)
    
    async def run_script(self, script_path: str, args: list = None) -> str:
        """Execute Python script from virtual FS"""
        
        # Read script from virtual FS
        script_content = self.shell.fs.read_file(script_path)
        if script_content is None:
            return f"python: {script_path}: No such file or directory"
        
        # Set up sys.argv
        if args:
            self.namespace['sys'].argv = [script_path] + args
        else:
            self.namespace['sys'].argv = [script_path]
        
        return await self.execute_code(script_content)
    
    async def execute_code(self, code: str) -> str:
        """Execute Python code in virtual environment"""
        
        # Reset output buffer
        self.output_buffer = io.StringIO()
        self.namespace['sys'].stdout = self.output_buffer
        self.namespace['sys'].stderr = self.output_buffer
        
        try:
            # Compile and execute the code
            compiled = compile(code, '<script>', 'exec')
            exec(compiled, self.namespace)
            
            # Return captured output
            return self.output_buffer.getvalue()
            
        except SyntaxError as e:
            return f"SyntaxError: {e}"
        except Exception as e:
            # Format exception traceback
            tb = traceback.format_exc()
            return tb
    
    def run_script_sync(self, script_path: str, args: list = None) -> str:
        """Synchronous version of run_script"""
        script_content = self.shell.fs.read_file(script_path)
        if script_content is None:
            return f"python: {script_path}: No such file or directory"
        
        if args:
            self.namespace['sys'].argv = [script_path] + args
        else:
            self.namespace['sys'].argv = [script_path]
        
        return self.execute_code_sync(script_content)
    
    def execute_code_sync(self, code: str) -> str:
        """Synchronous version of execute_code"""
        self.output_buffer = io.StringIO()
        self.namespace['sys'].stdout = self.output_buffer
        self.namespace['sys'].stderr = self.output_buffer
        
        try:
            compiled = compile(code, '<script>', 'exec')
            exec(compiled, self.namespace)
            return self.output_buffer.getvalue()
        except SyntaxError as e:
            return f"SyntaxError: {e}"
        except Exception as e:
            tb = traceback.format_exc()
            return tb