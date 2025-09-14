"""
chuk_virtual_shell/commands/filesystem/touch.py - Create empty file command
"""

from chuk_virtual_shell.commands.command_base import ShellCommand


class TouchCommand(ShellCommand):
    name = "touch"
    help_text = """touch - Create empty files or update timestamps
Usage: touch [OPTION]... FILE...
Options:
  -a        Change only the access time
  -c        Do not create any files
  -m        Change only the modification time
  -t TIME   Use specified time instead of current time
  --help    Display this help and exit"""
    category = "file"

    def execute(self, args):
        if not args:
            return "touch: missing file operand"

        # Parse options
        no_create = False
        access_only = False
        modify_only = False
        custom_time = None
        
        files = []
        i = 0
        while i < len(args):
            arg = args[i]
            if arg.startswith("-") and arg != "-":
                if arg == "--help":
                    return self.help_text
                elif arg == "-c":
                    no_create = True
                elif arg == "-a":
                    access_only = True
                elif arg == "-m":
                    modify_only = True
                elif arg == "-t":
                    # Next argument should be the time
                    if i + 1 < len(args):
                        i += 1
                        custom_time = args[i]
                    else:
                        return "touch: option requires an argument -- 't'"
                elif arg == "--":
                    files.extend(args[i+1:])
                    break
                else:
                    # Check for combined flags
                    for flag in arg[1:]:
                        if flag == 'c':
                            no_create = True
                        elif flag == 'a':
                            access_only = True
                        elif flag == 'm':
                            modify_only = True
                        else:
                            return f"touch: invalid option -- '{flag}'"
            else:
                files.append(arg)
            i += 1

        if not files:
            return "touch: missing file operand"

        errors = []
        for path in files:
            # Check if file exists
            exists = self.shell.fs.exists(path)
            
            if exists:
                # File exists - update timestamp (in virtual filesystem, this is usually a no-op)
                # In a real implementation, we would update access/modification times
                if self.shell.fs.is_dir(path):
                    # touch works on directories too in Unix
                    pass
                else:
                    # Update file timestamp (read and rewrite to simulate)
                    if hasattr(self.shell.fs, 'update_timestamp'):
                        self.shell.fs.update_timestamp(path)
                    else:
                        # Simulate timestamp update by reading and rewriting
                        content = self.shell.fs.read_file(path)
                        if content is not None:
                            self.shell.fs.write_file(path, content)
            else:
                # File doesn't exist
                if no_create:
                    # Don't create if -c flag is set
                    continue
                    
                # Create empty file
                if not self.shell.fs.touch(path):
                    # Try alternative method
                    if not self.shell.fs.write_file(path, ""):
                        errors.append(f"touch: cannot touch '{path}': Permission denied")

        return "\n".join(errors) if errors else ""
