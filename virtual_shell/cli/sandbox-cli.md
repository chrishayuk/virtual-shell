# Sandbox CLI Guide

## Overview

The Sandbox CLI provides a comprehensive tool for managing and running isolated virtual shell environments.

## Installation

Sandbox CLI is installed automatically with the Virtual Shell package:

```bash
pip install virtual-shell
```

## Basic Usage

### Create a Sandbox Configuration

Interactively create a new sandbox configuration:

```bash
# Create a YAML sandbox configuration
sandbox-cli create my_project_sandbox

# Create a JSON sandbox configuration
sandbox-cli create my_project_sandbox --type json
```

Interactive Prompts:
1. Select filesystem provider (memory, SQLite, S3)
2. Enter provider-specific arguments
3. Add description
4. Set security profile
5. Define environment variables
6. Add initialization commands

### List Available Sandboxes

View all configured sandboxes:

```bash
sandbox-cli list
```

### View Sandbox Details

Inspect a specific sandbox configuration:

```bash
sandbox-cli view my_project_sandbox
```

### Run a Sandbox

Start an interactive shell with a specific sandbox configuration:

```bash
sandbox-cli run my_project_sandbox
```

### Delete a Sandbox Configuration

Remove an unwanted sandbox configuration:

```bash
sandbox-cli delete my_project_sandbox
```

## Sandbox Configuration Structure

A sandbox configuration is a YAML or JSON file with the following structure:

```yaml
name: my_project_sandbox
description: Development environment for my project
filesystem:
  provider: memory  # or sqlite, s3
  provider_args:
    db_path: ":memory:"  # for SQLite
environment:
  PYTHONPATH: /home/project/src
  DEBUG: "true"
security:
  profile: default
initialization:
  - mkdir -p /home/project
  - echo "Project setup complete" > /home/project/README.txt
```

### Configuration Options

#### Filesystem Providers
- **memory**: In-memory storage (default)
- **sqlite**: Persistent storage using SQLite
- **s3**: Cloud storage with AWS S3

#### Environment Variables
- Set custom environment variables for the sandbox
- Accessible within the shell environment

#### Security Profiles
- Apply predefined security settings
- Restrict filesystem access
- Control file operations

#### Initialization Commands
- Run shell commands during sandbox setup
- Create directories
- Write initial files
- Perform setup tasks

## Advanced Usage

### Specifying a Custom Sandbox Directory

```bash
# Use a custom directory for sandbox configurations
sandbox-cli --sandbox-dir /path/to/sandboxes list
```

## Security Considerations

- Sandbox configurations may contain sensitive information
- Protect configuration files
- Use appropriate file permissions
- Be cautious when sharing sandbox configurations

## Troubleshooting

- Verify filesystem provider availability
- Check configuration file syntax
- Ensure required dependencies are installed

## Limitations

- Sandboxes are isolated to the virtual filesystem
- Some advanced system interactions may be restricted

## Examples

### Development Environment Sandbox

```yaml
name: python_dev
description: Python development environment
filesystem:
  provider: sqlite
  provider_args:
    db_path: /home/projects/dev_projects.db
environment:
  PYTHON_ENV: development
  VIRTUAL_ENV: /home/venvs/dev_project
security:
  profile: development
initialization:
  - python3 -m venv /home/venvs/dev_project
  - pip install -r /home/projects/requirements.txt
```

### Data Science Sandbox

```yaml
name: data_science
description: Data analysis workspace
filesystem:
  provider: memory
environment:
  JUPYTER_PORT: "8888"
security:
  profile: restricted
initialization:
  - mkdir -p /home/notebooks
  - mkdir -p /home/data
```

## Contributing

- Report issues with sandbox functionality
- Suggest improvements
- Help develop new features

## Support

For additional support, consult the project documentation or file an issue on the GitHub repository.