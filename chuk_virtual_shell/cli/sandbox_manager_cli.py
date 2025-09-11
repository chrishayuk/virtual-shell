#!/usr/bin/env python
import sys
import argparse
import pickle
import logging
from pathlib import Path
from typing import Optional

# If your sandbox manager is in a different location, adjust the import:
from chuk_virtual_shell.sandbox_manager import SandboxManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global path to store session data (insecure for real usage)
STORAGE_FILE = Path(".sandbox_sessions.pkl")


def load_manager() -> SandboxManager:
    """
    Load (or create) a SandboxManager instance and its existing sessions from STORAGE_FILE.
    """
    if STORAGE_FILE.exists():
        with open(STORAGE_FILE, "rb") as f:
            mgr = pickle.load(f)
            if not isinstance(mgr, SandboxManager):
                logger.warning(
                    "Invalid data in .sandbox_sessions.pkl; creating a new manager."
                )
                return SandboxManager()
            return mgr
    else:
        return SandboxManager()


def save_manager(manager: SandboxManager):
    """
    Save the SandboxManager (with all active sessions) to STORAGE_FILE.
    """
    with open(STORAGE_FILE, "wb") as f:
        pickle.dump(manager, f)


def cmd_start(args):
    """
    Start a new sandbox session, optionally with --sandbox-yaml / --fs-provider / --fs-provider-args.
    """
    mgr = load_manager()
    session_id = mgr.start_sandbox(
        sandbox_yaml=args.sandbox_yaml,
        fs_provider=args.fs_provider,
        fs_provider_args=_parse_provider_args(args.fs_provider_args),
    )
    save_manager(mgr)
    print(f"Sandbox started with session_id: {session_id}")


def cmd_write_file(args):
    """
    Write a file into the sandbox.
    """
    mgr = load_manager()
    if args.session_id not in mgr._sessions:
        sys.exit(f"No such session: {args.session_id}")
    mgr.write_file(args.session_id, args.path, args.content)
    save_manager(mgr)
    print(f"Wrote file {args.path} in sandbox {args.session_id}.")


def cmd_download_file(args):
    """
    Download (read) a file from the sandbox and print its contents to stdout.
    """
    mgr = load_manager()
    if args.session_id not in mgr._sessions:
        sys.exit(f"No such session: {args.session_id}")
    content = mgr.download_file(args.session_id, args.path)
    print(content if content is not None else "")


def cmd_install(args):
    """
    Install a Python package in the sandbox. If running in Pyodide + micropip, it’s async.
    Otherwise, attempts pip.
    """
    mgr = load_manager()
    if args.session_id not in mgr._sessions:
        sys.exit(f"No such session: {args.session_id}")

    # In a synchronous CLI, if micropip is used, it returns a future we must run in event loop.
    future = mgr.install_package(args.session_id, args.package)
    if future and hasattr(future, "result"):
        import asyncio

        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)

    save_manager(mgr)
    print(f"Installed '{args.package}' in sandbox {args.session_id}.")


def cmd_stop(args):
    """
    Stop (destroy) a sandbox session by ID.
    """
    mgr = load_manager()
    mgr.stop_sandbox(args.session_id)
    save_manager(mgr)
    print(f"Stopped sandbox session {args.session_id}.")


def _parse_provider_args(raw_str: Optional[str]) -> dict:
    """
    Parse filesystem provider args from a simple "key=value" comma list, or JSON.
    E.g. --fs-provider-args "key1=val1,key2=val2"
    """
    if not raw_str:
        return {}
    if "=" not in raw_str and "{" in raw_str:
        # Possibly JSON
        import json

        return json.loads(raw_str)
    else:
        parts = raw_str.split(",")
        d = {}
        for p in parts:
            if "=" in p:
                k, v = p.split("=", 1)
                d[k.strip()] = v.strip()
        return d


def main():
    parser = argparse.ArgumentParser(description="CLI for managing sandbox sessions.")

    subparsers = parser.add_subparsers(help="Sub-commands")

    # start command
    parser_start = subparsers.add_parser("start", help="Start a new sandbox")
    parser_start.add_argument(
        "--sandbox-yaml",
        type=str,
        default=None,
        help="Path/name of sandbox YAML config",
    )
    parser_start.add_argument(
        "--fs-provider",
        type=str,
        default=None,
        help="Filesystem provider (e.g. memory, sqlite, etc.)",
    )
    parser_start.add_argument(
        "--fs-provider-args",
        type=str,
        default=None,
        help="Extra arguments for the filesystem provider; JSON or key=value pairs.",
    )
    parser_start.set_defaults(func=cmd_start)

    # write-file command
    parser_write = subparsers.add_parser(
        "write-file", help="Write a file into the sandbox"
    )
    parser_write.add_argument(
        "--session-id", required=True, help="Sandbox session to join"
    )
    parser_write.add_argument(
        "--path", required=True, help="Path in sandbox, e.g. /test.txt"
    )
    parser_write.add_argument("--content", required=True, help="Content to write")
    parser_write.set_defaults(func=cmd_write_file)

    # download-file command
    parser_dl = subparsers.add_parser(
        "download-file", help="Download (read) a file from the sandbox"
    )
    parser_dl.add_argument(
        "--session-id", required=True, help="Sandbox session to join"
    )
    parser_dl.add_argument(
        "--path", required=True, help="Path in sandbox, e.g. /test.txt"
    )
    parser_dl.set_defaults(func=cmd_download_file)

    # install command
    parser_install = subparsers.add_parser(
        "install", help="Install a Python package in the sandbox"
    )
    parser_install.add_argument(
        "--session-id", required=True, help="Sandbox session to join"
    )
    parser_install.add_argument(
        "--package", required=True, help="Package name (e.g. requests)"
    )
    parser_install.set_defaults(func=cmd_install)

    # stop command
    parser_stop = subparsers.add_parser(
        "stop", help="Stop (destroy) a sandbox session by ID"
    )
    parser_stop.add_argument(
        "--session-id", required=True, help="Sandbox session to stop"
    )
    parser_stop.set_defaults(func=cmd_stop)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
