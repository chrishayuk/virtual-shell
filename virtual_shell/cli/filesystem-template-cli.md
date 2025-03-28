# Templates CLI Guide

## Overview

The `filesystem-template-cli` is a command-line tool for managing filesystem templates in the Virtual Shell environment. It provides an intuitive interface for creating, listing, viewing, exporting, importing, and deleting templates.

## Installation

Templates CLI is installed automatically with the Virtual Shell package:

```bash
pip install virtual-shell
```

## Basic Usage

### Create a Template

Interactively create a new template:

```bash
# Create a YAML template (default)
filesystem-template-cli create my_project_template

# Create a JSON template
filesystem-template-cli create my_project_template --type json
```

Interactive Prompts:
1. Enter directories (one per line)
2. Enter files with their paths and contents

### List Templates

View all available templates:

```bash
filesystem-template-cli list
```

Example output:
```
Filename                        Directories   Files
-----------------------------------------------
web_project.yaml                3            5
python_app.json                 2            3
```

### View Template Details

Inspect a specific template:

```bash
filesystem-template-cli view web_project.yaml
```

### Export a Template

Export a template to a different location:

```bash
# Export to current directory
filesystem-template-cli export web_project.yaml

# Export to a specific path
filesystem-template-cli export web_project.yaml --output /path/to/backup/
```

### Import a Template

Import a template from an external file:

```bash
# Import from a file
filesystem-template-cli import /path/to/external/template.yaml

# Import with a custom name
filesystem-template-cli import /path/to/external/template.yaml --name custom_template
```

### Delete a Template

Remove an unwanted template:

```bash
filesystem-template-cli delete web_project.yaml
```

## Template Structure

Templates support two formats: YAML and JSON

### YAML Example

```yaml
directories:
  - /home/project
  - /home/project/src
  - /home/project/tests

files:
  - path: /home/project/README.md
    content: |
      # My Project
      Project description
  
  - path: /home/project/main.py
    content: |
      def main():
          print("Hello, World!")
```

### JSON Example

```json
{
    "directories": [
        "/home/project",
        "/home/project/src"
    ],
    "files": [
        {
            "path": "/home/project/README.md",
            "content": "# My Project\nProject description"
        }
    ]
}
```

## Advanced Features

### Variable Substitution

Templates support dynamic variable substitution:

```yaml
directories:
  - /home/${project_name}
  - /home/${project_name}/src

files:
  - path: /home/${project_name}/README.md
    content: |
      # ${project_name}
      Description: ${project_description}
```

### Custom Template Directory

By default, templates are stored in `~/.virtual_shell/templates`. You can specify a custom directory:

```bash
filesystem-template-cli --template-dir /path/to/templates list
```

## Best Practices

1. Use descriptive template names
2. Keep templates modular and reusable
3. Use variable substitution for flexibility
4. Organize templates by project type or purpose

## Troubleshooting

- Ensure you have read/write permissions in the template directory
- Verify template file formats (YAML or JSON)
- Check for syntax errors in template files

## Security Considerations

- Templates may contain sensitive file contents
- Protect template files from unauthorized access
- Be cautious when importing templates from unknown sources

## Limitations

- Templates are specific to the Virtual Shell environment
- Cannot directly apply templates to external filesystems
- Limited to directory and file creation

## Common Errors

- "Template not found": Verify the filename
- "Invalid template format": Check YAML/JSON syntax
- Permission errors: Check directory and file permissions

## Future Improvements

- Template versioning
- More advanced variable interpolation
- Template composition
- Template validation

## Support

For issues or feature requests, please file an issue on the project's GitHub repository.