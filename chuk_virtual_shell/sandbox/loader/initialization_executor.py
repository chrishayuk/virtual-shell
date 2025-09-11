# chuk_virtual_shell/sandbox/loader/initialization_executor.py
import os
import logging

from chuk_virtual_fs import VirtualFileSystem  # type: ignore

logger = logging.getLogger(__name__)


def execute_initialization(fs: VirtualFileSystem, commands: list) -> None:
    """
    Execute initialization commands on the provided filesystem.

    Args:
        fs: An instance of VirtualFileSystem.
        commands: A list of initialization command strings.
    """
    for command in commands:
        parts = command.split(maxsplit=1)
        cmd = parts[0]

        if cmd == "mkdir":
            if len(parts) > 1:
                args = parts[1].strip()
                if args.startswith("-p "):
                    path = args[3:].strip()
                    _ensure_directory(fs, path)
                else:
                    fs.mkdir(args)

        elif cmd == "echo":
            if len(parts) > 1 and ">" in parts[1]:
                content, path = parts[1].split(">", 1)
                content = content.strip()
                if (content.startswith("'") and content.endswith("'")) or (
                    content.startswith('"') and content.endswith('"')
                ):
                    content = content[1:-1]
                path = path.strip()
                parent_dir = os.path.dirname(path)
                if parent_dir:
                    _ensure_directory(fs, parent_dir)
                fs.write_file(path, content)
        else:
            logger.warning(f"Unrecognized initialization command: {command}")


def _ensure_directory(fs: VirtualFileSystem, path: str) -> None:
    """
    Ensure that a directory exists in the filesystem.
    """
    components = path.strip("/").split("/")
    current_path = "/"
    for component in components:
        if not component:
            continue
        current_path = current_path.rstrip("/") + "/" + component
        info = fs.get_node_info(current_path)
        if not info:
            fs.mkdir(current_path)
        elif not info.is_dir:
            raise ValueError(f"Path {current_path} exists but is not a directory")
