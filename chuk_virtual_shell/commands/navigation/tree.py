# src/chuk_virtual_shell/commands/navigation/tree.py
"""
chuk_virtual_shell/commands/navigation/tree.py - tree command implementation

Displays directory structure in a tree-like format.
"""

from chuk_virtual_shell.commands.command_base import ShellCommand


class TreeCommand(ShellCommand):
    """Display directory tree structure"""

    name = "tree"
    help_text = """tree - list contents of directories in a tree-like format
    
Usage: tree [options] [directory ...]

Options:
    -a          Show all files (including hidden)
    -d          List directories only
    -f          Print full path for each file
    -L level    Descend only level directories deep
    -I pattern  Do not list files that match the pattern
    --dirsfirst List directories before files

Description:
    Tree is a recursive directory listing program that produces
    a depth-indented listing of files.
    
Examples:
    tree                    # Show tree from current directory
    tree /home             # Show tree from /home
    tree -L 2              # Show only 2 levels deep
    tree -d                # Show only directories
    tree -a                # Show hidden files too
    tree -I "*.pyc"        # Exclude .pyc files"""

    category = "navigation"

    def execute(self, args):
        """Execute the tree command"""
        # Parse arguments
        show_all = False
        dirs_only = False
        full_path = False
        max_level = None
        ignore_pattern = None
        dirs_first = False
        directories = []

        i = 0
        while i < len(args):
            arg = args[i]

            if arg == "-a":
                show_all = True
            elif arg == "-d":
                dirs_only = True
            elif arg == "-f":
                full_path = True
            elif arg == "--dirsfirst":
                dirs_first = True
            elif arg == "-L":
                if i + 1 < len(args):
                    try:
                        max_level = int(args[i + 1])
                        i += 1
                    except ValueError:
                        return f"tree: Invalid level, must be numeric: {args[i + 1]}"
                else:
                    return "tree: option -L requires an argument"
            elif arg == "-I":
                if i + 1 < len(args):
                    ignore_pattern = args[i + 1]
                    i += 1
                else:
                    return "tree: option -I requires an argument"
            elif arg.startswith("-"):
                return f"tree: invalid option -- '{arg[1:]}'"
            else:
                directories.append(arg)
            i += 1

        # Default to current directory if no directories specified
        if not directories:
            directories = [self.shell.fs.pwd()]

        # Process each directory
        all_output = []
        total_dirs = 0
        total_files = 0

        for directory in directories:
            try:
                resolved_dir = self.shell.fs.resolve_path(directory)
                if not self.shell.fs.exists(resolved_dir):
                    all_output.append(f"tree: {directory}: No such file or directory")
                    continue

                if not self.shell.fs.is_dir(resolved_dir):
                    all_output.append(f"tree: {directory}: Not a directory")
                    continue

                # Display the root directory
                if full_path:
                    all_output.append(resolved_dir)
                else:
                    all_output.append(
                        directory if directory != "." else self.shell.fs.get_cwd()
                    )

                # Recursively display tree
                dir_count, file_count = self._display_tree(
                    resolved_dir,
                    "",
                    show_all,
                    dirs_only,
                    full_path,
                    max_level,
                    ignore_pattern,
                    dirs_first,
                    all_output,
                    1,
                )

                total_dirs += dir_count
                total_files += file_count

            except Exception as e:
                all_output.append(f"tree: {directory}: {str(e)}")

        # Add summary
        all_output.append("")
        if dirs_only:
            all_output.append(f"{total_dirs} directories")
        else:
            all_output.append(f"{total_dirs} directories, {total_files} files")

        return "\n".join(all_output)

    def _display_tree(
        self,
        path,
        prefix,
        show_all,
        dirs_only,
        full_path,
        max_level,
        ignore_pattern,
        dirs_first,
        output,
        current_level,
    ):
        """Recursively display directory tree"""
        dir_count = 0
        file_count = 0

        # Check max level
        if max_level is not None and current_level > max_level:
            return dir_count, file_count

        try:
            # Get directory contents
            items = self.shell.fs.list_directory(path)

            # Filter hidden files if needed
            if not show_all:
                items = [item for item in items if not item.startswith(".")]

            # Filter by ignore pattern
            if ignore_pattern:
                import fnmatch

                items = [
                    item for item in items if not fnmatch.fnmatch(item, ignore_pattern)
                ]

            # Separate directories and files
            dirs = []
            files = []

            for item in items:
                item_path = f"{path}/{item}"
                if self.shell.fs.is_dir(item_path):
                    dirs.append(item)
                else:
                    files.append(item)

            # Sort
            dirs.sort()
            files.sort()

            # Order based on dirs_first flag
            if dirs_first:
                all_items = dirs + files
            else:
                all_items = sorted(items)

            # Display items
            for i, item in enumerate(all_items):
                is_last = i == len(all_items) - 1
                item_path = f"{path}/{item}"
                is_dir = self.shell.fs.is_dir(item_path)

                # Skip files if dirs_only
                if dirs_only and not is_dir:
                    continue

                # Create the tree branch characters
                if is_last:
                    branch = "└── "
                    extension = "    "
                else:
                    branch = "├── "
                    extension = "│   "

                # Display the item
                if full_path:
                    display_name = item_path
                else:
                    display_name = item

                output.append(f"{prefix}{branch}{display_name}")

                # Count
                if is_dir:
                    dir_count += 1
                    # Recurse into directory
                    sub_dirs, sub_files = self._display_tree(
                        item_path,
                        prefix + extension,
                        show_all,
                        dirs_only,
                        full_path,
                        max_level,
                        ignore_pattern,
                        dirs_first,
                        output,
                        current_level + 1,
                    )
                    dir_count += sub_dirs
                    file_count += sub_files
                else:
                    file_count += 1

        except Exception:
            pass  # Silently skip directories we can't read

        return dir_count, file_count
