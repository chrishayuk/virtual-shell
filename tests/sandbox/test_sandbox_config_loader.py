# tests/sandbox/test_sandbox_config_loader.py
import os
import tempfile
import yaml
import pytest

# imports
from chuk_virtual_shell.sandbox.loader.sandbox_config_loader import (
    load_config_file,
    find_config_file,
)

SAMPLE_CONFIG = {
    "name": "test_sandbox",
    "description": "Test sandbox configuration",
    "environment": {"HOME": "/test/home", "USER": "tester", "PATH": "/bin:/usr/bin"},
}


def test_load_config_file():
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as temp:
        yaml.dump(SAMPLE_CONFIG, temp)
        temp_path = temp.name

    try:
        config = load_config_file(temp_path)
        assert config["name"] == "test_sandbox"
        assert config["environment"]["HOME"] == "/test/home"
    finally:
        os.unlink(temp_path)


def test_find_config_file():
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = os.path.join(temp_dir, "test_sandbox.yaml")
        with open(config_path, "w") as f:
            yaml.dump(SAMPLE_CONFIG, f)

        # Patch os.getcwd to return our temporary directory.
        with pytest.MonkeyPatch().context() as mp:
            mp.setenv("CHUK_VIRTUAL_SHELL_CONFIG_DIR", temp_dir)
            found = find_config_file("test_sandbox")
            assert found is not None
            assert "test_sandbox.yaml" in found


def test_find_config_file_not_found():
    with pytest.MonkeyPatch().context() as mp:
        mp.setenv("CHUK_VIRTUAL_SHELL_CONFIG_DIR", "/nonexistent")
        found = find_config_file("nonexistent")
        assert found is None
