#!/usr/bin/env python3
"""
Snapshot Management Command-Line Interface

Provides tools for managing filesystem snapshots
"""

import argparse
import json
import os
import sys
from typing import Dict, Any, Optional

class SnapshotCLI:
    """
    Command-line interface for snapshot management
    """
    
    def __init__(self, snapshot_dir: Optional[str] = None):
        """
        Initialize the Snapshot CLI
        
        Args:
            snapshot_dir: Directory to store/load snapshots (defaults to ~/.chuk_virtual_shell/snapshots)
        """
        # Determine snapshot directory
        if snapshot_dir is None:
            home_dir = os.path.expanduser("~")
            self.snapshot_dir = os.path.join(home_dir, ".chuk_virtual_shell", "snapshots")
        else:
            self.snapshot_dir = snapshot_dir
        
        # Ensure snapshot directory exists
        os.makedirs(self.snapshot_dir, exist_ok=True)
    
    def list_snapshots(self):
        """
        List all available snapshots in the snapshot directory
        """
        snapshots = []
        
        # Find all JSON files in the snapshot directory
        for filename in os.listdir(self.snapshot_dir):
            if filename.endswith(".snapshot.json"):
                try:
                    # Read snapshot metadata
                    with open(os.path.join(self.snapshot_dir, filename), 'r') as f:
                        snapshot_data = json.load(f)
                    
                    # Extract key metadata
                    metadata = snapshot_data.get('metadata', {})
                    snapshots.append({
                        'filename': filename,
                        'name': metadata.get('name', 'Unnamed Snapshot'),
                        'created': metadata.get('created', 'Unknown'),
                        'description': metadata.get('description', 'No description')
                    })
                except Exception as e:
                    print(f"Error reading snapshot {filename}: {e}")
        
        # Display snapshots
        if not snapshots:
            print("No snapshots found.")
            return
        
        # Print snapshots in a formatted table
        print(f"{'Filename':<30} {'Name':<20} {'Created':<20} Description")
        print("-" * 80)
        for snap in snapshots:
            print(f"{snap['filename']:<30} {snap['name']:<20} {snap['created']:<20} {snap['description']}")
    
    def export_snapshot(self, filename: str, output_path: Optional[str] = None):
        """
        Export a specific snapshot to a new location
        
        Args:
            filename: Name of the snapshot file to export
            output_path: Destination path (defaults to current directory)
        """
        # Validate snapshot exists
        input_path = os.path.join(self.snapshot_dir, filename)
        if not os.path.exists(input_path):
            print(f"Snapshot not found: {filename}")
            return
        
        # Determine output path
        if output_path is None:
            output_path = os.path.join(os.getcwd(), filename)
        
        try:
            # Copy the snapshot file
            import shutil
            shutil.copy2(input_path, output_path)
            print(f"Snapshot exported to: {output_path}")
        except Exception as e:
            print(f"Error exporting snapshot: {e}")
    
    def import_snapshot(self, snapshot_path: str, new_name: Optional[str] = None):
        """
        Import a snapshot from an external location
        
        Args:
            snapshot_path: Path to the snapshot file
            new_name: Optional new name for the snapshot
        """
        # Validate input file exists
        if not os.path.exists(snapshot_path):
            print(f"Snapshot file not found: {snapshot_path}")
            return
        
        try:
            # Read snapshot data to validate
            with open(snapshot_path, 'r') as f:
                snapshot_data = json.load(f)
            
            # Determine filename
            if new_name:
                # Use provided name with standard extension
                filename = f"{new_name}.snapshot.json"
            else:
                # Use original filename or generate one
                filename = os.path.basename(snapshot_path)
                if not filename.endswith(".snapshot.json"):
                    filename = f"{filename}.snapshot.json"
            
            # Copy to snapshots directory
            destination = os.path.join(self.snapshot_dir, filename)
            
            # Ensure unique filename
            counter = 1
            while os.path.exists(destination):
                base, ext = os.path.splitext(filename)
                destination = os.path.join(
                    self.snapshot_dir, 
                    f"{base}_{counter}{ext}"
                )
                counter += 1
            
            # Copy the file
            import shutil
            shutil.copy2(snapshot_path, destination)
            
            print(f"Snapshot imported: {destination}")
        
        except json.JSONDecodeError:
            print("Invalid snapshot file: Not a valid JSON format")
        except Exception as e:
            print(f"Error importing snapshot: {e}")
    
    def delete_snapshot(self, filename: str):
        """
        Delete a specific snapshot
        
        Args:
            filename: Name of the snapshot file to delete
        """
        # Construct full path
        snapshot_path = os.path.join(self.snapshot_dir, filename)
        
        # Check if file exists
        if not os.path.exists(snapshot_path):
            print(f"Snapshot not found: {filename}")
            return
        
        try:
            # Delete the file
            os.remove(snapshot_path)
            print(f"Snapshot deleted: {filename}")
        except Exception as e:
            print(f"Error deleting snapshot: {e}")

def main():
    """
    Main CLI entry point
    """
    parser = argparse.ArgumentParser(
        description="Virtual Shell Snapshot Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Optional snapshot directory argument
    parser.add_argument(
        '--snapshot-dir', 
        help='Directory to store/load snapshots'
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Snapshot operations')
    
    # List snapshots
    subparsers.add_parser('list', help='List all available snapshots')
    
    # Export snapshot
    export_parser = subparsers.add_parser('export', help='Export a snapshot')
    export_parser.add_argument('filename', help='Name of the snapshot to export')
    export_parser.add_argument('--output', help='Destination path for the exported snapshot')
    
    # Import snapshot
    import_parser = subparsers.add_parser('import', help='Import a snapshot')
    import_parser.add_argument('path', help='Path to the snapshot file')
    import_parser.add_argument('--name', help='Optional new name for the imported snapshot')
    
    # Delete snapshot
    delete_parser = subparsers.add_parser('delete', help='Delete a snapshot')
    delete_parser.add_argument('filename', help='Name of the snapshot to delete')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Create CLI instance
    cli = SnapshotCLI(args.snapshot_dir)
    
    # Dispatch to appropriate method
    if args.command == 'list':
        cli.list_snapshots()
    elif args.command == 'export':
        cli.export_snapshot(args.filename, args.output)
    elif args.command == 'import':
        cli.import_snapshot(args.path, args.name)
    elif args.command == 'delete':
        cli.delete_snapshot(args.filename)
    else:
        # No command specified
        parser.print_help()

if __name__ == "__main__":
    main()