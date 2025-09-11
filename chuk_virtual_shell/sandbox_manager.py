import sys
import uuid
import logging
import asyncio

try:
    import micropip  # type: ignore

    HAS_MICROPIP = True
except ImportError:
    HAS_MICROPIP = False

from chuk_virtual_shell.shell_interpreter import ShellInterpreter

logger = logging.getLogger(__name__)


class SandboxSession:
    """
    Represents a single sandbox session, holding a reference to the ShellInterpreter.
    """

    def __init__(self, sandbox_yaml=None, fs_provider=None, fs_provider_args=None):
        # Either create from sandbox config or from provider
        if sandbox_yaml:
            self.shell = ShellInterpreter(sandbox_yaml=sandbox_yaml)
        else:
            self.shell = ShellInterpreter(
                fs_provider=fs_provider or "memory",
                fs_provider_args=fs_provider_args or {},
            )

    def write_file(self, path: str, content: str):
        """
        Write content to the given path in the sandbox filesystem.
        """
        logger.debug(f"Writing file to sandbox path {path}")
        self.shell.fs.write_file(path, content)

    def read_file(self, path: str) -> str:
        """
        Read (download) content from the given path in the sandbox filesystem.
        Returns the file content as a string.
        """
        logger.debug(f"Reading file from sandbox path {path}")
        return self.shell.fs.read_file(path)

    def install_package(self, package_name: str):
        """
        Install a Python package into this sandbox environment.
        If in Pyodide, use micropip; otherwise attempt pip via the shell.
        """
        if "pyodide" in sys.modules and HAS_MICROPIP:
            # Use micropip (asynchronously in Pyodide)
            logger.info(f"Installing {package_name} via micropip...")
            return asyncio.ensure_future(micropip.install(package_name))
        else:
            # If not in Pyodide, or micropip is unavailable,
            # fallback to shell-based `pip install <pkg>`
            # (Assumes that `pip` is available in the environment.)
            logger.info(f"Installing {package_name} via pip in shell...")
            cmd_line = f"pip install {package_name}"
            return self.shell.execute(cmd_line)

    def stop(self):
        """
        Perform any cleanup for the session. For memory-based sessions,
        this might be minimal. If you had external resources, close them here.
        """
        logger.info("Stopping sandbox session")
        self.shell.running = False


class SandboxManager:
    """
    High-level API to manage multiple sandbox sessions.
    """

    def __init__(self):
        self._sessions = {}  # Maps session_id -> SandboxSession

    def start_sandbox(
        self, sandbox_yaml=None, fs_provider=None, fs_provider_args=None
    ) -> str:
        """
        Start (create) a new sandbox session. Optionally specify:
          - sandbox_yaml: path or name of YAML sandbox config
          - fs_provider: name of the fs provider (e.g. "memory", "sqlite", etc.)
          - fs_provider_args: dict of extra arguments for fs provider
        Returns a session_id you can use to join this sandbox.
        """
        session = SandboxSession(
            sandbox_yaml=sandbox_yaml,
            fs_provider=fs_provider,
            fs_provider_args=fs_provider_args,
        )
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = session

        logger.info(f"Started sandbox session {session_id}")
        return session_id

    def join_sandbox(self, session_id: str) -> SandboxSession:
        """
        Retrieve (join) an existing sandbox session by ID.
        Raises KeyError if the session doesn't exist.
        """
        return self._sessions[session_id]

    def stop_sandbox(self, session_id: str):
        """
        Stop (destroy) a sandbox session by ID.
        """
        if session_id in self._sessions:
            logger.info(f"Stopping sandbox session {session_id}")
            self._sessions[session_id].stop()
            del self._sessions[session_id]
        else:
            logger.warning(f"Attempted to stop unknown session ID: {session_id}")

    def write_file(self, session_id: str, path: str, content: str):
        """
        Write a file inside the sandbox.
        """
        if session_id not in self._sessions:
            raise KeyError(f"Session {session_id} not found")
        self._sessions[session_id].write_file(path, content)

    def download_file(self, session_id: str, path: str) -> str:
        """
        Download (read) a file's contents from the sandbox.
        """
        if session_id not in self._sessions:
            raise KeyError(f"Session {session_id} not found")
        return self._sessions[session_id].read_file(path)

    def install_package(self, session_id: str, package_name: str):
        """
        Install a Python package into the sandbox.
        In Pyodide, uses micropip (if present); otherwise attempts `pip install`.
        """
        if session_id not in self._sessions:
            raise KeyError(f"Session {session_id} not found")
        return self._sessions[session_id].install_package(package_name)
