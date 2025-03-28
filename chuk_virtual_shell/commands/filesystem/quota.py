# quota.py
import argparse
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
        parser.add_argument('-h', '--human-readable', action='store_true', help='Print sizes in human readable format')
        parser.add_argument('-g', '--group', action='store_true', help='Display group quotas')
        parser.add_argument('targets', nargs='*', help='Users or groups to display quotas for')
        
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
        results.append("Filesystem  blocks   quota   limit   grace   files   quota   limit   grace")
        
        for target in targets:
            # Get quota information from the shell
            quota_info = self._get_quota_info(target, parsed_args.group)
            
            if quota_info is None:
                entity_type = "group" if parsed_args.group else "user"
                results.append(f"quota: no {entity_type} quotas for {target}")
                continue
            
            # Format values based on human-readable flag
            if parsed_args.human_readable:
                blocks = self._format_size(quota_info['blocks'] * 1024)  # blocks are traditionally in KB
                quota = self._format_size(quota_info['quota'] * 1024)
                limit = self._format_size(quota_info['limit'] * 1024)
            else:
                blocks = str(quota_info['blocks'])
                quota = str(quota_info['quota'])
                limit = str(quota_info['limit'])
            
            # Format the output line
            fs = quota_info['filesystem']
            files = str(quota_info['files'])
            files_quota = str(quota_info['files_quota'])
            files_limit = str(quota_info['files_limit'])
            grace_block = quota_info['grace_block'] or "-"
            grace_file = quota_info['grace_file'] or "-"
            
            line = f"{fs:<12} {blocks:<8} {quota:<7} {limit:<7} {grace_block:<7} {files:<7} {files_quota:<7} {files_limit:<7} {grace_file}"
            results.append(line)
        
        return "\n".join(results)
    
    def _get_quota_info(self, target, is_group=False):
        """
        Get quota information for a user or group.
        In a real implementation, this would query the system.
        For this example, we'll simulate it.
        """
        # Check if user/group exists
        if is_group:
            if not self.shell.group_exists(target):
                return None
        else:
            if not self.shell.user_exists(target):
                return None
        
        # In a real implementation, this would query the actual quota system
        # For now, we'll return simulated data
        
        # Get home directory and calculate usage
        if is_group:
            base_path = f"/home/groups/{target}"
        else:
            base_path = f"/home/{target}"
        
        # Calculate simulated usage - in a real implementation this would be from the OS
        try:
            blocks_used = 0
            files_used = 0
            if self.shell.fs.exists(base_path):
                # This is a simplified calculation - real du would be more complex
                if self.shell.fs.is_dir(base_path):
                    for root, dirs, files in self.shell.fs.walk(base_path):
                        for f in files:
                            file_path = os.path.join(root, f)
                            size = self.shell.fs.get_size(file_path)
                            blocks_used += size // 1024  # Convert to KB blocks
                            files_used += 1
        except Exception:
            # If there's any error, use default values
            blocks_used = 5000
            files_used = 120
        
        # Simulate quota configuration
        # These would normally be read from a quota configuration file
        if target == "root" or target == "admin":
            quota = 10000000  # 10GB in KB
            limit = 12000000  # 12GB in KB
            files_quota = 1000000
            files_limit = 1200000
        else:
            quota = 5000000  # 5GB in KB
            limit = 6000000  # 6GB in KB
            files_quota = 500000
            files_limit = 600000
        
        # Simulate grace periods
        grace_block = None
        grace_file = None
        if blocks_used > quota:
            grace_block = "7days"
        if files_used > files_quota:
            grace_file = "7days"
        
        return {
            'filesystem': "/dev/sda1",
            'blocks': blocks_used,
            'quota': quota,
            'limit': limit,
            'grace_block': grace_block,
            'files': files_used,
            'files_quota': files_quota,
            'files_limit': files_limit,
            'grace_file': grace_file
        }
    
    def _format_size(self, size_bytes):
        """Format size in human-readable format"""
        for unit in ['B', 'K', 'M', 'G', 'T']:
            if size_bytes < 1024 or unit == 'T':
                if unit == 'B':
                    return f"{size_bytes}{unit}"
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024