#!/usr/bin/env python3
"""
Template Management Command-Line Interface

Provides tools for managing filesystem templates
"""

import os
import sys
import argparse
import json
import yaml
from typing import Dict, Any, Optional, List

class TemplateCLI:
    """
    Command-line interface for template management
    """
    
    def __init__(self, template_dirs: Optional[List[str]] = None):
        """
        Initialize the Template CLI
        
        Args:
            template_dirs: Optional list of directories to search for templates
        """
        # Determine template directories
        if template_dirs is None:
            # Default template locations
            home_dir = os.path.expanduser("~")
            project_template_dir = self._get_project_template_dir()
            
            self.template_dirs = [
                project_template_dir,  # Project-level templates (highest priority)
                os.path.join(home_dir, ".virtual_shell", "templates")  # User-level templates
            ]
        else:
            self.template_dirs = template_dirs
        
        # Ensure all template directories exist
        for template_dir in self.template_dirs:
            os.makedirs(template_dir, exist_ok=True)
    
    def _get_project_template_dir(self) -> str:
        """
        Get the project-level templates directory
        
        Returns:
            Path to the project-level templates directory
        """
        # Try to locate templates relative to the current module
        try:
            # Get the directory of the current module
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Go up one level to the project root
            project_root = os.path.dirname(current_dir)
            
            # Look for templates directory
            templates_dir = os.path.join(project_root, "templates")
            
            return templates_dir
        except Exception:
            # Fallback to a default location if detection fails
            return os.path.join(os.path.dirname(__file__), "..", "templates")
    
    def _find_template(self, filename: str) -> Optional[str]:
        """
        Find a template file in the configured directories
        
        Args:
            filename: Name of the template file to find
        
        Returns:
            Full path to the template file, or None if not found
        """
        for template_dir in self.template_dirs:
            full_path = os.path.join(template_dir, filename)
            if os.path.exists(full_path):
                return full_path
        return None
    
    def list_templates(self):
        """
        List all available templates from all configured directories
        """
        templates = []
        
        # Track seen filenames to avoid duplicates
        seen_filenames = set()
        
        # Collect templates from all directories
        for template_dir in self.template_dirs:
            try:
                if not os.path.exists(template_dir):
                    continue
                
                for filename in os.listdir(template_dir):
                    # Skip if already seen
                    if filename in seen_filenames:
                        continue
                    
                    # Only process YAML and JSON files
                    if filename.endswith(('.yaml', '.yml', '.json')):
                        filepath = os.path.join(template_dir, filename)
                        try:
                            # Read template metadata
                            with open(filepath, 'r') as f:
                                if filename.endswith('.json'):
                                    template_data = json.load(f)
                                else:
                                    template_data = yaml.safe_load(f)
                            
                            # Extract details
                            templates.append({
                                'filename': filename,
                                'source': template_dir,
                                'directories': len(template_data.get('directories', [])),
                                'files': len(template_data.get('files', []))
                            })
                            
                            # Mark as seen
                            seen_filenames.add(filename)
                        
                        except Exception as e:
                            print(f"Error reading template {filename}: {e}")
            except Exception as e:
                print(f"Error scanning template directory {template_dir}: {e}")
        
        # Display templates
        if not templates:
            print("No templates found.")
            return
        
        # Print templates in a formatted table
        print(f"{'Filename':<30} {'Source':<50} {'Directories':<15} {'Files':<10}")
        print("-" * 110)
        for temp in templates:
            print(f"{temp['filename']:<30} {temp['source']:<50} {temp['directories']:<15} {temp['files']:<10}")
    
    def view_template(self, filename: str):
        """
        View contents of a specific template
        
        Args:
            filename: Name of the template file to view
        """
        # Find the template file
        filepath = self._find_template(filename)
        
        # Check file exists
        if not filepath:
            print(f"Template not found: {filename}")
            return
        
        try:
            # Read and display template
            with open(filepath, 'r') as f:
                if filepath.endswith('.json'):
                    template_data = json.load(f)
                else:
                    template_data = yaml.safe_load(f)
            
            # Pretty print
            print(f"Template: {filename}")
            print(f"Source: {filepath}")
            print("\nDirectories:")
            for dir_path in template_data.get('directories', []):
                print(f"  - {dir_path}")
            
            print("\nFiles:")
            for file_info in template_data.get('files', []):
                print(f"  - Path: {file_info['path']}")
                content = file_info.get('content', '')
                preview = content[:200] + ('...' if len(content) > 200 else '')
                print("    Content Preview:")
                print(f"    {preview}")
        
        except Exception as e:
            print(f"Error viewing template: {e}")
    
    # ... (rest of the methods remain the same as in the previous implementation)

def main():
    """
    Main CLI entry point
    """
    parser = argparse.ArgumentParser(
        description="Virtual Shell Template Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Optional template directory arguments
    parser.add_argument(
        '--template-dir', 
        action='append',
        help='Additional directory to store/load templates (can be used multiple times)'
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Template operations')
    
    # Create template
    create_parser = subparsers.add_parser('create', help='Create a new template')
    create_parser.add_argument('name', help='Name of the template')
    create_parser.add_argument('--type', choices=['yaml', 'json'], default='yaml',
                                help='Template file format (default: yaml)')
    
    # List templates
    subparsers.add_parser('list', help='List all available templates')
    
    # View template
    view_parser = subparsers.add_parser('view', help='View template contents')
    view_parser.add_argument('filename', help='Name of the template to view')
    
    # Export template
    export_parser = subparsers.add_parser('export', help='Export a template')
    export_parser.add_argument('filename', help='Name of the template to export')
    export_parser.add_argument('--output', help='Destination path for the exported template')
    
    # Import template
    import_parser = subparsers.add_parser('import', help='Import a template')
    import_parser.add_argument('path', help='Path to the template file')
    import_parser.add_argument('--name', help='Optional new name for the imported template')
    
    # Delete template
    delete_parser = subparsers.add_parser('delete', help='Delete a template')
    delete_parser.add_argument('filename', help='Name of the template to delete')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Create CLI instance
    cli = TemplateCLI(args.template_dir)
    
    # Dispatch to appropriate method
    if args.command == 'create':
        cli.create_template(args.name, args.type)
    elif args.command == 'list':
        cli.list_templates()
    elif args.command == 'view':
        cli.view_template(args.filename)
    elif args.command == 'export':
        cli.export_template(args.filename, args.output)
    elif args.command == 'import':
        cli.import_template(args.path, args.name)
    elif args.command == 'delete':
        cli.delete_template(args.filename)
    else:
        # No command specified
        parser.print_help()

if __name__ == "__main__":
    main()