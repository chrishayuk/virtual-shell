# tests/sandbox/test_filesystem_initializer.py
import os
from unittest.mock import patch

# imports
from chuk_virtual_shell.sandbox.loader.filesystem_initializer import create_filesystem

# Create a sample config with security and filesystem-template sections.
SAMPLE_FS_CONFIG = {
    "security": {"profile": "default", "denied_patterns": ["\\.\\.", "^\\."]},
    "filesystem": {
        "provider": "memory",
        "provider_args": {"compression_threshold": 1024},
    },
    "filesystem-template": {
        "name": "python_project",
        "variables": {
            "project_name": "test_project",
            "project_description": "A test project",
            "project_version": "0.1.0",
        },
    },
}


def dummy_find_template(name: str) -> str:
    # Return a dummy path based on the name.
    return os.path.join("/dummy/templates", f"{name}.yaml")


@patch(
    "chuk_virtual_shell.sandbox.loader.filesystem_initializer._find_template",
    side_effect=dummy_find_template,
)
def test_create_filesystem(mock_find):
    fs = create_filesystem(SAMPLE_FS_CONFIG)
    # Verify that the filesystem is created (assuming VirtualFileSystem type check here).
    from chuk_virtual_fs import VirtualFileSystem

    assert isinstance(fs, VirtualFileSystem)
    # Check that denied patterns are compiled.
    denied = SAMPLE_FS_CONFIG["security"]["denied_patterns"]
    # Since they were modified in the config, verify at least that each pattern has a match method.
    for pattern in denied:
        assert hasattr(pattern, "match")
