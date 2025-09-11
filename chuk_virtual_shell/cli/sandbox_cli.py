#!/usr/bin/env python3
"""
Sandbox Configuration Management CLI

Provides tools for creating, managing, and running sandbox configurations
"""

import os
import argparse
import json
import yaml  # type: ignore
from typing import Optional, Dict, Any, List

from chuk_virtual_shell.sandbox.loader import (
    load_sandbox_config,
    find_sandbox_config,
    list_available_configs,
    create_filesystem_from_config,
    get_environment_from_config,
)
from chuk_virtual_shell.shell_interpreter import ShellInterpreter


class SandboxCLI:
    """
    Command-line interface for sandbox configuration management
    """

    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize the Sandbox CLI

        Args:
            config_dir: Optional directory to store/load sandbox configurations
        """
        # Determine configuration directory
        if config_dir is None:
            home_dir = os.path.expanduser("~")
            self.config_dir = os.path.join(home_dir, ".chuk_virtual_shell", "sandboxes")
        else:
            self.config_dir = config_dir

        # Ensure configuration directory exists
        os.makedirs(self.config_dir, exist_ok=True)

    def create_sandbox_config(self, name: str, config_type: str = "yaml"):
        """
        Interactively create a new sandbox configuration

        Args:
            name: Name of the sandbox configuration
            config_type: Output format (yaml or json)
        """
        # Initialize configuration dictionary
        config: Dict[str, Any] = {
            "name": name,
            "description": "",
            "filesystem": {"provider": "memory"},
            "security": {},
            "environment": {},
            "initialization": [],
        }

        # Filesystem provider selection
        print("\nSelect Filesystem Provider:")
        providers: List[str] = ["memory", "sqlite", "s3"]
        for i, provider in enumerate(providers, 1):
            print(f"{i}. {provider}")

        provider_choice = input("Enter provider number (default: memory): ").strip()
        if provider_choice:
            try:
                config["filesystem"]["provider"] = providers[int(provider_choice) - 1]
            except (ValueError, IndexError):
                print("Invalid choice. Using default (memory).")

        # Provider-specific arguments
        if config["filesystem"]["provider"] == "sqlite":
            db_path = input("Enter SQLite database path (default: :memory:): ").strip()
            config["filesystem"]["provider_args"] = {
                "db_path": db_path if db_path else ":memory:"
            }
        elif config["filesystem"]["provider"] == "s3":
            bucket_name = input("Enter S3 bucket name: ").strip()
            region_name = input("Enter AWS region (optional): ").strip()

            config["filesystem"]["provider_args"] = {"bucket_name": bucket_name}
            if region_name:
                config["filesystem"]["provider_args"]["region_name"] = region_name

        # Description
        config["description"] = input("Enter sandbox description: ").strip()

        # Security profile
        security_profile = input("Enter security profile (default: none): ").strip()
        if security_profile:
            config["security"]["profile"] = security_profile

        # Environment variables
        print("\nAdd environment variables (key=value, empty line to finish):")
        while True:
            env_input = input("Environment variable (key=value): ").strip()
            if not env_input:
                break

            try:
                key, value = env_input.split("=", 1)
                config["environment"][key.strip()] = value.strip()
            except ValueError:
                print("Invalid format. Use key=value")

        # Initialization commands
        print("\nAdd initialization commands (empty line to finish):")
        while True:
            cmd = input("Initialization command: ").strip()
            if not cmd:
                break
            config["initialization"].append(cmd)

        # Determine output filename
        if not name.endswith(f".{config_type}"):
            filename = f"{name}.{config_type}"
        else:
            filename = name

        # Full path
        full_path = os.path.join(self.config_dir, filename)

        try:
            # Write configuration
            with open(full_path, "w") as f:
                if config_type == "yaml":
                    yaml.safe_dump(config, f)
                else:
                    json.dump(config, f, indent=2)

            print(f"Sandbox configuration saved to: {full_path}")
        except Exception as e:
            print(f"Error saving configuration: {e}")

    def list_sandboxes(self):
        """List all available sandbox configurations"""
        # Find sandbox configurations
        configs = list_available_configs()

        if not configs:
            print("No sandbox configurations found.")
            return

        print("Available Sandbox Configurations:")
        for config_name in configs:
            try:
                # Try to find the full configuration path
                config_path = find_sandbox_config(config_name)
                if config_path:
                    print(f"- {config_name} (Path: {config_path})")
            except Exception:
                print(f"- {config_name}")

    def view_sandbox(self, name: str):
        """
        View details of a specific sandbox configuration

        Args:
            name: Name of the sandbox configuration
        """
        # Find the configuration file
        config_path = find_sandbox_config(name)

        if not config_path:
            print(f"Sandbox configuration not found: {name}")
            return

        try:
            # Load the configuration
            config = load_sandbox_config(config_path)

            # Pretty print configuration
            print(f"Sandbox Configuration: {name}")
            print(f"Path: {config_path}")
            print("\nDetails:")

            # Print filesystem details
            print("\nFilesystem:")
            print(f"  Provider: {config.get('filesystem', {}).get('provider', 'N/A')}")

            # Print security details
            print("\nSecurity:")
            security_config = config.get("security", {})
            for key, value in security_config.items():
                print(f"  {key}: {value}")

            # Print environment variables
            print("\nEnvironment Variables:")
            env_vars = config.get("environment", {})
            for key, value in env_vars.items():
                print(f"  {key}={value}")

            # Print initialization commands
            print("\nInitialization Commands:")
            for cmd in config.get("initialization", []):
                print(f"  {cmd}")

        except Exception as e:
            print(f"Error reading sandbox configuration: {e}")

    def run_sandbox(self, name: str):
        """
        Run a sandbox configuration

        Args:
            name: Name of the sandbox configuration
        """
        # Find the configuration file
        config_path = find_sandbox_config(name)

        if not config_path:
            print(f"Sandbox configuration not found: {name}")
            return

        try:
            # Load the configuration
            config = load_sandbox_config(config_path)

            # Create filesystem from configuration
            fs = create_filesystem_from_config(config)

            # Get environment variables
            env_vars = get_environment_from_config(config)

            # Create shell interpreter with the configured filesystem
            ShellInterpreter(fs)

            # Set environment variables
            for key, value in env_vars.items():
                os.environ[key] = value

            # Start interactive shell
            print(f"Starting sandbox: {name}")
            # TODO: Implement run_interactive method
            # shell.run_interactive()

        except Exception as e:
            print(f"Error running sandbox: {e}")

    def delete_sandbox(self, name: str):
        """
        Delete a sandbox configuration

        Args:
            name: Name of the sandbox configuration
        """
        # Find the configuration file
        config_path = find_sandbox_config(name)

        if not config_path:
            print(f"Sandbox configuration not found: {name}")
            return

        try:
            # Confirm deletion
            confirm = (
                input(
                    f"Are you sure you want to delete sandbox configuration '{name}'? (y/N): "
                )
                .strip()
                .lower()
            )

            if confirm == "y":
                os.remove(config_path)
                print(f"Sandbox configuration deleted: {name}")
            else:
                print("Deletion cancelled.")

        except Exception as e:
            print(f"Error deleting sandbox configuration: {e}")


def main():
    """
    Main CLI entry point
    """
    parser = argparse.ArgumentParser(
        description="Virtual Shell Sandbox Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Optional sandbox directory argument
    parser.add_argument(
        "--sandbox-dir", help="Directory to store/load sandbox configurations"
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Sandbox operations")

    # Create sandbox
    create_parser = subparsers.add_parser(
        "create", help="Create a new sandbox configuration"
    )
    create_parser.add_argument("name", help="Name of the sandbox configuration")
    create_parser.add_argument(
        "--type",
        choices=["yaml", "json"],
        default="yaml",
        help="Configuration file format (default: yaml)",
    )

    # List sandboxes
    subparsers.add_parser("list", help="List available sandbox configurations")

    # View sandbox
    view_parser = subparsers.add_parser(
        "view", help="View sandbox configuration details"
    )
    view_parser.add_argument("name", help="Name of the sandbox configuration to view")

    # Run sandbox
    run_parser = subparsers.add_parser("run", help="Run a sandbox configuration")
    run_parser.add_argument("name", help="Name of the sandbox configuration to run")

    # Delete sandbox
    delete_parser = subparsers.add_parser(
        "delete", help="Delete a sandbox configuration"
    )
    delete_parser.add_argument(
        "name", help="Name of the sandbox configuration to delete"
    )

    # Parse arguments
    args = parser.parse_args()

    # Create CLI instance
    cli = SandboxCLI(args.sandbox_dir)

    # Dispatch to appropriate method
    if args.command == "create":
        cli.create_sandbox_config(args.name, args.type)
    elif args.command == "list":
        cli.list_sandboxes()
    elif args.command == "view":
        cli.view_sandbox(args.name)
    elif args.command == "run":
        cli.run_sandbox(args.name)
    elif args.command == "delete":
        cli.delete_sandbox(args.name)
    else:
        # No command specified
        parser.print_help()


if __name__ == "__main__":
    main()
