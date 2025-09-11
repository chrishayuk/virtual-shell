"""
chuk_virtual_shell/interpreters/python_interpreter.py - Execute Python scripts with virtual FS access
"""

import sys
import io
import types
import traceback
from typing import Dict, Any, List, Optional


class VirtualPythonInterpreter:
    """Execute Python scripts with virtual FS access"""

    def __init__(self, shell):
        self.shell = shell
        self.output_buffer = io.StringIO()
        self.namespace = self._create_namespace()

    def _create_namespace(self) -> Dict[str, Any]:
        """Create Python namespace with virtual FS access"""

        # Store reference to avoid capture issues
        shell_fs = self.shell.fs
        shell_environ = self.shell.environ

        # Create virtual os module
        virtual_os = types.ModuleType("os")
        virtual_os.getcwd = (  # type: ignore
            lambda: shell_fs.pwd() if hasattr(shell_fs, "pwd") else shell_fs.cwd
        )
        virtual_os.chdir = (  # type: ignore
            lambda path: shell_fs.cd(path) if hasattr(shell_fs, "cd") else None
        )
        virtual_os.listdir = lambda path=".": self._listdir(path)  # type: ignore
        virtual_os.environ = shell_environ  # type: ignore
        virtual_os.getenv = lambda key, default=None: shell_environ.get(key, default)  # type: ignore
        virtual_os.path = types.ModuleType("path")  # type: ignore
        virtual_os.path.exists = lambda path: shell_fs.exists(  # type: ignore
            shell_fs.resolve_path(path)
        )
        virtual_os.path.isfile = lambda path: shell_fs.is_file(  # type: ignore
            shell_fs.resolve_path(path)
        )
        virtual_os.path.isdir = lambda path: shell_fs.is_dir(  # type: ignore
            shell_fs.resolve_path(path)
        )
        virtual_os.path.join = lambda *parts: "/".join(parts).replace("//", "/")  # type: ignore
        virtual_os.path.basename = lambda path: path.split("/")[-1]  # type: ignore
        virtual_os.path.dirname = lambda path: "/".join(path.split("/")[:-1]) or "/"  # type: ignore
        virtual_os.path.abspath = lambda path: shell_fs.resolve_path(path)  # type: ignore
        virtual_os.makedirs = lambda path, exist_ok=False: self._makedirs(  # type: ignore
            path, exist_ok
        )
        virtual_os.remove = lambda path: shell_fs.rm(path)  # type: ignore
        virtual_os.rmdir = lambda path: shell_fs.rmdir(path)  # type: ignore
        virtual_os.walk = lambda path=".": self._walk(path)  # type: ignore
        virtual_os.sep = "/"  # type: ignore  # Unix-style separator for virtual FS
        virtual_os.pathsep = ":"  # type: ignore  # Unix-style path separator

        # Create virtual sys module
        virtual_sys = types.ModuleType("sys")
        virtual_sys.argv = ["script.py"]  # type: ignore
        virtual_sys.path = sys.path.copy()  # type: ignore
        virtual_sys.version = sys.version  # type: ignore
        virtual_sys.platform = sys.platform  # type: ignore
        virtual_sys.stdout = self.output_buffer  # type: ignore
        virtual_sys.stderr = self.output_buffer  # type: ignore

        # Create virtual open function
        shell = self.shell  # Capture shell reference for closure

        def virtual_open(filepath, mode="r", encoding="utf-8"):
            """Virtual file open function"""

            class VirtualFile:
                def __init__(self, path, mode, encoding):
                    self.path = shell.fs.resolve_path(path)
                    self.mode = mode
                    self.encoding = encoding
                    self.position = 0
                    self.closed = False

                    # Initialize content
                    if "r" in mode:
                        self.content = shell.fs.read_file(self.path)
                        if self.content is None:
                            raise FileNotFoundError(f"No such file: {path}")
                        self.lines = self.content.splitlines(True)
                    elif "w" in mode:
                        self.content = ""
                        self.lines = []
                        if "a" not in mode:
                            # Create empty file for write mode
                            shell.fs.write_file(self.path, "")
                    elif "a" in mode:
                        self.content = shell.fs.read_file(self.path) or ""
                        self.lines = self.content.splitlines(True)

                def read(self, size=-1):
                    if self.closed:
                        raise ValueError("I/O operation on closed file")
                    if "r" not in self.mode:
                        raise IOError("File not open for reading")

                    if size == -1:
                        result = self.content[self.position :]
                        self.position = len(self.content)
                    else:
                        result = self.content[self.position : self.position + size]
                        self.position += len(result)
                    return result

                def readline(self):
                    if self.closed:
                        raise ValueError("I/O operation on closed file")
                    if "r" not in self.mode:
                        raise IOError("File not open for reading")

                    if self.position >= len(self.content):
                        return ""

                    # Find next newline
                    newline_pos = self.content.find("\n", self.position)
                    if newline_pos == -1:
                        result = self.content[self.position :]
                        self.position = len(self.content)
                    else:
                        result = self.content[self.position : newline_pos + 1]
                        self.position = newline_pos + 1
                    return result

                def readlines(self):
                    if self.closed:
                        raise ValueError("I/O operation on closed file")
                    if "r" not in self.mode:
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
                    if "w" not in self.mode and "a" not in self.mode:
                        raise IOError("File not open for writing")

                    self.content += str(data)
                    shell.fs.write_file(self.path, self.content)
                    return len(data)

                def writelines(self, lines):
                    for line in lines:
                        self.write(line)

                def flush(self):
                    if "w" in self.mode or "a" in self.mode:
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
        virtual_subprocess = types.ModuleType("subprocess")

        class CompletedProcess:
            def __init__(self, args, returncode, stdout=None, stderr=None):
                self.args = args
                self.returncode = returncode
                self.stdout = stdout
                self.stderr = stderr

        def virtual_run(args, shell=False, capture_output=False, text=True, **kwargs):
            """Virtual subprocess.run implementation"""
            if isinstance(args, list):
                cmd = " ".join(args)
            else:
                cmd = args

            # Execute through virtual shell
            result = self.shell.execute(cmd)

            if capture_output:
                return CompletedProcess(args, 0, result, "")
            else:
                if result:
                    self.output_buffer.write(result + "\n")
                return CompletedProcess(args, 0)

        virtual_subprocess.run = virtual_run  # type: ignore
        virtual_subprocess.CompletedProcess = CompletedProcess  # type: ignore
        virtual_subprocess.PIPE = -1  # type: ignore

        # Create custom __import__ to intercept module imports
        # Handle both dict and module forms of __builtins__
        if isinstance(__builtins__, dict):
            original_import = __builtins__["__import__"]
            custom_builtins = dict(__builtins__)
        else:
            original_import = __builtins__.__import__
            custom_builtins = dict(vars(__builtins__))

        def virtual_import(name, *args, **kwargs):
            # If it's one of our virtual modules, return it
            if name == "os":
                return virtual_os
            elif name == "sys":
                return virtual_sys
            elif name == "subprocess":
                return virtual_subprocess
            # Otherwise use the original import
            return original_import(name, *args, **kwargs)

        # Create custom builtins with our import
        custom_builtins["__import__"] = virtual_import

        # Create namespace
        namespace = {
            "__builtins__": custom_builtins,
            "__name__": "__main__",
            "os": virtual_os,
            "sys": virtual_sys,
            "open": virtual_open,
            "subprocess": virtual_subprocess,
            "print": self._virtual_print,
        }

        # Pre-populate sys.modules to ensure our virtual modules are used
        virtual_sys.modules = {  # type: ignore
            "os": virtual_os,
            "sys": virtual_sys,
            "subprocess": virtual_subprocess,
        }

        return namespace

    def _virtual_print(self, *args, **kwargs):
        """Custom print function that captures output"""
        output = io.StringIO()
        kwargs["file"] = output
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
        # Resolve path first
        resolved_path = self.shell.fs.resolve_path(path)

        if self.shell.fs.exists(resolved_path):
            if not exist_ok:
                raise FileExistsError(f"Directory exists: {resolved_path}")
            return

        # Create parent directories if needed
        parts = resolved_path.split("/")
        current = ""
        for part in parts:
            if part:
                current = current + "/" + part if current else "/" + part
                if not self.shell.fs.exists(current):
                    self.shell.fs.mkdir(current)

    def _walk(self, top):
        """Walk directory tree, yielding tuples (dirpath, dirnames, filenames)"""
        # Resolve the top directory path
        top = self.shell.fs.resolve_path(top)

        # Get all items in the current directory
        items = self.shell.fs.ls(top)
        if items is None:
            return

        dirnames = []
        filenames = []

        # Separate directories and files
        for item in items:
            item_path = f"{top}/{item}" if top != "/" else f"/{item}"
            if self.shell.fs.is_dir(item_path):
                dirnames.append(item)
            else:
                filenames.append(item)

        # Yield current directory info
        yield (top, dirnames, filenames)

        # Recursively walk subdirectories
        for dirname in dirnames:
            subdir = f"{top}/{dirname}" if top != "/" else f"/{dirname}"
            # Use yield from for recursive generator
            yield from self._walk(subdir)

    async def run_script(
        self, script_path: str, args: Optional[List[str]] = None
    ) -> str:
        """Execute Python script from virtual FS"""

        # Read script from virtual FS
        script_content = self.shell.fs.read_file(script_path)
        if script_content is None:
            return f"python: {script_path}: No such file or directory"

        # Set up sys.argv
        if args:
            self.namespace["sys"].argv = [script_path] + args
        else:
            self.namespace["sys"].argv = [script_path]

        return await self.execute_code(script_content)

    async def execute_code(self, code: str) -> str:
        """Execute Python code in virtual environment"""

        # Reset output buffer
        self.output_buffer = io.StringIO()
        self.namespace["sys"].stdout = self.output_buffer
        self.namespace["sys"].stderr = self.output_buffer

        try:
            # Compile and execute the code
            compiled = compile(code, "<script>", "exec")
            exec(compiled, self.namespace)

            # Return captured output
            return self.output_buffer.getvalue()

        except SyntaxError as e:
            return f"SyntaxError: {e}"
        except Exception:
            # Format exception traceback
            tb = traceback.format_exc()
            return tb

    def run_script_sync(
        self, script_path: str, args: Optional[List[str]] = None
    ) -> str:
        """Synchronous version of run_script"""
        script_content = self.shell.fs.read_file(script_path)
        if script_content is None:
            return f"python: {script_path}: No such file or directory"

        if args:
            self.namespace["sys"].argv = [script_path] + args
        else:
            self.namespace["sys"].argv = [script_path]

        return self.execute_code_sync(script_content)

    def execute_code_sync(self, code: str) -> str:
        """Synchronous version of execute_code"""
        self.output_buffer = io.StringIO()
        self.namespace["sys"].stdout = self.output_buffer
        self.namespace["sys"].stderr = self.output_buffer

        try:
            compiled = compile(code, "<script>", "exec")
            exec(compiled, self.namespace)
            return self.output_buffer.getvalue()
        except SyntaxError as e:
            return f"SyntaxError: {e}"
        except Exception:
            tb = traceback.format_exc()
            return tb
