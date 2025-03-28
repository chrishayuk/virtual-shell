"""
chuk_virtual_shell/shell_interpreter.py - Core shell interpreter for PyodideShell
"""
# Import necessary modules
from chuk_virtual_fs import VirtualFileSystem
from chuk_virtual_shell.commands.command_loader import CommandLoader

class ShellInterpreter:
    def __init__(self, fs_provider=None, fs_provider_args=None, sandbox_yaml=None):
        """
        Initialize the shell interpreter
        
        Args:
            fs_provider: Optional filesystem provider name
            fs_provider_args: Optional arguments for the filesystem provider
            sandbox_yaml: Optional path to sandbox YAML configuration
        """
        # Initialize filesystem
        if sandbox_yaml:
            # Use sandbox YAML configuration
            from chuk_virtual_shell.sandbox_loader import load_sandbox_config, create_filesystem_from_config
            from chuk_virtual_shell.sandbox_loader import get_environment_from_config, find_sandbox_config
            
            try:
                # Handle sandbox name (find configuration file) or direct path
                if not sandbox_yaml.endswith(('.yaml', '.yml')) and '/' not in sandbox_yaml:
                    config_path = find_sandbox_config(sandbox_yaml)
                    if not config_path:
                        raise ValueError(f"Sandbox configuration '{sandbox_yaml}' not found")
                else:
                    config_path = sandbox_yaml
                
                # Load and apply configuration
                config = load_sandbox_config(config_path)
                
                # Create filesystem with configuration
                try:
                    self.fs = create_filesystem_from_config(config)
                except Exception as fs_error:
                    print(f"Error creating filesystem: {fs_error}")
                    import traceback
                    traceback.print_exc()
                    # Fallback to default filesystem
                    self.fs = VirtualFileSystem()
                
                # Set environment variables from configuration
                # Use get with a default dict to ensure we always have a dictionary
                env_config = config.get('environment', {})
                
                # Ensure critical environment variables are set with sensible defaults
                self.environ = {
                    "HOME": env_config.get('HOME', '/sandbox'),
                    "PATH": env_config.get('PATH', '/bin'),
                    "USER": env_config.get('USER', 'ai'),
                    "SHELL": env_config.get('SHELL', '/bin/pyodide-shell'),
                    "TERM": env_config.get('TERM', 'xterm'),
                    "PWD": "/"  # Start at root
                }
                
                # Add any additional environment variables from the config
                for key, value in env_config.items():
                    if key not in self.environ:
                        self.environ[key] = value
                
                # Get home directory
                home_dir = self.environ['HOME']
                
                # Attempt to create home directory with improved error handling
                try:
                    # Resolve the home directory path first
                    resolved_home_dir = self.fs.resolve_path(home_dir)
                    
                    # Check if directory exists, create if not
                    existing_node = self.fs.get_node_info(resolved_home_dir)
                    if not existing_node:
                        # Attempt to create directory
                        create_result = self.fs.mkdir(resolved_home_dir)
                        if not create_result:
                            print(f"Warning: Could not create home directory {resolved_home_dir}")
                    elif not existing_node.is_dir:
                        print(f"Warning: Home path {resolved_home_dir} exists but is not a directory")
                except Exception as mkdir_error:
                    print(f"Error processing home directory {home_dir}: {mkdir_error}")
                
                # Attempt to change to home directory
                try:
                    if not self.fs.cd(home_dir):
                        print(f"Warning: Could not change to home directory {home_dir}")
                except Exception as cd_error:
                    print(f"Error changing to home directory {home_dir}: {cd_error}")
                
                print(f"Using sandbox configuration: {config.get('name', 'custom')}")
                print(f"Home directory set to: {home_dir}")
                print("Environment variables:")
                for key, value in self.environ.items():
                    print(f"  {key}: {value}")
            except Exception as e:
                print(f"Error loading sandbox configuration '{sandbox_yaml}': {e}")
                import traceback
                traceback.print_exc()
                print("Falling back to default configuration.")
                self.fs = VirtualFileSystem()
                self._setup_default_environment()
        elif fs_provider:
            # Use specified provider
            try:
                self.fs = VirtualFileSystem(fs_provider, **(fs_provider_args or {}))
                self._setup_default_environment()
            except Exception as e:
                print(f"Error initializing filesystem provider '{fs_provider}': {e}")
                print("Falling back to memory provider.")
                self.fs = VirtualFileSystem()  # Fallback to memory provider
                self._setup_default_environment()
        else:
            # Use default provider
            self.fs = VirtualFileSystem()
            self._setup_default_environment()
        
        # Command history
        self.history = []
        
        # Shell is running
        self.running = True
        
        # Last command return code
        self.return_code = 0
        
        # Register commands - using command loader for dynamic discovery
        self.commands = {}
        self._load_commands()

    def _setup_default_environment(self):
        """Set up default environment variables and directories"""
        # Create user home directory
        default_home = "/home/user"
        
        try:
            # Attempt to create home directory if possible
            resolved_home_dir = self.fs.resolve_path(default_home)
            
            # Check if directory exists, create if not
            existing_node = self.fs.get_node_info(resolved_home_dir)
            if not existing_node:
                # Attempt to create directory
                create_result = self.fs.mkdir(resolved_home_dir)
                if not create_result:
                    print(f"Warning: Could not create home directory {resolved_home_dir}")
            elif not existing_node.is_dir:
                print(f"Warning: Home path {resolved_home_dir} exists but is not a directory")
        except Exception as mkdir_error:
            print(f"Error processing home directory {default_home}: {mkdir_error}")
        
        # Set up environment
        self.environ = {
            "HOME": default_home,
            "PATH": "/bin:/usr/bin",
            "USER": "user",
            "SHELL": "/bin/pyodide-shell",
            "PWD": "/",
            "TERM": "xterm",
        }

    def _load_commands(self):
        """Dynamically load all available commands"""
        # Use the command loader to discover commands
        discovered_commands = CommandLoader.discover_commands(self)
        
        # Register all discovered commands
        self.commands.update(discovered_commands)
        
        # Optionally, load commands from external paths
        # This could be used to load user-defined commands
        # external_commands = CommandLoader.load_commands_from_path(self, "path/to/user/commands")
        # self.commands.update(external_commands)
    
    def _register_command(self, command):
        """Register a single command with the shell"""
        self.commands[command.name] = command
    
    def parse_command(self, cmd_line):
        """Parse a command line into command and arguments"""
        if not cmd_line or not cmd_line.strip():
            return None, []
            
        parts = cmd_line.strip().split()
        cmd = parts[0]
        args = parts[1:]
        return cmd, args
    
    def execute(self, cmd_line):
        """Execute a command line"""
        # Skip empty commands
        cmd_line = cmd_line.strip()
        if not cmd_line:
            return None
            
        # Add to history
        self.history.append(cmd_line)
        
        # Handle exit command specially (in case it's not registered)
        if cmd_line == "exit":
            self.running = False
            return "Goodbye!"
            
        # Parse the command
        cmd, args = self.parse_command(cmd_line)
        
        if not cmd:
            return ""
            
        # Execute the command
        if cmd in self.commands:
            try:
                result = self.commands[cmd].execute(args)
                
                # Update PWD if directory changed
                if cmd == "cd":
                    self.environ["PWD"] = self.fs.pwd()
                    
                return result
            except Exception as e:
                return f"Error executing command: {e}"
        else:
            return f"{cmd}: command not found"
    
    def prompt(self):
        """Return the command prompt"""
        # Basic prompt with current directory
        username = self.environ.get("USER", "user")
        hostname = "pyodide"
        pwd = self.environ.get("PWD", "/")
        
        # Format the prompt according to expected test format
        return f"{username}@{hostname}:{pwd}$ "
    
    def complete(self, text, state):
        """Tab completion for shell commands and paths"""
        # Implement tab completion here
        # This is just a stub for now
        return None