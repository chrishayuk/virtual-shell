# Filesystem Templates Guide

## Overview

Filesystem templates provide a powerful way to create consistent, reproducible filesystem structures with dynamic content generation.

## Template Structure

A filesystem template is a YAML or JSON document with two primary sections:

```yaml
directories:
  - directory/path/to/create
  - another/directory/path

files:
  - path: path/to/file
    content: File content goes here
```

## Template Components

### Directories

The `directories` section lists paths to create:

```yaml
directories:
  - /home/user/project
  - /home/user/project/src
  - /home/user/project/tests
```

### Files

The `files` section defines files to create:

```yaml
files:
  - path: /home/user/project/README.md
    content: |
      # My Project
      Project description goes here.
  
  - path: /home/user/project/main.py
    content: |
      def main():
          print("Hello, World!")
```

## Variable Substitution

Use `${variable_name}` for dynamic content:

```yaml
files:
  - path: /home/${project_name}/README.md
    content: |
      # ${project_name}
      
      Description: ${project_description}
      Version: ${version}
```

Apply with variables:
```bash
fs-cli template apply template.yaml \
  --var project_name myproject \
  --var project_description "An awesome project" \
  --var version "1.0.0"
```

## Template Creation Strategies

### Interactive Creation
```bash
fs-cli template create my_template
```

### Manual Creation
Create a YAML or JSON file manually:

```yaml
# my_template.yaml
directories:
  - /home/project
  - /home/project/src
  - /home/project/tests

files:
  - path: /home/project/README.md
    content: |
      # ${project_name}
      ${project_description}
```

## Advanced Features

### Conditional Content
Use shell-like variable substitution for complex scenarios:

```yaml
files:
  - path: /home/project/config.json
    content: |
      {
        "debug": ${enable_debug},
        "logging": ${logging_level}
      }
```

### File Content from External Sources

```yaml
files:
  - path: /home/project/LICENSE
    content_from: /path/to/license/template
```

## Best Practices

1. Use descriptive, meaningful path names
2. Keep templates modular and reusable
3. Use variables for dynamic content
4. Include comments for clarity
5. Test templates thoroughly

## Common Use Cases

- Project scaffolding
- Development environment setup
- Consistent file structure generation
- Reproducible filesystem layouts

## Error Handling

- Verify template syntax
- Check variable substitution
- Handle missing variables gracefully

## Security Considerations

- Avoid hardcoding sensitive information
- Use environment variables or secure vaults
- Validate template sources

## Example Complex Template

```yaml
# web_app_template.yaml
directories:
  - /home/${project_name}
  - /home/${project_name}/src
  - /home/${project_name}/tests
  - /home/${project_name}/docs
  - /home/${project_name}/scripts

files:
  - path: /home/${project_name}/README.md
    content: |
      # ${project_name}
      
      ## Overview
      ${project_description}
      
      ## Setup
      ```bash
      python -m venv venv
      source venv/bin/activate
      pip install -r requirements.txt
      ```

  - path: /home/${project_name}/requirements.txt
    content: |
      # Core dependencies
      flask==${flask_version}
      sqlalchemy==${sqlalchemy_version}
      
      # Development dependencies
      pytest
      mypy
```

## CLI Usage Examples

```bash
# Create a template interactively
fs-cli template create web_app_template

# Apply a template
fs-cli template apply web_app_template.yaml \
  --var project_name mywebapp \
  --var project_description "A Flask web application" \
  --var flask_version "2.0.1" \
  --var sqlalchemy_version "1.4.22"

# List available templates in a directory
fs-cli template load-directory /path/to/templates
```

## Troubleshooting

- Verify YAML/JSON syntax
- Check variable names match exactly
- Ensure all required variables are provided
- Use `--dry-run` for validation (if supported)

## Future Improvements

- Template versioning
- More advanced variable interpolation
- Template composition
- Validation mechanismss