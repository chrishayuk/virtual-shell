# chuk_virtual_shell/commands/filesystem/cp.py
"""
chuk_virtual_shell/commands/filesystem/cp.py - Copy files command
"""

from chuk_virtual_shell.commands.command_base import ShellCommand


class CpCommand(ShellCommand):
    name = "cp"
    help_text = """cp - Copy files and directories
Usage: cp [OPTIONS] source... destination
Options:
  -r, -R    Copy directories recursively
  -f        Force (ignore nonexistent files, never prompt)
  -i        Interactive (prompt before overwrite)
  -n        No clobber (do not overwrite existing files)
  -v        Verbose (explain what is being done)
  -p        Preserve mode, ownership, timestamps"""
    category = "file"

    def execute(self, args):
        if not args:
            return "cp: missing operand"

        # Parse options
        recursive = False
        force = False
        interactive = False
        verbose = False
        no_clobber = False

        sources = []
        i = 0
        while i < len(args):
            arg = args[i]
            if arg.startswith("-"):
                if "r" in arg or "R" in arg:
                    recursive = True
                if "f" in arg:
                    force = True
                if "i" in arg:
                    interactive = True
                if "v" in arg:
                    verbose = True
                if "n" in arg:
                    no_clobber = True
                if "p" in arg:
                    pass
                # Handle long-form options
                if arg == "--help":
                    return self.help_text
            else:
                sources.append(arg)
            i += 1

        if len(sources) < 2:
            return "cp: missing operand"

        *src_files, destination = sources

        # Check if destination is a directory if multiple sources are provided
        if len(src_files) > 1:
            dest_info = self.shell.fs.get_node_info(destination)
            if not dest_info or not dest_info.is_dir:
                return f"cp: target '{destination}' is not a directory"

        results = []
        for src in src_files:
            # Resolve source path (remove trailing slash for directories)
            src_resolved = self.shell.fs.resolve_path(src).rstrip("/")
            dest_resolved = self.shell.fs.resolve_path(destination).rstrip("/")

            # Check if source exists
            src_info = self.shell.fs.get_node_info(src_resolved)
            if not src_info:
                if not force:
                    return f"cp: cannot stat '{src}': No such file or directory"
                continue

            # Check if copying to self
            if src_resolved == dest_resolved:
                return f"cp: '{src}' and '{destination}' are the same file"
            
            # Check for circular copy (parent to child)
            if src_info.is_dir and dest_resolved.startswith(src_resolved + "/"):
                return f"cp: cannot copy directory '{src}' into itself '{destination}'"

            # Determine destination path
            dest_info = self.shell.fs.get_node_info(dest_resolved)
            if dest_info and dest_info.is_dir:
                # If destination is a directory, put the file inside the directory
                # Use portable path operations with forward slashes
                src_basename = (
                    src_resolved.split("/")[-1] if "/" in src_resolved else src_resolved
                )
                dest_path = dest_resolved.rstrip("/") + "/" + src_basename
            else:
                dest_path = dest_resolved

            # Handle directories
            if src_info.is_dir:
                if not recursive:
                    return f"cp: omitting directory '{src}'"

                # Use copy_dir if available and callable, fall back to manual recursion
                copy_dir_method = getattr(self.shell.fs, "copy_dir", None)
                if copy_dir_method and callable(copy_dir_method):
                    if copy_dir_method(src_resolved, dest_path):
                        if verbose:
                            results.append(f"'{src}' -> '{dest_path}'")
                    else:
                        # copy_dir failed, try manual recursion
                        copy_errors = self._copy_directory_recursive(src_resolved, dest_path, verbose)
                        if copy_errors:
                            return "\n".join(copy_errors)
                        if verbose:
                            results.append(f"'{src}' -> '{dest_path}'")
                else:
                    # Manual recursive copy
                    copy_errors = self._copy_directory_recursive(src_resolved, dest_path, verbose)
                    if copy_errors:
                        return "\n".join(copy_errors)
                    if verbose:
                        results.append(f"'{src}' -> '{dest_path}'")
            else:
                # Copy file
                # Check for no-clobber (don't overwrite existing files)
                if no_clobber and self.shell.fs.exists(dest_path):
                    continue
                
                # Check for interactive overwrite
                if interactive and self.shell.fs.exists(dest_path):
                    # In non-interactive mode, skip
                    continue

                # Check if destination parent directory exists
                dest_parent = "/".join(dest_path.split("/")[:-1]) if "/" in dest_path else ""
                if dest_parent and dest_parent != "" and not self.shell.fs.exists(dest_parent):
                    return f"cp: cannot create '{dest_path}': No such file or directory"

                content = self.shell.fs.read_file(src_resolved)
                if content is None:
                    if not force:
                        return f"cp: cannot read '{src}': Permission denied or file not found"
                    continue

                if not self.shell.fs.write_file(dest_path, content):
                    if not force:
                        return f"cp: failed to write to '{dest_path}'"
                elif verbose:
                    results.append(f"'{src}' -> '{dest_path}'")

        return "\n".join(results) if results else ""

    def _copy_directory_recursive(self, src, dst, verbose=False):
        """Recursively copy a directory"""
        errors = []
        
        # Create destination directory
        if not self.shell.fs.exists(dst):
            if not self.shell.fs.mkdir(dst):
                errors.append(f"cp: failed to create directory '{dst}'")
                return errors

        # List source directory contents
        if hasattr(self.shell.fs, "list_dir"):
            items = self.shell.fs.list_dir(src)
        elif hasattr(self.shell.fs, "ls"):
            items = self.shell.fs.ls(src)
        else:
            errors.append(f"cp: failed to list directory '{src}'")
            return errors

        # Copy each item
        for item in items:
            # Use portable path operations with forward slashes
            src_path = src.rstrip("/") + "/" + item
            dst_path = dst.rstrip("/") + "/" + item

            src_info = self.shell.fs.get_node_info(src_path)
            if src_info and src_info.is_dir:
                # Recursively copy subdirectory
                sub_errors = self._copy_directory_recursive(src_path, dst_path, verbose)
                errors.extend(sub_errors)
            else:
                # Copy file
                content = self.shell.fs.read_file(src_path)
                if content is not None:
                    if not self.shell.fs.write_file(dst_path, content):
                        errors.append(f"cp: failed to write file '{dst_path}'")

        return errors
