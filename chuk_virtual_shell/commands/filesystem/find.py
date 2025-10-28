"""
chuk_virtual_shell/commands/filesystem/find.py - Find files and directories
"""

import argparse
import fnmatch
import re
from typing import List, Optional
from chuk_virtual_shell.commands.command_base import ShellCommand


class FindCommand(ShellCommand):
    name = "find"
    help_text = (
        "find - Search for files in a directory hierarchy\n"
        "Usage: find [path...] [expression]\n"
        "Options:\n"
        "  -name pattern       File name matches pattern\n"
        "  -type d|f           File is of type d (directory) or f (file)\n"
        "  -maxdepth levels    Descend at most levels (a non-negative integer) levels\n"
        "  -regex pattern      File name matches regular expression pattern\n"
        "If no path is specified, the current directory is used."
    )
    category = "filesystem"

    def execute(self, args: List[str]) -> str:
        parser = argparse.ArgumentParser(prog=self.name, add_help=False)
        parser.add_argument("paths", nargs="*", default=["."], help="Paths to search")
        parser.add_argument("-name", type=str, help="Search for files matching pattern")
        parser.add_argument(
            "-type",
            choices=["d", "f"],
            help="Search for files of type (d=directory, f=file)",
        )
        parser.add_argument("-maxdepth", type=int, help="Maximum depth to search")
        parser.add_argument(
            "-regex", type=str, help="Search for files matching regex pattern"
        )

        try:
            parsed_args, _ = parser.parse_known_args(args)
        except SystemExit:
            return self.get_help()

        results = []

        for path in parsed_args.paths:
            # Resolve path to absolute
            abs_path = self.shell.fs.resolve_path(path)
            node_info = self.shell.fs.get_node_info(abs_path)

            # If the path does not exist, output an error message.
            if not node_info:
                # Use "No such file or directory" so that when lowercased it matches the test.
                results.append(f"find: '{path}': No such file or directory")
                continue

            # Compile regex pattern if provided
            regex_pattern = None
            if parsed_args.regex:
                try:
                    regex_pattern = re.compile(parsed_args.regex)
                except re.error:
                    results.append(
                        f"find: invalid regular expression '{parsed_args.regex}'"
                    )
                    continue

            # Search recursively
            found_paths = self._find_recursive(
                abs_path,
                0,
                parsed_args.maxdepth,
                parsed_args.name,
                parsed_args.type,
                regex_pattern,
            )

            # If -name filter is provided, show only the matching file’s basename.
            for found_path in found_paths:
                if parsed_args.name:
                    # Use portable path operations
                    display_path = (
                        found_path.split("/")[-1] if "/" in found_path else found_path
                    )
                else:
                    display_path = found_path

                results.append(display_path)

        return "\n".join(results) if results else ""

    def _find_recursive(
        self,
        path: str,
        current_depth: int,
        max_depth: Optional[int],
        name_pattern: Optional[str],
        type_filter: Optional[str],
        regex_pattern: Optional[re.Pattern] = None,
    ) -> List[str]:
        """
        Recursively find files and directories that match the given criteria.
        """
        if max_depth is not None and current_depth > max_depth:
            return []

        results = []
        node_info = self.shell.fs.get_node_info(path)
        if not node_info:
            return []

        include_this = True

        # Filter by type.
        if type_filter == "d" and not node_info.is_dir:
            include_this = False
        elif type_filter == "f" and node_info.is_dir:
            include_this = False

        # Use portable path operations
        base_name = path.split("/")[-1] if "/" in path else path or path

        if name_pattern and include_this:
            if not fnmatch.fnmatch(base_name, name_pattern):
                include_this = False

        if regex_pattern and include_this:
            if not regex_pattern.search(base_name):
                include_this = False

        if include_this:
            results.append(path)

        if node_info.is_dir:
            try:
                contents = self.shell.fs.ls(path)
                for item in contents:
                    # Use portable path operations
                    item_path = path.rstrip("/") + "/" + item
                    results.extend(
                        self._find_recursive(
                            item_path,
                            current_depth + 1,
                            max_depth,
                            name_pattern,
                            type_filter,
                            regex_pattern,
                        )
                    )
            except Exception as e:
                self.shell.error_log.append(f"find: '{path}': {str(e)}")

        return results
