# Snapshots CLI Guide

## Overview

The `snapshot-cli` is a command-line tool for managing filesystem snapshots in the Virtual Shell environment. It provides an easy-to-use interface for listing, exporting, importing, and deleting snapshots.

## Installation

Snapshots CLI is installed automatically with the Virtual Shell package:

```bash
pip install virtual-shell
```

## Basic Usage

### List Snapshots

View all available snapshots:

```bash
snapshot-cli list
```

Example output:
```
Filename                        Name                Created               Description
--------------------------------------------------------------------------------
initial_state.snapshot.json     initial_state       2024-03-15 10:30:45   Project start
working_copy.snapshot.json      working_copy        2024-03-16 14:22:11   Midproject checkpoint
```

### Export a Snapshot

Export a specific snapshot to a different location:

```bash
# Export to current directory
snapshot-cli export initial_state.snapshot.json

# Export to a specific path
snapshot-cli export initial_state.snapshot.json --output /path/to/backup/
```

### Import a Snapshot

Import a snapshot from an external file:

```bash
# Import from a file
snapshot-cli import /path/to/external/snapshot.json

# Import with a custom name
snapshot-cli import /path/to/external/snapshot.json --name custom_snapshot
```

### Delete a Snapshot

Remove an unwanted snapshot:

```bash
snapshot-cli delete initial_state.snapshot.json
```

## Advanced Usage

### Custom Snapshot Directory

By default, snapshots are stored in `~/.chuk_virtual_shell/snapshots`. You can specify a custom directory:

```bash
snapshot-cli --snapshot-dir /path/to/snapshots list
```

## Snapshot File Format

Snapshots are stored as JSON files with the following structure:

```json
{
    "metadata": {
        "name": "snapshot_name",
        "created": "timestamp",
        "description": "Snapshot description"
    },
    "snapshot": {
        "filesystem_state": { ... }
    }
}
```

## Best Practices

1. Regularly clean up old snapshots
2. Use descriptive names and descriptions
3. Store snapshots in a secure location
4. Be cautious when importing snapshots from untrusted sources

## Troubleshooting

- Ensure you have read/write permissions in the snapshot directory
- Check that snapshot files are valid JSON
- Verify the snapshot was created by the Virtual Shell

## Security Considerations

- Snapshots may contain sensitive file contents
- Protect snapshot files from unauthorized access
- Do not share snapshots containing sensitive information

## Limitations

- Snapshots are specific to the Virtual Shell environment
- Cannot directly restore snapshots to external filesystems
- Snapshot size is limited by available disk space

## Common Errors

- "Snapshot not found": Ensure the filename is correct
- "Invalid snapshot file": The JSON file is not a valid snapshot
- Permission errors: Check directory and file permissions

## Future Improvements

- Snapshot compression
- Encryption support
- Snapshot metadata search
- Snapshot versioning

## Support

For issues or feature requests, please file an issue on the project's GitHub repository.