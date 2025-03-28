# chuk_virtual_shell/commands/filesystem/du.py
import argparse
import os
from chuk_virtual_shell.commands.command_base import ShellCommand

class DuCommand(ShellCommand):
    name = "du"
    help_text = (
        "du - Display disk usage statistics\n"
        "Usage: du [-h] [-s] [path ...]\n"
        "Options:\n"
        "  -h, --human-readable  Print sizes in human readable format (e.g., 1K, 234M)\n"
        "  -s, --summarize       Display only a total for each argument\n"
        "If no path is provided, the current directory is used."
    )
    category = "filesystem"
    
    def execute(self, args):
        parser = argparse.ArgumentParser(prog=self.name, add_help=False)
        parser.add_argument('-h', '--human-readable', action='store_true', help='Print sizes in human readable format')
        parser.add_argument('-s', '--summarize', action='store_true', help='Display only a total for each argument')
        parser.add_argument('paths', nargs='*', default=['.'], help='Paths to analyze')
        
        try:
            parsed_args = parser.parse_args(args)
        except SystemExit:
            return self.get_help()
        
        results = []
        
        for path in parsed_args.paths:
            # Resolve the path within the virtual filesystem
            abs_path = self.shell.resolve_path(path)
            
            if not self.shell.fs.exists(abs_path):
                results.append(f"du: cannot access '{path}': No such file or directory")
                continue
            
            # Get directory size
            total_size = self._get_size(abs_path, parsed_args.summarize)
            
            # Format the output
            if parsed_args.human_readable:
                formatted_size = self._format_size(total_size)
            else:
                # Traditional du reports size in KB blocks
                formatted_size = str(total_size // 1024)
            
            results.append(f"{formatted_size}\t{path}")
        
        return "\n".join(results)
    
    def _get_size(self, path, summarize=False):
        """Calculate the size of a directory or file"""
        if self.shell.fs.is_file(path):
            return self.shell.fs.get_size(path)
        
        total = 0
        # For directories, recursively calculate size
        for item in self.shell.fs.list_dir(path):
            item_path = os.path.join(path, item)
            if self.shell.fs.is_dir(item_path) and not summarize:
                item_size = self._get_size(item_path)
                total += item_size
                # In non-summarize mode, we would print this subdirectory too
            else:
                total += self.shell.fs.get_size(item_path)
        
        return total
    
    def _format_size(self, size_bytes):
        """Format size in human-readable format"""
        for unit in ['B', 'K', 'M', 'G', 'T']:
            if size_bytes < 1024 or unit == 'T':
                if unit == 'B':
                    return f"{size_bytes}{unit}"
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024

