"""
chuk_virtual_shell/commands/filesystem/quota.py - Display disk usage and limits
"""

import argparse
import os
from typing import Dict, Optional, Any, Tuple
from chuk_virtual_shell.commands.command_base import ShellCommand


class QuotaCommand(ShellCommand):
    name = "quota"
    help_text = (
        "quota - Display disk usage and limits\n"
        "Usage: quota [-h] [-g] [user_or_group ...]\n"
        "Options:\n"
        "  -h, --human-readable  Print sizes in human readable format (e.g., 1K, 234M)\n"
        "  -g, --group           Display group quotas rather than user quotas\n"
        "If no user or group is specified, the current user's quota is displayed."
    )
    category = "filesystem"

    def execute(self, args):
        parser = argparse.ArgumentParser(prog=self.name, add_help=False)
        parser.add_argument(
            "-h",
            "--human-readable",
            action="store_true",
            help="Print sizes in human readable format",
        )
        parser.add_argument(
            "-g", "--group", action="store_true", help="Display group quotas"
        )
        parser.add_argument(
            "targets", nargs="*", help="Users or groups to display quotas for"
        )

        try:
            parsed_args = parser.parse_args(args)
        except SystemExit:
            return self.get_help()

        # Default to current user if no targets provided
        targets = parsed_args.targets
        if not targets:
            targets = [self.shell.current_user]

        results = []

        # Header
        if parsed_args.group:
            header = "Disk quotas for groups:"
        else:
            header = "Disk quotas for users:"
        results.append(header)
        results.append(
            "Filesystem  blocks   quota   limit   grace   files   quota   limit   grace"
        )

        for target in targets:
            # Get quota information from the shell
            quota_info = self._get_quota_info(target, parsed_args.group)

            if quota_info is None:
                entity_type = "group" if parsed_args.group else "user"
                results.append(f"quota: no {entity_type} quotas for {target}")
                continue

            # Format values based on human-readable flag
            if parsed_args.human_readable:
                blocks = self._format_size(
                    quota_info["blocks"] * 1024
                )  # blocks are traditionally in KB
                quota = self._format_size(quota_info["quota"] * 1024)
                limit = self._format_size(quota_info["limit"] * 1024)
            else:
                blocks = str(quota_info["blocks"])
                quota = str(quota_info["quota"])
                limit = str(quota_info["limit"])

            # Format the output line
            fs = quota_info["filesystem"]
            files = str(quota_info["files"])
            files_quota = str(quota_info["files_quota"])
            files_limit = str(quota_info["files_limit"])
            grace_block = quota_info["grace_block"] or "-"
            grace_file = quota_info["grace_file"] or "-"

            line = f"{fs:<12} {blocks:<8} {quota:<7} {limit:<7} {grace_block:<7} {files:<7} {files_quota:<7} {files_limit:<7} {grace_file}"
            results.append(line)

        return "\n".join(results)

    def _has_security_wrapper(self) -> bool:
        """
        Check if the filesystem has a security wrapper with quota information.
        """
        # Check if get_storage_stats method exists and returns security-related info
        if hasattr(self.shell.fs, "get_storage_stats"):
            try:
                stats = self.shell.fs.get_storage_stats()
                return "max_file_size" in stats and "max_total_size" in stats
            except Exception:
                pass

        # Check if the provider name contains 'security'
        if hasattr(self.shell.fs, "get_provider_name"):
            try:
                provider_name = self.shell.fs.get_provider_name().lower()
                return "security" in provider_name
            except Exception:
                pass

        return False

    def _get_quota_info(self, target, is_group=False) -> Optional[Dict[str, Any]]:
        """
        Get quota information for a user or group.
        Uses security wrapper information if available.
        """
        # Handle user/group existence check
        user_exists = self._check_user_exists(target, is_group)
        if not user_exists:
            return None

        # For real environments, check security wrapper first
        if self._has_security_wrapper():
            try:
                return self._get_security_wrapper_quota_info(target, is_group)
            except Exception:
                # If security wrapper approach fails, fall through to default behavior
                pass

        # Calculate actual usage stats
        blocks_used, files_used = self._calculate_usage_stats(target, is_group)

        # If we couldn't get real usage and no security wrapper, return None
        if blocks_used == 0 and files_used == 0 and not self._has_security_wrapper():
            return None

        # Use quota information if we can get it
        quota_dict = self._get_real_quota_info(
            target, is_group, blocks_used, files_used
        )
        if quota_dict:
            return quota_dict

        # If we reached here, we don't have any quota information
        return None

    def _check_user_exists(self, target, is_group=False) -> bool:
        """Check if user or group exists."""
        try:
            if is_group:
                if hasattr(self.shell, "group_exists"):
                    return self.shell.group_exists(target)
            else:
                if hasattr(self.shell, "user_exists"):
                    return self.shell.user_exists(target)
                # Check if it's the current user
                if hasattr(self.shell, "current_user"):
                    return target == self.shell.current_user
            return False
        except Exception:
            return False

    def _calculate_usage_stats(self, target, is_group=False) -> Tuple[int, int]:
        """Calculate actual disk usage stats for the user."""
        blocks_used = 0
        files_used = 0

        # Try to get the user's home directory without hardcoding paths
        base_path = None

        # First try user-specific APIs that might exist
        if hasattr(self.shell, "get_user_home"):
            base_path = self.shell.get_user_home(target)
        elif hasattr(self.shell, "get_group_directory") and is_group:
            base_path = self.shell.get_group_directory(target)

        # If we still don't have a path and current user, try environment variables
        if base_path is None and hasattr(self.shell, "environ"):
            if not is_group and target == getattr(self.shell, "current_user", None):
                base_path = self.shell.environ.get("HOME")

        # If we still don't have a directory, we can't determine stats
        if base_path is None:
            return 0, 0

        try:
            # Different methods to find files based on available APIs
            all_files = []
            if hasattr(self.shell.fs, "find") and callable(self.shell.fs.find):
                all_files = self.shell.fs.find(base_path, recursive=True)
            # Try using walk method if find is not available
            elif hasattr(self.shell.fs, "walk") and callable(self.shell.fs.walk):
                for root, _, files in self.shell.fs.walk(base_path):
                    for file in files:
                        all_files.append(os.path.join(root, file))

            # Calculate size and count
            for file_path in all_files:
                # Check if file (not directory)
                is_dir = False
                if hasattr(self.shell.fs, "is_dir"):
                    is_dir = self.shell.fs.is_dir(file_path)
                elif hasattr(self.shell.fs, "isdir"):
                    is_dir = self.shell.fs.isdir(file_path)
                elif hasattr(self.shell.fs, "get_node_info"):
                    node_info = self.shell.fs.get_node_info(file_path)
                    is_dir = (
                        node_info and hasattr(node_info, "is_dir") and node_info.is_dir
                    )

                if not is_dir:
                    try:
                        # Get file size
                        size = 0
                        if hasattr(self.shell.fs, "get_size"):
                            size = self.shell.fs.get_size(file_path)
                        elif hasattr(self.shell, "get_size"):
                            size = self.shell.get_size(file_path)
                        elif hasattr(self.shell.fs, "read_file"):
                            content = self.shell.fs.read_file(file_path)
                            if content:
                                size = len(content)

                        blocks_used += size // 1024  # Convert to KB blocks
                        files_used += 1
                    except Exception:
                        # Skip files with errors
                        pass
        except Exception:
            # If any error occurs, return zeros
            pass

        return blocks_used, files_used

    def _get_security_wrapper_quota_info(
        self, target, is_group=False
    ) -> Optional[Dict[str, Any]]:
        """Get quota info from security wrapper."""
        blocks_used, files_used = self._calculate_usage_stats(target, is_group)

        # Get stats from security wrapper
        stats = self.shell.fs.get_storage_stats()

        # Only proceed if we have the needed quota info
        if "max_total_size" not in stats or "max_files" not in stats:
            return None

        # Get quota values
        quota = stats.get("max_total_size", 0) // 1024  # Convert to KB
        limit = int(quota * 1.2)  # 20% over quota as hard limit
        max_files = stats.get("max_files", 0)

        # Handle grace periods
        grace_block = None
        grace_file = None
        if blocks_used > quota:
            grace_block = "7days"
        if files_used > max_files:
            grace_file = "7days"

        # Get filesystem name from stats, but don't assume a default
        filesystem = ""
        if "filesystem" in stats:
            filesystem = stats["filesystem"]
        elif "provider_name" in stats:
            filesystem = stats["provider_name"]

        return {
            "filesystem": filesystem,
            "blocks": blocks_used,
            "quota": quota,
            "limit": limit,
            "grace_block": grace_block,
            "files": files_used,
            "files_quota": max_files,
            "files_limit": int(max_files * 1.2),  # 20% over as hard limit
            "grace_file": grace_file,
        }

    def _get_real_quota_info(
        self, target, is_group, blocks_used, files_used
    ) -> Optional[Dict[str, Any]]:
        """Get real quota info if available from filesystem."""
        # In a real implementation, this would talk to a quota system API
        # For our virtual system, if we don't have a security wrapper,
        # we don't have a way to get real quota info yet
        return None

    def _format_size(self, size_bytes):
        """Format size in human-readable format"""
        for unit in ["B", "K", "M", "G", "T"]:
            if size_bytes < 1024 or unit == "T":
                if unit == "B":
                    return f"{size_bytes}{unit}"
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024
